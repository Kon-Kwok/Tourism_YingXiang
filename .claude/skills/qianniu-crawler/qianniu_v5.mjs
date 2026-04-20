#!/usr/bin/env node
/**
 * 千牛生意参谋数据采集 - v5
 * 基于原生 Chrome DevTools Protocol (CDP)
 * 核心改进：使用 Input.insertText 替代 eval，避免触发安全验证
 */

import { writeFileSync, existsSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// 配置
const CONFIG = {
  wsUrl: process.env.CDP_WS_URL || 'ws://localhost:9222/devtools/browser/...',
  dataDir: resolve(__dirname, '..', '..', '..', 'data'),
  screenshotDir: resolve(__dirname, '..', '..', '..', 'screenshots')
};

// 确保目录存在
[CONFIG.dataDir, CONFIG.screenshotDir].forEach(dir => {
  if (!existsSync(dir)) mkdirSync(dir, { recursive: true });
});

const sleep = ms => new Promise(r => setTimeout(r, ms));
const randomDelay = (min, max) => sleep(min + Math.random() * (max - min));

/**
 * CDP 客户端
 */
class CDPClient {
  #ws; #id = 0; #pending = new Map(); sessionId = null;

  async connect(wsUrl = CONFIG.wsUrl) {
    return new Promise((res, rej) => {
      this.#ws = new WebSocket(wsUrl);
      this.#ws.onopen = () => res();
      this.#ws.onerror = e => rej(new Error('WebSocket error'));
      this.#ws.onmessage = ev => {
        const msg = JSON.parse(ev.data);
        if (msg.id && this.#pending.has(msg.id)) {
          const { resolve, reject } = this.#pending.get(msg.id);
          this.#pending.delete(msg.id);
          msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
        }
      };
    });
  }

  send(method, params = {}, sessionId) {
    const id = ++this.#id;
    return new Promise((resolve, reject) => {
      this.#pending.set(id, { resolve, reject });
      const msg = { id, method, params };
      if (sessionId) msg.sessionId = sessionId;
      this.#ws.send(JSON.stringify(msg));
      setTimeout(() => {
        if (this.#pending.has(id)) {
          this.#pending.delete(id);
          reject(new Error(`Timeout: ${method}`));
        }
      }, 15000);
    });
  }

  close() { this.#ws.close(); }

  async attachToSycm() {
    console.log('🔍 查找生意参谋页面...');
    const { targetInfos } = await this.send('Target.getTargets');
    const page = targetInfos.find(t => 
      t.type === 'page' && t.url.includes('sycm.taobao.com')
    );
    if (!page) throw new Error('生意参谋页面未找到');
  
    console.log(`✅ 找到: ${page.title}`);
    const r = await this.send('Target.attachToTarget', {
      targetId: page.targetId,
      flatten: true
    });
    this.sessionId = r.sessionId;
  
    await this.send('Runtime.enable', {}, this.sessionId);
    await this.send('Page.enable', {}, this.sessionId);
    return page;
  }

  async eval(expression) {
    const r = await this.send('Runtime.evaluate', {
      expression,
      returnByValue: true,
      awaitPromise: true
    }, this.sessionId);
    if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
    return r.result.value;
  }

  async type(text) {
    console.log(`⌨️ 输入: ${text.slice(0, 30)}`);
    await randomDelay(500, 1000);
    await this.send('Input.insertText', { text }, this.sessionId);
  }

  async screenshot(name) {
    const { data } = await this.send('Page.captureScreenshot', { format: 'png' }, this.sessionId);
    const path = resolve(CONFIG.screenshotDir, name);
    writeFileSync(path, Buffer.from(data, 'base64'));
    return path;
  }
}

async function main() {
  console.log('🚀 千牛生意参谋数据采集 v5\n');
  const cdp = new CDPClient();

  try {
    await cdp.connect();
    await cdp.attachToSycm();
  
    // 截图验证
    await cdp.screenshot('sycm-v5.png');
    console.log('✅ 截图完成\n');
  
    // 获取页面信息
    const title = await cdp.eval('document.title');
    const url = await cdp.eval('location.href');
    console.log(`📍 ${title}`);
    console.log(`   ${url.slice(0, 60)}...`);
  
    console.log('\n✅ 连接成功！');
  
  } catch (e) {
    console.error('❌', e.message);
  } finally {
    cdp.close();
  }
}

main();
