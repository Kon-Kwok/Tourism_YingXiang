"""飞猪客服KPI Playwright客户端

使用Playwright CLI进行数据采集，支持headless模式
"""

from __future__ import annotations

import json
import subprocess
from typing import Dict
from urllib.parse import urlencode


class PlaywrightKpiClient:
    """基于Playwright CLI的KPI客户端"""

    def __init__(self, headless: bool = True):
        """
        Args:
            headless: 是否使用headless模式（后台运行）
        """
        self.headless = headless
        self.cli_path = "@playwright/cli"

    def _run_playwright(self, js_code: str, url: str = None) -> Dict:
        """运行Playwright命令执行JavaScript

        Args:
            js_code: 要执行的JavaScript代码
            url: 要导航到的URL（可选）

        Returns:
            Dict: 执行结果
        """
        # 使用临时文件来传递JavaScript代码
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            js_file = f.name

        try:
            if url:
                # 先打开页面
                open_result = subprocess.run(
                    ["npm", "exec", "-g", self.cli_path, "--", "open", url],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if open_result.returncode != 0:
                    raise Exception(f"打开页面失败: {open_result.stderr}")

            # 执行JavaScript
            cmd = ["npm", "exec", "-g", self.cli_path, "--", "eval", js_file]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            # 关闭浏览器
            subprocess.run(
                ["npm", "exec", "-g", self.cli_path, "--", "close"],
                capture_output=True,
                timeout=10
            )

            if result.returncode != 0:
                raise Exception(f"Playwright执行失败: {result.stderr}")

            # 解析输出 - 从输出中提取JSON
            output = result.stdout.strip()

            # 查找JSON输出
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('{') or line.startswith('['):
                    try:
                        return json.loads(line)
                    except:
                        pass

            # 如果没有找到JSON，返回整个输出
            return {"raw_output": output}

        finally:
            import os
            if os.path.exists(js_file):
                os.unlink(js_file)

    def get_employee_rank(self, date: str, kpi_id: str = "1721", wwt: str = "ALL") -> Dict:
        """获取员工排名数据

        Args:
            date: 业务日期
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Dict: API响应数据
        """
        url = f"https://kf.topchitu.com/web/custom-kpi/employee-kpi?id={kpi_id}&wwt={wwt}"
        params = {
            "from": date,
            "to": date,
            "queryDateType": "DAY"
        }

        api_url = f"/api/homepage/team/employee-rank?{urlencode(params)}"

        # JavaScript代码 - 在页面中执行fetch（使用简单的字符串拼接）
        js_code = f'''
fetch("{api_url}").then(r=>r.json()).then(d=>JSON.stringify({{success:true,count:d.valueList?d.valueList.length:0,data:d}})).catch(e=>JSON.stringify({{success:false,error:e.message}}))
'''

        return self._run_playwright(js_code, url)
