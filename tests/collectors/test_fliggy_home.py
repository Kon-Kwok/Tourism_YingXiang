import unittest
from unittest import mock

from tourism_automation.collectors.fliggy_home.client import build_module_requests
from tourism_automation.collectors.fliggy_home.collector import collect_home
from tourism_automation.collectors.fliggy_home.normalize import (
    normalize_business_center,
    normalize_merchant_growth,
    normalize_product_operation_center,
    normalize_rule_center,
    normalize_service_todos,
)
from tourism_automation.shared.result import build_module_collection_result


class FliggyHomeNormalizeTests(unittest.TestCase):
    def test_normalize_service_todos_extracts_visible_counts(self):
        todo_payload = {
            "success": True,
            "data": [
                {
                    "groupName": "服务待办",
                    "todoList": [
                        {"todoName": "待处理预警", "todoCount": "0"},
                        {"todoName": "待处理违规", "todoCount": "1"},
                    ],
                },
                {
                    "groupName": "套餐待办",
                    "todoList": [
                        {"todoName": "电子凭证待确认", "todoCount": "2"},
                    ],
                },
                {
                    "groupName": "营销待办",
                    "todoList": [
                        {"todoName": "活动邀约", "todoCount": "3"},
                    ],
                },
                {
                    "groupName": "评价待办",
                    "todoList": [
                        {"todoName": "待回复差评", "todoCount": "4"},
                    ],
                },
            ],
        }
        message_payload = {
            "success": True,
            "data": [{"title": "您有差评待回复，请及时处理！", "num": 4}],
        }

        result = normalize_service_todos(todo_payload, message_payload)

        self.assertEqual(result["pending_warning_count"], 0)
        self.assertEqual(result["pending_violation_count"], 1)
        self.assertEqual(result["pending_certificate_confirm_count"], 2)
        self.assertEqual(result["activity_invitation_count"], 3)
        self.assertEqual(result["pending_bad_review_reply_count"], 4)
        self.assertEqual(result["todo_messages"][0]["num"], 4)

    def test_normalize_business_center_extracts_trade_summary(self):
        trade_payload = {
            "success": True,
            "data": {
                "momPayGmv": 0.853,
                "payGmv": 40552.99,
                "payGmvRank": 14,
                "payGmvRankRise": 0,
                "performGmv": 0,
                "measureResultVOList": [
                    {"industry": "MORE", "rows": []},
                    {
                        "industry": "CRUISE",
                        "rows": [
                            {
                                "seller_id": "2985601233",
                                "sycm_pay_gmv": 40552.99,
                                "sycm_used_gmv": None,
                            }
                        ],
                    },
                ],
            },
        }
        graph_payload = {
            "success": True,
            "data": {
                "rows": [
                    {"stat_date": "20260401", "pay_gmv": 176808.02, "perform_gmv": 0},
                    {"stat_date": "20260402", "pay_gmv": 1024, "perform_gmv": 0},
                ]
            },
        }
        industry_payload = {
            "success": True,
            "data": {
                "industry": ["CRUISE", "MORE"],
                "statisticsDateVO": {"finish": True, "finishAt": "2026-04-20 07:05:21"},
            },
        }

        result = normalize_business_center(trade_payload, graph_payload, industry_payload)

        self.assertEqual(result["total_pay_amount"], 40552.99)
        self.assertEqual(result["total_pay_amount_change"], 0.853)
        self.assertEqual(result["total_pay_amount_rank"], 14)
        self.assertEqual(result["cruise_pay_amount"], 40552.99)
        self.assertEqual(result["trend"][0]["stat_date"], "20260401")
        self.assertEqual(result["statistics_finished_at"], "2026-04-20 07:05:21")

    def test_normalize_product_operation_center_extracts_shop_metrics(self):
        shop_block_payload = {
            "success": True,
            "data": {
                "shopName": "皇家加勒比国际游轮旗舰店",
                "runStatus": 2,
                "runStatusDesc": "正常",
                "qualWarnStatus": False,
            },
        }
        item_ability_payload = {
            "success": True,
            "result": {
                "data": {
                    "avgScore": 44,
                    "goodNum": 0,
                    "mediumNum": 0,
                    "lowNum": 0,
                    "totalItemNum": 0,
                }
            },
        }
        dest_prefer_payload = {
            "success": True,
            "result": {
                "destInfoList": [],
                "isDestPreferSeller": False,
                "scoreDescList": [],
            },
        }

        result = normalize_product_operation_center(
            shop_block_payload,
            item_ability_payload,
            dest_prefer_payload,
        )

        self.assertEqual(result["shop_name"], "皇家加勒比国际游轮旗舰店")
        self.assertEqual(result["run_status_desc"], "正常")
        self.assertEqual(result["item_ability_score"], 44)
        self.assertFalse(result["is_dest_prefer_seller"])

    def test_normalize_merchant_growth_tolerates_optional_endpoint_errors(self):
        new_mci_payload = {
            "success": True,
            "result": {
                "isQualitySeller": False,
                "scoreDescList": [],
            },
        }
        home_mci_payload = {
            "success": True,
            "data": {
                "score": 5.5,
                "scoreChanged": -2.3,
                "peerMean": 5.4,
                "todoCount": 1,
                "startDate": "2026-04-06",
                "endDate": "2026-04-12",
                "indexTask": [
                    {
                        "indexName": "即时确认订单占比（邮轮）",
                        "indexDesc": "店铺即时确认订单占比（邮轮）为差，会造成用户流失",
                        "guideButtonText": "发布即时确认",
                        "guideButtonLink": "https://item.upload.tmall.com/router/publish.htm",
                    }
                ],
            },
        }
        operator_payload = {"errorCode": "999", "errorMsg": "custom error"}
        excellent_payload = {"errorCode": "999", "errorMsg": "custom error"}

        result = normalize_merchant_growth(
            new_mci_payload,
            home_mci_payload,
            operator_payload,
            excellent_payload,
        )

        self.assertEqual(result["mci_score"], 5.5)
        self.assertEqual(result["peer_mean"], 5.4)
        self.assertEqual(result["todo_count"], 1)
        self.assertEqual(result["tasks"][0]["index_name"], "即时确认订单占比（邮轮）")
        self.assertEqual(result["operator_center_error"], "custom error")
        self.assertEqual(result["excellent_error"], "custom error")

    def test_normalize_rule_center_extracts_tabs(self):
        rule_payload = {
            "code": 0,
            "data": {
                "title": "规则中心",
                "tabs": [
                    {
                        "title": "规则公示",
                        "items": [
                            {
                                "text": "关于调整“包车”“接送”商品发布范围的通知",
                                "updateTime": "2026-04-17",
                                "link": "//seller.fliggy.com/ruleDiff/seller/#/detail?id=20009926",
                            }
                        ],
                    }
                ],
            },
        }

        result = normalize_rule_center(rule_payload)

        self.assertEqual(result["title"], "规则中心")
        self.assertEqual(result["tabs"][0]["title"], "规则公示")
        self.assertEqual(result["tabs"][0]["items"][0]["title"], "关于调整“包车”“接送”商品发布范围的通知")

    def test_build_collect_result_keeps_partial_failures(self):
        modules = {
            "service_todos": {
                "status": "ok",
                "raw": {},
                "normalized": {"pending_bad_review_reply_count": 4},
                "fetched_at": "2026-04-20T10:00:00Z",
            },
            "business_center": {
                "status": "error",
                "error": {
                    "message": "HTTP 500",
                    "endpoint": "https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure",
                    "http_status": 500,
                },
                "raw": None,
                "normalized": None,
                "fetched_at": "2026-04-20T10:00:00Z",
            },
        }

        result = build_module_collection_result(
            source="chrome_cookie_http",
            shop_name="皇家加勒比国际游轮旗舰店",
            modules=modules,
            fetched_at="2026-04-20T10:00:00Z",
        )

        self.assertEqual(result["summary"]["modules_requested"], 2)
        self.assertEqual(result["summary"]["modules_succeeded"], 1)
        self.assertEqual(result["summary"]["modules_failed"], 1)
        self.assertEqual(result["summary"]["fetched_at"], "2026-04-20T10:00:00Z")
        self.assertEqual(result["errors"][0]["module"], "business_center")


