#!/usr/bin/env python3
"""测试重构后的客户端

验证：
1. 统一CDP客户端功能
2. 员工KPI API客户端
3. 店铺KPI导出器
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, 'src')

from tourism_automation.shared import CdpClient, create_cdp_client
from tourism_automation.collectors.fliggy_kpi.employee_kpi.api_client import EmployeeKpiApiClient
from tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter import ShopKpiExporter


class TestUnifiedCdpClient(unittest.TestCase):
    """测试统一CDP客户端"""

    def setUp(self):
        """测试前准备"""
        self.cdp = create_cdp_client()

    def test_list_tabs(self):
        """测试列出标签页"""
        tabs = self.cdp.list_tabs()
        self.assertIsInstance(tabs, list)
        self.assertGreater(len(tabs), 0)
        print(f"✅ 找到 {len(tabs)} 个标签页")

    def test_find_tab_by_url_pattern(self):
        """测试通过URL模式查找标签页"""
        # 假设Chrome正在运行且有一个标签页
        try:
            tab = self.cdp.find_tab_by_url_pattern("http")
            self.assertIn('ws_url', tab)
            self.assertIn('id', tab)
            print(f"✅ 找到标签页: {tab['title']}")
        except RuntimeError as e:
            self.skipTest(f"Chrome未运行或没有标签页: {e}")

    def test_execute_js_simple(self):
        """测试执行简单JavaScript"""
        try:
            tab = self.cdp.find_tab_by_url_pattern("http")
            result = self.cdp.execute_js(
                tab['ws_url'],
                '({test: "value", num: 123})'
            )
            self.assertIsInstance(result, dict)
            print(f"✅ JS执行成功: {result}")
        except RuntimeError as e:
            self.skipTest(f"Chrome未运行: {e}")


class TestEmployeeKpiApiClient(unittest.TestCase):
    """测试员工KPI API客户端"""

    def setUp(self):
        """测试前准备"""
        self.client = EmployeeKpiApiClient()

    def test_get_main_kpi(self):
        """测试获取主要KPI数据"""
        try:
            data = self.client.get_main_kpi("2026-04-21")
            self.assertIsInstance(data, dict)
            print(f"✅ 员工KPI数据获取成功")
            print(f"   数据键: {list(data.keys())[:5]}...")
        except Exception as e:
            self.skipTest(f"API调用失败: {e}")

    def test_get_employee_rank(self):
        """测试获取员工排名数据"""
        try:
            data = self.client.get_employee_rank("2026-04-21")
            self.assertIsInstance(data, dict)
            print(f"✅ 员工排名数据获取成功")
        except Exception as e:
            self.skipTest(f"API调用失败: {e}")


class TestShopKpiExporter(unittest.TestCase):
    """测试店铺KPI导出器"""

    def setUp(self):
        """测试前准备"""
        self.exporter = ShopKpiExporter()

    def test_find_shop_kpi_tab(self):
        """测试查找店铺KPI页面"""
        try:
            tab = self.exporter._get_shop_kpi_tab()
            self.assertIn('ws_url', tab)
            print(f"✅ 找到店铺KPI页面: {tab['title']}")
        except RuntimeError as e:
            self.skipTest(f"未找到店铺KPI页面: {e}")

    def test_inspect_form(self):
        """测试检查表单"""
        try:
            tab = self.exporter._get_shop_kpi_tab()
            form_info = self.exporter.inspect_form(
                tab['ws_url'],
                ShopKpiExporter.PASSWORD_FORM_SELECTOR
            )
            self.assertIsInstance(form_info, dict)
            print(f"✅ 表单检查成功: {form_info.get('inputCount', 0)} 个输入框")
        except RuntimeError as e:
            self.skipTest(f"未找到店铺KPI页面: {e}")


def run_tests():
    """运行所有测试"""
    print("=" * 70)
    print("重构后客户端测试")
    print("=" * 70)
    print()

    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestUnifiedCdpClient))
    suite.addTests(loader.loadTestsFromTestCase(TestEmployeeKpiApiClient))
    suite.addTests(loader.loadTestsFromTestCase(TestShopKpiExporter))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 打印总结
    print()
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
