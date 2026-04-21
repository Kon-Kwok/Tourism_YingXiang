# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

飞猪/千牛电商数据自动化采集系统，通过复用本机 Chrome 登录态自动采集网页数据并存储到 MySQL 数据库。

**核心特性**:
- 复用本机 Chrome 登录态
- 模块化容错设计（单模块失败不影响整体采集）
- 统一CLI命令入口
- 按场景使用 HTTP + Cookie 或 CDP + fetch

## 系统配置

### 密码信息
- **sudo密码**: `1`
- **MySQL连接方式**: `sudo mysql` (使用socket认证，无需密码)

### 数据库连接
```bash
# 连接到MySQL
sudo mysql

# 连接到指定数据库
sudo mysql qianniu    # 千牛数据库
sudo mysql feizhu     # 飞猪数据库
```

## 核心架构

### 代码组织

主代码位于 `src/tourism_automation/`:

```
src/tourism_automation/
├── cli/                    # 统一命令行入口
├── collectors/             # 数据采集器
│   ├── sycm/              # 生意参谋采集器
│   ├── fliggy_home/       # 飞猪商家工作台首页采集器
│   └── fliggy_kpi/        # 飞猪客服与店铺KPI采集器
└── shared/                # 共享组件
    ├── chrome/            # Chrome登录态读取
    ├── http/              # HTTP客户端
    ├── cdp_client.py      # 统一CDP能力
    └── result/            # 模块化结果汇总
```

### 关键设计模式

1. **CLI统一入口**: 所有采集器通过 `python3 -m tourism_automation.cli.main` 调用
2. **Collector模式**: 每个采集器包含 `collector.py`, `client.py`, `normalize.py`, `storage.py`
3. **Chrome会话复用**: 统一复用 `9222` 调试 Chrome 登录态
4. **双轨采集**: 常规页面走 HTTP + Cookie，KPI 等场景走 CDP + fetch

## 常用命令

### Chrome调试窗口管理

```bash
# 启动Chrome调试窗口（首次或重启）
./bin/start-chrome-unified.sh

# 检查Chrome调试窗口状态
ps aux | grep "remote-debugging-port=9222"

# 检查Chrome调试端口
curl -s http://localhost:9222/json/version

# 查看Chrome标签页
curl -s http://localhost:9222/json | jq '.[] | {id, url, title}'

# 查看Chrome日志
tail -f /tmp/chrome_debug.log

# ⚠️ 不要使用这些命令（会关闭Chrome）：
# pkill chrome  # 禁止！
# pkill -9 chrome  # 禁止！
```

### 数据采集

```bash
# 生意参谋 - 健康检查
python3 -m tourism_automation.cli.main sycm healthcheck

# 生意参谋 - 采集首页数据
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"

# 生意参谋 - 列出所有可用页面
python3 -m tourism_automation.cli.main sycm list-pages

# 生意参谋 - 采集指定页面数据（支持多页面采集）
python3 -m tourism_automation.cli.main sycm collect-page --page-id flow_monitor --date-range "2026-04-19|2026-04-19"

# 飞猪商家工作台 - 采集首页数据
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"

# 飞猪客服KPI - 采集员工KPI数据（需要Chrome调试窗口运行）
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api --shop-name "皇家加勒比国际游轮旗舰店"
```

### 测试

```bash
# 运行所有测试
python3 -m unittest discover tests

# 运行特定测试
python3 -m unittest tests.cli.test_main
python3 -m unittest tests.collectors.test_sycm
python3 -m unittest tests.collectors.test_fliggy_home
python3 -m unittest tests.test_refactored_clients
```

### 数据库操作

```bash
# 查看采集批次记录
sudo mysql -e "SELECT * FROM sycm_collection_batches ORDER BY started_at DESC LIMIT 10;"

# 查看原始API响应
sudo mysql -e "SELECT * FROM sycm_api_raw_payloads WHERE batch_id = <batch_id>;"

# 查看采集的指标数据
sudo mysql -e "SELECT * FROM sycm_homepage_metrics WHERE biz_date = '2026-04-19';"
```

## 数据库结构

