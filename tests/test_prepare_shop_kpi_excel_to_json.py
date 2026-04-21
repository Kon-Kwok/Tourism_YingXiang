import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import openpyxl


MODULE_PATH = Path(__file__).resolve().parent.parent / "bin" / "prepare_shop_kpi_excel_to_json.py"
SPEC = importlib.util.spec_from_file_location("prepare_shop_kpi_excel_to_json", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class PrepareShopKpiExcelToJsonTests(unittest.TestCase):
    def _build_excel_file(self, filename: str) -> Path:
        tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(tmpdir.cleanup)

        file_path = Path(tmpdir.name) / filename
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Sheet1"
        sheet.append(["客服昵称", "接待人数", "回复率"])
        sheet.append(["alice", 12, "80%"])
        sheet.append(["bob", 8, "75%"])
        workbook.save(file_path)
        return file_path

    def test_prepare_payload_returns_summary_and_rows(self):
        file_path = self._build_excel_file("自定义报表_人均日接入_下单优先判定_2026-04-20至2026-04-20.xlsx")

        result = MODULE.prepare_payload(str(file_path))

        self.assertEqual(result["summary"]["source"], "shop_kpi_excel")
        self.assertEqual(result["summary"]["report_name"], "人均日接入")
        self.assertEqual(result["summary"]["file_path"], str(file_path))
        self.assertEqual(result["summary"]["row_count"], 2)
        self.assertEqual(result["rows"][0]["客服昵称"], "alice")
        self.assertEqual(result["rows"][1]["接待人数"], 8)

    def test_main_reads_excel_path_and_writes_json(self):
        file_path = self._build_excel_file("自定义报表_客服数据23年新_下单优先判定_2026-04-20至2026-04-20.xlsx")
        stdout = io.StringIO()

        with mock.patch("sys.stdout", stdout):
            exit_code = MODULE.main([str(file_path)])

        self.assertEqual(exit_code, 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["summary"]["report_name"], "客服数据23年新")
        self.assertEqual(result["summary"]["row_count"], 2)
        self.assertEqual(len(result["rows"]), 2)


if __name__ == "__main__":
    unittest.main()
