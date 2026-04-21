import importlib.util
import io
import json
import unittest
from pathlib import Path
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parent.parent / "bin" / "prepare_qianniu_shop_daily_key_sql.py"
SPEC = importlib.util.spec_from_file_location("prepare_qianniu_shop_daily_key_sql", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PrepareQianniuShopDailyKeySqlTests(unittest.TestCase):
    def test_build_upsert_sql_maps_summary_fields(self):
        payload = {
            "summary": {
                "deal_start": "2026-04-20 00:00:00",
                "total_page": 1,
                "total_booking": 10,
                "total_pax": 23,
                "gmv": 90715,
            },
            "rows": [],
        }

        sql = MODULE.build_upsert_sql(payload)

        self.assertIn("INSERT INTO qianniu.qianniu_fliggy_shop_daily_key_data", sql)
        self.assertIn("VALUES ('2026-04-20', 10, 23.00, 90715.00)", sql)
        self.assertIn("total_bookings = VALUES(total_bookings)", sql)
        self.assertIn("total_pax = VALUES(total_pax)", sql)
        self.assertIn("gmv = VALUES(gmv)", sql)

    def test_build_upsert_sql_rejects_multi_page_payload(self):
        payload = {
            "summary": {
                "deal_start": "2026-04-07 00:00:00",
                "total_page": 2,
                "total_booking": 17,
                "total_pax": 49,
                "gmv": 179551,
            },
            "rows": [],
        }

        with self.assertRaises(ValueError):
            MODULE.build_upsert_sql(payload)

    def test_build_upsert_sql_accepts_multi_page_when_all_pages_collected(self):
        payload = {
            "summary": {
                "deal_start": "2026-04-07 00:00:00",
                "total_page": 2,
                "all_pages": True,
                "total_booking": 17,
                "total_pax": 49,
                "gmv": 179551,
            },
            "rows": [],
        }

        sql = MODULE.build_upsert_sql(payload)

        self.assertIn("VALUES ('2026-04-07', 17, 49.00, 179551.00)", sql)

    def test_main_reads_stdin_and_writes_sql(self):
        payload = {
            "summary": {
                "deal_start": "2026-04-20 00:00:00",
                "total_page": 1,
                "total_booking": 10,
                "total_pax": 23,
                "gmv": 90715,
            },
            "rows": [],
        }
        stdin = io.StringIO(json.dumps(payload, ensure_ascii=False))
        stdout = io.StringIO()

        with mock.patch("sys.stdin", stdin), mock.patch("sys.stdout", stdout):
            exit_code = MODULE.main()

        self.assertEqual(exit_code, 0)
        self.assertIn("VALUES ('2026-04-20', 10, 23.00, 90715.00)", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
