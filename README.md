# 飞猪/千牛电商数据自动化采集系统

基于本机 Chrome 登录态的电商数据采集仓库，统一通过 CLI 运行，覆盖 SYCM、飞猪商家工作台和 Topchitu KPI 场景。

## 快速开始

### 1. 启动统一 Chrome 调试会话

```bash
./bin/start-chrome-unified.sh
```

首次使用时，在该 Chrome 窗口中登录：

- `https://sycm.taobao.com`
- `https://fsc.fliggy.com`
- `https://kf.topchitu.com`

### 2. 运行采集命令

```bash
# SYCM 健康检查
python3 -m tourism_automation.cli.main sycm healthcheck

# SYCM 首页采集
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-21

# SYCM 流量看板采集
python3 -m tourism_automation.cli.main sycm flow-monitor --date 2026-04-20 --shop-name "SYCM"

# 飞猪首页采集
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-21

# 员工 KPI 采集
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-21 --method api

# 店铺 KPI 导出
python3 -m tourism_automation.cli.main shop-kpi-export

# 店铺 KPI 导出后直接转统一 JSON
python3 -m tourism_automation.cli.main shop-kpi-export --json

# 飞猪订单列表采集
python3 -m tourism_automation.cli.main fliggy-order-list list --page-num 1 --page-size 10

# 飞猪订单列表最常用命令：采集后直接做入库前汇总处理
python3 -m tourism_automation.cli.main fliggy-order-list list --page-num 1 --page-size 20 --deal-start "2026-04-20 00:00:00" --deal-end "2026-04-20 23:59:39" | python3 bin/prepare_fliggy_order_list_for_storage.py
```

## 核心能力

- `SYCM`：首页指标和多页面数据采集，主要使用 HTTP + Cookie。
- `fliggy-home`：飞猪商家工作台首页核心模块采集。
- `fliggy-kpi employee`：员工 KPI 采集，使用 CDP + fetch。
- `shop-kpi-export`：店铺 KPI 页面导出自动化，支持直接输出统一 `summary + rows` JSON。
- `fliggy-order-list list`：飞猪订单列表采集，使用纯 HTTP + Cookie。

## SYCM 流量看板说明

`python3 -m tourism_automation.cli.main sycm flow-monitor --date YYYY-MM-DD --shop-name "SYCM"` 当前输出统一 JSON 结构：

- `summary`
- `rows`

日期口径：

- 当 `--date` 是当天时，`访客数`、`浏览量`、`关注店铺人数` 走 SYCM 页面实时 `today` 接口。
- 当 `--date` 不是当天时，这 3 个字段走 SYCM 历史 `compareRange` 接口，返回指定日期的日数据。
- `广告流量`、`平台流量` 走店铺来源汇总接口；如果源接口当天未返回数据，这两个字段会是 `null`。

示例输出：

```json
{
  "summary": {
    "source": "chrome_cookie_http",
    "shop_name": "SYCM",
    "page_code": "flow_monitor",
    "page_name": "流量监控概览",
    "biz_date": "2026-04-20",
    "device": "2",
    "row_count": 1
  },
  "rows": [
    {
      "访客数": 13653,
      "浏览量": 31835,
      "关注店铺人数": 26,
      "广告流量": 10510,de 
      "平台流量": 4030
    }
  ]
}
```

## 项目结构

```text
Tourism_YingXiang/
├── src/tourism_automation/
│   ├── cli/              # CLI 入口
│   ├── collectors/       # 采集器实现
│   └── shared/           # Chrome / HTTP / CDP / 结果封装
├── tests/                # unittest 测试
├── docs/                 # 使用与实现文档
├── sql/                  # SQL 资产
└── bin/                  # 启动与辅助脚本
```

## 测试

```bash
python3 -m unittest discover tests
python3 -m unittest tests.cli.test_main
python3 -m unittest tests.collectors.test_sycm
python3 -m unittest tests.collectors.test_fliggy_home
python3 -m unittest tests.test_refactored_clients
```

## 文档入口

- `docs/README.md`：文档总入口与阅读顺序
- `docs/collectors/unified_chrome_guide.md`：统一 Chrome 使用规范
- `docs/architecture/project-structure.md`：项目结构说明
- `CLAUDE.md`：仓库开发指引
- `AGENTS.md`：贡献者约定

## 运维注意事项

- 所有浏览器相关采集都依赖 `9222` 端口的统一 Chrome 会话。
- 不要关闭该 Chrome 窗口，也不要删除 `~/.config/google-chrome-debug`。
- 登录失效时，只在统一 Chrome 中重新登录，不要新建独立浏览器配置。
- 采集失败时，先检查 `curl -s http://localhost:9222/json/version` 是否可访问。
- `fliggy-order-list` 运行时不依赖 CDP，只依赖共享 Chrome cookie 登录态。

## 系统要求

- Python 3.10+
- MySQL 8.0+
- Chrome/Chromium
- 常用依赖：`requests`、`pymysql`、`websockets`、`secretstorage`、`cryptography`
