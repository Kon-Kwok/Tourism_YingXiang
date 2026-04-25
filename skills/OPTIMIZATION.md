# Skills性能优化迭代计划

## 📊 当前版本：v1（已更新）

**实现**：`skills/` 目录下的基础脚本

**性能**：
- 赤兔KPI三个报表：~3分钟（串行导出，检测到下载完成后立即继续）
- 飞猪订单列表：~30秒
- SYCM流量看板：~20秒
- **总计**：约 **4分钟**

**优化点**：
1. KPI报表仍为串行导出
2. 下载完成检测仍受 `KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS` 超时限制
3. 无失败重试机制

---

## 🚀 优化路线图

### 迭代1：并行导出（预计提升30%）

**目标**：减少KPI报表导出等待时间

**实现**：
- 同时发起3个报表导出请求
- 统一等待一次（12秒）
- 串行处理Excel转换和入库

**预期耗时**：~2.8分钟（节省30秒）

**脚本**：`skills/v2/kpi_reports_parallel.sh`

```bash
# 并行导出
for report in "人均日接入" "每周店铺个人数据" "客服数据23年新"; do
  python3 -m tourism_automation.cli.main shop-kpi-export \
    --report-name "$report" --date-mode day --date $DATE &
done
wait
sleep 12  # 统一等待

# 串行处理
...
```

---

### 迭代2：智能等待（预计提升20%）

**目标**：动态检测文件下载完成，避免固定等待

**实现**：
- 使用 `inotifywait` 监控下载目录
- 检测到新文件立即处理
- 设置超时保护（15秒）

**预期耗时**：~2.2分钟（节省40秒）

**脚本**：`skills/v2/kpi_reports_smart_wait.sh`

```bash
# 智能等待
timeout=15
elapsed=0
while [ $elapsed -lt $timeout ]; do
  if ls ~/Downloads/自定义报表*${DATE}至${DATE}*.xlsx 2>/dev/null | grep -q .; then
    break
  fi
  sleep 1
  elapsed=$((elapsed + 1))
done
```

---

### 迭代3：失败重试（提升稳定性）

**目标**：自动重试失败的请求，提高成功率

**实现**：
- 每个步骤最多重试3次
- 指数退避策略（1秒、2秒、4秒）
- 详细的错误日志

**脚本**：`skills/v3/kpi_reports_retry.sh`

```bash
retry_command() {
  local max_attempts=3
  local attempt=1
  local timeout=1

  while [ $attempt -le $max_attempts ]; do
    if "$@"; then
      return 0
    fi
    echo "失败，${timeout}秒后重试..."
    sleep $timeout
    timeout=$((timeout * 2))
    attempt=$((attempt + 1))
  done
  return 1
}
```

---

### 迭代4：全流程并行（预计提升50%）

**目标**：三个业务并行执行

**实现**：
- KPI报表导出期间，同时执行订单和SYCM采集
- 使用进程池管理并发
- 解决资源竞争

**预期耗时**：~1.5分钟

**脚本**：`skills/v4/all_parallel.sh`

```bash
# 并行执行所有业务
./skills/kpi_reports.sh $DATE &
PID_KPI=$!

./skills/fliggy_orders.sh $DATE &
PID_ORDERS=$!

./skills/sycm_flow.sh $DATE &
PID_SYCM=$!

wait $PID_KPI $PID_ORDERS $PID_SYCM
```

---

## 📈 性能测试方法

### 1. 使用基准测试脚本

```bash
# 测试当前版本
./skills/benchmark.sh 2026-04-24

# 查看结果
cat /tmp/skills_benchmark_*/results.csv
```

### 2. 手动计时测试

```bash
# 记录开始时间
START=$(date +%s)

# 执行脚本
./skills/all.sh 2026-04-24

# 计算耗时
END=$(date +%s)
ELAPSED=$((END - START))
echo "总耗时：$ELAPSED 秒"
```

### 3. 详细性能分析

```bash
# 使用time命令查看详细时间
time ./skills/all.sh 2026-04-24

# 输出示例：
# real    4m12s    # 实际耗时
# user    0m45s    # CPU时间
# sys     0m12s    # 系统调用时间
```

---

## 🎯 优化目标

| 版本 | 优化措施 | 预期耗时 | 提升 |
|------|----------|----------|------|
| v1 | Baseline | 4分钟 | - |
| v2 | 并行导出 | 2.8分钟 | 30% ↑ |
| v3 | 智能等待 | 2.2分钟 | 45% ↑ |
| v4 | 失败重试 | 2.2分钟 | 稳定性↑ |
| v5 | 全流程并行 | 1.5分钟 | 62% ↑ |

---

## 🔄 迭代流程

1. **实现优化版本**
   ```bash
   mkdir -p skills/v2
   # 编写优化脚本
   ```

2. **基准测试对比**
   ```bash
   ./skills/benchmark.sh 2026-04-24
   ```

3. **验证数据正确性**
   ```bash
   # 对比v1和v2的数据入库结果
   mysql ... -e "SELECT COUNT(*) FROM ... WHERE date = '2026-04-24'"
   ```

4. **确认稳定性和成功率**
   ```bash
   # 连续测试10次，统计失败率
   for i in {1..10}; do
     ./skills/all.sh 2026-04-24
   done
   ```

5. **合并到主线**
   ```bash
   # 如果效果显著且稳定，替换旧版本
   cp skills/v2/kpi_reports.sh skills/
   ```

---

## 📝 测试记录

| 日期 | 版本 | 测试日期 | 耗时 | 结果 | 备注 |
|------|------|----------|------|------|------|
| 2026-04-25 | v1 | 2026-04-24 | 待测试 | - | 初始版本 |

---

## 🛠️ 下一步行动

1. **运行基准测试**：了解当前性能baseline
   ```bash
   ./skills/benchmark.sh 2026-04-24
   ```

2. **实现v2并行导出**：创建 `skills/v2/kpi_reports_parallel.sh`

3. **对比测试**：验证v2是否比v1快

4. **迭代优化**：根据测试结果继续优化

---

**当前版本**: v1
**最后更新**: 2026-04-25
**状态**: 待测试baseline
