#!/bin/bash
# 每日数据采集入口脚本
# 用法: wsl bash /mnt/c/Users/Gzk/.openclaw/workspace/skills/openclaw-daily-data-collection/run_all.sh YYYY-MM-DD

# 关键环境变量：保证 Chrome cookie 解密和 DBus 通信正常
export WAYLAND_DISPLAY=wayland-0
export DISPLAY=:0
export XDG_RUNTIME_DIR=/run/user/1000/
export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus

cd ~/Xiangwang

# 数据库连接（.env 中的变量不带 export，不能 source）
export HOST='172.28.190.60'
export PORT='3306'
export USER='remote_user'
export PASS='Tourism2024'

DATE="${1:-$(date -d 'yesterday' +%Y-%m-%d)}"
./scripts/all.sh "$DATE"
