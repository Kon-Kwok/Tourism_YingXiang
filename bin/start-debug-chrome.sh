#!/bin/bash
# 启动带远程调试端口的Chrome
# 这样CDP连接就不需要每次点击"允许"

set -e

# 远程调试端口
DEBUG_PORT=9222

# 检查Chrome是否已经在运行
if pgrep -f "chrome.*--remote-debugging-port=$DEBUG_PORT" > /dev/null; then
    echo "✓ Chrome已经在运行（调试端口 $DEBUG_PORT）"
    exit 0
fi

echo "正在启动Chrome（远程调试端口: $DEBUG_PORT）..."

# 关闭所有现有的Chrome进程（可选）
# pkill chrome || true

# 启动Chrome with remote debugging
chrome "$(cat <<EOF
google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir=/tmp/chrome-debug-profile \
  about:blank
EOF
)" &

# 等待Chrome启动
sleep 3

# 验证Chrome是否正常运行
if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    echo "✓ Chrome启动成功！"
    echo "  远程调试端口: $DEBUG_PORT"
    echo "  现在CDP连接不需要点击'允许'了"
else
    echo "✗ Chrome启动失败"
    exit 1
fi
