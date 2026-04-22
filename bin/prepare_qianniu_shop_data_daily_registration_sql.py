#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def _to_int(value) -> int:
    if value is None:
        return 0
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"invalid integer value: {value}")
    return int(decimal_value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def _extract_biz_date(payload: dict) -> str:
    summary = payload.get("summary") or {}
    biz_date = summary.get("biz_date") or payload.get("biz_date")
    if not biz_date:
        raise ValueError("biz_date is required")
    return str(biz_date)


def _extract_follow_count(payload: dict) -> int:
    rows = payload.get("rows")
    if rows:
        first_row = rows[0] or {}
        if "关注店铺人数" in first_row:
            return _to_int(first_row["关注店铺人数"])
    if "关注店铺人数" in payload:
        return _to_int(payload["关注店铺人数"])
    raise ValueError("关注店铺人数 is required")


def build_upsert_sql(payload: dict) -> str:
    biz_date = _extract_biz_date(payload)
    follow_count = _extract_follow_count(payload)
    return (
        "INSERT INTO qianniu.qianniu_shop_data_daily_registration\n"
        "(`日期`, `关注店铺人数`)\n"
        f"VALUES ('{biz_date}', {follow_count})\n"
        "ON DUPLICATE KEY UPDATE\n"
        "`关注店铺人数` = VALUES(`关注店铺人数`);"
    )


def main() -> int:
    payload = json.load(sys.stdin)
    sql = build_upsert_sql(payload)
    sys.stdout.write(sql)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
