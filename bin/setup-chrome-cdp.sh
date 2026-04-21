#!/bin/bash
# 一次性设置：配置Chrome支持CDP免授权连接
#
# 使用方法：
#   ./setup-chrome-cdp.sh
#
# 设置完成后，所有CDP操作都不需要点击"允许调试"

set -e

echo "======================================"
echo "Chrome CDP 免授权设置"
echo "======================================"
echo ""

DEBUG_PORT=9222
CONFIG_DIR="$HOME/.config/google-chrome-debug"
PROFILE_DIR="/tmp/chrome-debug-profile"

# 检查是否已经设置过
if [ -f "$CONFIG_DIR/.cdp_setup_done" ]; then
    echo "✓ 检测到已完成设置"
    echo ""
    echo "启动Chrome（调试模式）："
    echo "  google-chrome --remote-debugging-port=$DEBUG_PORT --user-data-dir=$PROFILE_DIR"
    echo ""
    echo "或者使用便捷命令："
    echo "  ensure-chrome-debug"
    exit 0
fi

echo "步骤 1/3: 创建配置目录"
mkdir -p "$CONFIG_DIR"
echo "✓ 配置目录: $CONFIG_DIR"
echo ""

echo "步骤 2/3: 创建便捷脚本"
cat > "$HOME/bin/ensure-chrome-debug" << 'EOF'
#!/bin/bash
DEBUG_PORT=9222

if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    exit 0
fi

nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir=/tmp/chrome-debug-profile \
  about:blank > /dev/null 2>&1 &

sleep 3

if ! curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    echo "✗ Chrome启动失败" >&2
    exit 1
fi
EOF

chmod +x "$HOME/bin/ensure-chrome-debug"
echo "✓ 创建命令: ensure-chrome-debug"
echo ""

echo "步骤 3/4: 启动Chrome（首次）"
echo "正在启动Chrome，请稍候..."
nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --no-first-run \
  --no-default-browser-check \
  --user-data-dir="$PROFILE_DIR" \
  "https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL" > /dev/null 2>&1 &

sleep 5

# 验证启动成功
if curl -s http://localhost:$DEBUG_PORT/json/version > /dev/null 2>&1; then
    # 标记设置完成
    touch "$CONFIG_DIR/.cdp_setup_done"
    echo "✓ Chrome启动成功！"
    echo ""
else
    echo "✗ Chrome启动失败" >&2
    echo "请检查Chrome是否已安装" >&2
    exit 1
fi

echo "步骤 4/4: 打开KPI页面"
echo "正在打开KPI页面..."
# 等待一秒让页面完全加载
sleep 2
echo "✓ KPI页面已打开"
echo ""

echo "======================================"
echo "✓ 设置完成！"
echo "======================================"
echo ""
echo "现在可以："
echo ""
echo "1. 使用便捷命令启动Chrome（如需要）："
echo "   ensure-chrome-debug"
echo ""
echo "2. 采集数据（无需点击授权）："
echo "   python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api"
echo ""
echo "提示：Chrome窗口最小化也可以，数据采集在后台进行"
echo ""
