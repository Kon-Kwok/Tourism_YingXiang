"""直接连接Chrome调试端口的CDP客户端

使用WebSocket直接连接到Chrome的远程调试端口，
不需要每次点击"允许调试"
"""

from __future__ import annotations

import json
import os
import subprocess
from typing import Dict, Any
from urllib.parse import urlencode
import time


class DirectCDPClient:
    """直接连接Chrome调试端口的客户端"""

    def __init__(self, debug_port: int = 9222):
        """
        Args:
            debug_port: Chrome远程调试端口，默认9222
        """
        self.debug_port = debug_port
        self._ensure_chrome_running()

    def _ensure_chrome_running(self):
        """确保Chrome正在运行并带调试端口"""
        # 检查Chrome是否已在运行
        if self._is_chrome_running():
            return

        # 启动Chrome
        launch_script = "/home/kk/Tourism_YingXiang/bin/start-debug-chrome.sh"
        try:
            subprocess.run(
                [launch_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            # 等待Chrome完全启动
            time.sleep(2)
        except Exception as e:
            raise Exception(f"启动Chrome失败: {e}\n请运行: {launch_script}")

    def _is_chrome_running(self) -> bool:
        """检查Chrome是否在运行"""
        try:
            result = subprocess.run(
                ["curl", "-s", f"http://localhost:{self.debug_port}/json/version"],
                capture_output=True,
                text=True,
                timeout=3
            )
            return result.returncode == 0 and "Chrome" in result.stdout
        except Exception:
            return False

    def _get_target_id(self) -> str:
        """获取当前激活的标签页ID"""
        # 设置环境变量
        env = {
            **os.environ,
            'CDP_PORT_FILE': '/home/kk/.config/google-chrome-debug/Default/DevToolsActivePort'
        }

        result = subprocess.run(
            ["curl", "-s", f"http://localhost:{self.debug_port}/json"],
            capture_output=True,
            text=True,
            timeout=5,
            env=env
        )

        if result.returncode != 0:
            raise Exception(f"无法连接到Chrome调试端口: {self.debug_port}")

        try:
            tabs = json.loads(result.stdout)
            # 找到KPI页面
            for tab in tabs:
                url = tab.get('url', '')
                if 'custom-kpi/employee-kpi' in url:
                    return tab.get('id')

            # 如果没找到KPI页面，返回第一个标签页
            if tabs:
                return tabs[0].get('id')

            raise Exception("没有找到任何浏览器标签页")

        except json.JSONDecodeError:
            raise Exception("解析Chrome标签页列表失败")

    def execute_js(self, js_code: str) -> Any:
        """在页面中执行JavaScript（已弃用，请使用get_employee_rank）

        Args:
            js_code: JavaScript代码

        Returns:
            执行结果
        """
        target_id = self._get_target_id()
        return self._execute_via_cdp(target_id, js_code)

    def _execute_via_cdp(self, target_id: str, js_code: str) -> Dict:
        """通过CDP执行JavaScript"""
        cdp_path = "/home/kk/Tourism_YingXiang/.claude/skills/chrome-cdp/scripts/cdp.mjs"

        # 设置环境变量，指定DevToolsActivePort文件位置
        env = {
            **os.environ,
            'CDP_PORT_FILE': '/home/kk/.config/google-chrome-debug/Default/DevToolsActivePort'
        }

        result = subprocess.run(
            [cdp_path, "eval", target_id, js_code],
            capture_output=True,
            text=True,
            timeout=30,
            env=env
        )

        if result.returncode != 0:
            raise Exception(f"CDP执行失败: {result.stderr}")

        try:
            return json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {"raw_output": result.stdout.strip()}

    def get_employee_rank(self, date: str) -> Dict:
        """获取员工排名数据"""
        target_id = self._get_target_id()

        # 构建JavaScript
        params = {"from": date, "to": date, "queryDateType": "DAY"}
        from urllib.parse import urlencode
        api_url = f"/api/homepage/team/employee-rank?{urlencode(params)}"

        js_code = f'''fetch("{api_url}").then(r=>r.json()).then(d=>JSON.stringify({{success:true,count:d.valueList?d.valueList.length:0,data:d}})).catch(e=>JSON.stringify({{success:false,error:e.message}}))'''

        return self._execute_via_cdp(target_id, js_code)
