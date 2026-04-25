# Tourism Automation Skills

此目录包含飞猪业务数据采集的标准 Claude Skill。

## 📋 技能列表

### daily-data-collection ⭐
每日数据采集技能（统一技能）

**功能**：
一键采集飞猪业务的三大核心日报数据：
- 赤兔KPI客服报表（3个报表：人均日接入、每周店铺个人数据、客服数据23年新）
- 飞猪订单列表（订单明细 + 千牛日度关键表订单汇总）
- SYCM流量看板

**使用**：
```bash
./scripts/all.sh YYYY-MM-DD
```

**示例**：
```bash
# 采集昨日数据
./scripts/all.sh $(date -d "yesterday" +%Y-%m-%d)

# 采集指定日期
./scripts/all.sh 2026-04-24
```

**详细文档**：[daily-data-collection/SKILL.md](./daily-data-collection/SKILL.md)

---

## 🚀 快速开始

### 配置环境

```bash
# 设置数据库连接
export HOST="your_mysql_host"
export PORT="3306"
export USER="your_mysql_user"
export PASS="your_mysql_password"
```

### 一键采集

```bash
# 采集昨日所有数据
./scripts/all.sh $(date -d "yesterday" +%Y-%m-%d)
```

### 单独执行某个业务

```bash
# 只采集KPI报表
./scripts/kpi_reports.sh 2026-04-24

# 只采集飞猪订单
./scripts/fliggy_orders.sh 2026-04-24

# 只采集SYCM流量
./scripts/sycm_flow.sh 2026-04-24
```

---

## 📊 技能结构

```
daily-data-collection/
├── SKILL.md              # 技能说明文档（约12KB）
└── scripts/              # 可执行脚本
    ├── all.sh            # 一键执行所有业务
    ├── kpi_reports.sh    # KPI报表采集
    ├── fliggy_orders.sh  # 飞猪订单采集
    └── sycm_flow.sh      # SYCM流量采集
```

### SKILL.md 包含

- **名称和描述** - 技能标识和触发条件
- **概述** - 三大核心业务介绍
- **快速开始** - 使用方法和示例
- **执行流程** - 完整步骤说明
- **验证数据** - SQL查询验证结果
- **故障排查** - 常见问题和解决方案
- **性能指标** - 耗时分析和优化方向
- **定时任务** - crontab配置示例
- **监控日志** - 日志记录和监控方法

---

## 🎯 三大核心业务

### 1. 赤兔KPI客服报表

**目标表**：
- `fliggy_customer_service_data_daily`
- `fliggy_customer_service_performance_summary`
- `fliggy_customer_service_performance_workload_analysis`

**数据量**：每个报表约12条记录
**耗时**：约3分钟

### 2. 飞猪订单列表

**目标表**：
- `feizhu.fliggy_order_list` - 订单明细
- `qianniu.qianniu_fliggy_shop_daily_key_data` - `total_bookings`、`total_pax`、`gmv`

**数据量**：每天50-100单
**耗时**：约30秒

**处理步骤**：
订单采集必须带 `--all-pages`，采集结果先经过 `bin/prepare_fliggy_order_list_for_storage.py` 计算汇总指标，再分别通过 `bin/prepare_fliggy_order_list_sql.py` 和 `bin/prepare_qianniu_shop_daily_key_sql.py` 写入订单明细表和千牛日度关键表。

### 3. SYCM流量看板

**目标表**：
- `qianniu.qianniu_fliggy_shop_daily_key_data` - 访客、浏览、广告流量、平台流量
- `qianniu.qianniu_shop_data_daily_registration` - 关注店铺人数

**采集指标**：
- total_uv - 总访客数
- total_pv - 总浏览量
- 关注店铺人数 - 来自 flow-monitor 原始 JSON 的 `关注店铺人数`
- 流量来源广告_uv - 广告访客
- 流量来源平台_uv - 平台访客

**耗时**：约20秒

---

## 🔧 技能 vs Shell 脚本

### Shell 脚本（skills/*.sh）

- 快速执行
- 简单直接
- 适合命令行使用

### 标准技能（skills/skills/daily-data-collection/）

- 完整文档
- 可被 Claude Code 识别
- 支持技能触发
- 便于分享和复用

**两者可以并存**，根据场景选择使用方式。

---

## 📖 相关文档

- **[../README.md](../README.md)** - Skills使用手册
- **[../QUICKSTART.md](../QUICKSTART.md)** - 30秒快速开始
- **[../OPTIMIZATION.md](../OPTIMIZATION.md)** - 性能优化计划
- **[../SKILL_CREATOR_GUIDE.md](../SKILL_CREATOR_GUIDE.md)** - Skill Creator使用指南
- **[daily-data-collection/SKILL.md](./daily-data-collection/SKILL.md)** - 详细技能说明

---

## 🔄 版本历史

- **v1** - 初始版本，统一三大核心业务为单一技能

---

## 📝 维护说明

### 修改技能

1. 修改 scripts/ 中的脚本
2. 同步更新 SKILL.md 中的说明
3. 更新版本历史

### 测试技能

```bash
# 测试一键执行
./skills/skills/daily-data-collection/scripts/all.sh 2026-04-24

# 测试单个业务
./skills/skills/daily-data-collection/scripts/kpi_reports.sh 2026-04-24
```

### 安装到本地

```bash
# 复制到 .claude/skills/
cp -r skills/skills/daily-data-collection .claude/skills/

# 现在可以在 Claude Code 中使用了
```

---

**最后更新**: 2026-04-25
**技能版本**: v1
**状态**: ✅ 生产就绪
