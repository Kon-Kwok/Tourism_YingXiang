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


def _format_bigint(value: Decimal) -> str:
    normalized = value.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    if normalized != value:
        raise ValueError(f"value must be an integer for BIGINT column: {value}")
    return str(int(normalized))


def build_update_sql(payload: dict) -> str:
    summary = payload.get("summary") or {}
    rows = payload.get("rows") or []

    biz_date = summary.get("biz_date")
    if not biz_date:
        raise ValueError("summary.biz_date is required")
    if len(rows) != 1:
        raise ValueError("rows must contain exactly one record")

    row = rows[0]
    total_uv = _format_bigint(_to_decimal(row.get("访客数")))
    total_pv = _format_bigint(_to_decimal(row.get("浏览量")))
    ad_uv = _format_bigint(_to_decimal(row.get("广告流量")))
    platform_uv = _format_bigint(_to_decimal(row.get("平台流量")))

    return (
        "INSERT INTO qianniu.qianniu_fliggy_shop_daily_key_data\n"
        "(`日期`, total_pv, total_uv, `流量来源广告_uv`, `流量来源平台_uv`)\n"
        f"VALUES ('{biz_date}', {total_pv}, {total_uv}, {ad_uv}, {platform_uv})\n"
        "ON DUPLICATE KEY UPDATE\n"
        "total_pv = VALUES(total_pv),\n"
        "total_uv = VALUES(total_uv),\n"
        "`流量来源广告_uv` = VALUES(`流量来源广告_uv`),\n"
        "`流量来源平台_uv` = VALUES(`流量来源平台_uv`);"
    )


def main() -> int:
    payload = json.load(sys.stdin)
    sql = build_update_sql(payload)
    sys.stdout.write(sql)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
