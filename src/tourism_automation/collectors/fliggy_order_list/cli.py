from __future__ import annotations

import json
from datetime import datetime, timedelta

from tourism_automation.collectors.fliggy_order_list.collector import collect_order_list

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _now_local() -> datetime:
    return datetime.now()


def _resolve_deal_range(deal_start: str | None, deal_end: str | None) -> tuple[str, str]:
    yesterday = (_now_local() - timedelta(days=1)).strftime("%Y-%m-%d")
    resolved_start = deal_start or f"{yesterday} 00:00:00"
    resolved_end = deal_end or f"{yesterday} 23:59:59"
    start_dt = datetime.strptime(resolved_start, DATETIME_FORMAT)
    end_dt = datetime.strptime(resolved_end, DATETIME_FORMAT)
    if start_dt > end_dt:
        raise ValueError("deal_start must be earlier than or equal to deal_end")
    return resolved_start, resolved_end


def register_subparser(subparsers):
    parser = subparsers.add_parser("fliggy-order-list", help="Fliggy order list collector commands")
    collector_subparsers = parser.add_subparsers(dest="collector_command", required=True)

    list_parser = collector_subparsers.add_parser("list", help="Collect Fliggy order list")
    list_parser.add_argument("--page-num", type=int, default=1, help="Page number")
    list_parser.add_argument("--page-size", type=int, default=10, help="Page size")
    list_parser.add_argument("--biz-type", type=int, default=0, help="Business type")
    list_parser.add_argument(
        "--sort-field-enum",
        default="ORDER_CREATE_TIME_DESC",
        help="Sort field enum",
    )
    list_parser.add_argument(
        "--all-pages",
        action="store_true",
        help="Fetch all pages and merge rows into one payload",
    )
    list_parser.add_argument("--deal-start", help="Deal time start in YYYY-MM-DD HH:MM:SS")
    list_parser.add_argument("--deal-end", help="Deal time end in YYYY-MM-DD HH:MM:SS")

    parser.set_defaults(handler=run)


def run(args) -> int:
    if args.collector_command == "list":
        deal_start, deal_end = _resolve_deal_range(args.deal_start, args.deal_end)
        payload = collect_order_list(
            page_num=args.page_num,
            page_size=args.page_size,
            biz_type=args.biz_type,
            sort_field_enum=args.sort_field_enum,
            deal_start=deal_start,
            deal_end=deal_end,
            all_pages=args.all_pages,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    return 1
