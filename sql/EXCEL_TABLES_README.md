# Excel数据表建表说明

## 文件组织结构

每个SQL文件都与对应的Excel文件放在同一个文件夹中：

```
sql/
├── 千牛/
│   ├── 店铺数据每日登记/
│   │   ├── 店铺数据每日登记.xlsx      ← 原始Excel文件
│   │   └── 店铺数据每日登记.sql      ← 对应建表SQL
│   └── 飞猪店铺日度关键数据/
│       ├── 飞猪店铺日度关键数据.xlsx
│       └── 飞猪店铺日度关键数据.sql
└── 飞猪/
    ├── 万相台/
    │   ├── 万相台.xlsx
    │   └── 万相台.sql
    ├── 客服数据汇总-周数据/
    │   ├── 客服数据汇总-周数据.xlsx
    │   └── 客服数据汇总-周数据.sql
    ├── 客服数据汇总-日数据/
    │   ├── 客服数据汇总-日数据.xlsx
    │   └── 客服数据汇总-日数据.sql
    ├── 客服绩效-工作量分析/
    │   ├── 客服绩效-工作量分析.xlsx
    │   └── 客服绩效-工作量分析.sql
    ├── 客服绩效-汇总/
    │   ├── 客服绩效-汇总.xlsx
    │   └── 客服绩效-汇总.sql
    ├── 引力魔方/
    │   ├── 引力魔方.xlsx
    │   └── 引力魔方.sql
    ├── 明星店铺/
    │   ├── 明星店铺.xlsx
    │   └── 明星店铺.sql
    └── 直通车/
        ├── 直通车.xlsx
        └── 直通车.sql
```

## 表清单

### 千牛数据表 (2张)

| 序号 | 表名 | 中文名称 | Excel文件路径 |
|------|------|----------|---------------|
| 1 | qianniu_shop_data_daily_registration | 千牛店铺数据每日登记 | sql/千牛/店铺数据每日登记/ |
| 2 | qianniu_fliggy_shop_daily_key_data | 千牛飞猪店铺日度关键数据 | sql/千牛/飞猪店铺日度关键数据/ |

### 飞猪数据表 (8张)

| 序号 | 表名 | 中文名称 | Excel文件路径 |
|------|------|----------|---------------|
| 3 | fliggy_wanxiangtai | 飞猪万相台 | sql/飞猪/万相台/ |
| 4 | fliggy_customer_service_data_weekly | 飞猪客服数据汇总周数据 | sql/飞猪/客服数据汇总-周数据/ |
| 5 | fliggy_customer_service_data_daily | 飞猪客服数据汇总日数据 | sql/飞猪/客服数据汇总-日数据/ |
| 6 | fliggy_customer_service_performance_workload_analysis | 飞猪客服绩效工作量分析 | sql/飞猪/客服绩效-工作量分析/ |
| 7 | fliggy_customer_service_performance_summary | 飞猪客服绩效汇总 | sql/飞猪/客服绩效-汇总/ |
| 8 | fliggy_gravity_rubiks_cube | 飞猪引力魔方 | sql/飞猪/引力魔方/ |
| 9 | fliggy_star_store | 飞猪明星店铺 | sql/飞猪/明星店铺/ |
| 10 | fliggy_tmall_express | 飞猪直通车 | sql/飞猪/直通车/ |

## 使用方法

### 方法1: 一键导入所有表（推荐）
```bash
mysql -u root -p xiangwang_fliggy_system < sql/import_all_excel_tables.sql
```

### 方法2: 单独导入某个表
```bash
# 导入单个表
mysql -u root -p xiangwang_fliggy_system < sql/飞猪/万相台/万相台.sql
```

### 方法3: 在MySQL客户端中执行
```sql
USE xiangwang_fliggy_system;
SOURCE sql/千牛/店铺数据每日登记/店铺数据每日登记.sql;
SOURCE sql/飞猪/万相台/万相台.sql;
-- 可以继续添加其他表...
```

## 数据类型说明

- **BIGINT**: 用于大数值，如PV、UV、展示量等
- **INT**: 用于普通整数，如人数、订单数等
- **DECIMAL(M,D)**: 用于精确的小数，如金额、比率等
  - M=总位数, D=小数位数
  - 例如: DECIMAL(14,2) 可存储最大999999999999.99
- **VARCHAR(N)**: 用于变长字符串
- **DATE**: 用于日期
- **TIMESTAMP**: 用于时间戳

## 表结构特点

1. **所有表都包含**:
   - `id`: 自增主键
   - `data_batch_id`: 关联批次ID（用于数据追溯）
   - `created_at`: 创建时间戳

2. **索引设计**:
   - 日期字段都有索引
   - 关键业务字段（如旺旺昵称）有索引
   - batch_id字段有索引

3. **字符集**:
   - 使用 `utf8mb4` 字符集，支持中文和特殊字符

## 数据导入

创建表后，可以使用项目中的 `import_excel_to_mysql.py` 脚本将Excel数据导入到对应的表中。

## 注意事项

1. **执行顺序**: 建议先执行 `sql/import_all_excel_tables.sql` 创建所有表，再导入数据
2. **数据库**: 确保数据库 `xiangwang_fliggy_system` 已创建
3. **字符编码**: 确保MySQL连接使用utf8mb4字符集
4. **数据清理**: Excel中的特殊值（如"-"）在导入时需要处理为NULL
