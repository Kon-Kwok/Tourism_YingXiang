"""SYCM页面元数据配置

此模块定义了各个SYCM页面的元数据，包括URL、API端点、参数等信息。
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ApiEndpoint:
    """API端点定义"""
    name: str  # 端点名称，如 "overview", "trend"
    path: str  # API路径，如 "overview.json"
    required_params: Dict[str, str]  # 必需参数
    optional_params: Dict[str, str]  # 可选参数


@dataclass
class SycmPage:
    """SYCM页面定义"""
    page_id: str  # 页面标识，如 "home", "flow_monitor"
    name: str  # 页面名称
    url: str  # 页面URL
    api_prefix: str  # API前缀
    endpoints: List[ApiEndpoint]  # 该页面支持的API端点
    default_date_type: str = "day"  # 默认日期类型


# SYCM页面配置
SYCM_PAGES: Dict[str, SycmPage] = {
    "home": SycmPage(
        page_id="home",
        name="首页",
        url="https://sycm.taobao.com/portal/home.htm",
        api_prefix="/portal/coreIndex/new",
        endpoints=[
            ApiEndpoint(
                name="overview",
                path="overview/v3.json",
                required_params={"dateType": "day", "needCycleCrc": "true"},
                optional_params={}
            ),
            ApiEndpoint(
                name="trend",
                path="trend/v3.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
            ApiEndpoint(
                name="table",
                path="getTableData/v3.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
        ]
    ),

    "flow_monitor": SycmPage(
        page_id="flow_monitor",
        name="流量监控",
        url="https://sycm.taobao.com/flow/monitor/overview",
        api_prefix="/flow/long/period/nodistinct/new/guide/trend",
        endpoints=[
            ApiEndpoint(
                name="overview",
                path="overview.json",
                required_params={"dateType": "compareRange", "device": "2"},
                optional_params={}
            ),
        ]
    ),

    "trade_analysis": SycmPage(
        page_id="trade_analysis",
        name="交易分析",
        url="https://sycm.taobao.com/trade/analysis/overview",
        api_prefix="/portal/trade/analysis",
        endpoints=[
            ApiEndpoint(
                name="overview",
                path="overview.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
            ApiEndpoint(
                name="trend",
                path="trend.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
        ]
    ),

    "goods_analysis": SycmPage(
        page_id="goods_analysis",
        name="商品分析",
        url="https://sycm.taobao.com/goods/analysis/overview",
        api_prefix="/portal/goods/analysis",
        endpoints=[
            ApiEndpoint(
                name="overview",
                path="overview.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
            ApiEndpoint(
                name="list",
                path="list.json",
                required_params={"dateType": "day"},
                optional_params={}
            ),
        ]
    ),

    "shop_source": SycmPage(
        page_id="shop_source",
        name="店铺来源",
        url="https://sycm.taobao.com/flow/monitor/shopsource/construction",
        api_prefix="/flow/v3/shop/source/constitute",
        endpoints=[
            ApiEndpoint(
                name="menu",
                path="menu/v3.json",
                required_params={"dateType": "day", "device": "2"},
                optional_params={"activeKey": "item", "belong": "all"}
            ),
        ]
    ),
}


def get_page(page_id: str) -> Optional[SycmPage]:
    """获取页面配置"""
    return SYCM_PAGES.get(page_id)


def list_pages() -> List[str]:
    """列出所有可用的页面ID"""
    return list(SYCM_PAGES.keys())


def get_page_endpoints(page_id: str) -> List[ApiEndpoint]:
    """获取页面的所有API端点"""
    page = get_page(page_id)
    return page.endpoints if page else []


def build_api_url(page_id: str, endpoint_name: str, date_range: str, **kwargs) -> Optional[str]:
    """构建完整的API URL

    Args:
        page_id: 页面ID
        endpoint_name: 端点名称
        date_range: 日期范围，如 "2026-04-19|2026-04-19"
        **kwargs: 额外的查询参数

    Returns:
        完整的API URL，如果页面或端点不存在则返回None
    """
    from urllib.parse import urlencode

    page = get_page(page_id)
    if not page:
        return None

    endpoint = next((ep for ep in page.endpoints if ep.name == endpoint_name), None)
    if not endpoint:
        return None

    # 合并参数
    params = {
        **endpoint.required_params,
        "dateRange": date_range,
        **kwargs
    }

    # 构建URL
    api_path = f"{page.api_prefix}/{endpoint.path}"
    return f"{api_path}?{urlencode(params)}"
