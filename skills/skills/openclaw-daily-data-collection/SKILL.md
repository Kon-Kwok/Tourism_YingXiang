---
name: openclaw-daily-data-collection
description: 飞猪业务日报数据采集技能（Windows OpenClaw专用版）。在Windows环境下通过OpenClaw调用WSL中的采集脚本，一键采集三大核心日报数据。当用户在Windows下使用OpenClaw需要"日报数据"、"昨日数据采集"时使用此技能。
---

# 每日数据采集技能（Windows OpenClaw专用版）

## 🎯 运行环境说明

**本版本专为 Windows + OpenClaw 环境设计**：
- **运行环境**：Windows 侧 OpenClaw
- **执行方式**：Windows OpenClaw → WSL bash → Linux 采集脚本
- **适用场景**：你在 Windows 下使用 OpenClaw，通过它调用 WSL 中的采集系统

**架构图**：
```
Windows 侧                        WSL/Linux 侧
─────────────────────────────────────────────────────
OpenClaw Gateway                    ~/Tourism_Xiangwang/
     ↓                                   ↓
调用 run_all.sh                    执行采集脚本
     ↓                                   ↓
wsl bash project               实际数据采集工作
     ↓
返回结果到 OpenClaw
```



## 🚫 绝对禁止

1. **不要修改项目代码** — 源码在正确环境下能正常工作，出错一定是环境问题
2. **不要碰 Chrome** — 不要杀掉、重启、或自己启动 Chrome
3. **不要深入调试** — 不要研究 Cookie 加密、不要写调试脚本，第 2 次失败就报告用户

## 执行方式

### OpenClaw 标准调用（推荐）

在 Windows 下的 OpenClaw 中直接说：

```
"采集昨日数据"
"采集 2026-04-30 的日报"
"运行数据采集"
```

OpenClaw 会自动调用 WSL 中的采集脚本。

### 手动测试（调试用）

如果需要手动测试，可以在 Windows PowerShell 或 CMD 中：

```powershell
# 方式1：通过 WSL 调用（推荐）
wsl bash ~/Tourism_Xiangwang/scripts/all.sh 2026-04-30

# 方式2：使用 install.sh 生成的 run_all.sh
wsl bash C:\Users\YourUsername\.openclaw\workspace\skills\openclaw-daily-data-collection\run_all.sh 2026-04-30
```

### 单独采集某个业务（高级用法）

当需要单独调试某个模块时，可以进入 WSL 直接调用：

```bash
# 在 WSL 中执行
cd ~/Tourism_Xiangwang

# 单独采集KPI报表
./scripts/kpi_reports.sh 2026-04-30

# 单独采集飞猪订单
./scripts/fliggy_orders.sh 2026-04-30

# 单独采集SYCM流量
./scripts/sycm_flow.sh 2026-04-30
```

**注意**：单独调用前需要在 WSL 中设置环境变量：
```bash
export HOST="your_mysql_host"
export PORT="3306"
export USER="your_mysql_user"
export PASS="your_mysql_password"
```

## 安装方法（Windows 用户）

### 前提条件

1. **Windows 电脑已安装 WSL2**（Ubuntu 推荐）
2. **WSL2 中已配置项目**：`~/Tourism_Xiangwang`
3. **已安装 OpenClaw**（Windows 侧）

### 安装步骤

```bash
# 1. 打开 WSL 终端（Windows Terminal 或 PowerShell 中输入 wsl）
# 2. 进入项目目录
cd ~/Tourism_Xiangwang

# 3. 创建 .env 文件（数据库配置）
cat > .env << EOF
HOST=your_mysql_host
PORT=3306
USER=your_mysql_user
PASS=your_mysql_password
EOF

# 4. 运行安装脚本
bash skills/skills/openclaw-daily-data-collection/install.sh

# 5. 重启 OpenClaw Gateway（Windows 侧）
```

**install.sh 会自动**：
- 检测 WSL 环境
- 找到 Windows 侧的 OpenClaw workspace
- 从 `.env` 读取数据库配置
- 生成适配当前环境的 `run_all.sh`（在 WSL 和 Windows 间传递环境变量）
- 将 skill 安装到 OpenClaw

## 前置条件（采集前检查）

在 Windows 侧使用 OpenClaw 调用前，确保 WSL 中环境就绪：

**1. Chrome 在 WSL2 中运行**
   - 在 WSL 终端中启动：`~/Tourism_Xiangwang/bin/start-chrome-unified.sh`
   - 检查：`ps aux | grep remote-debugging-port=9222`

