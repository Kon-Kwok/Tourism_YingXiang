"""Fliggy home CLI integration."""

from __future__ import annotations

import json

from tourism_automation.collectors.fliggy_home.collector import collect_home


def register_subparser(subparsers):
    parser = subparsers.add_parser("fliggy-home", help="Fliggy home collector commands")
    collector_subparsers = parser.add_subparsers(dest="collector_command", required=True)

    collect = collector_subparsers.add_parser("collect-home", help="Collect Fliggy homepage data")
    collect.add_argument("--date", required=True, help="Business date in YYYY-MM-DD")
    collect.add_argument("--shop-name", default="Fliggy Home", help="Shop name label in the output")

    parser.set_defaults(handler=run)


def run(args) -> int:
    if args.collector_command == "collect-home":
        payload = collect_home(shop_name=args.shop_name, biz_date=args.date)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    return 1
