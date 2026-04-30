#!/bin/bash
# 赤兔KPI三个报表采集脚本
# 用途：采集、转换、入库赤兔KPI三个报表数据
# 使用：./scripts/kpi_reports.sh YYYY-MM-DD

set -e  # 遇到错误立即退出

# 引入公共函数库
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/common.sh"

# 参数检查
check_date_argument "$1"
DATE=$1

# 初始化数据库连接
MYSQL="$(init_mysql)"

# 下载完成等待超时（秒），检测到新文件后立即继续。默认60秒
MAX_WAIT_SECONDS="${KPI_DOWNLOAD_WAIT_TIMEOUT_SECONDS:-${KPI_DOWNLOAD_WAIT_SECONDS:-60}}"

# 查找最新文件的函数
find_latest_file() {
  local report_name=$1
  ls -t ~/Downloads/自定义报表*${report_name}*${DATE}至${DATE}*.xlsx 2>/dev/null | head -1
}

# 等待下载完成的函数
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

# 打印开始标题
print_collection_start "赤兔KPI三个报表采集" "$DATE"

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
    print_error "下载超时：未在 ${MAX_WAIT_SECONDS}s 内找到报表 [$report_name] 的新文件"
    exit 1
  fi

  if [[ "$(basename "$EXCEL")" != *"$report_name"* || "$(basename "$EXCEL")" != *"${DATE}至${DATE}"* ]]; then
    print_error "下载文件日期或报表不匹配：$(basename "$EXCEL")"
    echo -e "  ${RED}  期望：报表 [$report_name]，日期范围 [$DATE至$DATE]${NC}"
    exit 1
  fi

  print_success "找到文件：$(basename "$EXCEL")"

  # 步骤3: 转换并入库
  echo -e "  [3/3] 转换并入库..."
  python3 bin/prepare_shop_kpi_excel_to_json.py "$EXCEL" | \
    python3 "bin/$script_name" | \
    $MYSQL feizhu

  print_success "$report_name 处理完成"
done

# 打印完成标题
print_collection_end "所有报表处理"
