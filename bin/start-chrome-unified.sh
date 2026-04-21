#!/bin/bash
# 启动统一的调试Chrome（作为主浏览器使用）

set -e

DEBUG_PORT=9222
CONFIG_DIR="$HOME/.config/google-chrome-debug"

echo "======================================"
echo "启动统一Chrome（调试模式）"
echo "======================================"
echo ""

# 1. 关闭旧的调试Chrome
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
mkdir -p "$CONFIG_DIR"
echo "✓ 配置目录: $CONFIG_DIR"
echo ""

# 3. 启动Chrome
echo "步骤 3/4: 启动Chrome..."
nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --user-data-dir="$CONFIG_DIR" \
  --no-first-run \
  --no-default-browser-check \
  > /tmp/chrome_debug.log 2>&1 &

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
        mkdir -p "$CONFIG_DIR/Default"
        # 获取浏览器WebSocket URL
        BROWSER_WS=$(curl -s http://localhost:$DEBUG_PORT/json/version | jq -r '.webSocketDebuggerUrl' | sed 's|ws://[^:]*:[0-9]*/||')
        echo -e "${DEBUG_PORT}\n${BROWSER_WS}" > "$CONFIG_DIR/Default/DevToolsActivePort"

        echo "✓ Chrome调试端口已就绪！"
        echo ""
        echo "======================================"
        echo "✓ 启动成功！"
        echo "======================================"
        echo ""
        echo "这是你的统一Chrome浏览器："
        echo "  - 所有登录都在这个Chrome中"
        echo "  - 支持CDP数据采集"
        echo "  - 登录状态永久保存"
        echo ""
        echo "现在可以："
        echo "  1. 登录所有需要的网站（topchitu、淘宝等）"
        echo "  2. 采集KPI数据"
        echo ""
        echo "采集数据命令："
        echo "  python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api"
        echo ""
        echo "管理Chrome："
        echo "  查看日志: tail -f /tmp/chrome_debug.log"
        echo "  停止Chrome: pkill -f 'chrome.*remote-debugging-port=$DEBUG_PORT'"
        echo "  重启Chrome: ./bin/start-chrome-unified.sh"
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

pkill -9 -f "chrome.*--remote-debugging-port=$DEBUG_PORT" || true
exit 1
