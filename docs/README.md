# 文档说明

`docs/` 只保留对开发、运维和功能扩展有直接指导意义的内容。阶段性汇报、一次性分析结果和测试样本不再保留。

## 建议阅读顺序

1. [architecture/project-structure.md](architecture/project-structure.md)：了解目录结构、模块边界和 CLI 入口。
2. [collectors/unified_chrome_guide.md](collectors/unified_chrome_guide.md)：准备统一 Chrome 调试会话。
3. 按目标功能阅读对应采集器文档：
   - [collectors/sycm.md](collectors/sycm.md)
   - [collectors/sycm_multi_page.md](collectors/sycm_multi_page.md)
   - [collectors/fliggy-home.md](collectors/fliggy-home.md)
   - [collectors/fliggy_kpi_usage.md](collectors/fliggy_kpi_usage.md)
   - [collectors/shop_kpi_export_guide.md](collectors/shop_kpi_export_guide.md)

## 保留的参考文档

- [sycm_shop_source_api.md](sycm_shop_source_api.md)：SYCM 店铺来源接口参数和响应格式。
- [implementation/fliggy_kpi_implementation.md](implementation/fliggy_kpi_implementation.md)：飞猪 KPI 采集实现背景和代码路径。

## 维护原则

- 优先保留“怎么运行、怎么排查、怎么扩展”。
- 重复内容合并到单一文档，不保留平行摘要。
- 临时分析结果和导出的原始样本不进入长期文档集合。
