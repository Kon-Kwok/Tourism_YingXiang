---
name: daily-data-collection
description: 一键采集飞猪业务的三大核心日报数据（赤兔KPI客服报表、飞猪订单列表、SYCM流量看板）。当用户需要"日报数据"、"昨日数据采集"、"一键获取所有数据"或提及"KPI"、"订单"、"流量"等关键词时使用此技能。这是每日数据采集的标准流程。
---

# 每日数据采集技能

## 概述

此技能是飞猪业务的**每日数据采集标准流程**，一键完成三大核心业务的数据采集、转换和入库：
1. 赤兔KPI客服报表（3个报表）
2. 飞猪订单列表
3. SYCM流量看板

## 适用场景

✅ **推荐使用**：
- 每日例行数据采集
- 批量获取昨日数据
- 一键完成全量数据更新
- 定时任务自动执行

❌ **不推荐使用**：
- 只需要单个业务数据（使用对应的子技能）
- 需要单独调试某个业务
- 历史数据批量补录

## 快速开始

### 日期范围硬性要求

日报采集必须把所有业务日期范围固定为同一天：开始日期 = 结束日期 = 用户指定的 `YYYY-MM-DD`。

赤兔KPI三个报表全部必须使用 `--date-mode day --date YYYY-MM-DD`，包括名字带“每周”的 `每周店铺个人数据` 和历史上常被误设为周范围的 `客服数据23年新`。不要因为报表名包含“每周”而使用 `week`，也不要省略 `--date` 让程序使用默认日期。下载到的 xlsx 文件名必须包含 `YYYY-MM-DD至YYYY-MM-DD`，否则视为错误数据，重新导出。

### 一键采集昨日数据

```bash
./scripts/all.sh YYYY-MM-DD
```

### 示例

```bash
# 采集昨日数据
./scripts/all.sh $(date -d "yesterday" +%Y-%m-%d)

# 采集指定日期
./scripts/all.sh 2026-04-24
```

### KPI导出等待配置

赤兔KPI报表导出后不再固定等待固定秒数，检测到对应报表文件下载完成后会立刻继续。可设置超时时间：

```bash
export KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS=60
```
执行示例：

```bash
KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS=90 ./scripts/all.sh 2026-04-24
```

## 三大核心业务

### 1. 赤兔KPI客服报表（3个）

**目标表**：
- `fliggy_customer_service_data_daily` - 人均日接入
- `fliggy_customer_service_performance_summary` - 每周店铺个人数据
- `fliggy_customer_service_performance_workload_analysis` - 客服数据23年新

**数据量**：每个报表约12条记录
**耗时**：约3分钟

### 2. 飞猪订单列表

**目标表**：`fliggy_order_list`

**数据量**：每天50-100单
**耗时**：约30秒

### 3. SYCM流量看板

**目标表**：
- `qianniu.qianniu_fliggy_shop_daily_key_data` - 访客、浏览、广告流量、平台流量
- `qianniu.qianniu_shop_data_daily_registration` - 关注店铺人数

**采集指标**：
- total_uv - 总访客数
- total_pv - 总浏览量
- 关注店铺人数 - 来自 flow-monitor 原始 JSON 的 `关注店铺人数`
- 流量来源广告_uv - 广告访客
- 流量来源平台_uv - 平台访客

**耗时**：约20秒

## 执行流程

```
开始
  ↓
1. 赤兔KPI报表采集（3个报表）
   - 导出Excel → 下载完成后立即继续（最多等待 `KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS`）→ 转换JSON → 生成SQL → 入库
   ↓
2. 飞猪订单列表采集
   - HTTP采集 → 预处理 → 入库
   ↓
3. SYCM流量看板采集
   - HTTP采集 → 转换SQL → 入库飞猪店铺日度关键数据和店铺数据每日登记
   ↓
完成（总耗时约4分钟）
```

## 前置条件

### Chrome调试窗口

```bash
# 检查Chrome是否运行
ps aux | grep "remote-debugging-port=9222"

# 如果未运行，启动Chrome
./bin/start-chrome-unified.sh
```

### 网站登录状态

