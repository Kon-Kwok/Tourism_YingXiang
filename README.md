
# 象往科技飞猪数据系统 - 交付说明 v2.0

按师兄要求调整后的版本：
- ✅ SQL文件拆分（每张表一个SQL）
- ✅ 分文件夹组织
- ✅ JSON配置去冗余（登录抽离）
- ✅ 支持Cookie登录（避免验证码）

---

## 目录结构

```
象往科技飞猪数据系统交付/
├── README.md                          # 本文档
├── spider_executor_v2.py              # 执行层（v2.0，推荐）
├── init_biz_database_v2.py            # 数据库初始化（v2.0，推荐）
│
├── config/                            # 配置文件夹
│   ├── spider_config.json             # 爬虫配置（v2.0，去冗余）
│   └── database.json                  # 数据库连接配置
│
├── sql/                               # SQL文件夹
│   ├── import_all.sql                 # 一键导入所有表
│   │
│   ├── 01_init/                       # 初始化
│   │   └── 01_create_database.sql     # 创建数据库
│   │
│   ├── 02_biz_tables/                 # 业务表（7张，每张一个SQL）
│   │   ├── biz_customer_service_daily.sql
│   │   ├── biz_customer_service_weekly.sql
│   │   ├── biz_cs_workload_log.sql
│   │   ├── biz_agent_performance_daily.sql
│   │   ├── biz_agent_sales_daily.sql
│   │   ├── biz_fliggy_store_daily.sql
│   │   └── biz_fliggy_order_daily.sql
│   │
│   └── 03_data_batch/                 # 批次表
│       └── spider_data_batch.sql
│
├── docs/                              # 文档文件夹
│   └── (旧文档放这里)
│
└── (旧版本文件，仅供参考)
    ├── spider_executor.py
    ├── init_biz_database.py
    ├── config.json
    ├── spider_config.json
    ├── 交付说明.md
    └── 系统架构图.txt
```

---

## 主要改进（按师兄要求）

### 1. SQL文件拆分
- **之前**：所有表在一个Python文件里
- **现在**：每张表一个独立的SQL文件
- **位置**：`sql/02_biz_tables/`

### 2. 登录去冗余
- **之前**：每个页面都配置重复的登录步骤
- **现在**：登录配置抽离到 `login` 节点
- **支持**：优先Cookie登录，避免验证码

### 3. 文件夹组织
- `config/` - 所有配置文件
- `sql/` - 所有SQL文件（分子文件夹）
- `docs/` - 文档

---

## 快速开始

### 1. 初始化数据库（推荐用v2版本）

```bash
python init_biz_database_v2.py
```

或者手动导入SQL：
```bash
mysql -u root -p &lt; sql/import_all.sql
```

### 2. 配置MySQL连接

编辑 `config/database.json`：
```json
{
  "mysql": {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "Ffh050618",
    "charset": "utf8mb4"
  }
}
```

### 3. 配置爬虫

编辑 `config/spider_config.json`：
- 调整 `selector_value` 为实际页面元素
- 可选：保存cookie到 `cookies.json` 避免验证码

### 4. 运行爬虫

```bash
python spider_executor_v2.py
```

---

## 配置说明

### spider_config.json v2.0 结构

```json
{
  "login": {
    "type": "cookie_or_password",
    "base_url": "https://fsc.fliggy.com",
    "username": "...",
    "password": "...",
    "cookie_file": "cookies.json",
    "note": "优先用cookie登录，避免验证码"
  },

  "pages": [
    {
      "page_id": "chitu_customer_service",
      "requires_login": true,
      "steps": [...],        // 不再包含重复的登录步骤
      "field_mappings": [...]
    }
  ]
}
```

---

## 业务表清单（8张）

| 文件夹 | 表名 | 说明 |
|--------|------|------|
| 03_data_batch | spider_data_batch | 数据采集批次表 |
| 02_biz_tables | biz_customer_service_daily | 客服数据日报 |
| 02_biz_tables | biz_customer_service_weekly | 客服数据周报 |
| 02_biz_tables | biz_cs_workload_log | 客服工作量分析 |
| 02_biz_tables | biz_agent_performance_daily | Agent绩效日报 |
| 02_biz_tables | biz_agent_sales_daily | Agent销售日报 |
| 02_biz_tables | biz_fliggy_store_daily | 飞猪店铺每日数据 |
| 02_biz_tables | biz_fliggy_order_daily | 飞猪订单每日数据 |

---

## 下一步工作

1. **调整选择器** - 修改 `config/spider_config.json` 中的 `selector_value`
2. **集成浏览器** - 在 `spider_executor_v2.py` 中集成 Selenium/Playwright
3. **测试Cookie登录** - 保存cookie到 `cookies.json` 避免验证码

---

**版本**：v2.0  
**更新时间**：2026-04-16  
**MySQL版本要求**：5.7+ 或 8.0+

