"""飞猪客服KPI HTTP客户端（纯HTTP方式）"""

from __future__ import annotations

import json
import subprocess
from typing import Dict, List
from urllib.parse import urlencode
import requests


class EmployeeKpiHttpClient:
    """员工KPI HTTP客户端（纯HTTP）"""

    def __init__(self):
        from tourism_automation.collectors.fliggy_kpi.employee_kpi.auth_manager import AuthManager
        self.auth_manager = AuthManager()
        self.session = None

    def _get_session(self) -> requests.Session:
        """获取带有认证信息的session"""
        if self.session is None:
            # 获取认证信息
            auth_info = self.auth_manager.get_auth_info()

            # 创建session
            self.session = requests.Session()

            # 设置cookies
            cookies_str = auth_info.get('cookies', '')
            if cookies_str:
                for cookie in cookies_str.split('; '):
                    if '=' in cookie:
                        name, value = cookie.split('=', 1)
                        self.session.cookies.set(name, value)

            # 设置headers
            self.session.headers.update({
                'User-Agent': auth_info.get('userAgent', 'Mozilla/5.0'),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Content-Type': 'application/json',
                'Origin': 'https://kf.topchitu.com',
                'Referer': 'https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL'
            })

        return self.session

    def get_employee_rank(self, date: str) -> Dict:
        """获取员工排名数据（纯HTTP）

        Args:
            date: 业务日期

        Returns:
            Dict: API响应数据
        """
        session = self._get_session()

        # 构建URL
        url = "https://kf.topchitu.com/api/homepage/team/employee-rank"
        params = {
            "from": date,
            "to": date,
            "queryDateType": "DAY"
        }

        # 发送请求
        response = session.get(url, params=params, timeout=10)

        if response.status_code != 200:
            raise Exception(f"HTTP请求失败: {response.status_code}")

        return response.json()

    def refresh_auth(self):
        """刷新认证信息（重新从浏览器获取）"""
        self.auth_manager.clear_cache()
        self.session = None
        return self._get_session()
