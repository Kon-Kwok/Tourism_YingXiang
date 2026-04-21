"""SYCM CLI integration."""

from __future__ import annotations

import json

from tourism_automation.collectors.sycm.collector import HomePageCollector
from tourism_automation.collectors.sycm.universal_client import UniversalSycmClient
from tourism_automation.collectors.sycm.shop_source.collector import ShopSourceCollector
from tourism_automation.shared.chrome import ChromeHttpClient


def register_subparser(subparsers):
    parser = subparsers.add_parser("sycm", help="SYCM collector commands")
    collector_subparsers = parser.add_subparsers(dest="collector_command", required=True)

    # 健康检查
    collector_subparsers.add_parser("healthcheck", help="Check local Chrome login state availability")

    # 首页数据采集（原有命令，保持向后兼容）
    collect_home = collector_subparsers.add_parser("collect-home", help="Collect homepage data")
    collect_home.add_argument("--date", required=True, help="Business date in YYYY-MM-DD")
    collect_home.add_argument("--shop-name", default="SYCM", help="Shop name label in the output")

    # 列出可用页面
    collector_subparsers.add_parser("list-pages", help="List all available SYCM pages")

    # 页面信息
    page_info = collector_subparsers.add_parser("page-info", help="Get information about a specific page")
    page_info.add_argument("--page-id", required=True, help="Page ID (e.g., home, flow_monitor)")

    # 采集指定页面
    collect_page = collector_subparsers.add_parser("collect-page", help="Collect data from a specific page")
    collect_page.add_argument("--page-id", required=True, help="Page ID (e.g., home, flow_monitor)")
    collect_page.add_argument("--endpoint", help="Specific endpoint name (if not specified, collect all endpoints)")
    collect_page.add_argument("--date-range", required=True, help="Date range (e.g., '2026-04-19|2026-04-19')")

    # 流量监控数据采集
    flow_monitor = collector_subparsers.add_parser("flow-monitor", help="Flow monitor overview data collection")
    flow_monitor.add_argument("--date", required=True, help="Business date (YYYY-MM-DD)")
    flow_monitor.add_argument("--shop-name", default="SYCM", help="Shop name label in the output")
    flow_monitor.add_argument("--device", default="2", help="Device type (2=wireless, 1=PC)")

    # 店铺来源数据采集
    shop_source = collector_subparsers.add_parser("shop-source", help="Shop source data collection")
    shop_source_subparsers = shop_source.add_subparsers(dest="shop_source_command", required=True)

    # 店铺来源 - 采集命令
    shop_source_collect = shop_source_subparsers.add_parser("collect", help="Collect shop source data")
    shop_source_collect.add_argument("--date", required=True, help="Business date (YYYY-MM-DD)")
    shop_source_collect.add_argument("--shop-name", default="default", help="Shop name")
    shop_source_collect.add_argument("--active-key", default="item", help="Activity type (item=product)")
    shop_source_collect.add_argument("--belong", default="all", help="Category (all=all)")
    shop_source_collect.add_argument("--device", default="2", help="Device type (2=wireless, 1=PC)")
    shop_source_collect.add_argument("--save", action="store_true", help="Save to database")

    parser.set_defaults(handler=run)


