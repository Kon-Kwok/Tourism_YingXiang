"""SYCM店铺来源数据规范化"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, List, Any


@dataclass
class NormalizedShopSource:
    """规范化的店铺来源数据"""
    biz_date: date
    page_code: str
    source_name: str
    uv: int
    uv_ratio: float | None
    page_id: int | None
    channel_type: str | None
    shop_name: str

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "biz_date": self.biz_date.isoformat(),
            "page_code": self.page_code,
            "source_name": self.source_name,
            "uv": self.uv,
            "uv_ratio": self.uv_ratio,
            "page_id": self.page_id,
            "channel_type": self.channel_type,
            "shop_name": self.shop_name
        }


def normalize_shop_source_data(
    raw_data: List[Dict],
    biz_date: str,
    shop_name: str = "default"
) -> List[NormalizedShopSource]:
    """规范化店铺来源数据

    Args:
        raw_data: API返回的原始数据
        biz_date: 业务日期
        shop_name: 店铺名称

    Returns:
        List[NormalizedShopSource]: 规范化后的数据列表
    """
    from datetime import datetime

    parsed_date = datetime.strptime(biz_date, "%Y-%m-%d").date()

    results = []
    for item in raw_data:
        try:
            # 提取字段
            page_name_obj = item.get('pageName', {})
            source_name = page_name_obj.get('value', 'Unknown') if isinstance(page_name_obj, dict) else str(page_name_obj)

            uv_obj = item.get('uv', {})
            if isinstance(uv_obj, dict):
                uv = uv_obj.get('value', 0)
                ratio = uv_obj.get('ratio')
            else:
                uv = uv_obj if isinstance(uv_obj, (int, float)) else 0
                ratio = None

            # 转换UV为整数
            if isinstance(uv, float):
                uv = int(uv)

            # 提取其他字段
            page_id_obj = item.get('pageId', {})
            page_id = page_id_obj.get('value')
            if page_id and isinstance(page_id, str) and page_id.isdigit():
                page_id = int(page_id)

            channel_type_obj = item.get('channelType', {})
            channel_type = channel_type_obj.get('value')
            if channel_type and isinstance(channel_type, str):
                channel_type = str(channel_type)

            normalized = NormalizedShopSource(
                biz_date=parsed_date,
                page_code="shop_source_item",  # 商品来源
                source_name=source_name,
                uv=uv,
                uv_ratio=float(ratio) if ratio else None,
                page_id=page_id,
                channel_type=channel_type,
                shop_name=shop_name
            )

            results.append(normalized)

        except (ValueError, TypeError, KeyError) as e:
            # 跳过无效数据
            continue

    return results
