# Project Structure

主代码统一放在 `src/tourism_automation/`，根目录以脚本、文档和测试为主。

## 目录约定

- `src/tourism_automation/cli/`：统一 CLI 入口与子命令注册。
- `src/tourism_automation/collectors/`：具体采集器实现。
- `src/tourism_automation/shared/`：Chrome 会话、HTTP 请求、结果封装等共享能力。
- `tests/`：按 CLI 和采集器拆分的 `unittest` 测试。
- `bin/`：Chrome 启动、调试和辅助脚本。
- `sql/`：数据库脚本与数据导入资产。

## 采集器组织

- `collectors/sycm/`：SYCM 首页与多页面采集。
- `collectors/fliggy_home/`：飞猪商家工作台首页采集。
- `collectors/fliggy_kpi/employee_kpi/`：员工 KPI API 采集。
- `collectors/fliggy_kpi/shop_kpi/`：店铺 KPI 导出自动化。

新增采集器时，优先沿用 `collector.py`、`client.py`、`normalize.py`、`storage.py`、`cli.py` 的分层方式。

## 统一运行入口

```bash
python3 -m tourism_automation.cli.main sycm healthcheck
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-21
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-21
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-21 --method api
```

仓库根目录的 `tourism_automation/` 是运行时 shim，用来让 `python3 -m tourism_automation...` 能直接定位 `src/` 下的包。
