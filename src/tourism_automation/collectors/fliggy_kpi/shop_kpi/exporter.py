"""店铺KPI导出器

通过CDP自动点击导出按钮，输入密码，下载文件
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

from tourism_automation.shared import CdpClient


class ShopKpiExporter:
    """店铺KPI导出器 - 自动化导出流程"""

    # 页面URL和选择器常量
    SHOP_KPI_URL = "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL"
    EXPORT_PASSWORD = "1234"
    DEFAULT_REPORT_NAME = "人均日接入"
    REPORT_URLS = {
        "人均日接入": "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL",
        "每周店铺个人数据": "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1996&wwt=ALL",
        "客服数据23年新": "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=2496&wwt=ALL",
    }
    SUPPORTED_REPORT_NAMES = (
        "人均日接入",
        "每周店铺个人数据",
        "客服数据23年新",
    )
    SUPPORTED_DATE_MODES = ("day", "week", "month")
    PASSWORD_FORM_SELECTOR = '#root > section > section > main > div:nth-child(2) > div > div.formContainer___3uYye'
    EXPORT_BUTTON_SELECTORS = (
        "button.download___7ocOy",
        'button[class*="download"]',
        'span[class*="download"] > button',
        'span[class*="exportButton"] > button',
        'span[class*="export"] > button',
        "form button",
    )
    PASSWORD_INPUT_SELECTORS = (
        "#password > span.inputWrapper___1eYh- > span > input",
        "#password input",
        'input[placeholder="请输入密码"]',
        f"{PASSWORD_FORM_SELECTOR} input",
        "input[type='password']",
    )

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
        """获取自定义 KPI 页面标签

        Returns:
            Dict: 标签页信息 {id, title, url, ws_url}

        Raises:
            RuntimeError: 未找到页面
        """
        for pattern in ("shop-kpi", "employee-kpi", "custom-kpi"):
            try:
                return self.cdp.find_tab_by_url_pattern(pattern)
            except RuntimeError:
                continue
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

        result = self.cdp.execute_js(ws_url, js_code, user_gesture=True)
        return result.get('success', False)

    def click_button_by_text(self, ws_url: str, text: str) -> bool:
        """按按钮文案点击，避免依赖脆弱的样式类名。"""
        text_json = json.dumps(text)

        js_code = f'''
        (function() {{
            const expected = {text_json}.replace(/\\s+/g, '');
            const button = Array.from(document.querySelectorAll('button')).find((el) => {{
                const actual = (el.innerText || el.textContent || '').replace(/\\s+/g, '');
                return actual === expected;
            }});
            if (!button) {{
                return {{success: false, error: 'Button not found'}};
            }}
            button.scrollIntoView();
            button.click();
            return {{success: true, text: button.textContent || button.innerText}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code, user_gesture=True)
        return result.get("success", False)

    def click_element_by_text(self, ws_url: str, text: str, selector: str) -> bool:
        """按文案点击指定集合中的元素。"""
        text_json = json.dumps(text)
        selector_json = json.dumps(selector)

        js_code = f'''
        (function() {{
            const expected = {text_json}.replace(/\\s+/g, '');
            const el = Array.from(document.querySelectorAll({selector_json})).find((node) => {{
                const actual = (node.innerText || node.textContent || '').replace(/\\s+/g, '');
                return actual === expected;
            }});
            if (!el) {{
                return {{success: false, error: 'Element not found'}};
            }}
            el.scrollIntoView();
            el.click();
            return {{success: true, text: el.textContent || el.innerText}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code, user_gesture=True)
        return result.get("success", False)

    def input_text(self, ws_url: str, selector: str, text: str) -> bool:
        """在输入框中输入文本

        Args:
            ws_url: WebSocket URL
            selector: CSS选择器
            text: 要输入的文本

        Returns:
            bool: 是否输入成功
        """
        selector_json = json.dumps(selector)
        text_json = json.dumps(text)

        js_code = f'''
        (function() {{
            const input = document.querySelector({selector_json});
            if (input) {{
                input.scrollIntoView();
                input.focus();
                const descriptor = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value');
                if (descriptor && descriptor.set) {{
                    descriptor.set.call(input, {text_json});
                }} else {{
                    input.value = {text_json};
                }}
                input.dispatchEvent(new Event('input', {{bubbles: true}}));
                input.dispatchEvent(new Event('change', {{bubbles: true}}));
                return {{success: true}};
            }}
            return {{success: false, error: 'Input not found'}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code, user_gesture=True)
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

    def _today_local_str(self) -> str:
        return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    def _validate_report_name(self, report_name: str) -> None:
        if report_name not in self.SUPPORTED_REPORT_NAMES:
            supported = ", ".join(self.SUPPORTED_REPORT_NAMES)
            raise ValueError(f"不支持的报表名称: {report_name}；支持: {supported}")

    def _validate_date_mode(self, date_mode: str) -> None:
        if date_mode not in self.SUPPORTED_DATE_MODES:
            supported = ", ".join(self.SUPPORTED_DATE_MODES)
            raise ValueError(f"不支持的时间模式: {date_mode}；支持: {supported}")

    def _default_output_file(self, report_name: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return str(self.download_dir / f"shop_kpi_{report_name}_{timestamp}.xlsx")

    def _candidate_download_dirs(self) -> list[Path]:
        candidates = [
            Path.home() / "下载",
            Path.home() / "Downloads",
            self.download_dir,
            Path("/tmp"),
        ]
        seen = set()
        ordered = []
        for candidate in candidates:
            key = str(candidate)
            if key in seen:
                continue
            seen.add(key)
            ordered.append(candidate)
        return ordered

    def _find_recent_downloaded_file(self, report_name: str, started_at: float) -> Optional[str]:
        suffixes = (".xlsx", ".xls", ".csv")
        matches: list[tuple[float, str]] = []
        report_name_normalized = report_name.replace(" ", "")

        for directory in self._candidate_download_dirs():
            if not directory.exists():
                continue

            for entry in directory.iterdir():
                if not entry.is_file() or entry.suffix.lower() not in suffixes:
                    continue
                stat = entry.stat()
                if stat.st_mtime < started_at:
                    continue
                if report_name_normalized not in entry.name.replace(" ", ""):
                    continue
                matches.append((stat.st_mtime, str(entry)))

        if not matches:
            return None
        return max(matches, key=lambda item: item[0])[1]

    def _wait_for_downloaded_file(
        self,
        report_name: str,
        started_at: float,
        timeout_seconds: float = 15.0,
        poll_interval: float = 0.5,
    ) -> Optional[str]:
        deadline = time.time() + timeout_seconds

        while time.time() <= deadline:
            actual_file = self._find_recent_downloaded_file(
                report_name=report_name,
                started_at=started_at,
            )
            if actual_file:
                return actual_file
            time.sleep(poll_interval)

        return None

    def select_report(self, ws_url: str, report_name: str) -> bool:
        report_name_json = json.dumps(report_name)
        report_url_json = json.dumps(self.REPORT_URLS.get(report_name))

        js_code = f'''
        (function() {{
            const expected = {report_name_json}.replace(/\\s+/g, '');
            const link = Array.from(document.querySelectorAll('.ant-menu-sub.ant-menu-inline a')).find((node) => {{
                const actual = (node.innerText || node.textContent || '').replace(/\\s+/g, '');
                return actual === expected;
            }});

            const href = (link && link.href) || {report_url_json};
            if (!href) {{
                return {{success: false, error: 'Report link not found'}};
            }}
            if (window.location.href === href) {{
                return {{success: true, href, navigated: false}};
            }}

            if (link) {{
                link.scrollIntoView();
                link.click();
                return {{success: true, href, navigated: true}};
            }}

            window.location.href = href;
            return {{success: true, href, navigated: true}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code)
        if result.get("success") and result.get("navigated"):
            time.sleep(2)
        return result.get("success", False)

    def select_date_mode(self, ws_url: str, mode: str) -> bool:
        mode_text = {"day": "日", "week": "周", "month": "月"}[mode]
        return self.click_element_by_text(ws_url, mode_text, "#dateType label")

    def select_date_range(self, ws_url: str, start_date: str, end_date: str) -> bool:
        start_json = json.dumps(start_date)
        end_json = json.dumps(end_date)

        js_code = f'''
        (async function() {{
            const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
            const monthValue = (text) => {{
                const match = text.match(/(\\d+)年\\s*(\\d+)月/);
                if (!match) return null;
                return Number(match[1]) * 12 + Number(match[2]);
            }};
            const ensureVisible = async (target) => {{
                for (let i = 0; i < 24; i += 1) {{
                    const cell = document.querySelector(`.ant-picker-dropdown td[title="${{target}}"]`);
                    if (cell) return cell;

                    const panels = Array.from(document.querySelectorAll('.ant-picker-dropdown .ant-picker-header-view'));
                    const values = panels.map((panel) => monthValue((panel.innerText || '').replace(/\\s+/g, ''))).filter(Boolean);
                    const targetMonth = monthValue(target.replace(/-(\\d{{2}})$/, '年$1月').replace(/^(\\d{{4}})-(\\d{{2}})/, '$1年$2月'));
                    if (!targetMonth || values.length === 0) return null;
                    const minVisible = Math.min(...values);
                    const maxVisible = Math.max(...values);
                    if (targetMonth < minVisible) {{
                        const prev = document.querySelector('.ant-picker-dropdown .ant-picker-header-prev-btn');
                        if (!prev) return null;
                        prev.click();
                    }} else if (targetMonth > maxVisible) {{
                        const nextButtons = Array.from(document.querySelectorAll('.ant-picker-dropdown .ant-picker-header-next-btn'));
                        const next = nextButtons[nextButtons.length - 1];
                        if (!next) return null;
                        next.click();
                    }} else {{
                        return null;
                    }}
                    await wait(100);
                }}
                return null;
            }};

            const firstInput = document.querySelector('.ant-picker-range .ant-picker-input input');
            if (!firstInput) return {{success: false, error: 'Range picker not found'}};
            firstInput.parentElement.click();
            await wait(150);

            const startCell = await ensureVisible({start_json});
            if (!startCell) return {{success: false, error: 'Start date not visible'}};
            startCell.click();
            await wait(150);

            const endCell = await ensureVisible({end_json});
            if (!endCell) return {{success: false, error: 'End date not visible'}};
            endCell.click();
            await wait(150);

            return {{success: true}};
        }})()
        '''

        result = self.cdp.execute_js(ws_url, js_code)
        return result.get("success", False)

    def export_shop_kpi(
        self,
        password: str = "1234",
        output_file: Optional[str] = None,
        report_name: str = DEFAULT_REPORT_NAME,
        date_mode: str = "day",
        date: Optional[str] = None,
    ) -> str:
        """导出店铺KPI数据

        Args:
            password: 导出密码
            output_file: 输出文件路径（可选，默认自动命名）

        Returns:
            str: 下载文件的路径
        """
        password = self.EXPORT_PASSWORD
        self._validate_report_name(report_name)
        self._validate_date_mode(date_mode)

        # 1. 找到店铺KPI页面
        print("🔍 正在查找店铺KPI页面...")
        tab_info = self._get_shop_kpi_tab()
        print(f"✅ 找到页面: {tab_info['title']}")
        ws_url = tab_info['ws_url']

        # 2. 切换报表
        print(f"\n📋 步骤 1/5: 切换报表到 {report_name}...")
        if not self.select_report(ws_url, report_name):
            raise RuntimeError(f"无法切换到报表: {report_name}")

        # 3. 切换时间模式和日期
        print(f"\n🗓️ 步骤 2/5: 设置时间模式 {date_mode}...")
        if not self.select_date_mode(ws_url, date_mode):
            raise RuntimeError(f"无法切换时间模式: {date_mode}")

        if date_mode == "day":
            resolved_date = date or self._today_local_str()
            print(f"  使用日期: {resolved_date}")
            if not self.select_date_range(ws_url, resolved_date, resolved_date):
                raise RuntimeError(f"无法设置日期: {resolved_date}")

        if not self.click_button_by_text(ws_url, "查询"):
            raise RuntimeError("无法点击查询按钮")
        time.sleep(1)

        # 4. 点击导出按钮
        print("\n📌 步骤 3/5: 点击导出按钮...")
        download_started_at = time.time()

        clicked = False
        for selector in self.EXPORT_BUTTON_SELECTORS:
            print(f"  尝试选择器: {selector}")
            if self.click_element(ws_url, selector):
                clicked = True
                print("✓ 导出按钮已点击")
                break
            else:
                print(f"  ✗ 未找到元素")

        if not clicked:
            raise RuntimeError("无法找到或点击导出按钮")

        # 5. 等待密码弹窗并输入密码
        print("\n🔑 步骤 4/5: 等待密码输入框...")
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
        password_found = False
        for selector in self.PASSWORD_INPUT_SELECTORS:
            print(f"  尝试选择器: {selector}")
            if self.wait_for_element(ws_url, selector, timeout_ms=3000):
                password_found = True
                print("  ✓ 密码输入框已找到")

                # 输入密码
                print("\n🔑 步骤 4/5: 输入密码...")
                if self.input_text(ws_url, selector, password):
                    print("  ✓ 密码已输入")
                    time.sleep(0.5)  # 等待输入生效

                    # 查找并点击确认按钮
                    print("  查找确认按钮...")
                    if self.click_button_by_text(ws_url, "确定"):
                        print("  ✓ 确认按钮已点击")
                    else:
                        print("  ⚠️  未找到确认按钮，可能自动提交了")

                    break
                else:
                    print(f"  ⚠️  输入密码失败")
                break
            else:
                print(f"  ✗ 未找到元素")

        if not password_found:
            print("  ⚠️  未检测到密码弹窗，跳过密码步骤")

        # 6. 等待下载
        print("\n📥 步骤 5/5: 等待下载...")

        # 生成默认文件名
        if output_file is None:
            output_file = self._default_output_file(report_name)

        actual_file = self._wait_for_downloaded_file(
            report_name=report_name,
            started_at=download_started_at,
        )
        if not actual_file:
            raise RuntimeError("导出已触发，但未在真实下载目录中找到文件")
        output_file = actual_file

        print(f"📁 下载目录: {Path(output_file).parent}")
        print(f"📄 保存为: {output_file}")
        print("\n✅ 导出流程已启动！")
        print(f"\n💡 提示: 请在浏览器中确认下载保存位置")
        print(f"💡 文件将下载到Chrome的默认下载目录")

        return output_file


def export_shop_kpi(
    password: str = "1234",
    output_file: Optional[str] = None,
    report_name: str = ShopKpiExporter.DEFAULT_REPORT_NAME,
    date_mode: str = "day",
    date: Optional[str] = None,
) -> str:
    """便捷函数：导出店铺KPI数据

    Args:
        password: 导出密码（默认1234）
        output_file: 输出文件路径（可选）

    Returns:
        str: 下载文件的路径
    """
    exporter = ShopKpiExporter()
    return exporter.export_shop_kpi(
        password=password,
        output_file=output_file,
        report_name=report_name,
        date_mode=date_mode,
        date=date,
    )


if __name__ == "__main__":
    # 测试导出
    print("店铺KPI导出测试\n")

    try:
        file_path = export_shop_kpi("1234")
        print(f"\n✅ 导出成功！")
        print(f"文件路径: {file_path}")
    except Exception as e:
        print(f"\n❌ 导出失败: {e}")
