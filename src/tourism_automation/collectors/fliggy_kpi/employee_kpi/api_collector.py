"""飞猪客服KPI采集器（基于API）"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import json

from tourism_automation.collectors.fliggy_kpi.employee_kpi.api_client import EmployeeKpiApiClient
from tourism_automation.collectors.fliggy_kpi.employee_kpi.normalize_api import normalize_employee_kpi_api_data


@dataclass
class EmployeeKpiApiCollector:
    """员工KPI数据采集器（使用API）"""

    def collect(
        self,
        biz_date: str,
        shop_name: str = "default",
        kpi_id: str = "1721",
        wwt: str = "ALL"
    ) -> Dict[str, object]:
        """采集员工KPI数据（使用API）

        Args:
            biz_date: 业务日期，格式 "2026-04-19"
            shop_name: 店铺名称
            kpi_id: KPI模板ID
            wwt: 时间范围类型

        Returns:
            Dict: 包含summary和metrics的字典
        """
        client = EmployeeKpiApiClient()

        # 获取API数据
        api_data = client.get_employee_rank(biz_date)

        # 规范化数据
        normalized_data = normalize_employee_kpi_api_data(
            api_data,
            biz_date,
            shop_name
        )

        return {
            "summary": {
                "metric_source": "api_fetch",
                "shop_name": shop_name,
                "page_code": "employee_kpi",
                "collection_date": biz_date,
                "kpi_id": kpi_id,
                "employee_count": len(normalized_data)
            },
            "metrics": [item.to_dict() for item in normalized_data],
            "raw_api_data": api_data
        }
