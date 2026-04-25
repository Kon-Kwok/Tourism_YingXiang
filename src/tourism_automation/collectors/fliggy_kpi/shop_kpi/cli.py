"""店铺KPI导出CLI命令"""

from __future__ import annotations

import contextlib
import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter import (
    ShopKpiExporter,
    export_shop_kpi
)
from tourism_automation.collectors.fliggy_kpi.shop_kpi.json_payload import prepare_payload


def register_subparser(subparsers):
    """注册店铺KPI导出子命令

    Args:
        subparsers: argparse subparsers对象
    """
    parser = subparsers.add_parser(
        'shop-kpi-export',
        help='导出店铺KPI数据（需要Chrome调试窗口运行）'
    )

    parser.add_argument(
        '--output',
        '-o',
        help='输出文件路径（可选，默认自动生成）'
    )

    parser.add_argument(
        '--debug-port',
        type=int,
        default=9222,
        help='Chrome调试端口（默认9222）'
    )

    parser.add_argument(
        '--report-name',
        default=ShopKpiExporter.DEFAULT_REPORT_NAME,
        choices=ShopKpiExporter.SUPPORTED_REPORT_NAMES,
        help='要导出的报表名称'
    )

    parser.add_argument(
        '--date-mode',
        default='day',
        choices=ShopKpiExporter.SUPPORTED_DATE_MODES,
        help='日期模式：day/week/month，默认 day'
    )

    parser.add_argument(
        '--date',
        help='day 模式的日期，格式 YYYY-MM-DD；不传时默认前一天'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='导出 Excel 后直接转成统一 JSON 输出到 stdout'
    )

    parser.set_defaults(handler=run)

    batch_parser = subparsers.add_parser(
        'shop-kpi-export-batch',
        help='批量导出店铺KPI数据（需要Chrome调试窗口运行）'
    )

    batch_parser.add_argument(
        '--debug-port',
        type=int,
        default=9222,
        help='Chrome调试端口（默认9222）'
    )

    batch_parser.add_argument(
        '--date-mode',
        default='day',
        choices=ShopKpiExporter.SUPPORTED_DATE_MODES,
        help='日期模式：day/week/month，默认 day'
    )

    batch_parser.add_argument(
        '--date',
        help='day 模式的日期，格式 YYYY-MM-DD；不传时默认前一天'
    )

    batch_parser.set_defaults(handler=run_batch)


def run(args) -> int:
    """处理导出命令

    Args:
        args: argparse命名空间对象

    Returns:
        int: 退出码
    """
    try:
        if args.json:
            with contextlib.redirect_stdout(sys.stderr):
                output_file = export_shop_kpi(
                    output_file=args.output,
                    report_name=args.report_name,
                    date_mode=args.date_mode,
                    date=args.date,
                )
            payload = prepare_payload(output_file)
            json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return 0

        print("=" * 60)
        print("店铺KPI数据导出")
        print("=" * 60)

        print("\n前置条件检查：")
        print("✓ Chrome调试窗口是否运行")
        print("  检查命令: ps aux | grep 'remote-debugging-port=9222'")
        print("✓ 自定义 KPI 页面是否已打开")
        print(f"  URL: {ShopKpiExporter.SHOP_KPI_URL}")

        output_file = export_shop_kpi(
            output_file=args.output,
            report_name=args.report_name,
            date_mode=args.date_mode,
            date=args.date,
        )

        result = {
            "status": "success",
            "output_file": output_file,
            "message": "导出流程已启动，请检查浏览器下载"
        }

        print("\n" + "=" * 60)
        print("✅ 导出流程已启动！")
        print("=" * 60)
        print(f"文件将保存到: {output_file}")
        print("\n请检查:")
        print("1. 浏览器是否开始下载")
        print("2. 下载文件夹中是否有新文件")

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    except Exception as exc:
        error_result = {
            "status": "error",
            "error": str(exc),
            "args": {
                "output": args.output,
                "debug_port": args.debug_port,
                "report_name": args.report_name,
                "date_mode": args.date_mode,
                "date": args.date,
                "json": args.json,
            }
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        return 1


def run_batch(args) -> int:
    """批量导出 3 张固定报表。"""
    try:
        print("=" * 60)
        print("店铺KPI批量导出")
        print("=" * 60)

        print("\n前置条件检查：")
        print("✓ Chrome调试窗口是否运行")
        print("  检查命令: ps aux | grep 'remote-debugging-port=9222'")
        print("✓ 自定义 KPI 页面是否已打开")
        print(f"  URL: {ShopKpiExporter.SHOP_KPI_URL}")

        outputs = []
        for report_name in ShopKpiExporter.SUPPORTED_REPORT_NAMES:
            output_file = export_shop_kpi(
                output_file=None,
                report_name=report_name,
                date_mode=args.date_mode,
                date=args.date,
            )
            outputs.append(
                {
                    "report_name": report_name,
                    "output_file": output_file,
                }
            )

        result = {
            "status": "success",
            "exports": outputs,
            "message": "批量导出流程已启动，请检查浏览器下载",
        }

        print("\n" + "=" * 60)
        print("✅ 批量导出流程已启动！")
        print("=" * 60)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    except Exception as exc:
        error_result = {
            "status": "error",
            "error": str(exc),
            "args": {
                "debug_port": args.debug_port,
                "date_mode": args.date_mode,
                "date": args.date,
            }
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        return 1