### 自动采集数据表（SYCM）

- `sycm_collection_batches`: 采集批次记录
- `sycm_api_raw_payloads`: 原始API响应
- `sycm_homepage_metrics`: 首页核心指标
- `sycm_homepage_trends`: 首页趋势序列

### 手动导入数据表

#### 千牛数据库 (qianniu) - 2张表
- `qianniu_shop_data_daily_registration`: 店铺数据每日登记
- `qianniu_fliggy_shop_daily_key_data`: 飞猪店铺日度关键数据

#### 飞猪数据库 (feizhu) - 8张表
- `fliggy_wanxiangtai`: 万相台
- `fliggy_customer_service_data_daily`: 客服数据汇总-日数据
- `fliggy_customer_service_data_weekly`: 客服数据汇总-周数据
- `fliggy_customer_service_performance_workload_analysis`: 客服绩效-工作量分析
- `fliggy_customer_service_performance_summary`: 客服绩效-汇总
- `fliggy_gravity_rubiks_cube`: 引力魔方
- `fliggy_star_store`: 明星店铺
- `fliggy_tmall_express`: 直通车

详细表结构参见 `sql/` 目录下的SQL文件。

## 开发注意事项

### 添加新采集器

1. 在 `src/tourism_automation/collectors/` 创建新目录
2. 实现标准文件结构:
   - `collector.py`: 采集器主逻辑
   - `client.py`: API客户端
   - `normalize.py`: 数据规范化
   - `storage.py`: 数据库存储
   - `cli.py`: CLI命令注册
3. 在 `src/tourism_automation/cli/main.py` 中注册新的subparser

### Chrome会话管理

**⚠️ 重要规则：禁止关闭Chrome调试窗口！**

**Chrome调试窗口配置**：
- 调试端口：`9222`
- 配置目录：`~/.config/google-chrome-debug`
- Cookie路径：`~/.config/google-chrome-debug/Default/Cookies`
- 启动脚本：`bin/start-chrome-unified.sh`

**为什么不能关闭**：
- Chrome调试窗口用于所有数据采集（SYCM、飞猪、KPI）
- 关闭后需要重新登录所有网站（淘宝、Topchitu等）
- 可能需要再次输入验证码
- 破坏已建立的登录会话

**正确使用方式**：
1. Chrome调试窗口应该**一直运行**，不要关闭
2. 可以最小化窗口，但不关闭
3. 检查状态：`ps aux | grep "remote-debugging-port=9222"`
4. 如果意外停止，运行：`./bin/start-chrome-unified.sh`

**Chrome识别特征**：
```bash
# 调试Chrome（禁止关闭）
chrome --remote-debugging-port=9222 --user-data-dir=/home/kk/.config/google-chrome-debug

# 正常Chrome（可以关闭）
chrome --user-data-dir=/home/kk/.config/google-chrome
```

**禁止的操作**：
- ❌ 不要运行 `pkill chrome`（会关闭所有Chrome）
- ❌ 不要关闭Chrome调试窗口
- ❌ 不要删除 `~/.config/google-chrome-debug` 目录
- ❌ 不要在Chrome中点击"退出登录"

**Chrome会话管理技术细节**：
- 使用 `secretstorage` 读取Chrome加密密钥
- CDP脚本使用环境变量 `CDP_PORT_FILE` 定位调试端口
- 仅读取Cookie，不使用CDP进行页面操作（除非必要）

### 数据库Schema

- 所有自动采集表都需要 `batch_id` 字段用于追溯
- 使用 utf8mb4 字符集支持中文
- 日期字段使用 DATE 类型
- 金额字段使用 DECIMAL 类型保证精度

### 依赖管理

项目主要依赖:
- `requests`: HTTP客户端
- `pymysql`: MySQL连接
- `secretstorage`: Chrome密钥读取
- `cryptography`: Cookie解密

### 文档目录

- `docs/README.md`: 文档总入口
- `docs/architecture/`: 架构文档
- `docs/collectors/`: 采集器文档
- `docs/implementation/`: 实现背景与设计说明
- `sql/`: 建表SQL和Excel数据
