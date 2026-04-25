#!/bin/bash
# 赤兔KPI三个报表采集脚本
# 用途：采集、转换、入库赤兔KPI三个报表数据
# 使用：./skills/kpi_reports.sh YYYY-MM-DD

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 参数检查
if [ -z "$1" ]; then
  echo -e "${RED}错误：请提供日期参数${NC}"
  echo "使用：./skills/kpi_reports.sh YYYY-MM-DD"
  echo "示例：./skills/kpi_reports.sh 2026-04-24"
  exit 1
fi

DATE=$1
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
# 下载完成等待超时（秒），检测到新文件后立即继续。默认60秒
MAX_WAIT_SECONDS="${KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS:-${KPI_DOWNLOAD_WAIT_SECONDS:-60}}"

find_latest_file() {
  local report_name=$1
  ls -t ~/Downloads/自定义报表*${report_name}*${DATE}至${DATE}*.xlsx 2>/dev/null | head -1
}

wait_for_download() {
  local report_name=$1
  local started_at=$2
  local timeout_seconds=$3
  local end_time=$((started_at + timeout_seconds))
  local file_path=""

  while :; do
    file_path="$(find_latest_file "$report_name")"
    if [ -n "$file_path" ]; then
      local mtime
      mtime="$(stat -c %Y "$file_path" 2>/dev/null || echo 0)"
      if [ "$mtime" -ge "$started_at" ]; then
        echo "$file_path"
        return 0
      fi
    fi

    local now
    now="$(date +%s)"
    if [ "$now" -ge "$end_time" ]; then
      return 1
    fi

    sleep 0.5
  done
}

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}赤兔KPI三个报表采集${NC}"
echo -e "${GREEN}日期：$DATE${NC}"
echo -e "${GREEN}========================================${NC}"

# 报表列表
reports=(
  "人均日接入:prepare_fliggy_customer_service_data_daily_sql.py"
  "每周店铺个人数据:prepare_fliggy_customer_service_summary_sql.py"
  "客服数据23年新:prepare_fliggy_customer_service_workload_sql.py"
)

# 处理每个报表
for item in "${reports[@]}"; do
  IFS=':' read -r report_name script_name <<< "$item"

  echo ""
  echo -e "${YELLOW}▶ 开始处理：$report_name${NC}"

  # 步骤1: 导出Excel
  echo -e "  [1/3] 导出Excel..."
  export_started_at=$(date +%s)
  python3 -m tourism_automation.cli.main shop-kpi-export \
    --report-name "$report_name" \
    --date-mode day \
    --date "$DATE" > /dev/null

  # 步骤2: 等待下载完成
  echo -e "  [2/3] 等待下载...（检测到新文件后立即继续）"
  EXCEL="$(wait_for_download "$report_name" "$export_started_at" "$MAX_WAIT_SECONDS" || true)"
  if [ -z "$EXCEL" ]; then
    echo -e "  ${RED}✗ 下载超时：未在 ${MAX_WAIT_SECONDS}s 内找到报表 [$report_name] 的新文件${NC}"
    exit 1
  fi

  if [[ "$(basename "$EXCEL")" != *"$report_name"* || "$(basename "$EXCEL")" != *"${DATE}至${DATE}"* ]]; then
    echo -e "  ${RED}✗ 下载文件日期或报表不匹配：$(basename "$EXCEL")${NC}"
    echo -e "  ${RED}  期望：报表 [$report_name]，日期范围 [$DATE至$DATE]${NC}"
    exit 1
  fi

  echo -e "  ${GREEN}✓ 找到文件：$(basename "$EXCEL")${NC}"

  # 步骤3: 转换并入库
  echo -e "  [3/3] 转换并入库..."
  python3 bin/prepare_shop_kpi_excel_to_json.py "$EXCEL" | \
    python3 "bin/$script_name" | \
    $MYSQL feizhu

  echo -e "  ${GREEN}✓ $report_name 处理完成${NC}"
done

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 所有报表处理完成${NC}"
echo -e "${GREEN}========================================${NC}"
