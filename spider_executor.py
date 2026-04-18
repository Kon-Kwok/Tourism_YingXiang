
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞猪数据爬虫 - 执行层 v2.0
读取 JSON 配置文件，执行业务数据采集

主要改进：
- 支持cookie登录（避免验证码）
- 登录步骤抽离，去冗余
- 配置文件位置：config/spider_config.json
"""

import json
import pymysql
import os
from datetime import datetime


class SpiderExecutor:
    def __init__(self, config_path="config/spider_config.json"):
        self.config_path = config_path
        self.config = None
        self.conn = None
        self.browser = None  # 实际使用时初始化为 Selenium/Playwright
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def load_config(self):
        """加载JSON配置文件"""
        print("[1/5] 加载配置文件...")
        full_path = os.path.join(self.base_dir, self.config_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        print(f"   [OK] {self.config['spider_name']} v{self.config['version']}")
        return True

    def connect_db(self):
        """连接MySQL业务数据库"""
        print("[2/5] 连接业务数据库...")
        db_config = self.config['database']
        self.conn = pymysql.connect(
            host=db_config['host'],
            port=db_config['port'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            charset=db_config['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
        print("   [OK]")
        return True

    def get_page_config(self, page_id):
        """从JSON配置中获取页面配置"""
        for page in self.config['pages']:
            if page['page_id'] == page_id:
                return page
        raise ValueError(f"未找到 page_id: {page_id}")

    # ==================== 登录管理（抽离，去冗余） ====================

    def try_login_with_cookie(self):
        """尝试用cookie登录（优先，避免验证码）"""
        login_config = self.config.get('login', {})
        cookie_file = login_config.get('cookie_file', 'cookies.json')
        cookie_path = os.path.join(self.base_dir, cookie_file)

        if os.path.exists(cookie_path):
            print(f"   [INFO] 尝试用cookie登录: {cookie_file}")
            # TODO: 实际使用时加载cookie到浏览器
            return True
        return False

    def login_with_password(self):
        """用密码登录（cookie失效时使用）"""
        login_config = self.config.get('login', {})
        base_url = login_config.get('base_url')
        username = login_config.get('username')
        password = login_config.get('password')

        print(f"   [INFO] 用密码登录: {username}")
        # TODO: 实际使用时执行密码登录步骤
        # 1. 打开 base_url
        # 2. 输入用户名密码
        # 3. 保存cookie到 cookie_file

    def login(self):
        """统一登录入口"""
        print("[3/5] 检查登录状态...")

        if not self.try_login_with_cookie():
            self.login_with_password()
        else:
            print("   [OK] Cookie登录成功")

        return True

    # ==================== 批次管理 ====================

    def create_batch(self, page_id, page_name):
        """创建采集批次"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO spider_data_batch
                (page_id, page_name, status, batch_start_time)
                VALUES (%s, %s, 'running', NOW())
            """, (page_id, page_name))
            self.conn.commit()
            return cursor.lastrowid

    def update_batch_success(self, batch_id):
        """标记批次成功"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE spider_data_batch
                SET status='success', batch_end_time=NOW()
                WHERE id=%s
            """, (batch_id,))
        self.conn.commit()

    def update_batch_failed(self, batch_id, error_message):
        """标记批次失败"""
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE spider_data_batch
                SET status='failed', error_message=%s, batch_end_time=NOW()
                WHERE id=%s
            """, (error_message, batch_id))
        self.conn.commit()

    # ==================== 步骤执行 ====================

    def execute_step(self, step):
        """执行单个步骤"""
        step_type = step['step_type']
        selector_type = step.get('selector_type')
        selector_value = step.get('selector_value')
        input_value = step.get('input_value')
        wait_timeout = step.get('wait_timeout', 5000)

        print(f"  步骤 [{step['step_order']}]: {step['step_description']}")

        # ========== 这里需要替换为实际的 Selenium/Playwright 代码 ==========
        if step_type == 'navigate':
            print(f"    → 导航: {input_value}")
            # self.browser.get(input_value)

        elif step_type == 'click':
            print(f"    → 点击: {selector_type}={selector_value}")
            # element = self.browser.find_element(selector_type, selector_value)
            # element.click()

        elif step_type == 'input':
            print(f"    → 输入: {selector_type}={selector_value}")
            # element = self.browser.find_element(selector_type, selector_value)
            # element.send_keys(input_value)

        elif step_type == 'wait':
            print(f"    → 等待: {step.get('wait_condition')}")
            # WebDriverWait(self.browser, wait_timeout/1000).until(...)
        # =====================================================================

    def execute_all_steps(self, steps):
        """执行所有步骤"""
        print("\n--- 开始执行操作步骤 ---")
        for step in steps:
            self.execute_step(step)
        print("--- 步骤完成 ---\n")

    # ==================== 数据提取 ====================

    def extract_value(self, field_mapping):
        """从页面提取单个字段值"""
        selector_type = field_mapping['selector_type']
        selector_value = field_mapping['selector_value']
        extract_type = field_mapping['extract_type']
        clean_rule = field_mapping.get('clean_rule')

        print(f"  提取: {field_mapping['frontend_control_name']}")

        # ========== 这里需要替换为实际的 Selenium/Playwright 代码 ==========
        # element = self.browser.find_element(selector_type, selector_value)
        #
        # if extract_type == 'text':
        #     value = element.text
        # elif extract_type == 'attribute':
        #     value = element.get_attribute(field_mapping.get('extract_attribute'))
        # else:
        #     value = None

        value = "模拟数据"  # 模拟返回
        # =====================================================================

        if value and clean_rule:
            value = self.clean_data(value, clean_rule)

        return value

    def clean_data(self, value, clean_rule):
        """数据清洗"""
        if '提取数字' in clean_rule:
            import re
            nums = re.findall(r'\d+\.?\d*', str(value))
            value = nums[0] if nums else None
        elif '去除%' in clean_rule:
            value = str(value).replace('%', '')
        elif '去除¥' in clean_rule or '去除逗号' in clean_rule:
            value = str(value).replace('¥', '').replace(',', '')
        return value

    def extract_and_save_data(self, field_mappings, batch_id):
        """提取并保存数据"""
        print("--- 开始提取数据 ---")

        # 按目标表分组
        table_data = {}
        for mapping in field_mappings:
            target_table = mapping['target_table']
            if target_table not in table_data:
                table_data[target_table] = {'mappings': [], 'values': {}}
            table_data[target_table]['mappings'].append(mapping)

        # 提取数据
        for mapping in field_mappings:
            value = self.extract_value(mapping)
            target_table = mapping['target_table']
            target_field = mapping['target_field']
            table_data[target_table]['values'][target_field] = value

        # 保存到业务表
        for table_name, data in table_data.items():
            self.save_to_biz_table(table_name, data['values'], batch_id)

        print("--- 数据提取完成 ---\n")

    def save_to_biz_table(self, table_name, values, batch_id):
        """保存数据到业务表"""
        if not values:
            return

        values['data_batch_id'] = batch_id

        columns = ', '.join([f"`{k}`" for k in values.keys()])
        placeholders = ', '.join(['%s'] * len(values))

        sql = f"INSERT INTO `{table_name}` ({columns}) VALUES ({placeholders})"

        with self.conn.cursor() as cursor:
            cursor.execute(sql, list(values.values()))
        self.conn.commit()

        print(f"  [OK] 保存到 {table_name}")

    # ==================== 主流程 ====================

    def run(self, page_id):
        """运行爬虫"""
        print("=" * 60)
        print("  飞猪数据爬虫 - 执行层 v2.0")
        print("  (配置: config/spider_config.json | SQL: 拆分到sql/)")
        print("=" * 60)

        try:
            # 1. 加载配置和连接数据库
            self.load_config()
            self.connect_db()
            self.login()

            # 2. 获取页面配置
            page_config = self.get_page_config(page_id)
            steps = page_config['steps']
            fields = page_config['field_mappings']

            print(f"\n页面: {page_config['page_name']}")
            print(f"操作步骤: {len(steps)} 步")
            print(f"字段映射: {len(fields)} 个")

            # 3. 创建批次
            batch_id = self.create_batch(page_id, page_config['page_name'])
            print(f"批次ID: {batch_id}")

            # 4. 执行步骤
            self.execute_all_steps(steps)

            # 5. 提取数据并保存
            self.extract_and_save_data(fields, batch_id)

            # 6. 标记成功
            self.update_batch_success(batch_id)
            print("\n[OK] 爬虫执行成功！")

        except Exception as e:
            import traceback
            error_msg = str(e) + "\n" + traceback.format_exc()
            if 'batch_id' in locals():
                self.update_batch_failed(batch_id, error_msg)
            print(f"\n[FAIL] {e}")

        finally:
            if self.conn:
                self.conn.close()


if __name__ == "__main__":
    # 示例：爬取赤兔名品
    executor = SpiderExecutor()
    executor.run(page_id="chitu_customer_service")

