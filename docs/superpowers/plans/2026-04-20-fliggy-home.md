# Fliggy Home Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a `fliggy_home` collector that reuses local Chrome login state to fetch and normalize the `https://fsc.fliggy.com/#/new/home` data for five homepage modules.

**Architecture:** Add a new `fliggy_home/` package parallel to `sycm/`, reusing the Chrome cookie HTTP capability from `sycm.chrome_http`. Fetch five fixed module groups from `fsc.fliggy.com`, `seller.fliggy.com`, `sell.fliggy.com`, and `mci.fliggy.com`, normalize them into a stable JSON shape, and tolerate partial module failures without failing the whole command.

**Tech Stack:** Python 3, standard library `unittest`, `requests`, existing Chrome cookie/session helpers

---

### Task 1: Add failing tests for fliggy homepage normalization and partial-failure aggregation

**Files:**
- Create: `tests/test_fliggy_home.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from fliggy_home.home import (
    normalize_service_todos,
    normalize_business_center,
    build_collect_result,
)


class FliggyHomeNormalizeTests(unittest.TestCase):
    def test_normalize_service_todos_extracts_visible_counts(self):
        todo_payload = {
            "code": "200",
            "data": {
                "riskCount": 0,
                "violationCount": 0,
                "certificateConfirmCount": 0,
                "activityInvitationCount": 0,
                "badCommentCount": 4,
            },
        }
        message_payload = {
            "code": "200",
            "data": [{"title": "待回复差评", "count": 4}],
        }

        result = normalize_service_todos(todo_payload, message_payload)

        self.assertEqual(result["pending_warning_count"], 0)
        self.assertEqual(result["pending_violation_count"], 0)
        self.assertEqual(result["pending_bad_review_reply_count"], 4)

    def test_normalize_business_center_extracts_trade_summary(self):
        trade_payload = {
            "success": True,
            "data": {
                "statDate": "2026-04-19",
                "totalPayAmt": 40552.99,
                "totalPayAmtChange": 0.853,
                "cruisePayAmt": 40552.99,
                "fulfilAmt": 0,
            },
        }
        graph_payload = {
            "success": True,
            "data": [{"date": "2026-04-19", "totalPayAmt": 40552.99}],
        }
        industry_payload = {
            "success": True,
            "data": {"industryName": "邮轮", "operatorCenterGray": False},
        }

        result = normalize_business_center(trade_payload, graph_payload, industry_payload)

        self.assertEqual(result["stat_date"], "2026-04-19")
        self.assertEqual(result["total_pay_amount"], 40552.99)
        self.assertEqual(result["cruise_pay_amount"], 40552.99)
        self.assertEqual(result["trend_points"], 1)

    def test_build_collect_result_keeps_partial_failures(self):
        modules = {
            "service_todos": {"status": "ok", "raw": {}, "normalized": {"pending_bad_review_reply_count": 4}, "fetched_at": "2026-04-20T10:00:00Z"},
            "business_center": {"status": "error", "error": {"message": "HTTP 500", "endpoint": "https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure", "http_status": 500}, "raw": None, "normalized": None, "fetched_at": "2026-04-20T10:00:00Z"},
        }

        result = build_collect_result(shop_name="皇家加勒比国际游轮旗舰店", modules=modules)

        self.assertEqual(result["summary"]["modules_requested"], 2)
        self.assertEqual(result["summary"]["modules_succeeded"], 1)
        self.assertEqual(result["summary"]["modules_failed"], 1)
        self.assertEqual(result["errors"][0]["module"], "business_center")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_fliggy_home -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'fliggy_home'`

- [ ] **Step 3: Write minimal implementation**

