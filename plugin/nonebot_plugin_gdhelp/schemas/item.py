from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Item:
    """
    物品类
    """

    # 物品的中文名称
    zh_name: str
    # 物品的英文名称
    eng_name: str
    # 物品的名称ID
    item_nameid: int
    # 物品的价格
    price: float
