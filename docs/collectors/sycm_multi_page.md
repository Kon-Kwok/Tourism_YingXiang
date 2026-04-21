# SYCM 多页面采集说明

除首页外，SYCM 还支持按页面元数据配置采集多个页面。

## 核心实现

- `src/tourism_automation/collectors/sycm/pages.py`：页面 ID、URL、端点定义。
- `src/tourism_automation/collectors/sycm/universal_client.py`：通用页面采集客户端。
- `src/tourism_automation/collectors/sycm/cli.py`：`list-pages`、`page-info`、`collect-page` 等命令。

## 当前页面

| 页面 ID | 页面说明 |
|---|---|
| `home` | 首页 |
| `flow_monitor` | 流量监控 |
| `trade_analysis` | 交易分析 |
| `goods_analysis` | 商品分析 |

## 常用命令

```bash
python3 -m tourism_automation.cli.main sycm list-pages

python3 -m tourism_automation.cli.main sycm page-info --page-id flow_monitor

python3 -m tourism_automation.cli.main sycm collect-page \
  --page-id flow_monitor \
  --date-range "2026-04-21|2026-04-21"

python3 -m tourism_automation.cli.main sycm collect-page \
  --page-id flow_monitor \
  --endpoint overview \
  --date-range "2026-04-21|2026-04-21,2026-04-20|2026-04-20"
```

## 日期与参数约定

- 单日范围：`YYYY-MM-DD|YYYY-MM-DD`
- 对比范围：`YYYY-MM-DD|YYYY-MM-DD,YYYY-MM-DD|YYYY-MM-DD`
- 某些页面需要额外参数；优先通过 `page-info` 查看页面定义。

## 流量监控页面说明

流量监控页的真实接口路径与最初猜测不同。当前参考实现使用页面配置中定义的接口，不应再手工假设 `/portal/flow/monitor/*.json` 一类旧路径。

## 扩展新页面

1. 在 `pages.py` 中增加页面元数据与端点。
2. 使用 `page-info` 检查配置。
3. 为新增页面补充 `tests/collectors/` 下的测试。

## 排查建议

- 先执行 `sycm healthcheck` 确认登录态可用。
- 页面采集失败时，先确认 URL 和页面 ID 是否匹配。
- 如果是新页面，优先检查 `pages.py` 中的 API 前缀、端点路径和必填参数。
