from __future__ import annotations

DEFAULT_EXCLUDED_STATUSES = {"交易关闭", "等待买家付款"}


def _extract_package_type(order: dict) -> str | None:
    for item in order.get("itemInfo", {}).get("skuText", []):
        if item.get("name") == "套餐类型：":
            return item.get("value")
    return None


def normalize_order_list_payload(
    payload: dict,
    *,
    page_num: int | None = None,
    page_size: int | None = None,
    deal_start: str | None = None,
    deal_end: str | None = None,
) -> dict:
    request_params = dict(payload.get("requestParams", {}))
    if deal_start is not None and deal_end is not None:
        request_params.setdefault("orderCreateTime", f"{deal_start}~{deal_end}")
    raw_orders = payload.get("orderList", [])
    rows = [
        {
            "orderId": order.get("orderId"),
            "package_type": _extract_package_type(order),
            "buy_mount": order.get("payInfo", {}).get("buyMount"),
            "actual_fee": order.get("payInfo", {}).get("actualFee"),
            "order_time": order.get("orderInfo", {}).get("orderTime"),
            "status_text": order.get("statusInfo", {}).get("statusText"),
        }
        for order in raw_orders
        if order.get("statusInfo", {}).get("statusText") not in DEFAULT_EXCLUDED_STATUSES
    ]
    resolved_order_create_time = request_params.get("orderCreateTime")
    if isinstance(resolved_order_create_time, str):
        resolved_deal_range = resolved_order_create_time.split("~", 1)
    else:
        resolved_deal_range = [deal_start, deal_end]
    return {
        "summary": {
            "order_count": len(rows),
            "total": payload.get("total", 0),
            "total_page": payload.get("totalPage", 0),
            "page_num": request_params.get("pageNum", page_num),
            "page_size": request_params.get("pageSize", page_size),
            "deal_start": resolved_deal_range[0] if len(resolved_deal_range) > 0 else None,
            "deal_end": resolved_deal_range[1] if len(resolved_deal_range) > 1 else None,
        },
        "rows": rows,
    }
