"""飞猪客服KPI数据规范化（API版本）"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Any, Dict


@dataclass
class NormalizedEmployeeKpiApi:
    """规范化的员工KPI数据（API版本）"""
    biz_date: date
    employee_name: str
    show_name: str
    service_count: int  # 接待人数
    consult_count: int  # 咨询人数
    avg_first_reply_cost: float  # 平均首次响应时长
    avg_total_reply_cost: float  # 平均总响应时长
    no_reply_count: int  # 未回复人数
    slow_reception_count: int  # 慢接待人数
    shop_name: str = "default"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "biz_date": self.biz_date.isoformat(),
            "employee_name": self.employee_name,
            "show_name": self.show_name,
            "service_count": self.service_count,
            "consult_count": self.consult_count,
            "avg_first_reply_cost": self.avg_first_reply_cost,
            "avg_total_reply_cost": self.avg_total_reply_cost,
            "no_reply_count": self.no_reply_count,
            "slow_reception_count": self.slow_reception_count,
            "shop_name": self.shop_name
        }


def normalize_employee_kpi_api_data(
    api_data: Dict,
    biz_date: str,
    shop_name: str = "default"
) -> List[NormalizedEmployeeKpiApi]:
    """规范化员工KPI API数据

    Args:
        api_data: API返回的数据
        biz_date: 业务日期
        shop_name: 店铺名称

    Returns:
        List[NormalizedEmployeeKpiApi]: 规范化后的数据列表
    """
    from datetime import datetime

    parsed_date = datetime.strptime(biz_date, "%Y-%m-%d").date()

    results = []
    value_list = api_data.get('valueList', [])

    for item in value_list:
        try:
            normalized = NormalizedEmployeeKpiApi(
                biz_date=parsed_date,
                employee_name=item.get('employee_name', ''),
                show_name=item.get('show_name', ''),
                service_count=item.get('service_num', 0),
                consult_count=item.get('consult_num', 0),
                avg_first_reply_cost=float(item.get('avg_first_reply_cost', 0)),
                avg_total_reply_cost=float(item.get('avg_total_reply_cost', 0)),
                no_reply_count=item.get('no_reply_reception_num', 0),
                slow_reception_count=item.get('slow_reception_num', 0),
                shop_name=shop_name
            )

            results.append(normalized)

        except (ValueError, TypeError, KeyError) as e:
            # 跳过无效数据
            continue

    return results
