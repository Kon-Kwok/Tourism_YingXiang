import unittest
from unittest import mock
from pathlib import Path
from tempfile import TemporaryDirectory
import os
from datetime import datetime

from tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter import ShopKpiExporter


class ShopKpiExporterTests(unittest.TestCase):
    def test_supported_report_names_exclude_zhoujixiaodianpu(self):
        self.assertEqual(
            ShopKpiExporter.DEFAULT_REPORT_NAME,
            "人均日接入",
        )
        self.assertEqual(
            ShopKpiExporter.SUPPORTED_REPORT_NAMES,
            ("人均日接入", "每周店铺个人数据", "客服数据23年新"),
        )

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.datetime")
    def test_yesterday_local_str_defaults_to_previous_day(self, mock_datetime):
        mock_datetime.now.return_value = datetime(2026, 4, 21, 8, 0, 0)

        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        self.assertEqual(exporter._today_local_str(), "2026-04-20")

    def test_find_recent_downloaded_file_prefers_actual_download_in_candidate_dirs(self):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        with TemporaryDirectory() as tmpdir:
            download_dir = Path(tmpdir) / "下载"
            download_dir.mkdir()
            old_file = download_dir / "自定义报表_人均日接入_旧.xlsx"
            old_file.write_text("old")
            os.utime(old_file, (100, 100))

            recent_file = download_dir / "自定义报表_人均日接入_2026-04-21.xlsx"
            recent_file.write_text("new")
            os.utime(recent_file, (200, 200))

            with mock.patch.object(
                exporter,
                "_candidate_download_dirs",
                return_value=[download_dir],
            ):
                found = exporter._find_recent_downloaded_file(
                    report_name="人均日接入",
                    started_at=150,
                )

        self.assertEqual(found, str(recent_file))

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.time.sleep", return_value=None)
    def test_export_shop_kpi_day_mode_defaults_to_today_and_queries_before_export(self, _mock_sleep):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        with mock.patch.object(
            exporter,
            "_get_shop_kpi_tab",
            return_value={"title": "shop-kpi", "ws_url": "ws://example"},
        ), mock.patch.object(
            exporter,
            "_today_local_str",
            return_value="2026-04-21",
        ), mock.patch.object(
            exporter,
            "select_report",
            return_value=True,
        ) as mock_select_report, mock.patch.object(
            exporter,
            "select_date_mode",
            return_value=True,
        ) as mock_select_date_mode, mock.patch.object(
            exporter,
            "select_date_range",
            return_value=True,
        ) as mock_select_date_range, mock.patch.object(
            exporter,
            "_wait_for_downloaded_file",
            return_value="/home/kk/下载/人均日接入.xlsx",
        ), mock.patch.object(
            exporter,
            "click_element",
            side_effect=lambda ws_url, selector: selector == "button.download___7ocOy",
        ), mock.patch.object(
            exporter,
            "inspect_form",
            return_value={"inputCount": 1, "buttonCount": 2},
        ), mock.patch.object(
            exporter,
            "wait_for_element",
            side_effect=lambda ws_url, selector, timeout_ms=5000: (
                selector == "#password > span.inputWrapper___1eYh- > span > input"
            ),
        ), mock.patch.object(
            exporter,
            "input_text",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "click_button_by_text",
            return_value=True,
        ) as mock_click_button_by_text:
            exporter.export_shop_kpi(
                output_file="/tmp/out.xlsx",
                report_name="人均日接入",
                date_mode="day",
            )

        mock_select_report.assert_called_once_with("ws://example", "人均日接入")
        mock_select_date_mode.assert_called_once_with("ws://example", "day")
        mock_select_date_range.assert_called_once_with(
            "ws://example",
            "2026-04-21",
            "2026-04-21",
        )
        self.assertEqual(
            mock_click_button_by_text.call_args_list[0],
            mock.call("ws://example", "查询"),
        )

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.time.sleep", return_value=None)
    def test_export_shop_kpi_inputs_password_and_confirms_export(self, _mock_sleep):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        with mock.patch.object(
            exporter,
            "_get_shop_kpi_tab",
            return_value={"title": "shop-kpi", "ws_url": "ws://example"},
        ), mock.patch.object(
            exporter,
            "select_report",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_mode",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_range",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "_wait_for_downloaded_file",
            return_value="/home/kk/下载/人均日接入.xlsx",
        ), mock.patch.object(
            exporter,
            "click_element",
            side_effect=lambda ws_url, selector: selector == "button.download___7ocOy",
        ) as mock_click_element, mock.patch.object(
            exporter,
            "inspect_form",
            return_value={"inputCount": 1, "buttonCount": 2},
        ), mock.patch.object(
            exporter,
            "wait_for_element",
            side_effect=lambda ws_url, selector, timeout_ms=5000: (
                selector == "#password > span.inputWrapper___1eYh- > span > input"
            ),
        ), mock.patch.object(
            exporter,
            "input_text",
            return_value=True,
        ) as mock_input_text, mock.patch.object(
            exporter,
            "click_button_by_text",
            return_value=True,
        ) as mock_click_button_by_text:
            output_file = exporter.export_shop_kpi(password="9999", output_file="/tmp/out.xlsx")

        self.assertEqual(output_file, "/home/kk/下载/人均日接入.xlsx")
        mock_click_element.assert_any_call("ws://example", "button.download___7ocOy")
        mock_input_text.assert_called_once_with(
            "ws://example",
            "#password > span.inputWrapper___1eYh- > span > input",
            "1234",
        )
        self.assertEqual(
            mock_click_button_by_text.call_args_list,
            [
                mock.call("ws://example", "查询"),
                mock.call("ws://example", "确定"),
            ],
        )

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.time.sleep", return_value=None)
    def test_export_shop_kpi_skips_password_when_prompt_not_present(self, _mock_sleep):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        with mock.patch.object(
            exporter,
            "_get_shop_kpi_tab",
            return_value={"title": "shop-kpi", "ws_url": "ws://example"},
        ), mock.patch.object(
            exporter,
            "select_report",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_mode",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_range",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "_wait_for_downloaded_file",
            return_value="/home/kk/下载/人均日接入.xlsx",
        ), mock.patch.object(
            exporter,
            "click_element",
            side_effect=lambda ws_url, selector: selector == "button.download___7ocOy",
        ), mock.patch.object(
            exporter,
            "inspect_form",
            return_value={"inputCount": 0, "buttonCount": 0},
        ), mock.patch.object(
            exporter,
            "wait_for_element",
            return_value=False,
        ), mock.patch.object(
            exporter,
            "input_text",
            return_value=True,
        ) as mock_input_text, mock.patch.object(
            exporter,
            "click_button_by_text",
            return_value=True,
        ) as mock_click_button_by_text:
            output_file = exporter.export_shop_kpi(output_file="/tmp/out.xlsx")

        self.assertEqual(output_file, "/home/kk/下载/人均日接入.xlsx")
        mock_input_text.assert_not_called()
        self.assertEqual(
            mock_click_button_by_text.call_args_list,
            [mock.call("ws://example", "查询")],
        )

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.time.sleep", return_value=None)
    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.datetime")
    def test_export_shop_kpi_raises_when_real_download_file_not_found(self, mock_datetime, _mock_sleep):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")
        mock_datetime.now.return_value.strftime.return_value = "20260421_220000"

        with mock.patch.object(
            exporter,
            "_get_shop_kpi_tab",
            return_value={"title": "shop-kpi", "ws_url": "ws://example"},
        ), mock.patch.object(
            exporter,
            "select_report",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_mode",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "select_date_range",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "_wait_for_downloaded_file",
            return_value=None,
        ), mock.patch.object(
            exporter,
            "click_element",
            side_effect=lambda ws_url, selector: selector == "button.download___7ocOy",
        ), mock.patch.object(
            exporter,
            "inspect_form",
            return_value={"inputCount": 1, "buttonCount": 2},
        ), mock.patch.object(
            exporter,
            "wait_for_element",
            side_effect=lambda ws_url, selector, timeout_ms=5000: (
                selector == "#password > span.inputWrapper___1eYh- > span > input"
            ),
        ), mock.patch.object(
            exporter,
            "input_text",
            return_value=True,
        ), mock.patch.object(
            exporter,
            "click_button_by_text",
            return_value=True,
        ):
            with self.assertRaises(RuntimeError):
                exporter.export_shop_kpi(report_name="客服数据23年新")

    @mock.patch("tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter.time.sleep", return_value=None)
    def test_wait_for_downloaded_file_polls_until_file_appears(self, _mock_sleep):
        exporter = ShopKpiExporter(cdp_client=mock.Mock(), download_dir="/tmp/downloads")

        with mock.patch.object(
            exporter,
            "_find_recent_downloaded_file",
            side_effect=[None, None, "/home/kk/下载/客服数据23年新.xlsx"],
        ):
            output_file = exporter._wait_for_downloaded_file(
                report_name="客服数据23年新",
                started_at=100.0,
                timeout_seconds=3.0,
                poll_interval=0.1,
            )

        self.assertEqual(output_file, "/home/kk/下载/客服数据23年新.xlsx")


if __name__ == "__main__":
    unittest.main()