```python
# fliggy_home/home.py
def normalize_service_todos(todo_payload, message_payload):
    return {
        "pending_warning_count": todo_payload["data"]["riskCount"],
        "pending_violation_count": todo_payload["data"]["violationCount"],
        "pending_bad_review_reply_count": todo_payload["data"]["badCommentCount"],
        "items": message_payload["data"],
    }


def normalize_business_center(trade_payload, graph_payload, industry_payload):
    data = trade_payload["data"]
    return {
        "stat_date": data["statDate"],
        "total_pay_amount": data["totalPayAmt"],
        "total_pay_amount_change": data["totalPayAmtChange"],
        "cruise_pay_amount": data["cruisePayAmt"],
        "fulfil_amount": data["fulfilAmt"],
        "industry_name": industry_payload["data"]["industryName"],
        "trend_points": len(graph_payload["data"]),
    }


def build_collect_result(*, shop_name, modules):
    succeeded = sum(1 for item in modules.values() if item["status"] == "ok")
    failed = sum(1 for item in modules.values() if item["status"] == "error")
    errors = [
        {"module": module_name, **module_payload["error"]}
        for module_name, module_payload in modules.items()
        if module_payload["status"] == "error"
    ]
    return {
        "summary": {
            "source": "chrome_cookie_http",
            "shop_name": shop_name,
            "modules_requested": len(modules),
            "modules_succeeded": succeeded,
            "modules_failed": failed,
        },
        **modules,
        "errors": errors,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_fliggy_home -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_fliggy_home.py fliggy_home/home.py
git commit -m "feat: add fliggy homepage normalization"
```

### Task 2: Implement HTTP client and five module fetchers for the Fliggy homepage

**Files:**
- Create: `fliggy_home/__init__.py`
- Create: `fliggy_home/client.py`
- Modify: `fliggy_home/home.py`
- Test: `tests/test_fliggy_home.py`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from fliggy_home.client import build_module_requests


class FliggyHomeRequestTests(unittest.TestCase):
    def test_build_module_requests_contains_expected_endpoints(self):
        requests_map = build_module_requests("2026-04-19")

        self.assertEqual(
            requests_map["service_todos"],
            [
                "https://fsc.fliggy.com/api/home/getTodoData",
                "https://fsc.fliggy.com/api/message/todomessages",
            ],
        )
        self.assertIn(
            "https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure?compInterval=DAY&beginDate=2026-04-19&endDate=2026-04-19",
            requests_map["business_center"],
        )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_fliggy_home.FliggyHomeRequestTests -v`
Expected: FAIL with `ImportError` or missing function

- [ ] **Step 3: Write minimal implementation**

```python
# fliggy_home/client.py
from dataclasses import dataclass
from datetime import datetime, timezone

from sycm.chrome_http import ChromeHttpClient


def build_module_requests(biz_date: str):
    return {
        "service_todos": [
            "https://fsc.fliggy.com/api/home/getTodoData",
            "https://fsc.fliggy.com/api/message/todomessages",
        ],
        "business_center": [
            f"https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure?compInterval=DAY&beginDate={biz_date}&endDate={biz_date}",
            "https://seller.fliggy.com/api/sycm/measure/front/graphMeasure?compInterval=THIRTY_DAY",
            "https://seller.fliggy.com/api/sycm/measure/industry",
        ],
        "product_operation_center": [
            "https://fsc.fliggy.com/api/home/shopBlock",
            "https://sell.fliggy.com/icenter/itemability/ItemAbilityTotalPage.htm?&_input_charset=UTF-8&_output_charset=UTF-8",
            "https://sell.fliggy.com/icenter/mci/ajx/GetDestPreferInfo.json?_input_charset=UTF-8&_output_charset=UTF-8",
        ],
        "merchant_growth": [
            "https://sell.fliggy.com/icenter/mci/ajx/GetNewMciInfo.json?_input_charset=UTF-8&_output_charset=UTF-8",
            "https://mci.fliggy.com/seller/service/homeMciIndex",
        ],
        "rule_center": [
            "https://seller.fliggy.com/api/blocks/ruleCenter",
        ],
    }


@dataclass
class FliggyHomeClient:
    http: ChromeHttpClient

    @classmethod
    def from_local_chrome(cls):
        return cls(http=ChromeHttpClient.from_local_chrome())

    def fetch_json(self, url: str):
        return self.http.fetch_json(url, referer="https://fsc.fliggy.com/#/new/home")

    def fetched_at(self) -> str:
        return datetime.now(timezone.utc).isoformat()
```

```python
# fliggy_home/home.py
from fliggy_home.client import build_module_requests, FliggyHomeClient


