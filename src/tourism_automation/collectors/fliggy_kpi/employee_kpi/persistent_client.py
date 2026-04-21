"""飞猪客服KPI持久化客户端

优化的CDP客户端，保持Chrome连接活跃
"""

from __future__ import annotations

import json
import subprocess
from typing import Dict
from urllib.parse import urlencode


class PersistentKpiClient:
    """持久化KPI客户端（优化的CDP方式）"""

    def __init__(self):
        self.cdp_path = "/home/kk/Tourism_YingXiang/.claude/skills/chrome-cdp/scripts/cdp.mjs"
        self._target_id = None

    def get_target_id(self) -> str:
        """获取或复用Chrome target ID"""
        if self._target_id is None:
            self._target_id = self._find_target_page()
        return self._target_id

    def _find_target_page(self) -> str:
        """查找Chrome中的KPI页面"""
        result = subprocess.run(
            [self.cdp_path, "list"],
            capture_output=True,
            text=True,
            timeout=10
        )

        for line in result.stdout.split('\n'):
            if 'custom-kpi/employee-kpi' in line:
                return line.split()[0]

        raise Exception("未找到目标页面，请先打开: https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721")

    def fetch_api(self, api_path: str, params: Dict = None) -> Dict:
        """执行fetch调用（优化版）

        Args:
            api_path: API路径
            params: 查询参数

        Returns:
            Dict: API响应数据
        """
        target_id = self.get_target_id()

        # 构建URL
        if params:
            url = f"{api_path}?{urlencode(params)}"
        else:
            url = api_path

        # 优化的JavaScript - 使用Promise链
        js_code = f'''fetch("{url}").then(r=>r.json()).then(d=>JSON.stringify({{success:true,count:d.valueList?d.valueList.length:0,data:d}})).catch(e=>JSON.stringify({{success:false,error:e.message}}))'''

        result = subprocess.run(
            [self.cdp_path, "eval", target_id, js_code],
            capture_output=True,
            text=True,
            timeout=20  # 增加超时时间
        )

        if result.returncode != 0:
            raise Exception(f"CDP执行失败: {result.stderr}")

        response_obj = json.loads(result.stdout.strip())

        if not response_obj.get('success'):
            raise Exception(f"Fetch失败: {response_obj.get('error')}")

        # 返回data或整个response_obj（如果没有data字段）
        return response_obj.get('data', response_obj)

    def get_employee_rank(self, date: str) -> Dict:
        """获取员工排名数据（快速版）

        Args:
            date: 业务日期

        Returns:
            Dict: API响应数据
        """
        params = {
            "from": date,
            "to": date,
            "queryDateType": "DAY"
        }

        return self.fetch_api("/api/homepage/team/employee-rank", params)
