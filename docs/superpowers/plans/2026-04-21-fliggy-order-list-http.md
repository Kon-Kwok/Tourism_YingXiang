# Fliggy Order List HTTP Collector Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 新增一个纯 `HTTP + Cookie` 的飞猪订单列表采集器，并扩展共享 Chrome 会话以覆盖飞猪相关域名。

**Architecture:** 先把共享 Chrome cookie 会话从“SYCM 专用”扩展成“按域名集合加载”，再新增 `fliggy_order_list` 采集器模块。采集器通过共享会话自动读取 `_tb_token_`，发送 `multipart/form-data` 请求，解析以 `text/html` 返回的 JSON 字符串，并通过统一 CLI 输出订单列表与分页信息。

**Tech Stack:** Python 3.10+, `requests`, `argparse`, `unittest`, 本地 Chrome cookie 数据库

---

### Task 1: 扩展共享 Chrome 会话域名支持

**Files:**
- Modify: `src/tourism_automation/shared/chrome/session.py`
- Test: `tests/collectors/test_sycm.py`

- [ ] **Step 1: 写一个失败测试，证明共享会话不再只绑定 SYCM 域名**

```python
@mock.patch("tourism_automation.shared.chrome.session._read_chrome_safe_storage_secret", return_value="secret")
@mock.patch("tourism_automation.shared.chrome.session._read_cookie_db_version", return_value=24)
@mock.patch("tourism_automation.shared.chrome.session.sqlite3.connect")
def test_build_chrome_session_loads_fliggy_and_taobao_domains(
    self,
    mock_connect,
    _mock_version,
    _mock_secret,
):
    rows = [
        (".taobao.com", "_tb_token_", "token-value", b"", "/"),
        ("sell.fliggy.com", "cookie2", "cookie2-value", b"", "/"),
        ("fsc.fliggy.com", "JSESSIONID", "jsession", b"", "/"),
    ]
    mock_cursor = mock.Mock()
    mock_cursor.fetchall.return_value = rows
    mock_conn = mock.Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    session = build_chrome_session()

    self.assertEqual(session.cookies.get("_tb_token_"), "token-value")
    self.assertEqual(session.cookies.get("cookie2"), "cookie2-value")
    self.assertEqual(session.cookies.get("JSESSIONID"), "jsession")
```

- [ ] **Step 2: 运行测试，确认它先失败**

Run:

```bash
python3 -m unittest tests.collectors.test_sycm.ChromeCookieDecryptTests -v
```

Expected: 现有测试集里还没有这个用例，新增后应先因域名过滤逻辑不匹配而失败。

- [ ] **Step 3: 最小修改共享会话逻辑**

在 `session.py` 中：

- 抽出允许加载的 cookie 域名常量，例如 `CHROME_COOKIE_HOST_KEYS`
- 保留 `.taobao.com`
- 新增 `sell.fliggy.com`、`.fliggy.com`、`fsc.fliggy.com`、`seller.fliggy.com`
- SQL 查询改成基于这个集合过滤

关键代码方向：

```python
CHROME_COOKIE_HOST_KEYS = (
    "sycm.taobao.com",
    ".taobao.com",
    ".fliggy.com",
    "fsc.fliggy.com",
    "sell.fliggy.com",
    "seller.fliggy.com",
)
```

- [ ] **Step 4: 运行共享会话相关测试，确认通过**

Run:

```bash
python3 -m unittest tests.collectors.test_sycm -v
```

Expected: 共享会话与解密相关测试全部通过。

### Task 2: 为订单列表响应添加失败测试

**Files:**
- Create: `tests/collectors/test_fliggy_order_list.py`
- Read: `src/tourism_automation/collectors/fliggy_home/normalize.py`

- [ ] **Step 1: 写一个失败测试，覆盖 HTML 包裹 JSON 的响应解析**

```python
import unittest

from tourism_automation.collectors.fliggy_order_list.client import parse_order_list_response


class FliggyOrderListClientTests(unittest.TestCase):
    def test_parse_order_list_response_extracts_order_list_and_pagination(self):
        raw = '\\n\\n{"success":true,"code":200,"result":{"orderList":[{"orderId":"1"}],"total":35,"totalPage":4,"requestParams":{"pageNum":1}}}'

        parsed = parse_order_list_response(raw)

        self.assertEqual(parsed["orderList"][0]["orderId"], "1")
        self.assertEqual(parsed["total"], 35)
        self.assertEqual(parsed["totalPage"], 4)
        self.assertEqual(parsed["requestParams"]["pageNum"], 1)
```

- [ ] **Step 2: 运行测试，确认因模块缺失而失败**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: FAIL，提示 `fliggy_order_list.client` 或 `parse_order_list_response` 不存在。

- [ ] **Step 3: 创建最小 client 模块让测试转绿**

Create `src/tourism_automation/collectors/fliggy_order_list/client.py` with:

```python
from __future__ import annotations

import json


def parse_order_list_response(raw_text: str) -> dict:
    text = raw_text.lstrip()
    payload = json.loads(text)
    return payload["result"]
```

- [ ] **Step 4: 运行订单列表解析测试**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: PASS

### Task 3: 写请求层失败测试并实现纯 HTTP 调用

**Files:**
- Modify: `src/tourism_automation/collectors/fliggy_order_list/client.py`
- Modify: `tests/collectors/test_fliggy_order_list.py`

- [ ] **Step 1: 为请求参数与 `_tb_token_` 自动读取写失败测试**

