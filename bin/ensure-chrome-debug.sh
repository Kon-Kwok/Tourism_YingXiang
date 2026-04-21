#!/bin/bash
# 确保Chrome以远程调试模式运行

DEBUG_PORT=9222

# 检查Chrome是否已经在调试模式下运行
if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    exit 0
fi

# 启动Chrome（调试模式）
nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir=/tmp/chrome-debug-profile \
  about:blank > /dev/null 2>&1 &

sleep 3

# 验证启动成功
if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    echo "✓ Chrome已启动（调试端口: $DEBUG_PORT）"
else
    echo "✗ Chrome启动失败" >&2
    exit 1
fi
