# SYCM Collector

用途：采集 `https://sycm.taobao.com/portal/home.htm` 首页数据。

运行：

```bash
python3 -m tourism_automation.cli.main sycm healthcheck
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-19 --shop-name "皇家加勒比国际游轮旗舰店"
```

特点：

- 复用本机 Chrome 登录态
- 不依赖 CDP
- 输出首页指标、趋势和表格数据

实现位置：

- `src/tourism_automation/collectors/sycm/collector.py`
- `src/tourism_automation/collectors/sycm/client.py`
- `src/tourism_automation/collectors/sycm/normalize.py`