def collect_home(*, shop_name: str, biz_date: str):
    client = FliggyHomeClient.from_local_chrome()
    requests_map = build_module_requests(biz_date)
    modules = {}
    for module_name, urls in requests_map.items():
        try:
            payloads = [client.fetch_json(url) for url in urls]
            modules[module_name] = {
                "status": "ok",
                "raw": payloads,
                "normalized": {"request_count": len(payloads)},
                "fetched_at": client.fetched_at(),
            }
        except Exception as exc:
            modules[module_name] = {
                "status": "error",
                "raw": None,
                "normalized": None,
                "error": {
                    "message": str(exc),
                    "endpoint": urls[0],
                    "http_status": None,
                },
                "fetched_at": client.fetched_at(),
            }
    return build_collect_result(shop_name=shop_name, modules=modules)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_fliggy_home -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add fliggy_home/__init__.py fliggy_home/client.py fliggy_home/home.py tests/test_fliggy_home.py
git commit -m "feat: add fliggy homepage request client"
```

### Task 3: Replace request-count placeholders with real module normalization and add CLI entrypoint

**Files:**
- Create: `fliggy_home/cli.py`
- Modify: `fliggy_home/home.py`
- Modify: `tests/test_fliggy_home.py`
- Docs: `docs/sycm-collector.md`

- [ ] **Step 1: Write the failing test**

```python
import unittest

from fliggy_home.home import normalize_rule_center


class FliggyHomeRuleTests(unittest.TestCase):
    def test_normalize_rule_center_extracts_rule_cards(self):
        payload = {
            "success": True,
            "data": [
                {"typeName": "规则公示", "title": "关于调整“包车”“接送”商品发布范围的通知", "gmtCreateDesc": "2026-04-17"},
                {"typeName": "营销规则", "title": "2026年飞猪全球旅行节活动招商规则", "gmtCreateDesc": "2026-02-14"},
            ],
        }

        result = normalize_rule_center(payload)

        self.assertEqual(result["items"][0]["category"], "规则公示")
        self.assertEqual(result["items"][0]["title"], "关于调整“包车”“接送”商品发布范围的通知")
        self.assertEqual(result["items"][1]["published_at"], "2026-02-14")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_fliggy_home.FliggyHomeRuleTests -v`
Expected: FAIL with missing `normalize_rule_center`

- [ ] **Step 3: Write minimal implementation**

```python
# fliggy_home/home.py
def normalize_rule_center(payload):
    items = []
    for index, item in enumerate(payload.get("data", []), start=1):
        items.append(
            {
                "category": item.get("typeName"),
                "title": item.get("title"),
                "published_at": item.get("gmtCreateDesc"),
                "order": index,
            }
        )
    return {"items": items}
```

```python
# fliggy_home/cli.py
import argparse
import json

from fliggy_home.home import collect_home


def build_parser():
    parser = argparse.ArgumentParser(description="Fliggy homepage collector")
    subparsers = parser.add_subparsers(dest="command", required=True)
    collect = subparsers.add_parser("collect-home", help="Collect Fliggy seller homepage data")
    collect.add_argument("--date", default="2026-04-19")
    collect.add_argument("--shop-name", default="飞猪商家店铺")
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "collect-home":
        print(json.dumps(collect_home(shop_name=args.shop_name, biz_date=args.date), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
```

```markdown
<!-- docs/sycm-collector.md -->
Add one short section:

## Parallel Collectors

- `python3 -m sycm.cli collect-home --date YYYY-MM-DD --shop-name "..."`
- `python3 -m fliggy_home.cli collect-home --date YYYY-MM-DD --shop-name "..."`
```

- [ ] **Step 4: Run tests and live verification**

Run: `python3 -m unittest discover -s tests -v`
Expected: PASS

Run: `python3 -m fliggy_home.cli collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"`
Expected: JSON with top-level keys `summary`, `service_todos`, `business_center`, `product_operation_center`, `merchant_growth`, `rule_center`, `errors`

- [ ] **Step 5: Commit**

```bash
git add fliggy_home/cli.py fliggy_home/home.py tests/test_fliggy_home.py docs/sycm-collector.md
git commit -m "feat: add fliggy homepage collector"
```
