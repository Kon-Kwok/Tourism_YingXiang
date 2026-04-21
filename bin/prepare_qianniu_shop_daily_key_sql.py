#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _to_decimal(value) -> Decimal:
    if value is None:
        return Decimal("0")
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"invalid numeric value: {value}")


def _extract_biz_date(summary: dict) -> str:
    deal_start = summary.get("deal_start")
    if not deal_start:
        raise ValueError("summary.deal_start is required")
    return str(deal_start)[:10]


def _format_decimal(value: Decimal) -> str:
    return str(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def _format_bigint(value: Decimal) -> str:
    normalized = value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if normalized != value:
        raise ValueError(f"value must be an integer for BIGINT column: {value}")
    return str(int(normalized))


def build_upsert_sql(payload: dict) -> str:
    summary = payload.get("summary") or {}

    total_page = int(summary.get("total_page") or 0)
    all_pages = bool(summary.get("all_pages"))
    if total_page > 1 and not all_pages:
        raise ValueError("summary.total_page > 1; current payload is paginated and cannot be upserted safely")

    biz_date = _extract_biz_date(summary)
    total_booking = _format_bigint(_to_decimal(summary.get("total_booking")))
    total_pax = _format_decimal(_to_decimal(summary.get("total_pax")))
    gmv = _format_decimal(_to_decimal(summary.get("gmv")))

    return (
        "INSERT INTO qianniu.qianniu_fliggy_shop_daily_key_data\n"
        "(`日期`, total_bookings, total_pax, gmv)\n"
        f"VALUES ('{biz_date}', {total_booking}, {total_pax}, {gmv})\n"
        "ON DUPLICATE KEY UPDATE\n"
        "total_bookings = VALUES(total_bookings),\n"
        "total_pax = VALUES(total_pax),\n"
        "gmv = VALUES(gmv);"
    )


def main() -> int:
    payload = json.load(sys.stdin)
    sql = build_upsert_sql(payload)
    sys.stdout.write(sql)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
