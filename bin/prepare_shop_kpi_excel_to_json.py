#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from tourism_automation.collectors.fliggy_kpi.shop_kpi.json_payload import prepare_payload
warnings.filterwarnings(
    "ignore",
    message="Workbook contains no default style, apply openpyxl's default",
    category=UserWarning,
)


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    if len(args) != 1:
        raise SystemExit("Usage: python3 bin/prepare_shop_kpi_excel_to_json.py <excel_file>")

    payload = prepare_payload(args[0])
    json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
