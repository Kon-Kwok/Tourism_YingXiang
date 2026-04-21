# 飞猪客服 KPI 采集使用说明

员工 KPI 采集依赖统一 Chrome 调试会话和已打开的 Topchitu 页面。

## 前置条件

1. 先阅读并完成 [unified_chrome_guide.md](unified_chrome_guide.md)。
2. 在统一 Chrome 中打开：

```text
https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL
```

## 采集命令

```bash
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-21 --method api

python3 -m tourism_automation.cli.main fliggy-kpi employee \
  --date 2026-04-21 \
  --method api \
  --shop-name "皇家加勒比国际游轮旗舰店"
```

## 主要参数

- `--date`：业务日期，格式为 `YYYY-MM-DD`。
- `--method`：默认 `api`，推荐保持不变。
- `--shop-name`：输出中的店铺标识。
- `--kpi-id`：KPI 模板 ID，默认 `1721`。
- `--wwt`：时间范围类型，默认 `ALL`。

## 输出内容

返回 JSON，包含：

- `summary`：采集来源、日期、店铺、员工数量。
- `metrics`：员工级 KPI 明细。
- 指标字段：`service_count`、`consult_count`、`avg_first_reply_cost`、`avg_total_reply_cost` 等 13 项。

## 排查思路

### 未找到目标页面

说明员工 KPI 页未在统一 Chrome 中打开。先打开页面，再执行命令。

### 返回登录页或空结果

优先检查 Topchitu 登录态，再确认所选日期是否确实有数据。

### 端口连不上

先运行 `./bin/start-chrome-unified.sh`，再检查 `curl -s http://localhost:9222/json/version`。

## 代码位置

- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/`
- `src/tourism_automation/shared/cdp_client.py`
- `src/tourism_automation/cli/main.py`
