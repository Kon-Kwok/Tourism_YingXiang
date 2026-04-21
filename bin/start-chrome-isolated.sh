#!/bin/bash
# 启动带调试端口的Chrome（独立配置）

set -e

DEBUG_PORT=9222
PROFILE_DIR="/tmp/chrome-debug-profile"

echo "======================================"
echo "启动Chrome（调试模式 - 独立配置）"
echo "======================================"
echo ""

# 1. 关闭调试模式的Chrome（如果存在）
echo "步骤 1/4: 清理..."
if pgrep -f "chrome.*--remote-debugging-port=$DEBUG_PORT" > /dev/null 2>&1; then
    echo "正在关闭旧Chrome..."
    pkill -9 -f "chrome.*--remote-debugging-port=$DEBUG_PORT" || true
    sleep 2
fi

# 清理旧配置（可选，如果想重新开始）
# rm -rf "$PROFILE_DIR"
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

# 尝试连接多次（有时Chrome需要更长时间启动）
for i in {1..10}; do
    if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
        echo "✓ Chrome调试端口已就绪！"
        echo ""
        echo "======================================"
        echo "✓ 启动成功！"
        echo "======================================"
        echo ""
        echo "现在可以采集数据（无需授权）："
        echo ""
        echo "  python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api"
        echo ""
        echo "注意：由于使用独立配置，需要重新登录topchitu"
        echo ""
        echo "管理Chrome："
        echo "  查看日志: tail -f /tmp/chrome_debug.log"
        echo "  停止Chrome: pkill -f 'chrome.*remote-debugging-port=$DEBUG_PORT'"
        echo ""
        exit 0
    fi
    echo "等待中... ($i/10)"
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
