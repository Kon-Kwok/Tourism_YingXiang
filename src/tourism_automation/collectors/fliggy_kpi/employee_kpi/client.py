"""飞猪客服KPI API客户端

支持从天池客服系统获取员工KPI数据
"""

from __future__ import annotations

import json
import subprocess
from typing import Dict, List, Optional
from urllib.parse import urlencode


class EmployeeKpiClient:
    """员工KPI数据客户端"""

    def __init__(self, http=None):
        """初始化客户端

        Args:
            http: HTTP客户端（可选，预留用于API方式）
        """
        self.http = http
        self.base_url = "https://kf.topchitu.com"

    def fetch_kpi_data(
        self,
        date: str,
        kpi_id: str = "1721",
        wwt: str = "ALL"
    ) -> Dict[str, object]:
        """获取员工KPI数据

        Args:
            date: 业务日期 (YYYY-MM-DD)
            kpi_id: KPI模板ID，默认1721
            wwt: 时间范围类型，默认ALL

        Returns:
            Dict: 包含KPI数据的字典
        """
        # 当前使用CDP方式获取数据
        return self._fetch_via_cdp(date, kpi_id, wwt)

    def _fetch_via_cdp(
        self,
        date: str,
        kpi_id: str,
        wwt: str
    ) -> Dict[str, object]:
        """通过CDP从页面获取数据

        Args:
            date: 业务日期
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Dict: 包含KPI数据的字典
        """
        # TODO: 实现CDP数据提取
        # 当前返回示例数据结构
        return {
            "method": "cdp",
            "date": date,
            "kpi_id": kpi_id,
            "wwt": wwt,
            "data": []
        }

    def _fetch_via_api(
        self,
        date: str,
        kpi_id: str,
        wwt: str
    ) -> Optional[Dict[str, object]]:
        """通过API获取数据（预留）

        注意：当前API需要特殊认证，此方法预留用于未来实现

        Args:
            date: 业务日期
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Optional[Dict]: API响应数据，如果失败返回None
        """
        if not self.http:
            return None

        try:
            # API端点（从网络请求中发现）
            api_url = f"{self.base_url}/api/custom/report/kpi"

            # 参数
            params = {
                "range": json.dumps({"from": date, "to": date}),
                "dateType": "DAY",
                "id": kpi_id,
                "wwt": wwt
            }

            # 页面URL作为referer
            referer = f"{self.base_url}/web/custom-kpi/employee-kpi?id={kpi_id}&wwt={wwt}"

            response = self.http.fetch_json(api_url, referer=referer, params=params)
            return response

        except Exception as e:
            print(f"API请求失败: {e}")
            return None