**2. 赤兔 KPI 页面已在 Chrome 中打开**
   - Chrome 中必须有 `kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721` 标签页

**3. 三个网站已登录**（在 WSL 的 Chrome 中）
   - sycm.taobao.com、fsc.fliggy.com、kf.topchitu.com

## 三大核心业务

| 业务 | 原理 | 耗时 | 目标表 |
|------|------|------|--------|
| 赤兔KPI客服报表 | CDP 操控 Chrome 导出 Excel → 入库 | ~30s | `fliggy_customer_service_*` |
| 飞猪订单列表 | Chrome cookie + HTTP API | ~5s | `fliggy_order_list` + `qianniu_*` |
| SYCM流量看板 | Chrome cookie + HTTP API | ~5s | `qianniu_fliggy_shop_daily_key_data` |

## 错误处理

```
"数据库连接参数未配置" → 检查 .env 文件是否存在于 ~/Tourism_Xiangwang/
"latin-1 codec" 错误  → 检查 run_all.sh 是否正确生成（重新运行 install.sh）
"未找到店铺KPI页面"   → 在 WSL Chrome 中打开 KPI 页面
卡在"导出 Excel"      → 检查 WSL Chrome 是否正常运行
WSL 执行权限错误      → 在 WSL 中运行：chmod +x scripts/*.sh
其他错误              → 把错误信息报告给用户
```

## 技术实现细节

### 跨平台调用架构

**Windows → WSL 调用链**：
```
Windows OpenClaw
    ↓ (调用)
run_all.sh (OpenClaw workspace)
    ↓ (wsl bash)
cd ~/Tourism_Xiangwang
source .env (加载环境变量)
    ↓
./scripts/all.sh
    ↓
实际数据采集（在 WSL 中执行）
```
     
**环境变量传递**：
- Windows 侧：无需设置环境变量
- WSL 侧：`run_all.sh` 自动从 `.env` 加载数据库配置
- Chrome 环境：自动检测并继承 Wayland/DBus 环境变量

### 公共函数库设计

所有脚本共享 `scripts/lib/common.sh` 公共函数库，提供统一功能：

**1. 参数检查**
- `check_date_argument`：验证日期参数格式
- `init_mysql`：初始化数据库连接

**2. 统一输出格式**
- `print_collection_start/end`：打印采集标题
- `print_step`：打印步骤进度
- `print_success/error`：打印成功/错误消息

**3. 文件验证**
- `check_file_not_empty`：检查文件是否存在且非空

### 重构优势

**代码复用**：消除了约37%的重复代码，三个主要脚本共享公共函数库

**一致性**：所有脚本使用相同的错误处理、输出格式和参数验证逻辑

**可维护性**：修改公共逻辑只需更新 common.sh，所有脚本自动生效

**跨平台兼容**：专门优化 Windows → WSL 调用链，确保环境变量正确传递

## 文件结构

```
openclaw-daily-data-collection/
├── SKILL.md        # 本文件（Windows OpenClaw 使用指南）
├── install.sh      # 安装脚本（生成 Windows↔WSL 桥接）
├── run_all.sh      # 运行入口（install.sh 生成，位于 OpenClaw workspace）
└── scripts/        # 数据采集脚本（在 WSL 中执行）
    ├── lib/
    │   └── common.sh             # 公共函数库
    ├── all.sh                    # 一键采集主脚本
    ├── run_all_env.sh            # WSL 环境适配器
    ├── kpi_reports.sh            # KPI 报表采集
    ├── fliggy_orders.sh          # 飞猪订单采集
    └── sycm_flow.sh             # SYCM 流量采集
```

## 版本选择指南

本项目提供两个独立版本，请根据运行环境选择：

### 本版本（openclaw-daily-data-collection）

✅ **适用场景**：
- 在 **Windows** 下使用 **OpenClaw**
- 通过 OpenClaw 的语音或文本命令调用
- 需要 Windows ↔ WSL 的桥接

✅ **优势**：
- 专门优化 Windows → WSL 调用链
- 自动处理环境变量跨平台传递
- OpenClaw 集成，开箱即用

### daily-data-collection 版本

✅ **适用场景**：
- 直接在 **Linux/WSL** 终端下运行
- 需要更多技术细节和调试能力
- 不使用 OpenClaw，直接调用脚本

✅ **优势**：
- 完整的技术文档
- 支持多种调用方式
- 适合开发和调试

**快速选择**：
- 使用 OpenClaw → 本版本（openclaw-daily-data-collection）
- 直接在 WSL 终端操作 → daily-data-collection 版本
