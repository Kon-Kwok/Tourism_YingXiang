#!/bin/bash
# ============================================================
# openclaw-daily-data-collection 安装脚本
# 用法: bash install.sh
# 说明: 将日报数据采集技能安装到当前用户的 OpenClaw workspace
# ============================================================

set -e

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "  日报数据采集技能 - 安装向导"
echo "========================================"
echo ""

# 1. 检测运行环境
echo -e "${YELLOW}[1/4] 检测运行环境...${NC}"

# 检测是否在 WSL 中
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "  ✓ 检测到 WSL 环境"
    IN_WSL=true
else
    echo "  ✓ 检测到 Linux 环境"
    IN_WSL=false
fi

# 检测项目路径（本脚本在 skills/skills/openclaw-daily-data-collection/ 下）
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SKILL_DIR/../.." && pwd)"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo -e "  ${RED}✗ 未找到 .env 文件: $PROJECT_DIR/.env${NC}"
    echo "  请先创建 .env 文件，内容如下："
    echo "    HOST=your_mysql_host"
    echo "    PORT=3306"
    echo "    USER=your_mysql_user"
    echo "    PASS=your_mysql_password"
    exit 1
fi
echo "  ✓ 项目目录: $PROJECT_DIR"
echo "  ✓ .env 文件已存在"

# 2. 检测 OpenClaw workspace
echo ""
echo -e "${YELLOW}[2/4] 检测 OpenClaw workspace...${NC}"

if [ "$IN_WSL" = true ]; then
    # WSL 环境：OpenClaw workspace 在 Windows 侧
    WIN_USER="$(cmd.exe /c echo %USERNAME% 2>/dev/null | tr -d '\r')"
    if [ -z "$WIN_USER" ] || [ "$WIN_USER" = "%USERNAME%" ]; then
        echo -e "  ${RED}✗ 无法检测 Windows 用户名${NC}"
        echo "  请手动设置 OPENCLAW_WORKSPACE 环境变量后重试"
        exit 1
    fi
    WORKSPACE="/mnt/c/Users/$WIN_USER/.openclaw/workspace"
else
    # 原生 Linux
    WORKSPACE="$HOME/.openclaw/workspace"
fi

# 允许通过环境变量覆盖
WORKSPACE="${OPENCLAW_WORKSPACE:-$WORKSPACE}"

if [ ! -d "$WORKSPACE" ]; then
    echo -e "  ${RED}✗ 未找到 OpenClaw workspace: $WORKSPACE${NC}"
    echo "  请确认 OpenClaw 已安装，或设置 OPENCLAW_WORKSPACE 环境变量"
    exit 1
fi
echo "  ✓ OpenClaw workspace: $WORKSPACE"

# 3. 安装 skill
echo ""
echo -e "${YELLOW}[3/4] 安装 skill...${NC}"

SKILL_TARGET="$WORKSPACE/skills/openclaw-daily-data-collection"
mkdir -p "$SKILL_TARGET"

# 复制 SKILL.md
cp "$SKILL_DIR/SKILL.md" "$SKILL_TARGET/SKILL.md"
echo "  ✓ 复制 SKILL.md"

# 生成 run_all.sh（自动适配当前环境）
cat > "$SKILL_TARGET/run_all.sh" << RUNALL
#!/bin/bash
# 由 install.sh 自动生成 - 日报数据采集入口
# 用法: bash run_all.sh [YYYY-MM-DD]  （不传日期默认昨天）

# 从项目 .env 加载数据库配置（set -a 自动 export）
cd "$PROJECT_DIR"
set -a && source .env && set +a

# 自动检测 Wayland/DBus 环境（从当前 session 或 Chrome 进程继承）
if [ -z "\$WAYLAND_DISPLAY" ]; then
    # 尝试从 Chrome 进程继承
    _chrome_pid=\$(ps aux | grep 'chrome.*remote-debugging-port=9222' | grep -v grep | head -1 | awk '{print \$2}')
    if [ -n "\$_chrome_pid" ] && [ -f "/proc/\$_chrome_pid/environ" ]; then
        eval \$(cat /proc/\$_chrome_pid/environ | tr '\0' '\n' | grep -E '^(WAYLAND_DISPLAY|DISPLAY|XDG_RUNTIME_DIR|DBUS_SESSION_BUS_ADDRESS)=' | sed 's/^/export /')
    fi
fi

# 执行采集
DATE="\${1:-\$(date -d 'yesterday' +%Y-%m-%d)}"
./scripts/all.sh "\$DATE"
RUNALL

chmod +x "$SKILL_TARGET/run_all.sh"
echo "  ✓ 生成 run_all.sh（已适配当前环境）"

# 4. 如果是 WSL，生成 Windows 侧的调用方式说明
echo ""
echo -e "${YELLOW}[4/4] 完成${NC}"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✓ 安装成功！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "技能已安装到: $SKILL_TARGET"
echo ""
echo "在 OpenClaw 中使用："
echo "  直接说「采集昨日数据」或「采集 2026-03-01 的日报」"
echo ""
echo "首次使用前请确认："
echo "  1. Chrome 已启动: ~/Tourism_Xiangwang/bin/start-chrome-unified.sh"
echo "  2. 赤兔 KPI 页面已在 Chrome 中打开"
echo "  3. 三个网站已登录（topchitu、fliggy、sycm）"
if [ "$IN_WSL" = true ]; then
    echo ""
    echo "Windows 侧 OpenClaw 调用命令："
    echo "  wsl bash $SKILL_TARGET/run_all.sh YYYY-MM-DD"
fi
