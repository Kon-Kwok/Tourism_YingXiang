"""店铺KPI导出器

通过CDP自动点击导出按钮，输入密码，下载文件
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from tourism_automation.shared import CdpClient


class ShopKpiExporter:
    """店铺KPI导出器 - 自动化导出流程"""

    # 页面URL和选择器常量
    SHOP_KPI_URL = "https://kf.topchitu.com/web/custom-kpi/shop-kpi?id=941"
    PASSWORD_FORM_SELECTOR = '#root > section > section > main > div:nth-child(2) > div > div.formContainer___3uYye'

    def __init__(
        self,
        cdp_client: CdpClient | None = None,
        download_dir: str = "/tmp/downloads"
    ):
        """初始化导出器

        Args:
            cdp_client: CDP客户端，默认创建新实例
            download_dir: 下载目录
        """
        self.cdp = cdp_client or CdpClient(default_timeout=30)
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def _get_shop_kpi_tab(self) -> Dict:
        """获取店铺KPI页面标签

        Returns:
            Dict: 标签页信息 {id, title, url, ws_url}

        Raises:
            RuntimeError: 未找到页面
        """
        try:
            return self.cdp.find_tab_by_url_pattern("shop-kpi")
        except RuntimeError:
            raise RuntimeError(
                f"未找到店铺KPI页面，请先打开: {self.SHOP_KPI_URL}"
            )

    def click_element(self, ws_url: str, selector: str) -> bool:
        """点击页面元素

        Args:
            ws_url: WebSocket URL
            selector: CSS选择器

        Returns:
            bool: 是否点击成功
        """
        # 转义选择器
        selector_escaped = selector.replace('\\', '\\\\').replace("'", "\\'")

        js_code = f'''
        (function() {{
            const el = document.querySelector('{selector_escaped}');
            if (el) {{
                el.scrollIntoView();
                el.click();
                return {{success: true, text: el.textContent || el.innerText}};
            }}
            return {{success: false, error: 'Element not found'}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code)
        return result.get('success', False)

    def input_text(self, ws_url: str, selector: str, text: str) -> bool:
        """在输入框中输入文本

        Args:
            ws_url: WebSocket URL
            selector: CSS选择器
            text: 要输入的文本

        Returns:
            bool: 是否输入成功
        """
        # 转义选择器和文本
        selector_escaped = selector.replace('\\', '\\\\').replace("'", "\\'")
        text_escaped = text.replace('\\', '\\\\').replace('"', '\\"')

        js_code = f'''
        (function() {{
            const input = document.querySelector('{selector_escaped}');
            if (input) {{
                input.scrollIntoView();
                input.focus();
                input.value = "{text_escaped}";
                // 触发input事件
                input.dispatchEvent(new Event('input', {{bubbles: true}}));
                input.dispatchEvent(new Event('change', {{bubbles: true}}));
                return {{success: true}};
            }}
            return {{success: false, error: 'Input not found'}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code)
        return result.get('success', False)

    def wait_for_element(
        self,
        ws_url: str,
        selector: str,
        timeout_ms: int = 5000
    ) -> bool:
        """等待元素出现

        Args:
            ws_url: WebSocket URL
            selector: CSS选择器
            timeout_ms: 超时时间（毫秒）

        Returns:
            bool: 元素是否出现
        """
        selector_escaped = selector.replace('\\', '\\\\').replace("'", "\\'")

        js_code = f'''
        (function() {{
            return new Promise((resolve) => {{
                const start = Date.now();
                const check = () => {{
                    if (document.querySelector('{selector_escaped}')) {{
                        resolve(true);
                        return;
                    }}
                    const elapsed = Date.now() - start;
                    if (elapsed > {timeout_ms}) {{
                        resolve(false);
                        return;
                    }}
                    setTimeout(check, 100);
                }};
                check();
            }});
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code)
        # Promise返回boolean，可能被包装在value中
        if isinstance(result, bool):
            return result
        elif isinstance(result, dict) and 'value' in result:
            return bool(result['value'])
        else:
            return bool(result)

    def inspect_form(self, ws_url: str, container_selector: str) -> Dict:
        """检查表单内的元素（用于调试）

        Args:
            ws_url: WebSocket URL
            container_selector: 容器选择器

        Returns:
            Dict: 表单内的元素信息
        """
        selector_escaped = container_selector.replace('\\', '\\\\').replace("'", "\\'")

        js_code = f'''
        (function() {{
            const container = document.querySelector('{selector_escaped}');
            if (!container) {{
                return {{error: "Container not found"}};
            }}

            const inputs = container.querySelectorAll('input');
            const buttons = container.querySelectorAll('button');

            return {{
                inputCount: inputs.length,
                buttonCount: buttons.length,
                inputs: Array.from(inputs).map(i => ({{
                    type: i.type,
                    name: i.name,
                    placeholder: i.placeholder,
                    className: i.className,
                    id: i.id
                }})),
                buttons: Array.from(buttons).map(b => ({{
                    text: b.textContent.trim(),
                    className: b.className,
                    type: b.type
                }}))
            }};
        }})()
        '''

        return self.cdp.execute_js(ws_url, js_code)

    def export_shop_kpi(
        self,
        password: str = "1234",
        output_file: Optional[str] = None
    ) -> str:
        """导出店铺KPI数据

        Args:
            password: 导出密码
            output_file: 输出文件路径（可选，默认自动命名）

        Returns:
            str: 下载文件的路径
        """
        # 1. 找到店铺KPI页面
        print("🔍 正在查找店铺KPI页面...")
        tab_info = self._get_shop_kpi_tab()
        print(f"✅ 找到页面: {tab_info['title']}")
        ws_url = tab_info['ws_url']

        # 2. 点击导出按钮
        print("\n📌 步骤 1/4: 点击导出按钮...")

        export_selectors = [
            'span.exportButton___RFKHu > button',
            'span[class*="exportButton"] > button',
            'span[class*="export"] > button',
            'form button:has(span)',
            'form button',
        ]

        clicked = False
        for selector in export_selectors:
            print(f"  尝试选择器: {selector}")
            if self.click_element(ws_url, selector):
                clicked = True
                print("✓ 导出按钮已点击")
                break
            else:
                print(f"  ✗ 未找到元素")

        if not clicked:
            raise RuntimeError("无法找到或点击导出按钮")

        # 3. 等待密码弹窗并输入密码
        print("\n🔑 步骤 2/4: 等待密码输入框...")
        time.sleep(1)  # 等待弹窗出现

        # 检查密码弹窗
        print("  检查密码弹窗...")
        try:
            form_info = self.inspect_form(ws_url, self.PASSWORD_FORM_SELECTOR)
            if 'error' in form_info:
                print(f"  ⚠️  密码弹窗容器未找到，尝试全局查找...")
                global_modal_selectors = [
                    '.ant-modal',
                    '.ant-modal-content',
                    '[class*="Modal"]',
                    '[class*="modal"]'
                ]
                for modal_sel in global_modal_selectors:
                    if self.wait_for_element(ws_url, modal_sel, timeout_ms=1000):
                        print(f"  ✓ 找到模态框: {modal_sel}")
                        form_info = self.inspect_form(ws_url, modal_sel)
                        break
            else:
                print(f"  ✓ 密码弹窗容器已找到")
                print(f"    - 输入框数量: {form_info.get('inputCount', 0)}")
                print(f"    - 按钮数量: {form_info.get('buttonCount', 0)}")
        except Exception as e:
            print(f"  ⚠️  检查弹窗时出错: {e}")

        # 密码输入框选择器
        password_selectors = [
            '#password input[type="password"]',
            '#password input',
            'input[type="password"]',
            '.ant-input[type="password"]'
        ]

        password_found = False
        for selector in password_selectors:
            print(f"  尝试选择器: {selector}")
            if self.wait_for_element(ws_url, selector, timeout_ms=3000):
                password_found = True
                print("  ✓ 密码输入框已找到")

                # 输入密码
                print("\n🔑 步骤 3/4: 输入密码...")
                if self.input_text(ws_url, selector, password):
                    print("  ✓ 密码已输入")
                    time.sleep(0.5)  # 等待输入生效

                    # 查找并点击确认按钮
                    print("  查找确认按钮...")
                    confirm_selectors = [
                        f'{self.PASSWORD_FORM_SELECTOR} button.ant-btn-primary',
                        f'{self.PASSWORD_FORM_SELECTOR} button:has(span:contains("确定"))',
                        f'{self.PASSWORD_FORM_SELECTOR} button',
                        '.ant-modal button.ant-btn-primary',
                        'button.ant-btn-primary',
                    ]

                    for confirm_sel in confirm_selectors:
                        print(f"    尝试: {confirm_sel}")
                        if self.click_element(ws_url, confirm_sel):
                            print("  ✓ 确认按钮已点击")
                            break
                    else:
                        print("  ⚠️  未找到确认按钮，可能自动提交了")

                    break
                else:
                    print(f"  ⚠️  输入密码失败")
                break
            else:
                print(f"  ✗ 未找到元素")

        if not password_found:
            raise RuntimeError("未找到密码输入框，导出流程失败")

        # 4. 等待下载
        print("\n📥 步骤 4/4: 等待下载...")

        # 生成默认文件名
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = str(self.download_dir / f"shop_kpi_{timestamp}.xlsx")

        print(f"📁 下载目录: {self.download_dir}")
        print(f"📄 保存为: {output_file}")
        print("\n✅ 导出流程已启动！")
        print(f"\n💡 提示: 请在浏览器中确认下载保存位置")
        print(f"💡 文件将下载到Chrome的默认下载目录")

        return output_file


def export_shop_kpi(
    password: str = "1234",
    output_file: Optional[str] = None
) -> str:
    """便捷函数：导出店铺KPI数据

    Args:
        password: 导出密码（默认1234）
        output_file: 输出文件路径（可选）

    Returns:
        str: 下载文件的路径
    """
    exporter = ShopKpiExporter()
    return exporter.export_shop_kpi(password, output_file)


if __name__ == "__main__":
    # 测试导出
    print("店铺KPI导出测试\n")

    try:
        file_path = export_shop_kpi("1234")
        print(f"\n✅ 导出成功！")
        print(f"文件路径: {file_path}")
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