确保已在Chrome中登录：
- ✅ sycm.taobao.com（生意参谋）
- ✅ fsc.fliggy.com（飞猪商家工作台）
- ✅ kf.topchitu.com（赤兔KPI）

### 数据库连接

```bash
# 设置环境变量
export HOST="your_mysql_host"
export PORT="3306"
export USER="your_mysql_user"
export PASS="your_mysql_password"

# 或设置MySQL命令
export MYSQL_CMD="mysql -h $HOST -P $PORT -u $USER -p$PASS"

# 可选：KPI报表下载等待超时（秒）
export KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS=60
```

## 使用方式

### 方式1：一键执行（推荐）

```bash
./scripts/all.sh 2026-04-24
```

### 方式2：单独执行某个业务

```bash
# 只采集KPI报表
./scripts/kpi_reports.sh 2026-04-24

# 只采集订单列表
./scripts/fliggy_orders.sh 2026-04-24

# 只采集流量数据
./scripts/sycm_flow.sh 2026-04-24
```

### 方式3：定时任务

```bash
# 添加到crontab（每天凌晨1点执行）
crontab -e

# 添加以下行
0 1 * * * cd /home/kk/Tourism_YingXiang && ./.claude/skills/daily-data-collection/scripts/all.sh $(date -d "yesterday" +\%Y-\%m-\%d) >> /var/log/daily_collection.log 2>&1
```

## 输出示例

```
========================================
   每日数据采集
   日期：2026-04-24
========================================

[18:30:00] 业务1：赤兔KPI三个报表
========================================
赤兔KPI三个报表采集
日期：2026-04-24
========================================

▶ 开始处理：人均日接入
  [1/3] 导出Excel...
  [2/3] 等待下载...
  ✓ 找到文件：自定义报表_人均日接入_2026-04-24至2026-04-24.xlsx
  [3/3] 转换并入库...
  ✓ 人均日接入 处理完成

▶ 开始处理：每周店铺个人数据
  [1/3] 导出Excel...
  # 必须使用 --date-mode day --date 2026-04-24
  ✓ 找到文件：自定义报表_每周店铺个人数据_2026-04-24至2026-04-24.xlsx
  [3/3] 转换并入库...
  ✓ 每周店铺个人数据 处理完成

▶ 开始处理：客服数据23年新
  [1/3] 导出Excel...
  # 必须使用 --date-mode day --date 2026-04-24
  ✓ 找到文件：自定义报表_客服数据23年新_2026-04-24至2026-04-24.xlsx
  [3/3] 转换并入库...
  ✓ 客服数据23年新 处理完成

========================================
✓ 所有报表处理完成
========================================

[18:33:00] 业务2：飞猪订单列表
========================================
飞猪订单列表采集
日期：2026-04-24
========================================

▶ [1/3] 采集订单数据...
  ✓ 采集到 85 条订单
▶ [2/3] 数据预处理...
  ✓ 预处理完成
▶ [3/3] 数据入库...
  ✓ 入库完成

========================================
✓ 飞猪订单采集完成
订单数量：85
========================================

[18:33:30] 业务3：SYCM流量看板
========================================
SYCM流量看板采集
日期：2026-04-24
店铺：皇家加勒比国际游轮旗舰店
========================================

▶ [1/3] 采集流量数据...
  ✓ 采集完成
▶ [2/3] 数据转换为SQL...
  ✓ 转换完成
▶ [3/3] 数据入库...
  ✓ 入库完成

========================================
✓ SYCM流量采集完成
========================================

========================================
   ✓ 所有业务采集完成！
   总耗时：4分12秒
========================================
```

## 验证数据

### 快速验证

