"""飞猪客服KPI API客户端（基于CDP fetch）

通过在浏览器页面中执行fetch来调用API，自动使用浏览器的认证信息
"""

from __future__ import annotations

import json
from typing import Dict
from urllib.parse import urlencode

from tourism_automation.shared import CdpClient


class EmployeeKpiApiClient:
    """员工KPI API客户端（使用CDP fetch）"""

    def __init__(self, cdp_client: CdpClient | None = None):
        """初始化客户端

        Args:
            cdp_client: CDP客户端，默认创建新实例
        """
        self.cdp = cdp_client or CdpClient(default_timeout=10)

    def _fetch_api(self, api_path: str, params: Dict | None = None) -> Dict:
        """调用Topchitu API

        Args:
            api_path: API路径
            params: 查询参数

        Returns:
            Dict: API响应数据
        """
        # 构建完整URL
        base_url = "https://kf.topchitu.com"
        if params:
            url = f"{base_url}{api_path}?{urlencode(params)}"
        else:
            url = f"{base_url}{api_path}"

        # 使用CDP fetch
        return self.cdp.fetch_api(
            url_pattern="topchitu.com",
            api_url=url,
            params={}
        )

    def get_main_kpi(self, date: str) -> Dict:
        """获取主要KPI数据

        Args:
            date: 业务日期 (YYYY-MM-DD)

        Returns:
            Dict: KPI数据
        """
        params = {
            "from": date,
            "to": date,
            "queryDateType": "DAY"
        }

        return self._fetch_api("/api/homepage/team/main-kpi", params)

    def get_employee_rank(self, date: str) -> Dict:
        """获取员工排名数据

        Args:
            date: 业务日期

        Returns:
            Dict: 员工排名数据
        """
        params = {
            "from": date,
            "to": date,
            "queryDateType": "DAY"
        }

        return self._fetch_api("/api/homepage/team/employee-rank", params)

    def get_custom_report_kpi(
        self,
        date: str,
        kpi_id: str = "1721",
        wwt: str = "ALL"
    ) -> Dict:
        """获取自定义报告KPI数据

        Args:
            date: 业务日期
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Dict: 自定义报告KPI数据
        """
        params = {
            "range": json.dumps({"from": date, "to": date}),
            "dateType": "DAY",
            "id": kpi_id,
            "wwt": wwt
        }

        return self._fetch_api("/api/custom/report/kpi", params)

    def get_all_indicators(self) -> Dict:
        """获取所有指标定义

        Returns:
            Dict: 指标定义
        """
        return self._fetch_api("/api/appraisal/all-indicators", {})
