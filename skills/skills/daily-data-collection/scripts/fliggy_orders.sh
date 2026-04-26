#!/bin/bash
# 飞猪订单列表采集脚本
# 用途：采集、转换、入库飞猪订单数据
# 使用：./skills/fliggy_orders.sh YYYY-MM-DD

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 参数检查
if [ -z "$1" ]; then
  echo -e "${RED}错误：请提供日期参数${NC}"
  echo "使用：./skills/fliggy_orders.sh YYYY-MM-DD"
  echo "示例：./skills/fliggy_orders.sh 2026-04-24"
  exit 1
fi

DATE=$1
MYSQL="${MYSQL_CMD:-mysql -h $HOST -P $PORT -u $USER -p$PASS}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}飞猪订单列表采集${NC}"
echo -e "${GREEN}日期：$DATE${NC}"
echo -e "${GREEN}========================================${NC}"

# 步骤1: 采集订单数据（带 all-pages，供后续总量计算）
echo -e "${YELLOW}▶ [1/4] 采集订单数据...${NC}"
python3 -m tourism_automation.cli.main fliggy-order-list list \
  --page-num 1 \
  --page-size 100 \
  --all-pages \
  --deal-start "${DATE} 00:00:00" \
  --deal-end "${DATE} 23:59:59" > /tmp/orders_raw_$$.json

if [ ! -s /tmp/orders_raw_$$.json ]; then
  echo -e "  ${RED}✗ 未采集到订单数据${NC}"
  rm -f /tmp/orders_raw_$$.json
  exit 1
fi

# 统计订单数量
ORDER_COUNT=$(jq 'length' /tmp/orders_raw_$$.json 2>/dev/null || echo "0")
echo -e "  ${GREEN}✓ 采集到 $ORDER_COUNT 条订单${NC}"

# 步骤2: 数据预处理
echo -e "${YELLOW}▶ [2/4] 数据预处理...${NC}"
cat /tmp/orders_raw_$$.json | \
  python3 bin/prepare_fliggy_order_list_for_storage.py > /tmp/orders_prep_$$.json

echo -e "  ${GREEN}✓ 预处理完成${NC}"

echo -e "${YELLOW}▶ [3/4] 订单明细入库...${NC}"
cat /tmp/orders_prep_$$.json | \
  python3 bin/prepare_fliggy_order_list_sql.py | \
  $MYSQL feizhu

# 步骤4: 订单汇总入库（total_bookings / total_pax / gmv）到千牛日度关键表
echo -e "${YELLOW}▶ [4/4] 订单汇总入库...${NC}"
cat /tmp/orders_prep_$$.json | \
  python3 bin/prepare_qianniu_shop_daily_key_sql.py | \
  $MYSQL qianniu

# 清理临时文件
rm -f /tmp/orders_raw_$$.json /tmp/orders_prep_$$.json

echo -e "  ${GREEN}✓ 入库完成${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 飞猪订单采集完成${NC}"
echo -e "${GREEN}订单数量：$ORDER_COUNT${NC}"
echo -e "${GREEN}========================================${NC}"
