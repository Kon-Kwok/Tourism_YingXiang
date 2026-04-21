# Fliggy Order List Deal Time Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add deal-time range support to `fliggy-order-list list`, defaulting to the current day when no range is passed.

**Architecture:** Extend the existing CLI to resolve a final `deal_start` / `deal_end` pair, pass those values through the collector into the HTTP client, and include them in normalized output. Keep the request shape consistent with the existing multipart form flow so current pagination and auth behavior remain unchanged.

**Tech Stack:** Python 3.10+, `argparse`, `datetime`, `unittest`, `requests`

---

### Task 1: Add CLI coverage for default and explicit deal-time ranges

**Files:**
- Modify: `tests/cli/test_main.py`
- Read: `src/tourism_automation/collectors/fliggy_order_list/cli.py`

- [ ] **Step 1: Write the failing tests**

```python
import unittest
from unittest import mock

from tourism_automation.cli.main import build_parser


class UnifiedCliTests(unittest.TestCase):
    def test_fliggy_order_list_list_uses_today_deal_range_defaults(self):
        parser = build_parser()

        with mock.patch("tourism_automation.collectors.fliggy_order_list.cli._now_local") as mock_now:
            mock_now.return_value.strftime.side_effect = ["2026-04-21", "2026-04-21"]

            args = parser.parse_args(["fliggy-order-list", "list"])

        self.assertEqual(args.deal_start, "2026-04-21 00:00:00")
        self.assertEqual(args.deal_end, "2026-04-21 23:59:59")

    def test_fliggy_order_list_list_accepts_explicit_deal_range(self):
        parser = build_parser()

        args = parser.parse_args(
            [
                "fliggy-order-list",
                "list",
                "--deal-start",
                "2026-04-07 00:00:00",
                "--deal-end",
                "2026-04-07 23:59:39",
            ]
        )

        self.assertEqual(args.deal_start, "2026-04-07 00:00:00")
        self.assertEqual(args.deal_end, "2026-04-07 23:59:39")
```

- [ ] **Step 2: Run the CLI tests to confirm they fail**

Run:

```bash
python3 -m unittest tests.cli.test_main -v
```

Expected: `AttributeError` or assertion failures because `deal_start` and `deal_end` are not wired into the CLI yet.

### Task 2: Add client and normalize coverage for deal-time fields

**Files:**
- Modify: `tests/collectors/test_fliggy_order_list.py`
- Read: `src/tourism_automation/collectors/fliggy_order_list/client.py`
- Read: `src/tourism_automation/collectors/fliggy_order_list/normalize.py`

- [ ] **Step 1: Write the failing client and normalize tests**

```python
    @mock.patch("tourism_automation.collectors.fliggy_order_list.client.ChromeHttpClient")
    def test_fetch_order_list_posts_deal_time_range(self, mock_http_cls):
        mock_http = mock.Mock()
        mock_http.session.cookies.get.return_value = "token-value"
        mock_http.session.post.return_value.text = (
            '\n{"success":true,"code":200,"result":{"orderList":[],"total":0,'
            '"totalPage":0,"requestParams":{}}}'
        )
        mock_http_cls.from_local_chrome.return_value = mock_http

        client = FliggyOrderListClient.from_local_chrome()
        client.fetch_order_list(
            page_num=1,
            page_size=10,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
        )

        files = mock_http.session.post.call_args.kwargs["files"]
        self.assertEqual(files["frTimeRange.min"], (None, "2026-04-07 00:00:00"))
        self.assertEqual(files["frTimeRange.max"], (None, "2026-04-07 23:59:39"))

    def test_normalize_order_list_payload_keeps_requested_deal_time_range(self):
        payload = {
            "orderList": [{"orderId": "1"}],
            "total": 1,
            "totalPage": 1,
            "requestParams": {},
        }

        normalized = normalize_order_list_payload(
            payload,
            page_num=1,
            page_size=10,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
        )

        self.assertEqual(normalized["summary"]["deal_start"], "2026-04-07 00:00:00")
        self.assertEqual(normalized["summary"]["deal_end"], "2026-04-07 23:59:39")
```

- [ ] **Step 2: Run the collector tests to confirm they fail**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: `TypeError` or assertion failures because `fetch_order_list()` and `normalize_order_list_payload()` do not accept deal-time arguments yet.

### Task 3: Implement CLI defaulting and validation

**Files:**
- Modify: `src/tourism_automation/collectors/fliggy_order_list/cli.py`
- Test: `tests/cli/test_main.py`

- [ ] **Step 1: Add minimal date helpers and arguments**

