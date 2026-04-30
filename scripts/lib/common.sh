#!/bin/bash
# 公共函数库 - 减少脚本间代码重复
# 使用方法：source "$(dirname "${BASH_SOURCE[0]}")/lib/common.sh"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 参数检查函数
check_date_argument() {
  if [ -z "$1" ]; then
    echo -e "${RED}错误：请提供日期参数${NC}"
    echo "使用：$0 YYYY-MM-DD"
    echo "示例：$0 2026-04-30"
    exit 1
  fi
}

# 数据库连接初始化
init_mysql() {
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
  echo "${MYSQL_CMD}"
}

# 打印采集开始标题
print_collection_start() {
  local title=$1
  local date=$2
  local extra_info="${3:-}"  # 可选的额外信息

  echo -e "${GREEN}========================================${NC}"
  echo -e "${GREEN}${title}${NC}"
  echo -e "${GREEN}日期：${date}${NC}"
  if [ -n "$extra_info" ]; then
    echo -e "${GREEN}${extra_info}${NC}"
  fi
  echo -e "${GREEN}========================================${NC}"
}

# 打印采集完成标题
print_collection_end() {
  local title=$1
  local extra_info="${2:-}"  # 可选的额外信息

  echo ""
  echo -e "${GREEN}========================================${NC}"
  echo -e "${GREEN}✓ ${title}完成${NC}"
  if [ -n "$extra_info" ]; then
    echo -e "${GREEN}${extra_info}${NC}"
  fi
  echo -e "${GREEN}========================================${NC}"
}

# 检查文件是否存在且非空
check_file_not_empty() {
  local file=$1
  local error_msg=$2

  if [ ! -s "$file" ]; then
    echo -e "  ${RED}✗ ${error_msg}${NC}"
    rm -f "$file"
    return 1
  fi
  return 0
}

# 步骤输出函数
print_step() {
  local step_num=$1
  local total_steps=$2
  local description=$3
  echo -e "${YELLOW}▶ [${step_num}/${total_steps}] ${description}...${NC}"
}

# 成功输出函数
print_success() {
  local message=$1
  echo -e "  ${GREEN}✓ ${message}${NC}"
}

# 错误输出函数
print_error() {
  local message=$1
  echo -e "  ${RED}✗ ${message}${NC}"
}
