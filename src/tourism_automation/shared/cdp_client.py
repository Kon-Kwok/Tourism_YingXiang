"""统一的Chrome DevTools Protocol (CDP) 客户端

支持两种主要用途：
1. API数据采集：通过fetch调用API
2. UI交互自动化：点击、输入等操作
"""

from __future__ import annotations

import asyncio
import json
import subprocess
import websockets
from typing import Dict, List, Optional
from pathlib import Path


class CdpClient:
    """统一的CDP客户端"""

    def __init__(self, debug_port: int = 9222, default_timeout: int = 30):
        """初始化CDP客户端

        Args:
            debug_port: Chrome调试端口
            default_timeout: 默认超时时间（秒）
        """
        self.debug_port = debug_port
        self.default_timeout = default_timeout

    def list_tabs(self) -> List[Dict]:
        """列出所有Chrome标签页

        Returns:
            List[Dict]: 标签页列表，每个包含 {id, title, url, type, webSocketDebuggerUrl}
        """
        result = subprocess.run(
            ["curl", "-s", f"http://localhost:{self.debug_port}/json"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            raise RuntimeError(f"无法连接到Chrome调试端口 {self.debug_port}")

        return json.loads(result.stdout)

    def find_tab_by_url_pattern(self, url_pattern: str) -> Dict:
        """根据URL模式查找标签页

        Args:
            url_pattern: URL包含的字符串

        Returns:
            Dict: 标签页信息 {id, title, url, ws_url}

        Raises:
            RuntimeError: 未找到匹配的标签页
        """
        tabs = self.list_tabs()

        for tab in tabs:
            if url_pattern in tab.get('url', '') and tab.get('type') == 'page':
                return {
                    'id': tab['id'],
                    'title': tab['title'],
                    'url': tab['url'],
                    'ws_url': tab['webSocketDebuggerUrl']
                }

        raise RuntimeError(f"未找到包含 '{url_pattern}' 的标签页")

    def find_tab_by_target_id(self, target_id: str) -> Dict:
        """根据target ID查找标签页

        Args:
            target_id: Chrome target ID（支持前缀匹配）

        Returns:
            Dict: 标签页信息 {id, title, url, ws_url}

        Raises:
            RuntimeError: 未找到匹配的标签页
        """
        tabs = self.list_tabs()

        # 支持前缀匹配
        for tab in tabs:
            tab_id = tab.get('id', '')
            if tab_id == target_id or tab_id.startswith(target_id[:8]):
                return {
                    'id': tab['id'],
                    'title': tab['title'],
                    'url': tab['url'],
                    'ws_url': tab['webSocketDebuggerUrl']
                }

        raise RuntimeError(f"未找到target_id: {target_id[:8]}...")

    def execute_js(
        self,
        ws_url: str,
        js_code: str,
        timeout: Optional[int] = None,
        await_promise: bool = True,
        user_gesture: bool = False,
    ) -> Dict:
        """通过WebSocket执行JavaScript

        Args:
            ws_url: WebSocket URL
            js_code: JavaScript代码
            timeout: 超时时间（秒），默认使用default_timeout
            await_promise: 是否等待Promise完成

        Returns:
            Dict: 执行结果

        Raises:
            RuntimeError: CDP执行错误
        """
        timeout = timeout or self.default_timeout

        async def _async_execute():
            async with websockets.connect(ws_url) as ws:
                cmd = {
                    "id": 1,
                    "method": "Runtime.evaluate",
                    "params": {
                        "expression": js_code,
                        "returnByValue": True,
                        "awaitPromise": await_promise,
                        "userGesture": user_gesture,
                    }
                }

                await ws.send(json.dumps(cmd))
                response = await asyncio.wait_for(ws.recv(), timeout=timeout)
                result_obj = json.loads(response)

                if 'error' in result_obj:
                    raise RuntimeError(f"CDP执行错误: {result_obj['error']}")

                # 解析嵌套的响应格式
                # 响应: {result: {result: {type: '...', value: '...'}}}
                result = result_obj.get('result', {}).get('result', {})

                if result.get('type') == 'string':
                    # 字符串类型，可能是JSON
                    value_str = result.get('value', '')
                    try:
                        return json.loads(value_str)
                    except json.JSONDecodeError:
                        return value_str

                elif result.get('type') == 'object':
                    # 对象类型，返回value
                    return result.get('value', result)

                elif result.get('type') == 'undefined':
                    return {}

                else:
                    # 其他类型（number, boolean等）
                    return result

        return asyncio.run(_async_execute())

    def fetch_api(
        self,
        url_pattern: str,
        api_url: str,
        params: Optional[Dict] = None,
        method: str = "GET"
    ) -> Dict:
        """使用fetch调用API（通过CDP）

        Args:
            url_pattern: 页面URL模式
            api_url: API URL
            params: 查询参数
            method: HTTP方法

        Returns:
            Dict: API响应数据

        Raises:
            RuntimeError: API调用失败
        """
        from urllib.parse import urlencode

        # 构建完整URL
        if params:
            full_url = f"{api_url}?{urlencode(params)}"
        else:
            full_url = api_url

        # 找到标签页
        tab = self.find_tab_by_url_pattern(url_pattern)

        # 执行fetch
        js_code = f'''
        (async () => {{
            try {{
                const response = await fetch("{full_url}", {{
                    method: "{method}",
                    headers: {{
                        "Accept": "application/json"
                    }}
                }});
                const data = await response.json();
                return JSON.stringify({{success: true, data: data}});
            }} catch (error) {{
                return JSON.stringify({{success: false, error: error.message}});
            }}
        }})()
        '''

        result = self.execute_js(tab['ws_url'], js_code, timeout=15)

        if not result.get('success'):
            raise RuntimeError(f"API调用失败: {result.get('error')}")

        return result.get('data')

    def click_element(
        self,
        url_pattern: str,
        selector: str,
        timeout: Optional[int] = None
    ) -> bool:
        """点击页面元素

        Args:
            url_pattern: 页面URL模式
            selector: CSS选择器
            timeout: 超时时间

        Returns:
            bool: 是否成功点击
        """
        tab = self.find_tab_by_url_pattern(url_pattern)

        js_code = f'''
        (async () => {{
            const element = document.querySelector("{selector}");
            if (!element) {{
                return {{success: false, error: "Element not found"}};
            }}
            element.click();
            await new Promise(resolve => setTimeout(resolve, 500));
            return {{success: true}};
        }})()
        '''

        result = self.execute_js(tab['ws_url'], js_code, timeout=timeout or 10)
        return result.get('success', False)

    def get_element_text(
        self,
        url_pattern: str,
        selector: str,
        timeout: Optional[int] = None
    ) -> Optional[str]:
        """获取元素文本

        Args:
            url_pattern: 页面URL模式
            selector: CSS选择器
            timeout: 超时时间

        Returns:
            Optional[str]: 元素文本，未找到返回None
        """
        tab = self.find_tab_by_url_pattern(url_pattern)

        js_code = f'''
        (async () => {{
            const element = document.querySelector("{selector}");
            if (!element) {{
                return {{success: false}};
            }}
            return {{success: true, text: element.textContent}};
        }})()
        '''

        result = self.execute_js(tab['ws_url'], js_code, timeout=timeout or 10)

        if result.get('success'):
            return result.get('text')
        return None


# 便捷函数
def create_cdp_client(debug_port: int = 9222, default_timeout: int = 30) -> CdpClient:
    """创建CDP客户端

    Args:
        debug_port: Chrome调试端口
        default_timeout: 默认超时时间（秒）

    Returns:
        CdpClient: CDP客户端实例
    """
    return CdpClient(debug_port=debug_port, default_timeout=default_timeout)
