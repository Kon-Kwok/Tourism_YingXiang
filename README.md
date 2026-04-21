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

# 飞猪首页采集
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-21

# 员工 KPI 采集
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-21 --method api

# 店铺 KPI 导出
python3 -m tourism_automation.cli.main shop-kpi-export
```

## 核心能力

- `SYCM`：首页指标和多页面数据采集，主要使用 HTTP + Cookie。
- `fliggy-home`：飞猪商家工作台首页核心模块采集。
- `fliggy-kpi employee`：员工 KPI 采集，使用 CDP + fetch。
- `shop-kpi-export`：店铺 KPI 页面导出自动化。

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

## 系统要求

- Python 3.10+
- MySQL 8.0+
- Chrome/Chromium
- 常用依赖：`requests`、`pymysql`、`websockets`、`secretstorage`、`cryptography`
