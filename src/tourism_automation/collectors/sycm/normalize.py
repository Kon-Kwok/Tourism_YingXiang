"""Normalization helpers for SYCM homepage payloads."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, List


PAGE_CODE = "sycm_home"


def normalize_home_payloads(
    *,
    biz_date: str,
    shop_name: str,
    overview_payload: Dict[str, object],
    trend_payload: Dict[str, object],
    table_payload: Dict[str, object],
) -> Dict[str, List[Dict[str, object]]]:
    overview_self = overview_payload["content"]["data"]["self"]
    metrics: List[Dict[str, object]] = []
    for metric_code, metric_payload in overview_self.items():
        if metric_code == "statDate":
            continue
        if not isinstance(metric_payload, dict) or "value" not in metric_payload:
            continue
        metrics.append(
            {
                "biz_date": biz_date,
                "page_code": PAGE_CODE,
                "shop_name": shop_name,
                "metric_code": metric_code,
                "metric_value": _coerce_number(metric_payload.get("value")),
                "cycle_crc": _coerce_number(metric_payload.get("cycleCrc")),
                "sync_crc": _coerce_number(metric_payload.get("syncCrc")),
                "year_sync_crc": _coerce_number(metric_payload.get("yearSyncCrc")),
            }
        )
    metrics.sort(key=lambda item: item["metric_code"])

    trend_data = trend_payload["content"]["data"]
    stat_dates = trend_data["self"]["statDate"]
    metric_codes = sorted(
        key for key, value in trend_data["self"].items() if isinstance(value, list) and key != "statDate"
    )
    trends: List[Dict[str, object]] = []
    for metric_code in metric_codes:
        self_values = trend_data["self"][metric_code]
        rival_avg_values = trend_data.get("rivalAvg", {}).get(metric_code, [])
        rival_good_values = trend_data.get("rivalGood", {}).get(metric_code, [])
        for index, stat_date_ms in enumerate(stat_dates):
            trends.append(
                {
                    "biz_date": biz_date,
                    "page_code": PAGE_CODE,
                    "shop_name": shop_name,
                    "metric_code": metric_code,
                    "stat_date": _ms_to_date(stat_date_ms),
                    "self_value": _coerce_number(self_values[index]) if index < len(self_values) else None,
                    "rival_avg_value": _coerce_number(rival_avg_values[index]) if index < len(rival_avg_values) else None,
                    "rival_good_value": _coerce_number(rival_good_values[index]) if index < len(rival_good_values) else None,
                }
            )

    table_rows_payload = table_payload["content"]["data"]
    table_rows: List[Dict[str, object]] = []
    for row in table_rows_payload:
        stat_date_value = row.get("statDate", {}).get("value")
        normalized = {
            "biz_date": biz_date,
            "page_code": PAGE_CODE,
            "shop_name": shop_name,
            "stat_date": _ms_to_date(stat_date_value) if stat_date_value else biz_date,
        }
        for metric_code, metric_payload in row.items():
            if not isinstance(metric_payload, dict) or "value" not in metric_payload:
                continue
            normalized[metric_code] = _coerce_number(metric_payload.get("value"))
        table_rows.append(normalized)

    return {
        "summary": {
            "metric_source": "api",
            "shop_name": shop_name,
        },
        "metrics": metrics,
        "trends": trends,
        "table_rows": table_rows,
    }


def build_api_collection(*, biz_date: str, shop_name: str, overview_payload, trend_payload, table_payload, metric_source: str):
    payload = normalize_home_payloads(
        biz_date=biz_date,
        shop_name=shop_name,
        overview_payload=overview_payload,
        trend_payload=trend_payload,
        table_payload=table_payload,
    )
    payload["summary"]["metric_source"] = metric_source
    payload["raw_payloads"] = {
        "overview": overview_payload,
        "trend": trend_payload,
        "table": table_payload,
    }
    return payload


def _ms_to_date(timestamp_ms: int) -> str:
    china_tz = timezone(timedelta(hours=8))
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=china_tz).strftime("%Y-%m-%d")


def _coerce_number(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return None
