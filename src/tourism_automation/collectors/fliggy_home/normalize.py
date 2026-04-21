"""Normalization helpers for Fliggy homepage modules."""

from __future__ import annotations


def normalize_service_todos(todo_payload, message_payload):
    data = _require_payload(todo_payload, "todo_payload")["data"]
    if isinstance(data, dict):
        return {
            "pending_warning_count": _to_int(_require_field(data, "riskCount", "todo_payload.data")),
            "pending_violation_count": _to_int(_require_field(data, "violationCount", "todo_payload.data")),
            "pending_certificate_confirm_count": _to_int(
                _require_field(data, "certificateConfirmCount", "todo_payload.data")
            ),
            "activity_invitation_count": _to_int(
                _require_field(data, "activityInvitationCount", "todo_payload.data")
            ),
            "pending_bad_review_reply_count": _to_int(
                _require_field(data, "badCommentCount", "todo_payload.data")
            ),
            "todo_messages": _require_payload(message_payload, "message_payload")["data"],
            "todo_groups": [],
            "other_todos": [],
        }
    if not isinstance(data, list):
        raise ValueError("todo_payload.data must be a list of todo groups")

    todo_groups = []
    todo_items = []
    for group in data:
        group_mapping = _require_mapping(group, "todo_group")
        group_name = _require_field(group_mapping, "groupName", "todo_group")
        todo_list = _require_field(group_mapping, "todoList", "todo_group")
        if not isinstance(todo_list, list):
            raise ValueError("todo_group.todoList must be a list")
        group_items = []
        for item in todo_list:
            item_mapping = _require_mapping(item, "todo_item")
            group_items.append(
                {
                    "title": _require_field(item_mapping, "todoName", "todo_item"),
                    "count": _to_int(_require_field(item_mapping, "todoCount", "todo_item")),
                    "url": item_mapping.get("todoUrl"),
                }
            )
        todo_groups.append({"group_name": group_name, "items": group_items})
        todo_items.extend(group_items)

    return {
        "pending_warning_count": _todo_count(todo_items, "待处理预警"),
        "pending_violation_count": _todo_count(todo_items, "待处理违规"),
        "pending_certificate_confirm_count": _todo_count(todo_items, "电子凭证待确认"),
        "activity_invitation_count": _todo_count(todo_items, "活动邀约"),
        "pending_bad_review_reply_count": _todo_count(todo_items, "待回复差评"),
        "todo_messages": _require_payload(message_payload, "message_payload")["data"],
        "todo_groups": todo_groups,
        "other_todos": [item for item in todo_items if item["title"] not in _CORE_TODO_TITLES],
    }


def normalize_business_center(trade_payload, graph_payload, industry_payload, *, biz_date=None):
    trade_data = _require_mapping(trade_payload, "trade_payload")["data"]
    graph_data = _require_mapping(graph_payload, "graph_payload")["data"]
    industry_data = _require_mapping(industry_payload, "industry_payload")["data"]

    rows = graph_data.get("rows", [])
    if not isinstance(rows, list):
        raise ValueError("graph_payload.data.rows must be a list")

    cruise_row = _find_cruise_row(trade_data.get("measureResultVOList", []))
    statistics = industry_data.get("statisticsDateVO", {})
    if statistics is not None and not isinstance(statistics, dict):
        raise ValueError("industry_payload.data.statisticsDateVO must be a mapping")

    if "totalPayAmt" in trade_data:
        total_pay_amount = _require_field(trade_data, "totalPayAmt", "trade_payload.data")
        total_pay_amount_change = _require_field(trade_data, "totalPayAmtChange", "trade_payload.data")
        total_pay_amount_rank = trade_data.get("payGmvRank")
        total_pay_amount_rank_rise = trade_data.get("payGmvRankRise")
        fulfil_amount = trade_data.get("fulfilAmt")
        cruise_pay_amount = trade_data.get("cruisePayAmt")
    else:
        total_pay_amount = _require_field(trade_data, "payGmv", "trade_payload.data")
        total_pay_amount_change = trade_data.get("momPayGmv")
        total_pay_amount_rank = trade_data.get("payGmvRank")
        total_pay_amount_rank_rise = trade_data.get("payGmvRankRise")
        fulfil_amount = trade_data.get("performGmv")
        cruise_pay_amount = cruise_row.get("sycm_pay_gmv")

    return {
        "stat_date": biz_date or (rows[-1]["stat_date"] if rows else None),
        "total_pay_amount": total_pay_amount,
        "total_pay_amount_change": total_pay_amount_change,
        "total_pay_amount_rank": total_pay_amount_rank,
        "total_pay_amount_rank_rise": total_pay_amount_rank_rise,
        "cruise_pay_amount": cruise_pay_amount,
        "fulfil_amount": fulfil_amount,
        "industries": industry_data.get("industry", []),
        "statistics_finished": statistics.get("finish") if isinstance(statistics, dict) else None,
        "statistics_finished_at": statistics.get("finishAt") if isinstance(statistics, dict) else None,
        "trend": [
            {
                "stat_date": row.get("stat_date"),
                "pay_gmv": row.get("pay_gmv"),
                "perform_gmv": row.get("perform_gmv"),
            }
            for row in rows
        ],
    }


