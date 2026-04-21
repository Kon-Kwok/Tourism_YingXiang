"""SYCM店铺来源采集器"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from tourism_automation.collectors.sycm.shop_source.client import ShopSourceClient
from tourism_automation.collectors.sycm.shop_source.normalize import normalize_shop_source_data
from tourism_automation.shared.chrome import ChromeHttpClient


@dataclass
class ShopSourceCollector:
    """店铺来源采集器"""
    http: ChromeHttpClient | None = None

    def collect(self, biz_date: str, shop_name: str = "default") -> Dict[str, object]:
        """采集店铺来源数据

        Args:
            biz_date: 业务日期，格式 "2026-04-19"
            shop_name: 店铺名称

        Returns:
            Dict: 包含summary和metrics的字典
        """
        client = ShopSourceClient(http=self.http)

        # 获取原始数据
        raw_data = client.fetch_menu_data(biz_date)

        # 规范化数据
        normalized_data = normalize_shop_source_data(raw_data, biz_date, shop_name)

        return {
            "summary": {
                "metric_source": "chrome_cookie_http",
                "shop_name": shop_name,
                "page_code": "shop_source",
                "collection_date": biz_date,
                "source_count": len(normalized_data)
            },
            "metrics": [item.to_dict() for item in normalized_data],
            "raw_payloads": {
                "menu_api": raw_data
            }
        }
