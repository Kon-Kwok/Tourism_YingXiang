# 飞猪商家工作台首页采集设计

## 目标

为 `https://fsc.fliggy.com/#/new/home` 新增一个与 `sycm/` 并列的首页采集器，默认复用本机 Chrome 登录态，通过 HTTP 直接请求页面已使用的业务接口，输出结构化 JSON。

第一版只覆盖 5 个首页模块：

- 服务待办
- 经营中心
- 商品运营中心
- 商家成长
- 规则中心

## 结构设计

项目结构按并列采集器组织：

- `sycm/`：生意参谋采集器
- `fliggy_home/`：飞猪商家工作台首页采集器
- 共享能力：Chrome 登录态读取和 HTTP 请求能力

`fliggy_home` 不依赖 CDP，不依赖当前已打开标签页，只要求本机 Chrome 保持登录态。

## 命令入口

新增命令：

```bash
python3 -m fliggy_home.cli collect-home
```

默认行为：

- 自动读取本机 Chrome 登录态
- 自动请求 5 个模块对应接口
- 输出结构化 JSON
- 不入库，不写文件

## 接口映射

### 服务待办

- `https://fsc.fliggy.com/api/home/getTodoData`
- `https://fsc.fliggy.com/api/message/todomessages`

归一化字段：
- 待处理预警
- 待处理违规
- 电子凭证待确认
- 活动邀约
- 待回复差评
- 其他待办列表

### 经营中心

- `https://seller.fliggy.com/api/sycm/measure/front/tradeMeasure`
- `https://seller.fliggy.com/api/sycm/measure/front/graphMeasure`
- `https://seller.fliggy.com/api/sycm/measure/industry`

归一化字段：
- 统计日期
- 总支付金额
- 支付金额较前 1 日
- 支付金额趋势
- 邮轮支付金额
- 履约金额
- 行业/同行对比摘要

### 商品运营中心

- `https://fsc.fliggy.com/api/home/shopBlock`
- `https://sell.fliggy.com/icenter/itemability/ItemAbilityTotalPage.htm`
- `https://sell.fliggy.com/icenter/mci/ajx/GetDestPreferInfo.json`

归一化字段：
- 渠道名
- 潜力商品数
- 近 30 天访问人数
- 近 30 天成交人数
- 同行优秀对比
- 渠道说明和要求

### 商家成长

- `https://sell.fliggy.com/icenter/mci/ajx/GetNewMciInfo.json`
- `https://mci.fliggy.com/seller/service/homeMciIndex`
- `https://seller.fliggy.com/api/sycm/measure/queryOperatorCenter`
- `https://seller.fliggy.com/api/sycm/measure/queryExcellent`

归一化字段：
- 商品力
- MCI
- 同行均值
- 提升任务数
- 任务标题
- 任务说明
- 跳转 key 或业务标识

### 规则中心

- `https://seller.fliggy.com/api/blocks/ruleCenter`

归一化字段：
- 分类
- 标题
- 发布时间
- 是否最新
- 列表顺序

## 输出结构

返回结构固定为：

```json
{
  "summary": {},
  "service_todos": {},
  "business_center": {},
  "product_operation_center": {},
  "merchant_growth": {},
  "rule_center": {},
  "errors": []
}
```

每个模块统一包含：

- `status`
- `raw`
- `normalized`
- `fetched_at`

## 失败处理

- 单个模块失败不影响其他模块
- 模块失败时返回 `status: error`
- 失败信息至少包含 `message`、`endpoint`、`http_status`
- 只有 Chrome 登录态不可读，或 5 个模块全部失败时，命令整体退出非 0

## 验收标准

- Chrome 已登录时，命令返回 JSON，`summary.source = chrome_cookie_http`
- 部分模块失败时，命令仍返回成功结果和模块级错误
- 登录态失效时，命令返回明确的认证错误
- 单元测试覆盖 Cookie 解密、模块归一化、结果汇总、部分失败场景