```sql
-- 验证KPI报表数据
SELECT '人均日接入' as 报表, COUNT(*) as 记录数
FROM fliggy_customer_service_data_daily
WHERE 日期 = '2026-04-24'
UNION ALL
SELECT '每周店铺个人数据', COUNT(*)
FROM fliggy_customer_service_performance_summary
WHERE date_time = '2026-04-24'
UNION ALL
SELECT '客服数据23年新', COUNT(*)
FROM fliggy_customer_service_performance_workload_analysis
WHERE date_time = '2026-04-24';

-- 验证订单数据
SELECT COUNT(*) as 订单数,
       SUM(actual_fee) as GMV
FROM fliggy_order_list
WHERE order_date = '2026-04-24';

-- 验证流量数据
SELECT 日期,
       total_uv as 访客数,
       total_pv as 浏览量
FROM qianniu.qianniu_fliggy_shop_daily_key_data
WHERE 日期 = '2026-04-24';

-- 验证关注店铺人数
SELECT 日期,
       关注店铺人数
FROM qianniu.qianniu_shop_data_daily_registration
WHERE 日期 = '2026-04-24';
```

### 完整验证脚本

保存为 `verify_data.sh`：

```bash
#!/bin/bash
DATE=$1

mysql -h $HOST -P $PORT -u $USER -p$PASS << EOF
SELECT '=== 数据验证：$DATE ===' as '';

SELECT 'KPI报表' as 类型,
       '人均日接入' as 报表名,
       COUNT(*) as 记录数
FROM fliggy_customer_service_data_daily
WHERE 日期 = '$DATE'
UNION ALL
SELECT 'KPI', '每周店铺个人数据', COUNT(*)
FROM fliggy_customer_service_performance_summary
WHERE date_time = '$DATE'
UNION ALL
SELECT 'KPI', '客服数据23年新', COUNT(*)
FROM fliggy_customer_service_performance_workload_analysis
WHERE date_time = '$DATE'
UNION ALL
SELECT '订单', '飞猪订单列表', COUNT(*)
FROM fliggy_order_list
WHERE order_date = '$DATE'
UNION ALL
SELECT '流量', 'SYCM流量看板', COUNT(*)
FROM qianniu.qianniu_fliggy_shop_daily_key_data
WHERE 日期 = '$DATE'
UNION ALL
SELECT '流量', '关注店铺人数', COUNT(*)
FROM qianniu.qianniu_shop_data_daily_registration
WHERE 日期 = '$DATE';
EOF
```

## 故障排查

### 问题1：某个业务失败

**现象**：某个业务显示失败，其他业务正常

**原因**：
- 单个业务的前置条件未满足
- 网络或数据库连接问题
- Excel文件下载失败

**解决**：
1. 查看错误信息
2. 单独运行失败的业务脚本
3. 修复问题后重新执行

```bash
# 单独测试失败的业务
./scripts/kpi_reports.sh 2026-04-24
```

### 问题2：所有业务都失败

**现象**：所有三个业务都显示失败

**原因**：
- Chrome未运行或未登录
- 数据库连接信息错误

**解决**：
```bash
# 检查Chrome
ps aux | grep "remote-debugging-port=9222"

# 测试数据库连接
mysql -h $HOST -P $PORT -u $USER -p$PASS

# 重新登录后重试
./scripts/all.sh 2026-04-24
```

### 问题3：数据缺失

**现象**：执行完成但某些数据缺失

**原因**：
- 某个Excel文件未下载
- 采集数据为空
- SQL插入失败

**解决**：
```bash
# 检查Chrome下载目录
ls -lt ~/Downloads/*.xlsx

# 手动验证单个业务
./scripts/kpi_reports.sh 2026-04-24
./scripts/fliggy_orders.sh 2026-04-24
./scripts/sycm_flow.sh 2026-04-24

# 针对性重新采集缺失数据
```

## 性能指标

### 当前版本（v1）

- **总耗时**：约4分钟
- **KPI报表**：约3分钟（串行导出，文件到达后立即处理，含超时兜底）
- **飞猪订单**：30秒
- **SYCM流量**：20秒

### 性能瓶颈

**主要瓶颈**：KPI报表的3个Excel导出是串行的

### 优化方向

- **v2**：并行导出KPI报表（预计节省30秒）
  - 同时发起3个导出请求
  - 统一并行后仅等待下载完成事件（含超时）
  - 总耗时：约2.8分钟

- **v3**：智能等待机制（预计节省40秒）
  - 使用 inotify 监控下载目录
  - 检测到文件立即处理
  - 总耗时：约2.2分钟

