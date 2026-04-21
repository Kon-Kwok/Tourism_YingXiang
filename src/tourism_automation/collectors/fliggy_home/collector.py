"""Fliggy home collector orchestration."""

from __future__ import annotations

from typing import Any

from tourism_automation.collectors.fliggy_home.client import FliggyHomeClient, build_module_request_specs
from tourism_automation.collectors.fliggy_home.normalize import (
    normalize_business_center,
    normalize_merchant_growth,
    normalize_product_operation_center,
    normalize_rule_center,
    normalize_service_todos,
)
from tourism_automation.shared.result import build_module_collection_result


def collect_home(*, shop_name: str, biz_date: str):
    client = FliggyHomeClient.from_local_chrome()
    request_specs = build_module_request_specs(biz_date)
    modules: dict[str, dict[str, Any]] = {}
    collected_at = client.fetched_at()

    for module_name, specs in request_specs.items():
        payloads = {}
        request_errors = []
        module_error = None
        for spec in specs:
            url = spec["url"]
            try:
                payloads[spec["name"]] = client.fetch_json(url)
            except Exception as exc:
                error = {
                    "message": str(exc),
                    "endpoint": url,
                    "http_status": _http_status(exc),
                }
                if spec["required"]:
                    module_error = error
                    break
                request_errors.append({"name": spec["name"], **error})

        if module_error is not None:
            modules[module_name] = {
                "status": "error",
                "raw": None,
                "normalized": None,
                "error": module_error,
                "fetched_at": client.fetched_at(),
            }
            continue

        try:
            normalized = _normalize_module(module_name, payloads, biz_date=biz_date)
            modules[module_name] = {
                "status": "ok",
                "raw": {
                    "payloads": payloads,
                    "request_errors": request_errors,
                },
                "normalized": normalized,
                "fetched_at": client.fetched_at(),
            }
        except Exception as exc:
            modules[module_name] = {
                "status": "error",
                "raw": {
                    "payloads": payloads,
                    "request_errors": request_errors,
                },
                "normalized": None,
                "error": {
                    "message": str(exc),
                    "endpoint": None,
                    "http_status": None,
                },
                "fetched_at": client.fetched_at(),
            }

    result = build_module_collection_result(
        source="chrome_cookie_http",
        shop_name=shop_name,
        modules=modules,
        fetched_at=collected_at,
    )
    if result["summary"]["modules_succeeded"] == 0:
        raise RuntimeError("all modules failed")
    return result


def _normalize_module(module_name: str, payloads: dict[str, Any], *, biz_date: str) -> dict[str, Any]:
    if module_name == "service_todos":
        return normalize_service_todos(payloads["todo_groups"], payloads["todo_messages"])
    if module_name == "business_center":
        return normalize_business_center(
            payloads["trade_measure"],
            payloads["graph_measure"],
            payloads["industry"],
            biz_date=biz_date,
        )
    if module_name == "product_operation_center":
        return normalize_product_operation_center(
            payloads["shop_block"],
            payloads["item_ability"],
            payloads["dest_prefer"],
        )
    if module_name == "merchant_growth":
        return normalize_merchant_growth(
            payloads["new_mci_info"],
            payloads["home_mci_index"],
            payloads.get("operator_center"),
            payloads.get("excellent"),
        )
    if module_name == "rule_center":
        return normalize_rule_center(payloads["rule_center"])
    raise ValueError(f"unsupported module: {module_name}")


def _http_status(exc):
    response = getattr(exc, "response", None)
    return getattr(response, "status_code", None)
