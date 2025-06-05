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
    group: int

    def __str__(self):
        return f"商品名称：{self.name} 购买价格：{self.price}\n最高卖出价格： {self.sold}\n添加时间：{self.time}\n添加方式：{self.type} {self.group}\n"


@dataclass
class User:
    """
    用户数据类

    Attributes:
        user (str): QQ号
        record (List[Record]): 用户的挂刀记录列表
    """

    user: str
    record: list[Record]

    def add_record(self, record: Record) -> None:
        """
        添加挂刀记录
        Args:
            record (Record): 挂刀记录
        """
        # 遍历recorde列表，如果有相同的记录，则不添加
        for r in self.record:
            if r.name == record.name and r.price == record.price:
                return
        self.record.append(record)
