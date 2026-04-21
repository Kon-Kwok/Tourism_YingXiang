import unittest
from unittest import mock
from requests.cookies import RequestsCookieJar

from tourism_automation.collectors.fliggy_order_list.client import (
    FliggyOrderListClient,
    ORDER_LIST_RETRY_DELAY_SECONDS,
    parse_order_list_response,
)
from tourism_automation.collectors.fliggy_order_list.collector import collect_order_list
from tourism_automation.collectors.fliggy_order_list.normalize import normalize_order_list_payload


class FliggyOrderListClientTests(unittest.TestCase):
    def test_parse_order_list_response_extracts_order_list_and_pagination(self):
        raw = '\n\n{"success":true,"code":200,"result":{"orderList":[{"orderId":"1"}],"total":35,"totalPage":4,"requestParams":{"pageNum":1}}}'

        parsed = parse_order_list_response(raw)

        self.assertEqual(parsed["orderList"][0]["orderId"], "1")
        self.assertEqual(parsed["total"], 35)
        self.assertEqual(parsed["totalPage"], 4)
        self.assertEqual(parsed["requestParams"]["pageNum"], 1)

    @mock.patch("tourism_automation.collectors.fliggy_order_list.client.ChromeHttpClient")
    def test_fetch_order_list_posts_multipart_form_with_cookie_token(self, mock_http_cls):
        mock_http = mock.Mock()
        mock_http.session.cookies.get.return_value = "token-value"
        mock_http.session.post.return_value.text = (
            '\n{"success":true,"code":200,"result":{"orderList":[],"total":0,'
            '"totalPage":0,"requestParams":{"pageNum":1}}}'
        )
        mock_http.session.post.return_value.status_code = 200
        mock_http.session.post.return_value.headers = {"content-type": "text/html;charset=UTF-8"}
        mock_http_cls.from_local_chrome.return_value = mock_http

        client = FliggyOrderListClient.from_local_chrome()
        result = client.fetch_order_list(
            page_num=1,
            page_size=10,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
        )

        self.assertEqual(result["requestParams"]["pageNum"], 1)
        mock_http.session.post.assert_called_once()
        files = mock_http.session.post.call_args.kwargs["files"]
        self.assertEqual(
            files,
            [
                ("_tb_token_", (None, "token-value")),
                ("bizType", (None, "0")),
                ("sortFieldEnum", (None, "ORDER_CREATE_TIME_DESC")),
                ("pageNum", (None, "1")),
                ("pageSize", (None, "10")),
                ("orderCreateTime", (None, "2026-04-07 00:00:00~2026-04-07 23:59:39")),
            ],
        )

    @mock.patch("tourism_automation.collectors.fliggy_order_list.client.time.sleep")
    @mock.patch("tourism_automation.collectors.fliggy_order_list.client.ChromeHttpClient")
    def test_fetch_order_list_retries_transient_search_failure(self, mock_http_cls, mock_sleep):
        mock_http = mock.Mock()
        mock_http.session.cookies.get.return_value = "token-value"
        mock_http.session.post.side_effect = [
            mock.Mock(
                text='{"success":true,"code":200,"result":{"success":false,"errorMsg":"订单搜索失败，请稍后再试","orderList":[],"total":0,"totalPage":0}}'
            ),
            mock.Mock(
                text='{"success":true,"code":200,"result":{"success":true,"orderList":[{"orderId":"1"}],"total":1,"totalPage":1,"requestParams":{"pageNum":1}}}'
            ),
        ]
        mock_http_cls.from_local_chrome.return_value = mock_http

        client = FliggyOrderListClient.from_local_chrome()
        result = client.fetch_order_list(
            page_num=1,
            page_size=10,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
        )

        self.assertEqual(result["orderList"][0]["orderId"], "1")
        self.assertEqual(mock_http.session.post.call_count, 2)
        mock_sleep.assert_called_once_with(ORDER_LIST_RETRY_DELAY_SECONDS)

    def test_get_tb_token_prefers_fliggy_cookie_when_multiple_tokens_exist(self):
        cookie_jar = RequestsCookieJar()
        cookie_jar.set("_tb_token_", "taobao-token", domain="taobao.com", path="/")
        cookie_jar.set("_tb_token_", "fliggy-token", domain="fliggy.com", path="/")
        http = mock.Mock()
        http.session.cookies = cookie_jar

        client = FliggyOrderListClient(http=http)

        self.assertEqual(client._get_tb_token(), "fliggy-token")

    def test_parse_order_list_response_rejects_login_page_html(self):
        with self.assertRaisesRegex(RuntimeError, "authentication"):
            parse_order_list_response("<!doctype html><html><title>登录</title></html>")

    def test_parse_order_list_response_includes_preview_for_invalid_json(self):
        with self.assertRaisesRegex(RuntimeError, "not-json-response"):
            parse_order_list_response("not-json-response")