class FliggyHomeCollectionTests(unittest.TestCase):
    def test_build_module_requests_contains_all_merchant_growth_endpoints(self):
        requests_map = build_module_requests("2026-04-19")

        self.assertEqual(
            requests_map["merchant_growth"],
            [
                "https://sell.fliggy.com/icenter/mci/ajx/GetNewMciInfo.json?_input_charset=UTF-8&_output_charset=UTF-8",
                "https://mci.fliggy.com/seller/service/homeMciIndex",
                "https://seller.fliggy.com/api/sycm/measure/queryOperatorCenter",
                "https://seller.fliggy.com/api/sycm/measure/queryExcellent",
            ],
        )

    def test_collect_home_reports_actual_failing_endpoint(self):
        class FakeClient:
            def __init__(self):
                self.calls = []

            def fetch_json(self, url):
                self.calls.append(url)
                if url.endswith("todomessages"):
                    raise RuntimeError("boom")
                if url.endswith("getTodoData"):
                    return {"success": True, "data": []}
                if "tradeMeasure" in url:
                    return {
                        "success": True,
                        "data": {
                            "payGmv": 1,
                            "measureResultVOList": [{"industry": "CRUISE", "rows": [{"sycm_pay_gmv": 1}]}],
                        },
                    }
                if "graphMeasure" in url:
                    return {"success": True, "data": {"rows": []}}
                if url.endswith("/industry"):
                    return {"success": True, "data": {"industry": [], "statisticsDateVO": {}}}
                if url.endswith("shopBlock"):
                    return {"success": True, "data": {"shopName": "test"}}
                if "ItemAbilityTotalPage" in url:
                    return {"success": True, "result": {"data": {}}}
                if "GetDestPreferInfo" in url:
                    return {"success": True, "result": {"destInfoList": [], "scoreDescList": []}}
                if "GetNewMciInfo" in url:
                    return {"success": True, "result": {"scoreDescList": []}}
                if "homeMciIndex" in url:
                    return {"success": True, "data": {"indexTask": []}}
                if "queryOperatorCenter" in url or "queryExcellent" in url:
                    return {"errorCode": "999", "errorMsg": "custom error"}
                if "ruleCenter" in url:
                    return {"code": 0, "data": {"tabs": []}}
                return {"success": True, "data": {}, "result": {}}

            def fetched_at(self):
                return "2026-04-20T10:00:00Z"

        fake_client = FakeClient()

        with mock.patch(
            "tourism_automation.collectors.fliggy_home.collector.FliggyHomeClient.from_local_chrome",
            return_value=fake_client,
        ):
            result = collect_home(shop_name="皇家加勒比国际游轮旗舰店", biz_date="2026-04-19")

        self.assertEqual(result["service_todos"]["status"], "error")
        self.assertEqual(
            result["service_todos"]["error"]["endpoint"],
            "https://fsc.fliggy.com/api/message/todomessages",
        )

    def test_collect_home_raises_when_all_modules_fail(self):
        class FakeClient:
            def fetch_json(self, url):
                raise RuntimeError(f"failed: {url}")

            def fetched_at(self):
                return "2026-04-20T10:00:00Z"

        with mock.patch(
            "tourism_automation.collectors.fliggy_home.collector.FliggyHomeClient.from_local_chrome",
            return_value=FakeClient(),
        ):
            with self.assertRaisesRegex(RuntimeError, "all modules failed"):
                collect_home(shop_name="皇家加勒比国际游轮旗舰店", biz_date="2026-04-19")


if __name__ == "__main__":
    unittest.main()
