# 飞猪订单列表 HTTP 采集器设计

## 目标

为飞猪订单管理页新增一个纯 `HTTP + Cookie` 的订单列表采集器。CDP 只用于前期定位真实请求和返回结构，运行时采集不能依赖 CDP。

## 范围

第一版只支持当前已经在浏览器中验证通过的请求形态：

- `POST https://sell.fliggy.com/orderlist/ajax/orderList.htm?_input_charset=UTF-8&_output_charset=UTF-8`
- `multipart/form-data`
- 表单字段：
  - `_tb_token_`
  - `bizType`
  - `sortFieldEnum`
  - `pageNum`
  - `pageSize`

当前版本只需要返回解析后的 `result.orderList`，以及分页相关字段，例如 `total`、`totalPage`。

## 设计

### 1. 扩展共享 Chrome HTTP 会话

修改 [src/tourism_automation/shared/chrome/session.py](/home/kk/Tourism_YingXiang/src/tourism_automation/shared/chrome/session.py)，把当前只面向 SYCM 的 cookie 加载逻辑改成“按域名集合加载”。共享会话至少要覆盖：

- `sell.fliggy.com`
- `.fliggy.com`
- `fsc.fliggy.com`
- `seller.fliggy.com`
- `.taobao.com`

这样既不影响现有 HTTP 采集器，也能让新订单采集器复用同一套登录态能力。

### 2. 新增订单列表采集器模块

在 `src/tourism_automation/collectors/fliggy_order_list/` 下新增一个采集器包，沿用现有 collector 模式：

- `client.py`：发送 multipart POST 请求，解析顶层 JSON 响应
- `collector.py`：组织请求与返回结果
- `normalize.py`：整理 `result.orderList` 和分页信息，便于 CLI 输出
- `cli.py`：注册新命令
- `__init__.py`

### 3. CLI 入口

新增最小命令：

```bash
python3 -m tourism_automation.cli.main fliggy-order-list list --page-num 1 --page-size 10
```

首批参数：

- `--page-num`
- `--page-size`
- `--biz-type`，默认 `0`
- `--sort-field-enum`，默认 `ORDER_CREATE_TIME_DESC`

`_tb_token_` 不从命令行传入，而是在运行时从共享 cookie 会话中自动读取。

## 数据流

1. 构建共享的 Chrome 登录态 HTTP 会话。
2. 从 cookie 中读取 `_tb_token_`。
3. 发送 `multipart/form-data` POST 请求。
4. 解析以 `text/html` 返回的 JSON 字符串。
5. 输出 `result.orderList`、`total`、`totalPage` 和 `requestParams`。

## 错误处理

- 如果 Chrome cookie 数据库不存在，要明确报错。
- 如果读取不到 `_tb_token_`，要明确报错。
- 如果接口返回登录页 HTML，要识别为认证失败。
- 如果响应不是合法 JSON，要在错误中附带一小段响应预览。

## 测试

补充以下单元测试：

- 共享会话层的 cookie 域名扩展测试
- “以 HTML 返回 JSON” 的订单列表响应解析测试
- `fliggy-order-list list` 的 CLI 参数接线测试

## 明确不做

当前设计暂不包含：

- 高级筛选条件
- 日期范围查询
- 数据库存储
- 批量翻页导出

先把基础分页列表采集跑稳，再扩展这些能力。
