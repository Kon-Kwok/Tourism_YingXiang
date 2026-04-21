"""SYCM店铺来源API客户端"""

from __future__ import annotations

from urllib.parse import urlencode
from typing import Dict, List

from tourism_automation.shared.chrome import ChromeHttpClient


class ShopSourceClient:
    """店铺来源API客户端"""

    def __init__(self, http: ChromeHttpClient | None = None):
        self.http = http or ChromeHttpClient.from_local_chrome()

    def fetch_menu_data(
        self,
        date: str,
        active_key: str = "item",
        belong: str = "all",
        device: str = "2"
    ) -> List[Dict]:
        """获取店铺来源菜单数据

        Args:
            date: 日期，格式 "2026-04-19"
            active_key: 活动类型
            belong: 归类
            device: 设备类型

        Returns:
            List[Dict]: 来源数据列表
        """
        api_url = "https://sycm.taobao.com/flow/v3/shop/source/constitute/menu/v3.json"

        params = {
            "activeKey": active_key,
            "belong": belong,
            "dateType": "day",
            "dateRange": f"{date}|{date}",
            "device": device
        }

        referer = "https://sycm.taobao.com/flow/monitor/shopsource/construction"

        response = self.http.fetch_json(f"{api_url}?{urlencode(params)}", referer=referer)

        if response.get('code') != 0:
            raise Exception(f"API错误: {response.get('message')} (code: {response.get('code')})")

        if 'data' not in response:
            raise Exception("API响应缺少data字段")

        return response['data']
