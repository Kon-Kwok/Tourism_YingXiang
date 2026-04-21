"""HTTP client helpers for the Fliggy home collector."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from tourism_automation.shared.chrome import ChromeHttpClient


REQUEST_SPECS = {
    "service_todos": [
        {
            "name": "todo_groups",
            "url": "https://fsc.fliggy.com/api/home/getTodoData",
            "required": True,
        },
        {
            "name": "todo_messages",
            "url": "https://fsc.fliggy.com/api/message/todomessages",
            "required": True,
        },
    ],
    "business_center": [
        {
            "name": "trade_measure",
            "url": (
                "https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure"
                "?compInterval=DAY&beginDate={biz_date}&endDate={biz_date}"
            ),
            "required": True,
        },
        {
            "name": "graph_measure",
            "url": "https://seller.fliggy.com/api/sycm/measure/front/graphMeasure?compInterval=THIRTY_DAY",
            "required": True,
        },
        {
            "name": "industry",
            "url": "https://seller.fliggy.com/api/sycm/measure/industry",
            "required": True,
        },
    ],
    "product_operation_center": [
        {
            "name": "shop_block",
            "url": "https://fsc.fliggy.com/api/home/shopBlock",
            "required": True,
        },
        {
            "name": "item_ability",
            "url": "https://sell.fliggy.com/icenter/itemability/ItemAbilityTotalPage.htm?&_input_charset=UTF-8&_output_charset=UTF-8",
            "required": True,
        },
        {
            "name": "dest_prefer",
            "url": "https://sell.fliggy.com/icenter/mci/ajx/GetDestPreferInfo.json?_input_charset=UTF-8&_output_charset=UTF-8",
            "required": True,
        },
    ],
    "merchant_growth": [
        {
            "name": "new_mci_info",
            "url": "https://sell.fliggy.com/icenter/mci/ajx/GetNewMciInfo.json?_input_charset=UTF-8&_output_charset=UTF-8",
            "required": True,
        },
        {
            "name": "home_mci_index",
            "url": "https://mci.fliggy.com/seller/service/homeMciIndex",
            "required": True,
        },
        {
            "name": "operator_center",
            "url": "https://seller.fliggy.com/api/sycm/measure/queryOperatorCenter",
            "required": False,
        },
        {
            "name": "excellent",
            "url": "https://seller.fliggy.com/api/sycm/measure/queryExcellent",
            "required": False,
        },
    ],
    "rule_center": [
        {
            "name": "rule_center",
            "url": "https://seller.fliggy.com/api/blocks/ruleCenter",
            "required": True,
        },
    ],
}


def build_module_request_specs(biz_date: str) -> dict[str, list[dict[str, Any]]]:
    requests_map = {}
    for module_name, specs in REQUEST_SPECS.items():
        requests_map[module_name] = [
            {
                **spec,
                "url": spec["url"].format(biz_date=biz_date),
            }
            for spec in specs
        ]
    return requests_map


def build_module_requests(biz_date: str) -> dict[str, list[str]]:
    return {
        module_name: [spec["url"] for spec in specs]
        for module_name, specs in build_module_request_specs(biz_date).items()
    }


@dataclass
class FliggyHomeClient:
    http: ChromeHttpClient

    @classmethod
    def from_local_chrome(cls) -> "FliggyHomeClient":
        return cls(http=ChromeHttpClient.from_local_chrome())

    def fetch_json(self, url: str):
        return self.http.fetch_json(url, referer="https://fsc.fliggy.com/#/new/home")

    def fetched_at(self) -> str:
        return datetime.now(timezone.utc).isoformat()
