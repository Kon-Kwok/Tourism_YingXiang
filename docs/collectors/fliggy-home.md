# Fliggy Home Collector

用途：采集 `https://fsc.fliggy.com/#/new/home` 首页的 5 个核心模块。

运行：

```bash
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"
```

当前覆盖模块：

- `service_todos`
- `business_center`
- `product_operation_center`
- `merchant_growth`
- `rule_center`

特点：

- 复用本机 Chrome 登录态
- 不依赖 CDP
- 模块级容错，单模块失败不会拖垮整次采集

实现位置：

- `src/tourism_automation/collectors/fliggy_home/collector.py`
- `src/tourism_automation/collectors/fliggy_home/client.py`
- `src/tourism_automation/collectors/fliggy_home/normalize.py`