def run(args) -> int:
    if args.collector_command == "healthcheck":
        result = {"status": "ok", "http_cookie_auth": False}
        try:
            ChromeHttpClient.from_local_chrome()
            result["http_cookie_auth"] = True
        except Exception as exc:
            result["http_cookie_error"] = str(exc)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.collector_command == "collect-home":
        payload = HomePageCollector(http=ChromeHttpClient.from_local_chrome()).collect(
            biz_date=args.date,
            shop_name=args.shop_name,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.collector_command == "list-pages":
        client = UniversalSycmClient()
        pages = client.list_available_pages()
        result = {
            "available_pages": [
                client.get_page_info(page_id)
                for page_id in pages
            ]
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    if args.collector_command == "page-info":
        client = UniversalSycmClient()
        info = client.get_page_info(args.page_id)
        if info is None:
            print(json.dumps({"error": f"Page not found: {args.page_id}"}, ensure_ascii=False, indent=2))
            return 1
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return 0

    if args.collector_command == "collect-page":
        client = UniversalSycmClient()

        if args.endpoint:
            # 采集单个端点
            page_result = client.fetch_page_endpoint(
                page_id=args.page_id,
                endpoint_name=args.endpoint,
                date_range=args.date_range
            )
            # 格式化输出
            result = {
                "page_id": page_result.page_id,
                "page_name": page_result.page_name,
                "endpoint": page_result.endpoint_name,
                "date_range": args.date_range,
                "status": page_result.status,
                "url": page_result.url,
                "data": page_result.data if page_result.status == "success" else None,
                "error": page_result.error if page_result.status == "error" else None
            }
            success = page_result.status == "success"
        else:
            # 采集所有端点
            page_results = client.fetch_page_all_endpoints(
                page_id=args.page_id,
                date_range=args.date_range
            )
            # 格式化输出
            result = {
                "page_id": args.page_id,
                "date_range": args.date_range,
                "endpoints": [
                    {
                        "endpoint": r.endpoint_name,
                        "status": r.status,
                        "url": r.url,
                        "data": r.data if r.status == "success" else None,
                        "error": r.error if r.status == "error" else None
                    }
                    for r in page_results
                ]
            }
            success = all(r.status == "success" for r in page_results)

        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if success else 1

    # 流量监控数据采集
    if args.collector_command == "flow-monitor":
        from datetime import datetime, timedelta

        try:
            # 解析日期
            biz_date = datetime.strptime(args.date, "%Y-%m-%d")
            # 计算对比日期（前一天）
            compare_date = biz_date - timedelta(days=1)

            # 构建对比日期范围格式
            date_range = f"{compare_date.strftime('%Y-%m-%d')}|{biz_date.strftime('%Y-%m-%d')},{biz_date.strftime('%Y-%m-%d')}|{biz_date.strftime('%Y-%m-%d')}"

            client = UniversalSycmClient()
            page_result = client.fetch_page_endpoint(
                page_id="flow_monitor",
                endpoint_name="overview",
                date_range=date_range,
                device=args.device
            )

            if page_result.status == "success" and page_result.data.get("code") == 0:
                # 格式化输出
                result = {
                    "summary": {
                        "metric_source": "chrome_cookie_http",
                        "shop_name": args.shop_name,
                        "page_code": "flow_monitor",
                        "page_name": "流量监控概览",
                        "collection_date": args.date,
                        "compare_date": compare_date.strftime('%Y-%m-%d'),
                        "device": args.device,
                        "metric_count": len(page_result.data.get("data", {}))
                    },
                    "metrics": page_result.data.get("data", {}),
                    "raw_payload": page_result.data
                }
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 0
            else:
                error_msg = page_result.error if page_result.status == "error" else page_result.data.get("message", "Unknown error")
                print(json.dumps({"status": "error", "error": error_msg}, ensure_ascii=False, indent=2))
                return 1

        except Exception as exc:
            print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
            return 1

    # 店铺来源数据采集
    if args.collector_command == "shop-source":
        # 店铺来源命令的参数通过getattr获取，因为它使用子命令
        if hasattr(args, 'shop_source_command'):
            if args.shop_source_command == "collect":
                try:
                    collector = ShopSourceCollector(http=ChromeHttpClient.from_local_chrome())
                    result = collector.collect(
                        biz_date=args.date,
                        shop_name=args.shop_name
                    )
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                    return 0
                except Exception as exc:
                    print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False, indent=2))
                    return 1
        else:
            # 如果没有子命令，显示帮助
            print(json.dumps({"error": "Please specify a shop-source command"}, ensure_ascii=False, indent=2))
            return 1

    return 1
