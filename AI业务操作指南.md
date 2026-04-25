# AI业务操作指南

> 三个核心数据采集流程

**使用说明**：
- `YYYY-MM-DD` 为日期示例格式，请替换为实际日期
- `$HOST`, `$PORT`, `$USER`, `$PASS` 需要替换为实际数据库连接信息

---

## ⚠️ 关键注意事项

**赤兔KPI报表必须使用 `--date-mode day`，不能用 `--date-mode week`！**

---

## 业务1：赤兔KPI三个报表

| 报表ID | 报表名 | 目标表 |
|--------|--------|--------|
| 1721 | 人均日接入 | `fliggy_customer_service_data_daily` |
| 1996 | 每周店铺个人数据 | `fliggy_customer_service_performance_summary` |
| 2496 | 客服数据23年新 | `fliggy_customer_service_performance_workload_analysis` |

**操作流程：**

```bash
# 设置变量（日期仅为示例）
DATE=YYYY-MM-DD
MYSQL="mysql -h $HOST -P $PORT -u $USER -p$PASS"

# 导出Excel → JSON → SQL → Database
for report in "人均日接入" "每周店铺个人数据" "客服数据23年新"; do
  python3 -m tourism_automation.cli.main shop-kpi-export \
    --report-name "$report" --date-mode day --date $DATE
  sleep 10

  EXCEL=$(ls -t ~/Downloads/自定义报表*${DATE}至${DATE}*.xlsx 2>/dev/null | head -1)

  case $report in
    "人均日接入")
      python3 bin/prepare_shop_kpi_excel_to_json.py "$EXCEL" | \
        python3 bin/prepare_fliggy_customer_service_data_daily_sql.py | \
        $MYSQL feizhu
      ;;
    "每周店铺个人数据")
      python3 bin/prepare_shop_kpi_excel_to_json.py "$EXCEL" | \
        python3 bin/prepare_fliggy_customer_service_summary_sql.py | \
        $MYSQL feizhu
      ;;
    "客服数据23年新")
      python3 bin/prepare_shop_kpi_excel_to_json.py "$EXCEL" | \
        python3 bin/prepare_fliggy_customer_service_workload_sql.py | \
        $MYSQL feizhu
      ;;
  esac
done
```

---

## 业务2：飞猪订单列表

**目标表**:
- `feizhu.fliggy_order_list` - 订单明细
- `qianniu.qianniu_fliggy_shop_daily_key_data` - `total_bookings`、`total_pax`、`gmv`

```bash
# 设置变量（日期仅为示例）
DATE=YYYY-MM-DD


python3 -m tourism_automation.cli.main fliggy-order-list list \
  --page-num 1 --page-size 100 --all-pages \
  --deal-start "${DATE} 00:00:00" \
  --deal-end "${DATE} 23:59:59" > /tmp/orders_raw.json

python3 bin/prepare_fliggy_order_list_for_storage.py < /tmp/orders_raw.json > /tmp/orders_prep.json

python3 bin/prepare_fliggy_order_list_sql.py < /tmp/orders_prep.json | \
  $MYSQL feizhu

python3 bin/prepare_qianniu_shop_daily_key_sql.py < /tmp/orders_prep.json | \
  $MYSQL qianniu
```

---

## 业务3：SYCM流量看板

**目标表**: `qianniu.qianniu_fliggy_shop_daily_key_data`

```bash
# 设置变量（日期仅为示例）
DATE=YYYY-MM-DD
SHOP="皇家加勒比国际游轮旗舰店"

python3 -m tourism_automation.cli.main sycm flow-monitor \
  --date $DATE --shop-name "$SHOP" | \
python3 bin/prepare_sycm_flow_sql.py | \
$MYSQL qianniu
```

---

## 一键采集日报数据

```bash
DATE=$(date -d "yesterday" +%Y-%m-%d)
MYSQL="mysql -h $HOST -P $PORT -u $USER -p$PASS"

# 赤兔KPI三个报表
for report in "人均日接入" "每周店铺个人数据" "客服数据23年新"; do
  python3 -m tourism_automation.cli.main shop-kpi-export --report-name "$report" --date-mode day --date $DATE
  sleep 10
  EXCEL=$(ls -t ~/Downloads/自定义报表*${DATE}至${DATE}*.xlsx 2>/dev/null | head -1)
  # ... (对应的转换和入库命令)
done

# SYCM流量
python3 -m tourism_automation.cli.main sycm flow-monitor --date $DATE --shop-name "皇家加勒比国际游轮旗舰店" | \
  python3 bin/prepare_sycm_flow_sql.py | $MYSQL qianniu

# 飞猪订单
python3 -m tourism_automation.cli.main fliggy-order-list list \
  --page-num 1 --page-size 100 --all-pages \
  --deal-start "${DATE} 00:00:00" --deal-end "${DATE} 23:59:59" > /tmp/orders_raw.json

python3 bin/prepare_fliggy_order_list_for_storage.py < /tmp/orders_raw.json > /tmp/orders_prep.json
python3 bin/prepare_fliggy_order_list_sql.py < /tmp/orders_prep.json | $MYSQL feizhu
python3 bin/prepare_qianniu_shop_daily_key_sql.py < /tmp/orders_prep.json | $MYSQL qianniu
```
