"""店铺KPI导出CLI命令"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter import (
    ShopKpiExporter,
    export_shop_kpi
)


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
        '--password',
        default='1234',
        help='导出密码（默认1234）'
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

    parser.set_defaults(handler=run)


def run(args) -> int:
    """处理导出命令

    Args:
        args: argparse命名空间对象

    Returns:
        int: 退出码
    """
    try:
        print("=" * 60)
        print("店铺KPI数据导出")
        print("=" * 60)

        print("\n前置条件检查：")
        print("✓ Chrome调试窗口是否运行")
        print("  检查命令: ps aux | grep 'remote-debugging-port=9222'")
        print("✓ 店铺KPI页面是否已打开")
        print("  URL: https://kf.topchitu.com/web/custom-kpi/shop-kpi?id=941")

        # 导出数据
        output_file = export_shop_kpi(
            password=args.password,
            output_file=args.output
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
                "password": "***",  # 隐藏密码
                "output": args.output,
                "debug_port": args.debug_port
            }
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        return 1
