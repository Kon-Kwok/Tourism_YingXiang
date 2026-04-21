# 店铺KPI导出器

通过CDP自动化店铺KPI数据导出流程。

## 功能特性

- ✅ 自动点击导出按钮
- ✅ 自动输入密码
- ✅ 自动点击确认按钮
- ✅ 启动文件下载
- ✅ CLI命令接口

## 前置条件

1. **Chrome调试窗口运行**
   ```bash
   ./bin/start-chrome-unified.sh
   ```

2. **店铺KPI页面已打开**
   ```
   https://kf.topchitu.com/web/custom-kpi/shop-kpi?id=941
   ```

## 使用方法

### CLI命令

```bash
# 基本使用
python3 -m tourism_automation.cli.main shop-kpi-export

# 自定义输出文件
python3 -m tourism_automation.cli.main shop-kpi-export \
  --output /path/to/export.xlsx

# 自定义密码
python3 -m tourism_automation.cli.main shop-kpi-export \
  --password 5678
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
    password="1234",
    output_file=None  # 自动生成文件名
)

print(f"文件已保存到: {output_file}")
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
    def __init__(self, debug_port: int = 9222, download_dir: str = "/tmp/downloads"):
        """初始化导出器

        Args:
            debug_port: Chrome调试端口
            download_dir: 下载目录
        """

    def export_shop_kpi(self, password: str = "1234", output_file: Optional[str] = None) -> str:
        """导出店铺KPI数据

        Args:
            password: 导出密码
            output_file: 输出文件路径（可选）

        Returns:
            str: 下载文件的路径
        """
```

## 选择器信息

| 元素 | CSS选择器 |
|------|-----------|
| 导出按钮 | `button.download___7ocOy` |
| 密码弹窗 | `#root > section > section > main > div:nth-child(2) > div > div.formContainer___3uYye` |
| 密码输入框 | `input[type="password"]` |
| 确认按钮 | `button.ant-btn-primary` |

## 工作流程

1. **查找页面**: 通过CDP找到店铺KPI标签页
2. **点击导出**: 使用多种选择器尝试点击导出按钮
3. **等待弹窗**: 检查密码弹窗是否出现
4. **输入密码**: 在密码输入框中输入1234
5. **点击确认**: 点击确认按钮提交密码
6. **等待下载**: 等待浏览器开始下载文件

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
