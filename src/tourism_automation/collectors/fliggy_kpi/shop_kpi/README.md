# 店铺KPI导出器

通过CDP自动化店铺KPI数据导出流程。

## 功能特性

- ✅ 自动点击导出按钮
- ✅ 自动输入密码
- ✅ 自动点击确认按钮
- ✅ 支持按报表名称切换
- ✅ 支持 `day/week/month` 时间模式
- ✅ `day` 模式可传日期，默认前一天
- ✅ 返回真实下载文件路径
- ✅ 支持直接转统一 `summary + rows` JSON
- ✅ CLI命令接口

## 前置条件

1. **Chrome调试窗口运行**
   ```bash
   ./bin/start-chrome-unified.sh
   ```

2. **店铺KPI页面已打开**
   ```
   https://kf.topchitu.com/web/custom-kpi/employee-kpi?id=1721&wwt=ALL
   ```

## 使用方法

### CLI命令

```bash
# 导出人均日接入
python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 人均日接入 \
  --date-mode day \
  --date 2026-04-20

# 导出每周店铺个人数据
python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 每周店铺个人数据 \
  --date-mode day \
  --date 2026-04-20

# 导出客服数据23年新
python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 客服数据23年新 \
  --date-mode day \
  --date 2026-04-20

# 导出后直接转 JSON
python3 -m tourism_automation.cli.main shop-kpi-export \
  --report-name 人均日接入 \
  --date-mode day \
  --date 2026-04-20 \
  --json

# 一次导出全部 3 张表
python3 -m tourism_automation.cli.main shop-kpi-export-batch \
  --date-mode day \
  --date 2026-04-20
```

### 测试脚本

```bash
./bin/test_shop_kpi_export.py
```

### Python代码

```python
from tourism_automation.collectors.fliggy_kpi.shop_kpi.exporter import export_shop_kpi

# 导出数据
output_file = export_shop_kpi(
    report_name="人均日接入",
    date_mode="day",
    date=None,
    output_file=None,
)

print(f"文件已保存到: {output_file}")
```

`shop-kpi-export` 普通模式返回的 `output_file` 是浏览器真实下载落地路径，例如 `/home/kk/下载/...xlsx`，不再是占位路径。

如果加 `--json`，命令会先导出 Excel，再直接输出：

```json
{
  "summary": {
    "source": "shop_kpi_excel",
    "report_name": "人均日接入",
    "file_path": "/home/kk/下载/xxx.xlsx",
    "row_count": 14
  },
  "rows": []
}
```

## 文件结构

```
shop_kpi/
├── exporter.py        # 导出器核心逻辑
├── cli.py             # CLI命令接口
└── README.md          # 本文件
```

## 核心类

### ShopKpiExporter

```python
class ShopKpiExporter:
    def __init__(self, cdp_client: CdpClient | None = None, download_dir: str = "/tmp/downloads"):
        """初始化导出器

        Args:
            cdp_client: CDP客户端
            download_dir: 下载目录
        """

    def export_shop_kpi(
        self,
        output_file: Optional[str] = None,
        report_name: str = "人均日接入",
        date_mode: str = "day",
        date: Optional[str] = None,
    ) -> str:
        """导出店铺KPI数据

        Args:
            output_file: 输出文件路径（可选）
            report_name: 报表名称
            date_mode: 日期模式，支持 day/week/month；日报采集必须使用 day
            date: day 模式的日期，格式 YYYY-MM-DD，不传默认前一天

        Returns:
            str: 下载文件的路径
        """
```

## 选择器信息

| 元素 | CSS选择器 |
|------|-----------|
| 导出按钮 | `button.download___7ocOy` |
| 密码弹窗 | `#root > section > section > main > div:nth-child(2) > div > div.formContainer___3uYye` |
| 密码输入框 | `#password > span.inputWrapper___1eYh- > span > input` / 回退选择器 |
| 确认按钮 | 按按钮文案 `确定` |

## 工作流程

1. **查找页面**: 通过CDP找到店铺KPI标签页
2. **切换报表**: 按报表文案点击目标项
3. **设置时间**: 切换日/周/月模式，`day` 时选择日期
4. **点击查询**: 刷新报表数据
5. **点击导出**: 使用多种选择器尝试点击导出按钮
6. **等待弹窗**: 检查密码弹窗是否出现
7. **输入密码**: 在密码输入框中输入1234
8. **点击确认**: 点击确认按钮提交密码
9. **等待下载**: 等待真实下载文件落地
10. **可选转 JSON**: `--json` 时把 Excel 转成统一 `summary + rows`

## 故障排查

### 问题1: 无法连接到Chrome调试端口

**解决**:
```bash
./bin/start-chrome-unified.sh
```

### 问题2: 未找到店铺KPI页面

**解决**: 在Chrome中打开店铺KPI页面

### 问题3: 无法点击导出按钮

**解决**:
1. 使用Chrome DevTools检查按钮选择器
2. 更新 `exporter.py` 中的选择器
3. 运行测试脚本查看详细日志

## 相关文档

- [店铺KPI导出功能使用指南](../../../docs/collectors/shop_kpi_export_guide.md)
- [飞猪KPI采集器实现文档](../../../docs/implementation/fliggy_kpi_implementation.md)
