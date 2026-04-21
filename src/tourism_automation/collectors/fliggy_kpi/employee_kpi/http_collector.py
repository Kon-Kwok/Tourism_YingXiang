"""飞猪客服KPI采集器（纯HTTP方式）"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from tourism_automation.collectors.fliggy_kpi.employee_kpi.http_client import EmployeeKpiHttpClient
from tourism_automation.collectors.fliggy_kpi.employee_kpi.normalize_api import normalize_employee_kpi_api_data


@dataclass
class EmployeeKpiHttpCollector:
    """员工KPI数据采集器（纯HTTP方式）"""

    def __init__(self):
        self.client = EmployeeKpiHttpClient()

    def collect(
        self,
        biz_date: str,
        shop_name: str = "default",
        kpi_id: str = "1721",
        wwt: str = "ALL"
    ) -> Dict[str, object]:
        """采集员工KPI数据（纯HTTP方式）

        Args:
            biz_date: 业务日期，格式 "2026-04-19"
            shop_name: 店铺名称
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Dict: 包含summary和metrics的字典
        """
        # 获取API数据（纯HTTP）
        try:
            api_data = self.client.get_employee_rank(biz_date)
        except Exception as e:
            # 如果失败，尝试刷新认证信息后重试
            print(f"首次请求失败: {e}，尝试刷新认证信息...")
            self.client.refresh_auth()
            api_data = self.client.get_employee_rank(biz_date)

        # 规范化数据
        normalized_data = normalize_employee_kpi_api_data(
            api_data,
            biz_date,
            shop_name
        )

        return {
            "summary": {
                "metric_source": "http_api",  # 标记为纯HTTP方式
                "shop_name": shop_name,
                "page_code": "employee_kpi",
                "collection_date": biz_date,
                "kpi_id": kpi_id,
                "employee_count": len(normalized_data)
            },
            "metrics": [item.to_dict() for item in normalized_data],
            "raw_api_data": api_data
        }