def normalize_product_operation_center(shop_block_payload, item_ability_payload, dest_prefer_payload):
    shop_block_data = _require_mapping(shop_block_payload, "shop_block_payload")["data"]
    item_ability_result = _require_mapping(item_ability_payload, "item_ability_payload").get("result")
    if not isinstance(item_ability_result, dict):
        raise ValueError("item_ability_payload.result must be a mapping")
    item_ability_data = _require_mapping(item_ability_result, "item_ability_payload.result")["data"]
    dest_prefer_result = _require_mapping(dest_prefer_payload, "dest_prefer_payload").get("result")
    if not isinstance(dest_prefer_result, dict):
        raise ValueError("dest_prefer_payload.result must be a mapping")

    return {
        "shop_name": shop_block_data.get("shopName"),
        "run_status": shop_block_data.get("runStatus"),
        "run_status_desc": shop_block_data.get("runStatusDesc"),
        "qualification_warning": shop_block_data.get("qualWarnStatus"),
        "item_ability_score": item_ability_data.get("avgScore"),
        "good_item_count": item_ability_data.get("goodNum"),
        "medium_item_count": item_ability_data.get("mediumNum"),
        "low_item_count": item_ability_data.get("lowNum"),
        "total_item_count": item_ability_data.get("totalItemNum"),
        "is_dest_prefer_seller": dest_prefer_result.get("isDestPreferSeller"),
        "dest_info_list": dest_prefer_result.get("destInfoList", []),
        "score_descriptions": dest_prefer_result.get("scoreDescList", []),
    }


def normalize_merchant_growth(new_mci_payload, home_mci_payload, operator_payload=None, excellent_payload=None):
    new_mci_result = _require_mapping(new_mci_payload, "new_mci_payload").get("result")
    if not isinstance(new_mci_result, dict):
        raise ValueError("new_mci_payload.result must be a mapping")
    home_mci_data = _require_mapping(home_mci_payload, "home_mci_payload")["data"]
    tasks = _require_field(home_mci_data, "indexTask", "home_mci_payload.data")
    if not isinstance(tasks, list):
        raise ValueError("home_mci_payload.data.indexTask must be a list")

    return {
        "is_quality_seller": new_mci_result.get("isQualitySeller"),
        "quality_seller_descriptions": new_mci_result.get("scoreDescList", []),
        "mci_score": home_mci_data.get("score"),
        "mci_score_change": home_mci_data.get("scoreChanged"),
        "peer_mean": home_mci_data.get("peerMean"),
        "todo_count": home_mci_data.get("todoCount"),
        "period_start_date": home_mci_data.get("startDate"),
        "period_end_date": home_mci_data.get("endDate"),
        "show_last_week_score": home_mci_data.get("showLastWeekScore"),
        "tasks": [
            {
                "index_name": task.get("indexName"),
                "index_desc": task.get("indexDesc"),
                "action_text": task.get("guideButtonText"),
                "action_link": task.get("guideButtonLink"),
            }
            for task in tasks
        ],
        "operator_center": _extract_optional_payload(operator_payload),
        "operator_center_error": _extract_optional_error(operator_payload),
        "excellent": _extract_optional_payload(excellent_payload),
        "excellent_error": _extract_optional_error(excellent_payload),
    }


def normalize_rule_center(rule_payload):
    rule_data = _require_mapping(rule_payload, "rule_payload")["data"]
    tabs = _require_field(rule_data, "tabs", "rule_payload.data")
    if not isinstance(tabs, list):
        raise ValueError("rule_payload.data.tabs must be a list")

    normalized_tabs = []
    for tab in tabs:
        tab_mapping = _require_mapping(tab, "rule_tab")
        items = tab_mapping.get("items", [])
        if not isinstance(items, list):
            raise ValueError("rule_tab.items must be a list")
        normalized_tabs.append(
            {
                "title": tab_mapping.get("title"),
                "items": [
                    {
                        "title": item.get("text"),
                        "published_at": item.get("updateTime"),
                        "link": item.get("link"),
                        "is_latest": index == 0,
                        "position": index + 1,
                    }
                    for index, item in enumerate(items)
                ],
            }
        )

    return {
        "title": rule_data.get("title", {}).get("text") if isinstance(rule_data.get("title"), dict) else rule_data.get("title"),
        "tabs": normalized_tabs,
        "subscribe_action": rule_data.get("action"),
        "bottom_action": rule_data.get("bottomAction"),
    }


def _extract_optional_payload(payload):
    if not isinstance(payload, dict):
        return None
    if payload.get("success") is False:
        return None
    if payload.get("errorCode") not in (None, 0, "0"):
        return None
    return payload.get("data", payload.get("result"))


def _extract_optional_error(payload):
    if not isinstance(payload, dict):
        return None
    error_code = payload.get("errorCode")
    if error_code in (None, 0, "0"):
        return None
    return payload.get("errorMsg") or str(error_code)


def _find_cruise_row(measure_result_list):
    if not isinstance(measure_result_list, list):
        return {}
    for item in measure_result_list:
        if not isinstance(item, dict):
            continue
        if item.get("industry") != "CRUISE":
            continue
        rows = item.get("rows", [])
        if isinstance(rows, list) and rows and isinstance(rows[0], dict):
            return rows[0]
    return {}


def _todo_count(todo_items, title):
    for item in todo_items:
        if item["title"] == title:
            return item["count"]
    return 0


def _to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"expected integer-compatible value, got {value!r}") from exc


def _require_payload(payload, payload_name):
    if not isinstance(payload, dict):
        raise ValueError(f"{payload_name} must be a mapping")
    if "data" not in payload:
        raise ValueError(f"{payload_name} missing required field: data")
    return payload


def _require_mapping(payload, payload_name):
    if not isinstance(payload, dict):
        raise ValueError(f"{payload_name} must be a mapping")
    if "data" in payload and isinstance(payload["data"], dict):
        return payload
    return payload


def _require_field(mapping, field_name, payload_name):
    if field_name not in mapping:
        raise ValueError(f"{payload_name} missing required field: {field_name}")
    return mapping[field_name]


_CORE_TODO_TITLES = {
    "待处理预警",
    "待处理违规",
    "电子凭证待确认",
    "活动邀约",
    "待回复差评",
}