```python
from datetime import datetime


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _now_local() -> datetime:
    return datetime.now()


def _resolve_deal_range(deal_start: str | None, deal_end: str | None) -> tuple[str, str]:
    today = _now_local().strftime("%Y-%m-%d")
    resolved_start = deal_start or f"{today} 00:00:00"
    resolved_end = deal_end or f"{today} 23:59:59"
    start_dt = datetime.strptime(resolved_start, DATETIME_FORMAT)
    end_dt = datetime.strptime(resolved_end, DATETIME_FORMAT)
    if start_dt > end_dt:
        raise ValueError("deal_start must be earlier than or equal to deal_end")
    return resolved_start, resolved_end
```

- [ ] **Step 2: Wire resolved values into parser defaults and handler**

```python
    list_parser.add_argument("--deal-start", help="Deal time start in YYYY-MM-DD HH:MM:SS")
    list_parser.add_argument("--deal-end", help="Deal time end in YYYY-MM-DD HH:MM:SS")

    parser.set_defaults(handler=run)
```

and in `run()`:

```python
        deal_start, deal_end = _resolve_deal_range(args.deal_start, args.deal_end)
        payload = collect_order_list(
            page_num=args.page_num,
            page_size=args.page_size,
            biz_type=args.biz_type,
            sort_field_enum=args.sort_field_enum,
            deal_start=deal_start,
            deal_end=deal_end,
        )
```

- [ ] **Step 3: Re-run the CLI tests**

Run:

```bash
python3 -m unittest tests.cli.test_main -v
```

Expected: PASS

### Task 4: Implement client, collector, and normalize support for deal-time ranges

**Files:**
- Modify: `src/tourism_automation/collectors/fliggy_order_list/client.py`
- Modify: `src/tourism_automation/collectors/fliggy_order_list/collector.py`
- Modify: `src/tourism_automation/collectors/fliggy_order_list/normalize.py`
- Test: `tests/collectors/test_fliggy_order_list.py`

- [ ] **Step 1: Extend client and collector signatures**

```python
def fetch_order_list(
    self,
    *,
    page_num: int,
    page_size: int,
    biz_type: int = 0,
    sort_field_enum: str = "ORDER_CREATE_TIME_DESC",
    deal_start: str,
    deal_end: str,
) -> dict:
```

and:

```python
def collect_order_list(
    *,
    page_num: int,
    page_size: int,
    biz_type: int = 0,
    sort_field_enum: str = "ORDER_CREATE_TIME_DESC",
    deal_start: str,
    deal_end: str,
) -> dict:
```

- [ ] **Step 2: Add the multipart form fields for the deal-time range**

```python
            files={
                "_tb_token_": (None, token),
                "bizType": (None, str(biz_type)),
                "sortFieldEnum": (None, sort_field_enum),
                "pageNum": (None, str(page_num)),
                "pageSize": (None, str(page_size)),
                "frTimeRange.min": (None, deal_start),
                "frTimeRange.max": (None, deal_end),
            },
```

- [ ] **Step 3: Keep the resolved deal-time range in normalized output**

```python
def normalize_order_list_payload(
    payload: dict,
    *,
    page_num: int | None = None,
    page_size: int | None = None,
    deal_start: str | None = None,
    deal_end: str | None = None,
) -> dict:
    request_params = dict(payload.get("requestParams", {}))
    request_params.setdefault("frTimeRange.min", deal_start)
    request_params.setdefault("frTimeRange.max", deal_end)
    ...
    return {
        "summary": {
            "order_count": len(orders),
            "total": payload.get("total", 0),
            "total_page": payload.get("totalPage", 0),
            "page_num": request_params.get("pageNum", page_num),
            "page_size": request_params.get("pageSize", page_size),
            "deal_start": request_params.get("frTimeRange.min"),
            "deal_end": request_params.get("frTimeRange.max"),
        },
```

- [ ] **Step 4: Re-run the order-list tests**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: PASS

### Task 5: Verify end-to-end behavior from the CLI

**Files:**
- Read: `src/tourism_automation/collectors/fliggy_order_list/cli.py`
- Read: `src/tourism_automation/collectors/fliggy_order_list/client.py`

- [ ] **Step 1: Run the two targeted suites**

```bash
python3 -m unittest tests.cli.test_main tests.collectors.test_fliggy_order_list -v
```

Expected: PASS

- [ ] **Step 2: Run a real command with defaults**

```bash
python3 -m tourism_automation.cli.main fliggy-order-list list --page-num 1 --page-size 5
```

Expected: JSON output includes `summary.deal_start` / `summary.deal_end` for the current date.

- [ ] **Step 3: Run a real command with the requested explicit range**

```bash
python3 -m tourism_automation.cli.main fliggy-order-list list \
  --page-num 1 \
  --page-size 5 \
  --deal-start "2026-04-07 00:00:00" \
  --deal-end "2026-04-07 23:59:39"
```

Expected: JSON output includes the requested `deal_start` / `deal_end`, and `request_params` shows the same range.
