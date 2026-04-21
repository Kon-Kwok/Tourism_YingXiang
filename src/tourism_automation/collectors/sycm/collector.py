"""SYCM homepage collector."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Dict

from tourism_automation.collectors.sycm.client import SycmHomeClient
from tourism_automation.collectors.sycm.normalize import build_api_collection
from tourism_automation.collectors.sycm.universal_client import UniversalSycmClient
from tourism_automation.shared.chrome import ChromeHttpClient


@dataclass
class HomePageCollector:
    http: ChromeHttpClient | None = None

    def collect(self, biz_date: str, shop_name: str) -> Dict[str, object]:
        overview_payload, trend_payload, table_payload = SycmHomeClient(self.http).fetch_home_payloads(biz_date)
        overview_payload, trend_payload, table_payload = _apply_flow_monitor_fallback(
            http=self.http,
            biz_date=biz_date,
            overview_payload=overview_payload,
            trend_payload=trend_payload,
            table_payload=table_payload,
        )
        return build_api_collection(
            biz_date=biz_date,
            shop_name=shop_name,
            overview_payload=overview_payload,
            trend_payload=trend_payload,
            table_payload=table_payload,
            metric_source="chrome_cookie_http",
        )


PRIMARY_METRICS = ("payAmt", "uv", "payByrCnt", "pv")


def _apply_flow_monitor_fallback(
    *,
    http: ChromeHttpClient | None,
    biz_date: str,
    overview_payload: Dict[str, object],
    trend_payload: Dict[str, object],
    table_payload: Dict[str, object],
) -> tuple[Dict[str, object], Dict[str, object], Dict[str, object]]:
    if not _needs_flow_monitor_fallback(
        biz_date=biz_date,
        overview_payload=overview_payload,
        table_payload=table_payload,
    ):
        return overview_payload, trend_payload, table_payload

    compare_date = datetime.strptime(biz_date, "%Y-%m-%d") - timedelta(days=1)
    date_range = (
        f"{compare_date.strftime('%Y-%m-%d')}|{biz_date},"
        f"{biz_date}|{biz_date}"
    )
    page_result = UniversalSycmClient(http).fetch_page_endpoint(
        page_id="flow_monitor",
        endpoint_name="overview",
        date_range=date_range,
        device="2",
    )
    flow_metrics = page_result.data.get("data", {}) if page_result.status == "success" else {}
    if not _has_meaningful_flow_metrics(flow_metrics):
        return overview_payload, trend_payload, table_payload

    _merge_overview_metrics(overview_payload, flow_metrics)
    _merge_trend_metrics(trend_payload, biz_date, flow_metrics)
    _merge_table_metrics(table_payload, biz_date, flow_metrics)
    return overview_payload, trend_payload, table_payload


def _needs_flow_monitor_fallback(
    *,
    biz_date: str,
    overview_payload: Dict[str, object],
    table_payload: Dict[str, object],
) -> bool:
    overview_self = overview_payload.get("content", {}).get("data", {}).get("self", {})
    if _has_meaningful_primary_metrics(overview_self):
        return False

    for row in table_payload.get("content", {}).get("data", []):
        stat_date = row.get("statDate", {}).get("value")
        if stat_date and _ms_to_date(stat_date) == biz_date:
            return _is_placeholder_metric_row(row)
    return True


def _has_meaningful_primary_metrics(metrics: Dict[str, object]) -> bool:
    if not isinstance(metrics, dict):
        return False
    return any(
        _read_metric_value(metrics.get(metric_code)) not in (None, 0.0)
        for metric_code in PRIMARY_METRICS
    )


def _has_meaningful_flow_metrics(metrics: Dict[str, object]) -> bool:
    if not isinstance(metrics, dict):
        return False
    return any(
        _read_metric_value(metrics.get(metric_code)) not in (None, 0.0)
        for metric_code in PRIMARY_METRICS
    )


def _is_placeholder_metric_row(row: Dict[str, object]) -> bool:
    return all(
        _read_metric_value(row.get(metric_code)) in (None, 0.0)
        for metric_code in PRIMARY_METRICS
    )


def _merge_overview_metrics(overview_payload: Dict[str, object], flow_metrics: Dict[str, object]) -> None:
    data = overview_payload.setdefault("content", {}).setdefault("data", {})
    overview_self = data.setdefault("self", {})
    for metric_code, metric_payload in flow_metrics.items():
        value = _read_metric_value(metric_payload)
        if value is None:
            continue
        existing = overview_self.get(metric_code)
        if isinstance(existing, dict):
            existing["value"] = value
        else:
            overview_self[metric_code] = {"value": value}


def _merge_trend_metrics(trend_payload: Dict[str, object], biz_date: str, flow_metrics: Dict[str, object]) -> None:
    trend_data = trend_payload.setdefault("content", {}).setdefault("data", {})
    trend_self = trend_data.setdefault("self", {})
    stat_dates = trend_self.get("statDate", [])
    target_index = _find_stat_date_index(stat_dates, biz_date)
    if target_index is None:
        return

    for metric_code, metric_payload in flow_metrics.items():
        value = _read_metric_value(metric_payload)
        if value is None:
            continue
        series = trend_self.setdefault(metric_code, [None] * len(stat_dates))
        if len(series) < len(stat_dates):
            series.extend([None] * (len(stat_dates) - len(series)))
        series[target_index] = value


def _merge_table_metrics(table_payload: Dict[str, object], biz_date: str, flow_metrics: Dict[str, object]) -> None:
    for row in table_payload.get("content", {}).get("data", []):
        stat_date = row.get("statDate", {}).get("value")
        if stat_date and _ms_to_date(stat_date) == biz_date:
            for metric_code, metric_payload in flow_metrics.items():
                value = _read_metric_value(metric_payload)
                if value is None:
                    continue
                existing = row.get(metric_code)
                if isinstance(existing, dict):
                    existing["value"] = value
                else:
                    row[metric_code] = {"value": value}
            return


def _find_stat_date_index(stat_dates: object, biz_date: str) -> int | None:
    if not isinstance(stat_dates, list):
        return None
    for index, stat_date in enumerate(stat_dates):
        if isinstance(stat_date, (int, float)) and _ms_to_date(int(stat_date)) == biz_date:
            return index
    return None


def _read_metric_value(metric_payload: object) -> float | None:
    if not isinstance(metric_payload, dict) or "value" not in metric_payload:
        return None
    value = metric_payload.get("value")
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _ms_to_date(timestamp_ms: int) -> str:
    china_tz = timezone(timedelta(hours=8))
    return datetime.fromtimestamp(timestamp_ms / 1000, tz=china_tz).strftime("%Y-%m-%d")
