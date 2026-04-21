#!/bin/bash
# 启动带远程调试端口的Chrome（保持登录态）
#
# 使用方法：
#   ./start-chrome-with-debug.sh

set -e

DEBUG_PORT=9222
CHROME_USER_DATA="$HOME/.config/google-chrome"

echo "======================================"
echo "启动Chrome（远程调试模式）"
echo "======================================"
echo ""

# 1. 关闭所有现有的Chrome进程
echo "步骤 1/3: 关闭现有Chrome..."
if pgrep -f "chrome" > /dev/null 2>&1; then
    echo "正在关闭Chrome进程..."
    pkill -f "chrome" || true
    sleep 3
    echo "✓ 已关闭现有Chrome进程"
else
    echo "✓ Chrome未运行"
fi
echo ""

# 2. 启动Chrome（带调试端口，使用现有配置）
echo "步骤 2/3: 启动Chrome（调试端口 $DEBUG_PORT）..."
echo "提示：Chrome会使用你现有的登录信息"

nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --user-data-dir="$CHROME_USER_DATA" \
  --no-first-run \
  --no-default-browser-check \
  "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL" > /tmp/chrome_debug.log 2>&1 &

CHROME_PID=$!
echo "✓ Chrome已启动（PID: $CHROME_PID）"
echo ""

# 3. 等待Chrome完全启动
echo "步骤 3/3: 等待Chrome加载页面..."
sleep 5

# 4. 验证调试端口可用
if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    echo "✓ Chrome调试端口正常运行"
    echo ""
    echo "======================================"
    echo "✓ 启动成功！"
    echo "======================================"
    echo ""
    echo "现在可以："
    echo "  1. 使用CLI采集数据（无需授权）："
    echo "     python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api"
    echo ""
    echo "  2. 查看Chrome日志："
    echo "     tail -f /tmp/chrome_debug.log"
    echo ""
    echo "  3. 停止Chrome："
    echo "     pkill -f chrome"
    echo ""
    echo "提示：Chrome窗口可以最小化，不影响数据采集"
else
    echo "✗ Chrome启动失败"
    echo "请检查："
    echo "  - Chrome是否已安装"
    echo "  - 是否有其他Chrome进程占用端口 $DEBUG_PORT"
    echo ""
    pkill -f chrome || true
    exit 1
fi
