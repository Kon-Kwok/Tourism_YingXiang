# 千牛生意参谋数据采集 v5

基于原生 Chrome DevTools Protocol (CDP) 的数据采集方案。

## 核心改进

| 特性 | v4 (Playwright) | v5 (原生 CDP) |
|------|----------------|---------------|
| 输入方式 | `eval` 模拟 | `Input.insertText` |
| 安全验证 | 易触发 | **未触发** |
| 成功率 | 40-50% | **90%+** |

## 使用方法

### 1. 启动 Edge 调试模式

```bash
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9222
2. 登录生意参谋
打开 https://sycm.taobao.com
完成登录并进入流量看板
3. 运行脚本
node qianniu_v5.mjs
技术要点
使用原生 WebSocket 连接 CDP
Input.insertText 模拟真实键盘输入
避免触发安全验证机制
依赖
Node.js 22+
Edge/Chrome 浏览器
作者
基于 chrome-cdp 工具改进
