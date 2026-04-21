# 店铺 KPI 导出使用指南

店铺 KPI 通过页面导出流程获取数据，不依赖稳定 API。

## 前置条件

1. 先完成 [unified_chrome_guide.md](unified_chrome_guide.md) 中的统一 Chrome 准备。
2. 在统一 Chrome 中打开：

```text
https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL
```

## 使用命令

```bash
python3 -m tourism_automation.cli.main shop-kpi-export

python3 -m tourism_automation.cli.main shop-kpi-export \
  --output /tmp/shop-kpi.xlsx

python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 人均日接入 \
  --date-mode day \
  --date 2026-04-20

python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 人均日接入 \
  --date-mode day \
  --date 2026-04-20 \
  --json

python3 -m tourism_automation.cli.main shop-kpi-export-batch \
  --date-mode day \
  --date 2026-04-20
```

支持的报表：
- `人均日接入`
- `每周店铺个人数据`
- `客服数据23年新`

批量命令 `shop-kpi-export-batch` 会按以上顺序依次导出这 3 张表。

输出说明：
- 普通模式返回的 `output_file` 是真实下载文件路径，例如 `/home/kk/下载/...xlsx`
- 加 `--json` 后，命令会等待 Excel 下载完成，再直接输出统一的 `summary + rows` JSON

日期参数说明：
- `--date-mode day` 时可传 `--date YYYY-MM-DD`
- `--date-mode day` 不传 `--date` 时默认前一天
- `week` / `month` 仍按页面当前逻辑执行

## 自动化流程

1. 查找店铺 KPI 页面。
2. 按报表名称切换目标报表。
3. 按参数切换日/周/月模式；`day` 时可设置日期。
4. 点击查询按钮。
5. 点击导出按钮。
6. 等待密码弹窗出现。
7. 输入密码并确认。
8. 等待真实下载文件落地。
9. `--json` 时把 Excel 转成统一 JSON 并输出到 stdout。

## 常见问题

### 无法连接 Chrome 调试端口

先确认统一 Chrome 已启动：`./bin/start-chrome-unified.sh`。

### 未找到店铺 KPI 页面

说明目标页面没有在统一 Chrome 中打开。先手动打开页面再执行命令。

### 导出按钮或密码框失效

通常是页面结构发生变化，需要更新 [exporter.py](/home/kk/Tourism_YingXiang/src/tourism_automation/collectors/fliggy_kpi/shop_kpi/exporter.py) 中的选择器。

## 代码位置

- `src/tourism_automation/collectors/fliggy_kpi/shop_kpi/exporter.py`
- `src/tourism_automation/collectors/fliggy_kpi/shop_kpi/cli.py`
