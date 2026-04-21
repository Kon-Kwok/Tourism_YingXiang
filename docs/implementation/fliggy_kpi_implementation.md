# 飞猪客服KPI数据采集系统 - 实施文档

**项目日期**: 2026-04-20
**实施人员**: Claude Code + 用户
**项目状态**: ✅ 已完成并测试通过

---

## 1. 项目背景

### 1.1 需求
集成飞猪客服KPI数据采集到现有的tourism自动化系统，从以下URL采集数据：
- URL: https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL

### 1.2 采集指标
13个客服KPI指标：
1. service_count - 服务人数
2. consult_count - 咨询人数
3. avg_first_reply_cost - 平均首次响应时间
4. avg_total_reply_cost - 平均总响应时间
5. no_reply_count - 未回复会话数
6. slow_reception_count - 慢接待数
7. employee_payments - 员工金额
8. employee_item_num - 商品件数
9. employee_paid_num - 支付人数
10. consult_buyer_num - 咨询买家数
11. service_buyer_num - 服务买家数
12. all_chat_buyer_num - 全部咨询买家数
13. fixed_employee_buyer_unit - 固定客单价

---

## 2. 技术方案演进

### 2.1 尝试的方案

#### 方案1: 纯HTTP请求 ❌
**思路**: 直接用requests调用API，从Chrome Cookie中读取认证信息
**问题**: 
- Topchitu使用复杂认证（CSRF token、session验证、动态签名）
- HTTP请求无法成功认证，返回登录页

#### 方案2: CDP表格提取 ❌
**思路**: 使用CDP抓取页面表格数据
**问题**: 
- 每次都需要点击"允许调试"
- 用户体验不友好

#### 方案3: CDP执行fetch调用API ✅（最终方案）
**思路**: 在浏览器页面中执行fetch()调用API，自动使用浏览器认证
**优点**:
- 无需处理复杂认证
- 复用浏览器登录态
- 数据直接来自API，准确可靠

---

## 3. Chrome配置问题与解决

### 3.1 遇到的问题

**问题1**: Chrome不允许在默认配置目录启用远程调试
```
错误: DevTools remote debugging requires a non-default data directory
```

**问题2**: 使用独立配置需要重新登录（验证码）

**问题3**: 多个Chrome配置管理混乱
- 正常Chrome: ~/.config/google-chrome
- 临时调试: /tmp/chrome-debug-profile
- 新调试: ~/.config/google-chrome-debug

### 3.2 最终解决方案

**统一使用调试模式Chrome**：
- 配置目录: `~/.config/google-chrome-debug`
- 调试端口: `9222`
- 启动脚本: `bin/start-chrome-unified.sh`

**关键配置**:
1. 所有采集器统一使用调试Chrome
2. 首次登录需要验证码，之后永久保存
3. 完全独立于正常Chrome

---

## 4. 实施步骤

### 4.1 创建采集器模块

**目录结构**:
```
src/tourism_automation/collectors/fliggy_kpi/employee_kpi/
├── __init__.py
├── api_client.py          # CDP fetch客户端
├── normalize_api.py       # 数据规范化
├── api_collector.py       # 采集器主逻辑
├── storage.py            # 数据库存储（已定义）
├── cli.py                # CLI命令注册
└── direct_cdp_client.py  # 直接CDP客户端（备用）
```

### 4.2 API端点发现

**通过CDP网络监控发现**:
```
API: /api/homepage/team/employee-rank
参数: 
  - from: 2026-04-19
  - to: 2026-04-19
  - queryDateType: DAY
```

### 4.3 核心代码实现

**CDP Fetch执行**:
```python
# api_client.py
def _execute_fetch(self, target_id: str, api_path: str, params: Dict = None):
    url = f"{api_path}?{urlencode(params)}"
    
    # JavaScript Promise链式调用
    js_code = f'''fetch("{url}")
        .then(r=>r.json())
        .then(d=>JSON.stringify({{success:true,data:d}}))
        .catch(e=>JSON.stringify({{success:false,error:e.message}}))'''
    
    # 设置环境变量指向DevToolsActivePort
    env = {**os.environ, 'CDP_PORT_FILE': '/home/kk/.config/google-chrome-debug/Default/DevToolsActivePort'}
    
    result = subprocess.run(
        [cdp_path, "eval", target_id, js_code],
        env=env  # 关键：传递环境变量
    )
```

### 4.4 统一Chrome配置

