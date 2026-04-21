import unittest

from tourism_automation.collectors.sycm.normalize import normalize_home_payloads
from tourism_automation.shared.chrome.session import _decrypt_cookie_value


class NormalizeHomePayloadsTests(unittest.TestCase):
    def test_normalize_home_payloads_emits_metrics_and_trends(self):
        overview_payload = {
            "content": {
                "code": 0,
                "data": {
                    "self": {
                        "statDate": {"value": 1776528000000},
                        "payAmt": {
                            "value": 40552.99,
                            "cycleCrc": -0.8390799257,
                            "syncCrc": 0.0985501562,
                            "yearSyncCrc": 0.9212142316,
                        },
                        "uv": {
                            "value": 10749,
                            "cycleCrc": -0.3620014245,
                            "syncCrc": -0.5784705882,
                            "yearSyncCrc": -0.1271619976,
                        },
                    }
                },
            },
            "hasError": False,
        }
        trend_payload = {
            "content": {
                "code": 0,
                "data": {
                    "self": {
                        "statDate": [1776441600000, 1776528000000],
                        "payAmt": [252007.03, 40552.99],
                        "uv": [16848, 10749],
                    },
                    "rivalAvg": {
                        "statDate": [1776441600000, 1776528000000],
                        "payAmt": [77187.2, 78490.4],
                        "uv": [3621, 3438],
                    },
                    "rivalGood": {
                        "statDate": [1776441600000, 1776528000000],
                        "payAmt": [198404, 197284.9],
                        "uv": [10063, 8381],
                    },
                },
            },
            "hasError": False,
        }
        table_payload = {
            "content": {
                "code": 0,
                "data": [
                    {
                        "statDate": {"value": 1776528000000},
                        "payAmt": {"value": 40552.99},
                        "uv": {"value": 10749},
                    }
                ],
            },
            "hasError": False,
        }

        normalized = normalize_home_payloads(
            biz_date="2026-04-19",
            shop_name="皇家加勒比国际游轮旗舰店",
            overview_payload=overview_payload,
            trend_payload=trend_payload,
            table_payload=table_payload,
        )

        self.assertEqual(normalized["metrics"][0]["metric_code"], "payAmt")
        self.assertEqual(normalized["metrics"][0]["metric_value"], 40552.99)
        self.assertEqual(normalized["metrics"][1]["metric_code"], "uv")
        self.assertEqual(normalized["table_rows"][0]["stat_date"], "2026-04-19")
        self.assertEqual(normalized["trends"][0]["stat_date"], "2026-04-18")
        self.assertEqual(normalized["trends"][0]["rival_good_value"], 198404.0)



class ChromeCookieDecryptTests(unittest.TestCase):
    def test_decrypt_cookie_value_returns_plain_bytes_when_not_encrypted(self):
        result = _decrypt_cookie_value(
            encrypted_value=b"plain-cookie",
            key=b"0" * 16,
            host_hash_len=32,
        )

        self.assertEqual(result, "plain-cookie")


if __name__ == "__main__":
    unittest.main()
