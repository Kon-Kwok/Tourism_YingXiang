# 统一 Chrome 使用指南

所有依赖浏览器登录态的采集器共用同一个 Chrome 调试会话。

## 固定配置

- 配置目录：`~/.config/google-chrome-debug`
- 调试端口：`9222`
- 启动脚本：`./bin/start-chrome-unified.sh`

## 首次准备

1. 启动统一 Chrome：

```bash
./bin/start-chrome-unified.sh
```

2. 在该窗口中登录以下站点：
   - `https://sycm.taobao.com`
   - `https://fsc.fliggy.com`
   - `https://kf.topchitu.com`

3. 需要 KPI 采集时，提前打开对应页面：
   - 员工 KPI：`https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL`
   - 店铺 KPI：`https://kf.topchitu.com/web/custom-kpi/shop-kpi?id=941`

## 日常检查

```bash
ps aux | grep "remote-debugging-port=9222"
curl -s http://localhost:9222/json/version
tail -f /tmp/chrome_debug.log
```

## 使用规则

- 不要关闭统一 Chrome 窗口；可以最小化。
- 不要删除 `~/.config/google-chrome-debug`。
- 登录失效时，只在该窗口里重新登录，不要新建独立浏览器配置。

## 常见问题

### 调试端口不可用

先执行 `./bin/start-chrome-unified.sh`，再检查 `http://localhost:9222/json/version` 是否可访问。

### 找不到 KPI 页面

说明目标页面未在统一 Chrome 中打开。先手动打开页面，再运行采集命令。

### API 返回登录页

说明对应站点登录态已失效。在统一 Chrome 中重新登录后重试。
