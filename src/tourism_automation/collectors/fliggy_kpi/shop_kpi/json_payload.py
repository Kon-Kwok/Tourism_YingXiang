"""Shop KPI Excel -> JSON payload helpers."""

from __future__ import annotations

import re
import warnings
from pathlib import Path

from tourism_automation.collectors.fliggy_kpi.shop_kpi.excel_reader import ShopKpiExcelReader


REPORT_NAME_PATTERN = re.compile(r"自定义报表_(.+?)_下单优先判定")
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
)


def extract_report_name(file_path: str) -> str:
    file_name = Path(file_path).name
    match = REPORT_NAME_PATTERN.search(file_name)
    if match:
        return match.group(1)
    return Path(file_path).stem


def prepare_payload(file_path: str) -> dict:
    reader = ShopKpiExcelReader()
    excel_data = reader.read_excel(file_path)
    rows = reader.to_dict(excel_data)

    return {
        "summary": {
            "source": "shop_kpi_excel",
            "report_name": extract_report_name(file_path),
            "file_path": str(Path(file_path).resolve()),
            "row_count": len(rows),
        },
        "rows": rows,
    }
