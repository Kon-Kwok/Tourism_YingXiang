#!/bin/bash
# 三大核心业务一键采集脚本
# 用途：一次性采集所有三个业务的数据
# 使用：./skills/all.sh YYYY-MM-DD

set -e  # 遇到错误立即退出

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数检查
if [ -z "$1" ]; then
  echo "错误：请提供日期参数"
  echo "使用：./skills/all.sh YYYY-MM-DD"
  echo "示例：./skills/all.sh 2026-04-24"
  exit 1
fi

DATE=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${GREEN}"
echo "========================================"
echo "   三大核心业务一键采集"
echo "   日期：$DATE"
echo "========================================"
echo -e "${NC}"

# 记录开始时间
START_TIME=$(date +%s)

# 业务1: 赤兔KPI三个报表
echo -e "${BLUE}[$(date +%H:%M:%S)] 业务1：赤兔KPI三个报表${NC}"
"$SCRIPT_DIR/kpi_reports.sh" "$DATE"
echo ""

# 业务2: 飞猪订单列表
echo -e "${BLUE}[$(date +%H:%M:%S)] 业务2：飞猪订单列表${NC}"
"$SCRIPT_DIR/fliggy_orders.sh" "$DATE"
echo ""

# 业务3: SYCM流量看板
echo -e "${BLUE}[$(date +%H:%M:%S)] 业务3：SYCM流量看板${NC}"
"$SCRIPT_DIR/sycm_flow.sh" "$DATE"
echo ""

# 计算耗时
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo -e "${GREEN}"
echo "========================================"
echo "   ✓ 所有业务采集完成！"
echo "   总耗时：${MINUTES}分${SECONDS}秒"
echo "========================================"
echo -e "${NC}"
