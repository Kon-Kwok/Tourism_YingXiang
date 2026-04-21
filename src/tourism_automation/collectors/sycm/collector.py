"""SYCM homepage collector."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from tourism_automation.collectors.sycm.client import SycmHomeClient
from tourism_automation.collectors.sycm.normalize import build_api_collection
from tourism_automation.shared.chrome import ChromeHttpClient


@dataclass
class HomePageCollector:
    http: ChromeHttpClient | None = None

    def collect(self, biz_date: str, shop_name: str) -> Dict[str, object]:
        overview_payload, trend_payload, table_payload = SycmHomeClient(self.http).fetch_home_payloads(biz_date)
        return build_api_collection(
            biz_date=biz_date,
            shop_name=shop_name,
            overview_payload=overview_payload,
            trend_payload=trend_payload,
            table_payload=table_payload,
            metric_source="chrome_cookie_http",
        )
