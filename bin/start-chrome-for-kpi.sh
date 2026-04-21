#!/bin/bash
# 启动带调试端口的Chrome（用于KPI数据采集）
#
# 使用方法：
#   ./start-chrome-for-kpi.sh

set -e

DEBUG_PORT=9222
PROFILE_DIR="/tmp/chrome-debug-profile"

echo "======================================"
echo "启动Chrome（KPI数据采集模式）"
echo "======================================"
echo ""

# 1. 关闭旧Chrome（如果存在）
echo "步骤 1/4: 清理..."
if pgrep -f "chrome.*--remote-debugging-port=$DEBUG_PORT" > /dev/null 2>&1; then
    echo "正在关闭旧Chrome..."
    pkill -9 -f "chrome.*--remote-debugging-port=$DEBUG_PORT" || true
    sleep 2
fi
echo "✓ 清理完成"
echo ""

# 2. 创建配置目录
echo "步骤 2/4: 准备配置..."
mkdir -p "$PROFILE_DIR"
echo "✓ 配置目录: $PROFILE_DIR"
echo ""

# 3. 启动Chrome
echo "步骤 3/4: 启动Chrome..."
nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --user-data-dir="$PROFILE_DIR" \
  --no-first-run \
  --no-default-browser-check \
  "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL" > /tmp/chrome_debug.log 2>&1 &

CHROME_PID=$!
echo "✓ Chrome PID: $CHROME_PID"
echo ""

# 4. 等待并验证
echo "步骤 4/4: 验证..."
sleep 6

# 等待Chrome启动并创建配置
for i in {1..15}; do
    if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
        # 创建DevToolsActivePort文件（CDP脚本需要）
        mkdir -p "$PROFILE_DIR/Default"
        # 获取浏览器WebSocket URL
        BROWSER_WS=$(curl -s http://localhost:$DEBUG_PORT/json/version | jq -r '.webSocketDebuggerUrl' | sed 's|ws://[^:]*:[0-9]*/||')
        echo -e "${DEBUG_PORT}\n${BROWSER_WS}" > "$PROFILE_DIR/Default/DevToolsActivePort"

        echo "✓ Chrome调试端口已就绪！"
        echo ""
        echo "======================================"
        echo "✓ 启动成功！"
        echo "======================================"
        echo ""
        echo "请在Chrome窗口中："
        echo "  1. 登录topchitu（首次需要）"
        echo "  2. 确保KPI页面已加载"
        echo ""
        echo "登录后可以采集数据："
        echo ""
        echo "  python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-20 --method api"
        echo ""
        echo "管理Chrome："
        echo "  查看日志: tail -f /tmp/chrome_debug.log"
        echo "  停止Chrome: pkill -f 'chrome.*remote-debugging-port=$DEBUG_PORT'"
        echo ""
        exit 0
    fi
    echo "等待中... ($i/15)"
    sleep 2
done

echo "✗ Chrome启动失败"
echo ""
echo "请检查："
echo "  1. 查看日志: cat /tmp/chrome_debug.log"
echo "  2. 检查进程: ps aux | grep chrome"
echo "  3. 尝试手动运行Chrome查看是否有错误"

pkill -9 -f "chrome.*--remote-debugging-port=$DEBUG_PORT" || true
exit 1