```python
from unittest import mock

from tourism_automation.collectors.fliggy_order_list.client import FliggyOrderListClient


@mock.patch("tourism_automation.collectors.fliggy_order_list.client.ChromeHttpClient")
def test_fetch_order_list_posts_multipart_form_with_cookie_token(self, mock_http_cls):
    mock_http = mock.Mock()
    mock_http.session.cookies.get.return_value = "token-value"
    mock_http.session.post.return_value.text = '\\n{"success":true,"code":200,"result":{"orderList":[],"total":0,"totalPage":0,"requestParams":{"pageNum":1}}}'
    mock_http.session.post.return_value.status_code = 200
    mock_http.session.post.return_value.headers = {"content-type": "text/html;charset=UTF-8"}
    mock_http_cls.from_local_chrome.return_value = mock_http

    client = FliggyOrderListClient.from_local_chrome()
    result = client.fetch_order_list(page_num=1, page_size=10)

    self.assertEqual(result["requestParams"]["pageNum"], 1)
    mock_http.session.post.assert_called_once()
```

- [ ] **Step 2: 运行测试，确认失败**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: FAIL，因为 `FliggyOrderListClient` 还不存在。

- [ ] **Step 3: 实现最小请求层**

在 `client.py` 中补齐：

- `ORDER_LIST_URL`
- `FliggyOrderListClient`
- `from_local_chrome()`
- `_get_tb_token()`
- `fetch_order_list()`

请求实现要求：

```python
response = self.http.session.post(
    ORDER_LIST_URL,
    headers={
        "Referer": "https://fsc.fliggy.com/",
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
    },
    files={
        "_tb_token_": (None, token),
        "bizType": (None, str(biz_type)),
        "sortFieldEnum": (None, sort_field_enum),
        "pageNum": (None, str(page_num)),
        "pageSize": (None, str(page_size)),
    },
    timeout=20,
)
```

- [ ] **Step 4: 增加登录页和非法 JSON 的错误测试**

再补两个测试：

- 登录页 HTML 返回时抛出认证错误
- 非法 JSON 返回时抛出带响应预览的错误

- [ ] **Step 5: 跑订单列表测试集**

Run:

```bash
python3 -m unittest tests.collectors.test_fliggy_order_list -v
```

Expected: PASS

### Task 4: 新增 collector / normalize / CLI 失败测试并接入统一入口

**Files:**
- Create: `src/tourism_automation/collectors/fliggy_order_list/__init__.py`
- Create: `src/tourism_automation/collectors/fliggy_order_list/collector.py`
- Create: `src/tourism_automation/collectors/fliggy_order_list/normalize.py`
- Create: `src/tourism_automation/collectors/fliggy_order_list/cli.py`
- Modify: `src/tourism_automation/cli/main.py`
- Modify: `tests/cli/test_main.py`
- Modify: `tests/collectors/test_fliggy_order_list.py`

- [ ] **Step 1: 写 CLI 接线失败测试**

```python
def test_build_parser_registers_fliggy_order_list_collector(self):
    parser = build_parser()
    collector_action = next(action for action in parser._actions if action.dest == "collector")

    self.assertIn("fliggy-order-list", collector_action.choices.keys())
```

- [ ] **Step 2: 写 normalize 失败测试**

```python
from tourism_automation.collectors.fliggy_order_list.normalize import normalize_order_list_payload


def test_normalize_order_list_payload_keeps_orders_and_pagination(self):
    payload = {
        "orderList": [{"orderId": "1"}],
        "total": 35,
        "totalPage": 4,
        "requestParams": {"pageNum": 1},
    }

    normalized = normalize_order_list_payload(payload)

    self.assertEqual(normalized["summary"]["order_count"], 1)
    self.assertEqual(normalized["summary"]["total"], 35)
    self.assertEqual(normalized["orders"][0]["orderId"], "1")
```

- [ ] **Step 3: 运行相关测试，确认先失败**

Run:

```bash
python3 -m unittest tests.cli.test_main tests.collectors.test_fliggy_order_list -v
```

Expected: FAIL，因为 CLI 和 normalize 还未接入。

- [ ] **Step 4: 实现最小 collector / normalize / cli**

实现要求：

- `collector.py` 提供 `collect_order_list(...)`
- `normalize.py` 输出：
  - `summary.order_count`
  - `summary.total`
  - `summary.total_page`
  - `summary.page_num`
  - `summary.page_size`
  - `orders`
  - `request_params`
- `cli.py` 注册：

```bash
fliggy-order-list list --page-num 1 --page-size 10
```

- `main.py` 注册 `fliggy-order-list`

- [ ] **Step 5: 运行 CLI 与订单列表测试**

Run:

```bash
python3 -m unittest tests.cli.test_main tests.collectors.test_fliggy_order_list -v
```

Expected: PASS

### Task 5: 端到端验证与文档补充

**Files:**
- Modify: `docs/README.md`
- Modify: `README.md`

- [ ] **Step 1: 补充文档入口**

在 `docs/README.md` 和 `README.md` 中加入：

- `fliggy-order-list` 命令示例
- 这是纯 `HTTP + Cookie` 实现，不依赖运行时 CDP

- [ ] **Step 2: 运行完整相关测试**

Run:

```bash
python3 -m unittest tests.collectors.test_sycm tests.collectors.test_fliggy_order_list tests.cli.test_main -v
```

Expected: PASS

- [ ] **Step 3: 运行一次本地命令做真实验证**

Run:

```bash
python3 -m tourism_automation.cli.main fliggy-order-list list --page-num 1 --page-size 10
```

Expected: 返回包含 `summary`、`orders`、`request_params` 的 JSON，且 `summary.order_count` 大于等于 0。
