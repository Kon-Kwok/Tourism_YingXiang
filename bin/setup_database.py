#!/usr/bin/env python3
"""数据库建表脚本"""

import pymysql
import os
from pathlib import Path

# 数据库配置 - 使用socket认证
DB_UNIX_SOCKET = '/var/run/mysqld/mysqld.sock'
DB_USER = 'root'
DB_PASSWORD = ''

# SQL文件列表
SQL_FILES = [
    # 千牛数据库表
    ('qianniu', 'sql/千牛/店铺数据每日登记/店铺数据每日登记.sql'),
    ('qianniu', 'sql/千牛/飞猪店铺日度关键数据/飞猪店铺日度关键数据.sql'),
    # 飞猪数据库表
    ('feizhu', 'sql/飞猪/万相台/万相台.sql'),
    ('feizhu', 'sql/飞猪/客服数据汇总-周数据/客服数据汇总-周数据.sql'),
    ('feizhu', 'sql/飞猪/客服数据汇总-日数据（人均日介入）/客服数据汇总-日数据.sql'),
    ('feizhu', 'sql/飞猪/客服绩效-工作量分析（23年新）/客服绩效-工作量分析.sql'),
    ('feizhu', 'sql/飞猪/客服绩效-汇总（每周店铺个人数据）/客服绩效-汇总.sql'),
    ('feizhu', 'sql/飞猪/引力魔方/引力魔方.sql'),
    ('feizhu', 'sql/飞猪/明星店铺/明星店铺.sql'),
    ('feizhu', 'sql/飞猪/直通车/直通车.sql'),
    ('feizhu', 'sql/飞猪/生意参谋/生意参谋.sql'),
]

def create_databases():
    """创建数据库"""
    print("正在创建数据库...")
    conn = pymysql.connect(unix_socket=DB_UNIX_SOCKET, user=DB_USER, password=DB_PASSWORD)
    cursor = conn.cursor()

    # 创建千牛数据库
    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS qianniu
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """)
    print("✓ 数据库 'qianniu' 创建成功")

    # 创建飞猪数据库
    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS feizhu
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """)
    print("✓ 数据库 'feizhu' 创建成功")

    conn.commit()
    conn.close()

def execute_sql_file(db_name, sql_file_path):
    """执行单个SQL文件"""
    if not os.path.exists(sql_file_path):
        print(f"✗ SQL文件不存在: {sql_file_path}")
        return False

    print(f"正在执行: {sql_file_path}")

    # 读取SQL文件内容
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    # 连接到指定数据库
    conn = pymysql.connect(unix_socket=DB_UNIX_SOCKET, user=DB_USER, password=DB_PASSWORD, database=db_name)
    cursor = conn.cursor()

    # 分割SQL语句（处理SOURCE命令）
    # 对于简单的CREATE TABLE语句，直接执行
    statements = []
    current_statement = []

    for line in sql_content.split('\n'):
        line = line.strip()

        # 跳过注释和空行
        if not line or line.startswith('--'):
            continue

        # 跳过USE和SOURCE语句
        if line.upper().startswith('USE ') or line.upper().startswith('SOURCE '):
            continue

        current_statement.append(line)

        # 检测语句结束
        if line.endswith(';'):
            stmt = ' '.join(current_statement)
            if stmt.strip():
                statements.append(stmt)
            current_statement = []

    # 执行所有语句
    success_count = 0
    for stmt in statements:
        try:
            if stmt.strip():
                cursor.execute(stmt)
                success_count += 1
        except Exception as e:
            print(f"  执行失败: {e}")
            print(f"  语句: {stmt[:100]}...")

    conn.commit()
    conn.close()

    print(f"✓ 成功执行 {success_count} 条语句")
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("开始创建数据库和表...")
    print("=" * 60)

    # 创建数据库
    create_databases()
    print()

    # 执行所有SQL文件
    success_count = 0
    fail_count = 0

    for db_name, sql_file in SQL_FILES:
        if execute_sql_file(db_name, sql_file):
            success_count += 1
        else:
            fail_count += 1
        print()

    print("=" * 60)
    print(f"建表完成！成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)

if __name__ == '__main__':
    main()
