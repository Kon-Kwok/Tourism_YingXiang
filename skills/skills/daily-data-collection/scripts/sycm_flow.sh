#!/bin/bash
# SYCM流量看板采集脚本
# 用途：采集、转换、入库SYCM流量数据
# 使用：./skills/sycm_flow.sh YYYY-MM-DD

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 参数检查
if [ -z "$1" ]; then
  echo -e "${RED}错误：请提供日期参数${NC}"
  echo "使用：./skills/sycm_flow.sh YYYY-MM-DD"
  echo "示例：./skills/sycm_flow.sh 2026-04-24"
  exit 1
fi

DATE=$1
SHOP_NAME="${SHOP_NAME:-皇家加勒比国际游轮旗舰店}"
if [ -z "${MYSQL_CMD}" ]; then
  PORT="${PORT:-3306}"
  if [ -z "${HOST}" ] || [ -z "${USER}" ] || [ -z "${PASS}" ]; then
    echo -e "${RED}错误：数据库连接参数未配置${NC}"
    echo "请设置以下变量后重试："
    echo "  export HOST=\"<mysql_host>\""
    echo "  export PORT=\"${PORT}\""
    echo "  export USER=\"<mysql_user>\""
    echo "  export PASS=\"<mysql_password>\""
    echo "或设置 MYSQL_CMD，例如："
    echo "  export MYSQL_CMD=\"mysql -h \$HOST -P \$PORT -u \$USER -p\$PASS\""
    exit 1
  fi
  MYSQL_CMD="mysql -h ${HOST} -P ${PORT} -u ${USER} -p${PASS}"
fi

MYSQL="${MYSQL_CMD}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}SYCM流量看板采集${NC}"
echo -e "${GREEN}日期：$DATE${NC}"
echo -e "${GREEN}店铺：$SHOP_NAME${NC}"
echo -e "${GREEN}========================================${NC}"

# 步骤1: 采集流量数据
echo -e "${YELLOW}▶ [1/3] 采集流量数据...${NC}"
python3 -m tourism_automation.cli.main sycm flow-monitor \
  --date "$DATE" \
  --shop-name "$SHOP_NAME" > /tmp/sycm_flow_$$.json

if [ ! -s /tmp/sycm_flow_$$.json ]; then
  echo -e "  ${RED}✗ 未采集到流量数据${NC}"
  rm -f /tmp/sycm_flow_$$.json
  exit 1
fi

echo -e "  ${GREEN}✓ 采集完成${NC}"

# 步骤2: 数据转换
echo -e "${YELLOW}▶ [2/3] 数据转换为SQL（含关注店铺人数）...${NC}"
cat /tmp/sycm_flow_$$.json | \
  python3 bin/prepare_sycm_flow_sql.py > /tmp/sycm_flow_$$.sql

if [ ! -s /tmp/sycm_flow_$$.sql ]; then
  echo -e "  ${RED}✗ SQL转换失败${NC}"
  rm -f /tmp/sycm_flow_$$.json /tmp/sycm_flow_$$.sql
  exit 1
fi

if ! grep -q "qianniu_shop_data_daily_registration" /tmp/sycm_flow_$$.sql; then
  echo -e "  ${RED}✗ SQL缺少关注店铺人数入库语句${NC}"
  rm -f /tmp/sycm_flow_$$.json /tmp/sycm_flow_$$.sql
  exit 1
fi

echo -e "  ${GREEN}✓ 转换完成${NC}"

# 步骤3: 入库
echo -e "${YELLOW}▶ [3/3] 数据入库...${NC}"
cat /tmp/sycm_flow_$$.sql | $MYSQL qianniu

# 清理临时文件
rm -f /tmp/sycm_flow_$$.json /tmp/sycm_flow_$$.sql

echo -e "  ${GREEN}✓ 入库完成${NC}"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ SYCM流量采集完成${NC}"
echo -e "${GREEN}========================================${NC}"
