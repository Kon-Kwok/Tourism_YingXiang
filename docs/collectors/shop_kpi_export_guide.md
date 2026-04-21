# 店铺 KPI 导出使用指南

店铺 KPI 通过页面导出流程获取数据，不依赖稳定 API。

## 前置条件

1. 先完成 [unified_chrome_guide.md](unified_chrome_guide.md) 中的统一 Chrome 准备。
2. 在统一 Chrome 中打开：

```text
https://kf.topchitu.com/web/custom-kpi/shop-kpi?id=941
```

## 使用命令

```bash
python3 -m tourism_automation.cli.main shop-kpi-export

python3 -m tourism_automation.cli.main shop-kpi-export \
  --output /tmp/shop-kpi.xlsx

python3 -m tourism_automation.cli.main shop-kpi-export \
  --password 5678
```

## 自动化流程

1. 查找店铺 KPI 页面。
2. 点击导出按钮。
3. 等待密码弹窗出现。
4. 输入密码并确认。
5. 等待浏览器开始下载。

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