**更新所有采集器**:
```python
# shared/chrome/session.py
CHROME_COOKIE_DB = Path.home() / ".config/google-chrome-debug/Default/Cookies"

# fliggy_kpi/api_client.py
env = {
    **os.environ,
    'CDP_PORT_FILE': '/home/kk/.config/google-chrome-debug/Default/DevToolsActivePort'
}
```

### 4.5 创建启动脚本

**bin/start-chrome-unified.sh**:
```bash
#!/bin/bash
DEBUG_PORT=9222
CONFIG_DIR="$HOME/.config/google-chrome-debug"

# 启动Chrome
nohup google-chrome \
  --remote-debugging-port=$DEBUG_PORT \
  --user-data-dir="$CONFIG_DIR" \
  --no-first-run \
  --no-default-browser-check \
  > /tmp/chrome_debug.log 2>&1 &

# 自动创建DevToolsActivePort文件
mkdir -p "$CONFIG_DIR/Default"
BROWSER_WS=$(curl -s http://localhost:$DEBUG_PORT/json/version | jq -r '.webSocketDebuggerUrl')
echo -e "${DEBUG_PORT}\n${BROWSER_WS}" > "$CONFIG_DIR/Default/DevToolsActivePort"
```

---

## 5. 关键技术点

### 5.1 CDP环境变量问题

**问题**: CDP脚本无法找到DevToolsActivePort文件
**原因**: Chrome启动后创建的文件路径，CDP脚本需要通过环境变量指定
**解决**: 
```python
env = {**os.environ, 'CDP_PORT_FILE': '/home/kk/.config/google-chrome-debug/Default/DevToolsActivePort'}
```

### 5.2 WebSocket错误处理

**问题**: CDP eval返回 "Uncaught"
**原因**: JavaScript async/await语法问题
**解决**: 使用Promise链式调用
```javascript
// 错误写法
fetch(url).then(async r => await r.json())

// 正确写法
fetch(url).then(r=>r.json()).then(d=>JSON.stringify({data:d}))
```

### 5.3 URL更正

**用户纠正**:
- ❌ 飞猪商家工作台不是: https://feizhu.taobao.com
- ✅ 正确地址: https://fsc.fliggy.com/#/new/home
- ✅ 生意参谋: https://sycm.taobao.com/portal/home.htm
- ✅ Topchitu: https://kf.topchitu.com

---

## 6. 测试验证

### 6.1 测试结果

**SYCM采集器**:
```bash
python3 -m tourism_automation.cli.main sycm healthcheck
# 结果: {"status": "ok", "http_cookie_auth": true}
```

**KPI采集器**（2026-04-19数据）:
```bash
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-19 --method api
# 结果: 成功采集12个员工数据，包含13个指标
```

### 6.2 数据示例

```json
{
  "summary": {
    "metric_source": "api_fetch",
    "shop_name": "皇家加勒比国际游轮旗舰店",
    "page_code": "employee_kpi",
    "collection_date": "2026-04-19",
    "kpi_id": "1721",
    "employee_count": 12
  },
  "metrics": [
    {
      "biz_date": "2026-04-19",
      "employee_name": "皇家加勒比国际游轮旗舰店:dianna",
      "show_name": "dianna",
      "service_count": 55,
      "consult_count": 72,
      "avg_first_reply_cost": 21.58,
      "avg_total_reply_cost": 33.25,
      "no_reply_count": 0,
      "slow_reception_count": 0
    }
  ]
}
```

---

## 7. 使用指南

### 7.1 首次使用

```bash
# 1. 启动调试Chrome（全新配置）
./bin/start-chrome-unified.sh

# 2. 在Chrome中登录网站（首次需要验证码）
#    - https://kf.topchitu.com
#    - https://fsc.fliggy.com/#/new/home
#    - https://sycm.taobao.com/portal/home.htm
```

### 7.2 日常使用

```bash
# 启动Chrome（如果未运行）
./bin/start-chrome-unified.sh

# 采集KPI数据（无需登录，无需验证码）
python3 -m tourism_automation.cli.main fliggy-kpi employee \
  --date 2026-04-21 \
  --method api \
  --shop-name "皇家加勒比国际游轮旗舰店"
```

### 7.3 管理Chrome

```bash
# 查看状态
ps aux | grep "remote-debugging-port=9222"

# 查看日志
tail -f /tmp/chrome_debug.log

# 重启Chrome
./bin/start-chrome-unified.sh
```

---

## 8. 配置文件总览

### 8.1 Chrome配置