class FliggyOrderListNormalizeTests(unittest.TestCase):
    def test_normalize_order_list_payload_keeps_rows_and_pagination(self):
        payload = {
            "orderList": [
                {
                    "orderId": "1",
                    "itemInfo": {
                        "skuText": [
                            {"name": "套餐类型：", "value": "家庭阳台房3D3人房"},
                        ]
                    },
                    "payInfo": {"buyMount": 3, "actualFee": "￥9367.01"},
                }
            ],
            "total": 35,
            "totalPage": 4,
            "requestParams": {"pageNum": 1, "pageSize": 10},
        }

        normalized = normalize_order_list_payload(payload)

        self.assertEqual(normalized["summary"]["order_count"], 1)
        self.assertEqual(normalized["summary"]["total"], 35)
        self.assertEqual(normalized["summary"]["total_page"], 4)
        self.assertEqual(normalized["summary"]["page_num"], 1)
        self.assertEqual(normalized["summary"]["page_size"], 10)
        self.assertNotIn("request_params", normalized)
        self.assertEqual(normalized["rows"][0]["orderId"], "1")
        self.assertEqual(normalized["rows"][0]["package_type"], "家庭阳台房3D3人房")
        self.assertEqual(normalized["rows"][0]["buy_mount"], 3)
        self.assertEqual(normalized["rows"][0]["actual_fee"], "￥9367.01")

    def test_normalize_order_list_payload_uses_requested_paging_when_response_omits_it(self):
        payload = {
            "orderList": [{"orderId": "1"}],
            "total": 35,
            "totalPage": 4,
            "requestParams": {},
        }

        normalized = normalize_order_list_payload(
            payload,
            page_num=2,
            page_size=50,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
        )

        self.assertEqual(normalized["summary"]["page_num"], 2)
        self.assertEqual(normalized["summary"]["page_size"], 50)
        self.assertEqual(normalized["summary"]["deal_start"], "2026-04-07 00:00:00")
        self.assertEqual(normalized["summary"]["deal_end"], "2026-04-07 23:59:39")
        self.assertNotIn("request_params", normalized)

    def test_normalize_order_list_payload_excludes_default_statuses(self):
        payload = {
            "orderList": [
                {"orderId": "1", "statusInfo": {"statusText": "交易关闭"}},
                {"orderId": "2", "statusInfo": {"statusText": "等待买家付款"}},
                {"orderId": "3", "statusInfo": {"statusText": "卖家已发货"}},
            ],
            "total": 3,
            "totalPage": 1,
            "requestParams": {"pageNum": 1, "pageSize": 10},
        }

        normalized = normalize_order_list_payload(payload)

        self.assertEqual(normalized["summary"]["order_count"], 1)
        self.assertEqual(normalized["rows"][0]["orderId"], "3")


class FliggyOrderListCollectorTests(unittest.TestCase):
    @mock.patch("tourism_automation.collectors.fliggy_order_list.collector.FliggyOrderListClient")
    def test_collect_order_list_all_pages_merges_rows_and_marks_complete(self, mock_client_cls):
        mock_client = mock.Mock()
        mock_client.fetch_order_list.side_effect = [
            {
                "orderList": [
                    {
                        "orderId": "1",
                        "statusInfo": {"statusText": "卖家已发货"},
                        "payInfo": {"buyMount": 1, "actualFee": "￥100.00"},
                    }
                ],
                "total": 3,
                "totalPage": 2,
                "requestParams": {"pageNum": 1, "pageSize": 2},
            },
            {
                "orderList": [
                    {
                        "orderId": "2",
                        "statusInfo": {"statusText": "卖家已发货"},
                        "payInfo": {"buyMount": 2, "actualFee": "￥200.00"},
                    },
                    {
                        "orderId": "3",
                        "statusInfo": {"statusText": "交易关闭"},
                        "payInfo": {"buyMount": 9, "actualFee": "￥999.00"},
                    },
                ],
                "total": 3,
                "totalPage": 2,
                "requestParams": {"pageNum": 2, "pageSize": 2},
            },
        ]
        mock_client_cls.from_local_chrome.return_value = mock_client

        result = collect_order_list(
            page_num=1,
            page_size=2,
            deal_start="2026-04-07 00:00:00",
            deal_end="2026-04-07 23:59:39",
            all_pages=True,
        )

        self.assertEqual(mock_client.fetch_order_list.call_count, 2)
        self.assertEqual(result["summary"]["order_count"], 2)
        self.assertEqual(result["summary"]["total"], 3)
        self.assertEqual(result["summary"]["total_page"], 2)
        self.assertTrue(result["summary"]["all_pages"])
        self.assertEqual([row["orderId"] for row in result["rows"]], ["1", "2"])


if __name__ == "__main__":
    unittest.main()
