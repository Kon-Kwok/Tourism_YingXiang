# Skills - 快速执行脚本

三大核心业务的快速执行脚本。

## 📋 脚本列表

| 脚本 | 业务 | 用途 |
|------|------|------|
| `kpi_reports.sh` | 赤兔KPI三个报表 | 采集、转换、入库客服数据 |
| `fliggy_orders.sh` | 飞猪订单列表 | 采集、转换、入库订单数据 |
| `sycm_flow.sh` | SYCM流量看板 | 采集、转换、入库流量数据和关注店铺人数 |
| `all.sh` | 全部业务 | 一键执行所有三个业务 |

## 🚀 使用方法

### 1. 配置环境变量（首次使用）

```bash
# 设置数据库连接信息
export HOST="your_mysql_host"
export PORT="your_mysql_port"
export USER="your_mysql_user"
export PASS="your_mysql_password"

# 或者一次性设置
export MYSQL_CMD="mysql -h $HOST -P $PORT -u $USER -p$PASS"
```

### 2. 给脚本添加执行权限

```bash
chmod +x skills/*.sh
```

### 3. 执行单个业务

```bash
# 赤兔KPI三个报表
./skills/kpi_reports.sh 2026-04-24

# 飞猪订单列表
./skills/fliggy_orders.sh 2026-04-24

# SYCM流量看板
./skills/sycm_flow.sh 2026-04-24
```

### 4. 一键执行所有业务

```bash
# 采集昨日数据
./skills/all.sh $(date -d "yesterday" +%Y-%m-%d)

# 采集指定日期
./skills/all.sh 2026-04-24
```

## ⚡ 性能优化建议

### 当前版本（v1）

- ✅ 串行执行各个报表
- ✅ 下载完成后立即继续，超时由 `KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS` 控制
- ✅ 基本错误处理

### 下一步优化方向

- [ ] 并行导出多个报表（减少总等待时间）
- [x] 智能等待机制（检测文件是否下载完成）
- [ ] 失败重试机制
- [ ] 进度条显示
- [ ] 详细的性能统计

## 🔍 验证数据

执行完成后，可以验证数据是否成功入库：

```bash
# 验证赤兔KPI数据
mysql -h $HOST -P $PORT -u $USER -p$PASS feizhu << EOF
SELECT '报表1' as 类型, COUNT(*) FROM fliggy_customer_service_data_daily WHERE 日期 = '2026-04-24'
UNION ALL
SELECT '报表2', COUNT(*) FROM fliggy_customer_service_performance_summary WHERE date_time = '2026-04-24'
UNION ALL
SELECT '报表3', COUNT(*) FROM fliggy_customer_service_performance_workload_analysis WHERE date_time = '2026-04-24';
EOF

# 验证飞猪订单数据
mysql -h $HOST -P $PORT -u $USER -p$PASS feizhu \
  -e "SELECT COUNT(*) as 订单数 FROM fliggy_order_list WHERE order_date = '2026-04-24';"

# 验证SYCM流量数据
mysql -h $HOST -P $PORT -u $USER -p$PASS qianniu \
  -e "SELECT 日期, total_uv as 访客数, total_pv as 浏览量 FROM qianniu_fliggy_shop_daily_key_data WHERE 日期 = '2026-04-24';"

# 验证关注店铺人数
mysql -h $HOST -P $PORT -u $USER -p$PASS qianniu \
  -e "SELECT 日期, 关注店铺人数 FROM qianniu_shop_data_daily_registration WHERE 日期 = '2026-04-24';"
```

## 📊 性能记录

| 版本 | 优化措施 | 预计耗时 |
|------|----------|----------|
| v1 | 基础版本 | ~5分钟 |
| v2 | 并行导出 | ~3分钟 |
| v3 | 智能等待 | ~2分钟 |

## 🛠️ 故障排查

### 问题1：未找到Excel文件

**原因**：下载还未完成或日期模式错误

**解决**：
- 检查是否使用了 `--date-mode day`
- 设置 `KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS` 增加下载完成检测的超时时间
- 手动检查下载目录：`ls -lt ~/Downloads/*.xlsx`

### 问题2：MySQL连接失败

**原因**：环境变量未设置或连接信息错误

**解决**：
```bash
# 检查环境变量
echo $HOST $PORT $USER $PASS

# 测试连接
mysql -h $HOST -P $PORT -u $USER -p$PASS
```

### 问题3：采集到空数据

**原因**：Chrome会话过期或未登录

**解决**：
1. 检查Chrome调试窗口是否运行：`ps aux | grep "remote-debugging-port=9222"`
2. 在Chrome中重新登录相关网站
3. 重启Chrome调试窗口：`./bin/start-chrome-unified.sh`

---

**最后更新**: 2026-04-25
**当前版本**: v1
