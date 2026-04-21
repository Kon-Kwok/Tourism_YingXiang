# SYCM店铺来源 - 商品来源 API文档

## API信息

**网页URL**: 
```
https://sycm.taobao.com/flow/monitor/shopsource/construction
```

**API端点**: 
```
https://sycm.taobao.com/flow/v3/shop/source/constitute/menu/v3.json
```

**验证状态**: ✅ 已验证 (2026-04-20)

## 请求参数

### 必需参数
```python
params = {
    "dateType": "day",                      # 日期类型
    "dateRange": "2026-04-19|2026-04-19",    # 日期范围
    "device": "2"                           # 设备类型
}
```

### 可选参数
```python
params = {
    "activeKey": "item",                    # 活动类型 (item=商品)
    "belong": "all"                         # 归类 (all=全部)
}
```

## 参数说明

| 参数 | 类型 | 必需 | 说明 | 可选值 |
|------|------|------|------|--------|
| dateType | string | ✅ | 日期类型 | day (日度) |
| dateRange | string | ✅ | 日期范围 | YYYY-MM-DD\|YYYY-MM-DD |
| device | string | ✅ | 设备类型 | 2=无线端, 1=PC端, 0=全部 |
| activeKey | string | ❌ | 活动类型 | item=商品 |
| belong | string | ❌ | 归类 | all=全部 |

## 响应格式

### 成功响应
```json
{
  "traceId": "213e04d017766831808627563e0deb",
  "code": 0,
  "message": "操作成功",
  "data": [
    {
      "pageName": {"value": "广告流量"},
      "uv": {"value": 5872, "ratio": 0.509},
      "statDate": {"value": "2026-04-19"},
      "pageId": {"value": 22},
      "channelType": {"value": "1"},
      "pageLevel": {"value": 1},
      "pageDesc": {"value": "..."},
      "showDesc": {"value": 2},
      "hiddenIndexgroup": {"value": "none"},
      "pPageId": {"value": "0"}
    },
    {
      "pageName": {"value": "平台流量"},
      "uv": {"value": 5664, "ratio": 0.491},
      ...
    }
  ]
}
```

### 数据字段说明

| 字段路径 | 说明 | 示例 |
|----------|------|------|
| data[].pageName.value | 来源名称 | "广告流量" |
| data[].uv.value | 访客数 | 5872 |
| data[].uv.ratio | 占比 | 0.509 (50.9%) |
| data[].statDate.value | 统计日期 | "2026-04-19" |
| data[].pageId.value | 页面ID | 22 |
| data[].channelType.value | 渠道类型 | "1" |
| data[].pageLevel.value | 页面级别 | 1 |

## 使用示例

### Python代码

```python
from tourism_automation.shared.chrome import ChromeHttpClient
from urllib.parse import urlencode

def get_shop_source_data(date: str):
    http = ChromeHttpClient.from_local_chrome()
    
    api_url = "https://sycm.taobao.com/flow/v3/shop/source/constitute/menu/v3.json"
    params = {
        "activeKey": "item",
        "belong": "all",
        "dateType": "day",
        "dateRange": f"{date}|{date}",
        "device": "2"
    }
    
    response = http.fetch_json(
        f"{api_url}?{urlencode(params)}",
        referer="https://sycm.taobao.com/flow/monitor/shopsource/construction"
    )
    
    if response['code'] == 0:
        return response['data']
    else:
        raise Exception(f"API错误: {response['message']}")
```

### 返回数据

API返回汇总级别的数据，包含2个主要来源：

1. **广告流量**: 付费广告渠道的总流量
2. **平台流量**: 平台自然流量的总和

## 数据限制

### ⚠️ 重要限制

**API返回汇总数据**：
- API只返回2个汇总来源（广告流量、平台流量）
- 页面显示44个详细来源
- 详细来源数据可能通过其他API或页面交互加载

### 数据对比

| 数据项 | API | 页面 | 说明 |
|--------|-----|------|------|
| 广告流量UV | 5,872 | 5,872 | ✅ 一致 |
| 平台流量UV | 5,664 | 5,664 | ✅ 一致 |
| 详细来源 | 不返回 | 44个 | ⚠️ API限制 |

### 获取详细数据的方法

如果需要获取页面上显示的所有44个详细来源，可能需要：

1. **页面交互**: 使用CDP模拟用户点击/滚动
2. **其他API**: 查找是否有专门的详细数据API
3. **数据导出**: 使用页面上的导出功能

## 错误处理

### 常见错误

| 错误代码 | 消息 | 原因 | 解决方法 |
|----------|------|------|----------|
| 1000 | 系统出错，未知异常 | 参数错误或权限问题 | 检查必需参数 |
| 1003 | dateType 必传 | 缺少必需参数 | 添加dateType="day" |

### 错误处理代码

```python
try:
    http = ChromeHttpClient.from_local_chrome()
    # ... API调用
except RuntimeError as e:
    if "Chrome cookie database" in str(e):
        raise Exception("请确保Chrome浏览器正在运行")
    raise
```

## 实际应用

### 采集脚本位置
- `extract_shop_source_daily_data.py` - 完整采集脚本

### 功能特性
- ✅ 单日数据提取
- ✅ 批量多日提取
- ✅ 错误处理和重试
- ✅ 数据格式标准化
- ✅ JSON输出

### 数据输出

示例输出：
```json
[
  {
    "date": "2026-04-19",
    "source_name": "广告流量",
    "uv": 5872,
    "ratio": 0.509,
    "page_id": 22,
    "channel_type": "1"
  },
  {
    "date": "2026-04-19",
    "source_name": "平台流量",
    "uv": 5664,
    "ratio": 0.491,
    "page_id": 30,
    "channel_type": "1"
  }
]
```

## 开发历程

### CDP探索阶段
1. 打开目标网页
2. 查看网络请求
3. 发现API端点: `/flow/v3/shop/source/constitute/menu/v3.json`

### 验证阶段
1. API获取数据: 2个来源
2. CDP获取数据: 44个来源
3. 数据一致性验证: ✅ 汇总数据100%一致
4. 确认限制: API只返回汇总数据

### 生产实现
1. 纯HTTP请求实现
2. 不包含CDP代码
3. 支持单日和批量采集

## 维护信息

**发现日期**: 2026-04-20
**最后验证**: 2026-04-20
**API版本**: v3
**支持平台**: SYCM (生意参谋)

## 相关文件

- API探索脚本: `test_shopsource_apis.py`
- 生产采集脚本: `extract_shop_source_daily_data.py`
- 完整响应数据: `docs/shopsource_api_full_response.json`
- 单日数据输出: `shop_source_data_2026-04-19.json`
- 批量数据输出: `shop_source_batch_data.json`
