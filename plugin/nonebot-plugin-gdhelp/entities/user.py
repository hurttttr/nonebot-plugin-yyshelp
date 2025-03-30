"""
用户数据模型模块

包含User类和Record类，用于表示挂刀推送的用户数据
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Record:
    """
    挂刀记录类

    Attributes:
        name (str): 商品名称（复制挂刀网）
        price (float): 购买价格
        sold (float): 最高卖出价格
        time (datetime): 添加时间，默认7天后开始查询
        type (str): 添加方式，group(群聊)/private(私聊)
        group (Optional[int]): 群号，当type为group时有效
    """

    name: str
    price: float
    sold: float
    time: datetime
    type: str
    group: int = None


@dataclass
class User:
    """
    用户数据类

    Attributes:
        user (int): QQ号
        record (List[Record]): 用户的挂刀记录列表
    """

    user: int
    record: list[Record]
