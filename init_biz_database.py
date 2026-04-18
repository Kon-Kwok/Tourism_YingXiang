
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化象往科技飞猪数据业务数据库
按SQL文件夹顺序依次执行：
1. sql/01_init - 创建数据库
2. sql/03_data_batch - 创建批次表
3. sql/02_biz_tables - 创建业务表（7张）
"""

import json
import pymysql
import os


class BizDatabaseInitializer:
    def __init__(self, db_config_path="config/database.json"):
        self.db_config_path = db_config_path
        self.config = None
        self.conn = None
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def load_config(self):
        print("[1/5] 加载数据库配置...")
        config_path = os.path.join(self.base_dir, self.db_config_path)
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        print("   [OK]")
        return True

    def connect_mysql(self):
        print("[2/5] 连接MySQL...")
        mysql_config = self.config['mysql']
        self.conn = pymysql.connect(
            host=mysql_config['host'],
            port=mysql_config['port'],
            user=mysql_config['user'],
            password=mysql_config['password'],
            charset=mysql_config['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
        print("   [OK]")
        return True

    def execute_sql_file(self, sql_file_path):
        """执行单个SQL文件"""
        full_path = os.path.join(self.base_dir, sql_file_path)
        with open(full_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # 按分号分割语句（简单处理）
        statements = []
        current_stmt = []
        for line in sql_content.split('\n'):
            line = line.strip()
            if line.startswith('--') or line.startswith('#'):
                continue
            if line:
                current_stmt.append(line)
                if line.endswith(';'):
                    statements.append(' '.join(current_stmt))
                    current_stmt = []

        with self.conn.cursor() as cursor:
            for stmt in statements:
                if stmt.strip():
                    cursor.execute(stmt)
        self.conn.commit()

    def create_database(self):
        print("[3/5] 创建数据库...")
        self.execute_sql_file("sql/01_init/01_create_database.sql")
        print("   [OK] 数据库: xiangwang_fliggy_system")
        return True

    def create_tables(self):
        print("[4/5] 创建表...")

        # 批次表
        print("   - spider_data_batch...")
        self.execute_sql_file("sql/03_data_batch/spider_data_batch.sql")

        # 业务表
        biz_tables = [
            "biz_customer_service_daily.sql",
            "biz_customer_service_weekly.sql",
            "biz_cs_workload_log.sql",
            "biz_agent_performance_daily.sql",
            "biz_agent_sales_daily.sql",
            "biz_fliggy_store_daily.sql",
            "biz_fliggy_order_daily.sql",
        ]
        for table_file in biz_tables:
            print(f"   - {table_file.replace('.sql', '')}...")
            self.execute_sql_file(f"sql/02_biz_tables/{table_file}")

        print(f"   [OK] 表创建成功 (8张)")
        return True

    def verify(self):
        print("[5/5] 验证...")
        tables = [
            'spider_data_batch',
            'biz_customer_service_daily',
            'biz_customer_service_weekly',
            'biz_cs_workload_log',
            'biz_agent_performance_daily',
            'biz_agent_sales_daily',
            'biz_fliggy_store_daily',
            'biz_fliggy_order_daily',
        ]
        with self.conn.cursor() as cursor:
            cursor.execute("USE xiangwang_fliggy_system")
            for table in tables:
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    print(f"   [OK] {table}")
        return True

    def close(self):
        if self.conn:
            self.conn.close()

    def run(self):
        print("\n" + "=" * 60)
        print("  象往科技飞猪业务数据库初始化 v2.0")
        print("  (SQL文件拆分，每张表一个SQL)")
        print("=" * 60 + "\n")

        try:
            if not self.load_config():
                return False
            if not self.connect_mysql():
                return False
            if not self.create_database():
                return False
            if not self.create_tables():
                return False
            if not self.verify():
                return False

            print("\n" + "=" * 60)
            print("  [OK] 业务数据库初始化完成!")
            print("  数据库名: xiangwang_fliggy_system")
            print("  SQL文件位置: sql/")
            print("=" * 60)
            return True

        except Exception as e:
            print(f"\n[FAIL] {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            self.close()


if __name__ == "__main__":
    init = BizDatabaseInitializer()
    success = init.run()
    import sys
    sys.exit(0 if success else 1)

