from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class PushControlGroup:
    """
    群组推送控制配置

    Attributes:
        type: str - 控制类型，"white"表示白名单模式，"black"表示黑名单模式
        group_id: list[int] - 群号列表，根据type决定是允许推送的群还是禁止推送的群
    """

    type: str  # "white" or "black"
    group_id: list[int]


@dataclass
class PushControlUser:
    """
    用户推送控制配置

    Attributes:
        user_id: list[int] - 允许接收推送的用户QQ号列表
    """

    user_id: list[int]


@dataclass
class PushControl:
    """
    推送控制配置

    Attributes:
        group: PushControlGroup - 群组推送控制配置
        user: PushControlUser - 用户推送控制配置
    """

    group: PushControlGroup
    user: PushControlUser


@dataclass
class GdConfig:
    """
    挂刀插件主配置

    Attributes:
        push_on: bool - 是否开启推送功能
        push_time: int - 推送时间(小时制，0-23)
        push_control: PushControl - 推送控制配置
    """

    push_on: bool = True
    push_time: int = 8
    push_control: PushControl
