"""飞猪客服KPI数据规范化"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Any


@dataclass
class NormalizedEmployeeKpi:
    """规范化的员工KPI数据"""
    biz_date: date
    employee_name: str
    service_count: int  # 接待人数
    avg_response_seconds: float  # 平均响应时间(秒)
    reply_rate: float  # 回复率
    conversion_rate: float | None  # 询单->最终付款转化率
    work_days: int  # 上班天数
    satisfaction_participation_rate: float | None  # 服务满意度评价参与率
    customer_satisfaction_rate: float | None  # 客户满意率
    very_satisfied_count: int | None  # 很满意数
    satisfied_count: int | None  # 满意数
    neutral_count: int | None  # 一般数
    dissatisfied_count: int | None  # 不满意数
    very_dissatisfied_count: int | None  # 很不满意数
    shop_name: str = "default"

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "biz_date": self.biz_date.isoformat(),
            "employee_name": self.employee_name,
            "service_count": self.service_count,
            "avg_response_seconds": self.avg_response_seconds,
            "reply_rate": self.reply_rate,
            "conversion_rate": self.conversion_rate,
            "work_days": self.work_days,
            "satisfaction_participation_rate": self.satisfaction_participation_rate,
            "customer_satisfaction_rate": self.customer_satisfaction_rate,
            "very_satisfied_count": self.very_satisfied_count,
            "satisfied_count": self.satisfied_count,
            "neutral_count": self.neutral_count,
            "dissatisfied_count": self.dissatisfied_count,
            "very_dissatisfied_count": self.very_dissatisfied_count,
            "shop_name": self.shop_name
        }


def normalize_employee_kpi_data(
    raw_data: List[List[str]],
    biz_date: str,
    shop_name: str = "default"
) -> List[NormalizedEmployeeKpi]:
    """规范化员工KPI数据

    Args:
        raw_data: 原始数据（表格行数据）
        biz_date: 业务日期
        shop_name: 店铺名称

    Returns:
        List[NormalizedEmployeeKpi]: 规范化后的数据列表
    """
    from datetime import datetime

    parsed_date = datetime.strptime(biz_date, "%Y-%m-%d").date()

    results = []
    for row in raw_data:
        try:
            # 跳过空行或标题行
            if not row or len(row) < 4 or row[0] in ["", "客服昵称"]:
                continue

            # 提取数据（索引对应表格列）
            employee_name = row[0] if row[0] else "Unknown"

            # 接待人数
            service_count = int(row[1]) if row[1] and row[1].isdigit() else 0

            # 平均响应时间
            try:
                avg_response = float(row[2]) if row[2] else 0.0
            except ValueError:
                avg_response = 0.0

            # 回复率（去掉%）
            try:
                reply_rate_str = row[3].replace("%", "") if len(row) > 3 else "0"
                reply_rate = float(reply_rate_str) / 100 if reply_rate_str else 0.0
            except (ValueError, IndexError):
                reply_rate = 0.0

            # 转化率
            conversion_rate = None
            if len(row) > 4 and row[4] and row[4] not in ["延迟统计", ""]:
                try:
                    conversion_rate_str = row[4].replace("%", "")
                    conversion_rate = float(conversion_rate_str) / 100
                except ValueError:
                    pass

            # 上班天数
            work_days = 0
            if len(row) > 5 and row[5] and row[5].isdigit():
                work_days = int(row[5])

            # 满意度相关数据（索引6-12）
            satisfaction_participation_rate = None
            customer_satisfaction_rate = None
            very_satisfied = satisfied = neutral = dissatisfied = very_dissatisfied = None

            # 这里简化处理，实际需要根据"延迟统计"等标记来判断
            for i in range(6, min(13, len(row))):
                val = row[i]
                if val and val != "延迟统计":
                    # 根据列索引映射到对应字段
                    if i == 6:  # 参与率
                        try:
                            satisfaction_participation_rate = float(val.replace("%", "")) / 100
                        except ValueError:
                            pass
                    elif i == 7:  # 客户满意率
                        try:
                            customer_satisfaction_rate = float(val.replace("%", "")) / 100
                        except ValueError:
                            pass
                    elif i == 8:  # 很满意
                        try:
                            very_satisfied = int(val)
                        except ValueError:
                            pass
                    elif i == 9:  # 满意
                        try:
                            satisfied = int(val)
                        except ValueError:
                            pass
                    elif i == 10:  # 一般
                        try:
                            neutral = int(val)
                        except ValueError:
                            pass
                    elif i == 11:  # 不满意
                        try:
                            dissatisfied = int(val)
                        except ValueError:
                            pass
                    elif i == 12:  # 很不满意
                        try:
                            very_dissatisfied = int(val)
                        except ValueError:
                            pass

            normalized = NormalizedEmployeeKpi(
                biz_date=parsed_date,
                employee_name=employee_name,
                service_count=service_count,
                avg_response_seconds=avg_response,
                reply_rate=reply_rate,
                conversion_rate=conversion_rate,
                work_days=work_days,
                satisfaction_participation_rate=satisfaction_participation_rate,
                customer_satisfaction_rate=customer_satisfaction_rate,
                very_satisfied_count=very_satisfied,
                satisfied_count=satisfied,
                neutral_count=neutral,
                dissatisfied_count=dissatisfied,
                very_dissatisfied_count=very_dissatisfied,
                shop_name=shop_name
            )

            results.append(normalized)

        except (ValueError, TypeError, IndexError) as e:
            # 跳过无效数据行
            continue

    return results
