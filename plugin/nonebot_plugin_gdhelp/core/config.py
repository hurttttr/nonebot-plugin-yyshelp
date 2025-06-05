from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import List

from nonebot.log import logger
from pydantic import Field

from ..schemas import User
from .core_utils import ConfigBase
from .os_env import OSEnv

DATA_PATH = Path(OSEnv.DATA_DIR) / "gd_data.json"  # 数据路径
CONFIG_PATH = Path(OSEnv.CONFIG_DIR) / "gd_config.yaml"  # 配置路径
DATA_PATH.parent.mkdir(parents=True, exist_ok=True)  # 创建数据目录
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)  # 创建配置目录


class ControlType(Enum):
    WHITE = "white"
    BLACK = "black"


class PushConfig(ConfigBase):
    SUPER_USERS: List[str] = Field(
        default=["123456"],
        title="管理员列表",
        description="此处指定的管理员用户可登陆 WebUI, 初始密码 123456",
    )
    ENABLE_COMMAND_UNAUTHORIZED_OUTPUT: bool = Field(
        default=False, title="启用未授权命令反馈"
    )
    PUSH_ON: bool = Field(
        default=True,
        metadata={
            "title": "是否开启推送功能",
            "description": "是否开启挂刀助手的推送功能",
        },
    )
    PUSH_TIME: int = Field(
        default=8,
        metadata={
            "title": "推送时间",
            "description": "推送功能的执行时间，单位为小时",
        },
    )
    GROUP_CONTROL_TYPE: ControlType = Field(
        default=ControlType.WHITE,
        metadata={
            "title": "群控制类型",
            "description": "black黑名单，white白名单，默认白名单有需要自行修改",
        },
    )
    GROUP_ID: List[str] = Field(
        default=["123456"],
        metadata={
            "title": "群ID列表",
            "description": "需要进行推送控制的群ID列表",
        },
    )
    USER_CONTROL_TYPE: ControlType = Field(
        default=ControlType.BLACK,
        metadata={
            "title": "用户控制类型",
            "description": "black黑名单，white白名单，默认黑名单有需要自行修改",
        },
    )
    USER_ID: List[str] = Field(
        default=["123456"],
        metadata={
            "title": "用户ID列表",
            "description": "需要进行推送控制的用户ID列表",
        },
    )


def save_config():
    """保存配置"""
    global config
    config.dump_config(file_path=CONFIG_PATH)
    logger.info("[gd_help] 配置文件保存成功")


def reload_config():
    """重新加载配置"""
    global config
    new_config = PushConfig.load_config(file_path=CONFIG_PATH)
    # 更新配置字段
    for Field_name in PushConfig.model_Fields:
        value = getattr(new_config, Field_name)
        setattr(config, Field_name, value)


def load_data():
    """加载数据"""
    global data
    # 尝试加载data数据
    if DATA_PATH.exists():
        with open(DATA_PATH, encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []


def save_data():
    """保存数据"""
    global data
    # 保存data数据到指定路径,使用json保存
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info("[gd_help] 数据文件保存成功")


# 尝试加载配置
try:
    config = PushConfig.load_config(CONFIG_PATH)
    data: list[User] = []
    load_data()
except Exception as e:
    print(f"[gd_help] 配置文件加载失败: {e} | 请检查配置文件是否符合语法要求")
    print("应用将退出...")
    exit(1)
config.dump_config(file_path=CONFIG_PATH)


if __name__ == "__main__":
    # save_config()
    save_data()
