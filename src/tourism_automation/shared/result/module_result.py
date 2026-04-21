"""Shared module-result aggregation helpers."""

from __future__ import annotations


def build_module_collection_result(*, source: str, shop_name: str, modules: dict, fetched_at: str) -> dict:
    modules_requested = len(modules)
    modules_succeeded = sum(1 for module in modules.values() if module["status"] == "ok")
    modules_failed = sum(1 for module in modules.values() if module["status"] == "error")
    errors = [
        {"module": module_name, **module_payload["error"]}
        for module_name, module_payload in modules.items()
        if module_payload["status"] == "error"
    ]
    result = {
        "summary": {
            "source": source,
            "shop_name": shop_name,
            "fetched_at": fetched_at,
            "modules_requested": modules_requested,
            "modules_succeeded": modules_succeeded,
            "modules_failed": modules_failed,
        },
        "errors": errors,
    }
    result.update(modules)
    return result