**调试Chrome（数据采集专用）**:
- 配置目录: `~/.config/google-chrome-debug`
- Cookie: `~/.config/google-chrome-debug/Default/Cookies`
- DevToolsActivePort: `~/.config/google-chrome-debug/Default/DevToolsActivePort`
- 调试端口: `9222`

**正常Chrome（日常浏览）**:
- 配置目录: `~/.config/google-chrome`
- 用途: 日常浏览，不受影响

### 8.2 代码配置

**所有采集器统一使用**:
- `shared/chrome/session.py` - SYCM采集器
- `fliggy_kpi/api_client.py` - KPI采集器
- `fliggy_home/client.py` - 飞采集器（间接通过session.py）

---

## 9. 重要文件清单

### 9.1 新增文件

**采集器代码**:
- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/api_client.py`
- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/normalize_api.py`
- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/api_collector.py`
- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/cli.py`
- `src/tourism_automation/collectors/fliggy_kpi/employee_kpi/direct_cdp_client.py`

**启动脚本**:
- `bin/start-chrome-unified.sh`
- `bin/start-chrome-isolated.sh`
- `bin/start-chrome-with-debug.sh`
- `bin/setup-chrome-cdp.sh`

**文档**:
- `docs/collectors/fliggy_kpi_usage.md`
- `docs/collectors/unified_chrome_guide.md`
- `memory/website_urls.md`

### 9.2 修改文件

- `src/tourism_automation/cli/main.py` - 注册fliggy-kpi子命令
- `src/tourism_automation/shared/chrome/session.py` - 切换到调试Chrome配置
- `.claude/skills/chrome-cdp/scripts/cdp.mjs` - CDP脚本（无修改）

---

## 10. 故障排除

### 10.1 Chrome相关

**问题**: Chrome无法启动
```bash
# 检查端口占用
lsof -i :9222

# 重新启动
./bin/start-chrome-unified.sh
```

**问题**: 找不到DevToolsActivePort文件
```bash
# 手动创建
mkdir -p ~/.config/google-chrome-debug/Default
BROWSER_WS=$(curl -s http://localhost:9222/json/version | jq -r '.webSocketDebuggerUrl')
echo -e "9222\n${BROWSER_WS}" > ~/.config/google-chrome-debug/Default/DevToolsActivePort
```

### 10.2 采集相关

**问题**: "未找到目标页面"
```bash
# 检查环境变量
export CDP_PORT_FILE=~/.config/google-chrome-debug/Default/DevToolsActivePort

# 检查Chrome标签页
curl -s http://localhost:9222/json | jq '.[] | {id, url, title}'
```

**问题**: API返回空数据
- 检查日期是否正确
- 确认KPI页面已加载
- 验证登录状态是否有效

---

## 11. 总结与经验

### 11.1 成功因素

1. **技术选型正确**: CDP执行fetch是最优方案
2. **统一配置管理**: 所有采集器使用同一个调试Chrome
3. **用户体验优化**: 首次登录后永久保存
4. **问题排查彻底**: 尝试多种方案，找到最优解

### 11.2 关键经验

1. **Chrome安全限制**: 不能在默认配置启用远程调试
2. **环境变量重要性**: CDP脚本需要CDP_PORT_FILE环境变量
3. **Promise链式调用**: JavaScript async/await在CDP中不稳定
4. **验证码机制**: 首次登录需要验证码，之后永久保存

### 11.3 未来改进

1. **自动化登录**: 可能的话实现验证码自动处理（不建议）
2. **Cookie监控**: 定期检查Cookie有效性
3. **数据存储**: 实现数据库存储功能
4. **定时任务**: 设置cron定时采集

---

## 12. 附录

### 12.1 网站地址汇总

- **飞猪商家工作台**: https://fsc.fliggy.com/#/new/home
- **生意参谋（SYCM）**: https://sycm.taobao.com/portal/home.htm
- **Topchitu（赤兔）**: https://kf.topchitu.com
- **KPI页面**: https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL

### 12.2 命令速查

```bash
# 启动Chrome
./bin/start-chrome-unified.sh

# SYCM采集
python3 -m tourism_automation.cli.main sycm collect-home --date 2026-04-21

# 飞采集器
python3 -m tourism_automation.cli.main fliggy-home collect-home --date 2026-04-21

# KPI采集
python3 -m tourism_automation.cli.main fliggy-kpi employee --date 2026-04-21 --method api
```

---

**文档创建时间**: 2026-04-21
**最后更新**: 2026-04-21
**版本**: 1.0
**状态**: ✅ 完成并验证通过