- **v4**：全流程并行（预计节省2分钟）
  - 三个业务并行执行
  - 总耗时：约1.5分钟

## 定时任务设置

### 每日自动执行

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨1点执行）
0 1 * * * cd /home/kk/Tourism_YingXiang && ./.claude/skills/daily-data-collection/scripts/all.sh $(date -d "yesterday" +\%Y-\%m-\%d) >> /var/log/daily_collection.log 2>&1

# 或者每天早上8点执行
0 8 * * * cd /home/kk/Tourism_YingXiang && ./.claude/skills/daily-data-collection/scripts/all.sh $(date -d "yesterday" +\%Y-\%m-\%d) >> /var/log/daily_collection.log 2>&1
```

### 每周自动执行（周一采集上周数据）

```bash
# 添加到crontab
0 1 * * 1 cd /home/kk/Tourism_YingXiang && for i in {1..7}; do DATE=$(date -d "$i days ago" +%Y-%m-%d); ./.claude/skills/daily-data-collection/scripts/all.sh $DATE; done >> /var/log/weekly_collection.log 2>&1
```

## 监控和日志

### 日志记录

```bash
# 执行时记录日志
./scripts/all.sh 2026-04-24 2>&1 | tee /var/log/daily_$(date +%Y%m%d).log
```

### 监控耗时

脚本会自动计算并显示总耗时，可用于：
- 性能监控
- 异常检测（超过5分钟视为异常）
- 优化验证

### 日志轮转

```bash
# 配置logrotate
sudo vi /etc/logrotate.d/daily-collection

# 添加以下内容
/var/log/daily_collection.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

## 日常运维

### 每日检查清单

- [ ] Chrome调试窗口运行正常
- [ ] 网站登录状态有效
- [ ] 定时任务执行成功
- [ ] 数据入库验证通过
- [ ] 日志无异常错误
- [ ] 耗时在正常范围（3-5分钟）

### 周期性维护

**每周**：
- 清理Chrome下载目录的旧Excel文件
- 检查日志文件大小
- 验证数据完整性

**每月**：
- 审查性能指标
- 评估是否需要优化
- 备份重要数据

## 相关技能

- **kpi-reports** - 单独执行KPI报表采集
- **fliggy-orders** - 单独执行飞猪订单采集
- **sycm-flow** - 单独执行SYCM流量采集

这些子技能可以独立使用，当只需要某个业务数据时更高效。

## 版本历史

- **v1** - 初始版本，串行执行三个业务
- **v2**（计划）- 并行导出优化
- **v3**（计划）- 智能等待机制
- **v4**（计划）- 全流程并行执行

## 最佳实践

### 推荐使用方式

```bash
# 1. 首次使用，设置环境变量
export HOST="your_host"
export PORT="3306"
export USER="your_user"
export PASS="your_password"

# 2. 测试执行（使用昨天的日期）
./scripts/all.sh $(date -d "yesterday" +%Y-%m-%d)

# 3. 验证数据（使用上面的SQL）

# 4. 设置定时任务（使用上面的crontab配置）

# 5. 每日检查日志
tail -f /var/log/daily_collection.log
```

### 生产环境建议

1. **设置定时任务** - 自动化每日采集
2. **配置日志记录** - 便于问题排查
3. **监控执行时间** - 异常时及时告警
4. **定期验证数据** - 确保数据质量
5. **备份重要数据** - 防止数据丢失

## 业务价值

### 数据完整性

每日采集三大业务数据，构建完整的数据仓库：
- 客服KPI数据 - 人员绩效分析
- 订单交易数据 - 业务指标分析
- 流量访客数据 - 营销效果分析

### 决策支持

基于数据做运营决策：
- 客服排班优化
- 销售策略调整
- 营销活动评估
- 资源配置优化

### 自动化收益

- **时间节省**：每日自动采集，无需人工操作
- **准确性提升**：标准化流程，减少人为错误
- **及时性保障**：定时任务，数据及时更新
- **可维护性**：完整日志，便于问题排查

---

**技能名称**: daily-data-collection
**技能版本**: v1
**最后更新**: 2026-04-25
**状态**: ✅ 生产就绪
