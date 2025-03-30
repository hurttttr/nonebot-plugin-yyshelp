from __future__ import annotations

from pathlib import Path

from nonebot.log import logger
from pushcontrol import (
    GdConfig,
    PushControl,
    PushControlGroup,
    PushControlUser,
)
from utils import load_config, save_config

DATA = Path.cwd() / "data"
CONFIG = Path.cwd() / "config"
DATA_PATH = DATA / "gd.json"  # 数据路径
CONFIG_PATH = CONFIG / "gd.yaml"  # 配置路径


# 初始化函数
def init() -> GdConfig:
    """
    初始化函数，用于初始化插件数据
    """
    # 配置目录不存在自动创建
    if not DATA.exists():
        DATA.mkdir(parents=True)
    if not CONFIG.exists():
        CONFIG.mkdir(parents=True)

    # 检查配置文件是否存在，不存在则创建
    if not CONFIG_PATH.exists():
        temp = GdConfig(
            push_control=PushControl(
                group=PushControlGroup(type="white", group_id=[]),
                user=PushControlUser(user_id=[]),
            )
        )
        CONFIG_PATH.write_text(temp, encoding="utf-8")
    # 读取配置文件
    temp_list = []
    if load_config(GdConfig, CONFIG_PATH, temp_list):
        logger.log("INFO", "挂刀助手配置文件读取成功")
        return temp_list[0]
    else:
        logger.log("ERROR", "挂刀助手配置文件读取失败,使用默认配置文件")
        return GdConfig(
            push_control=PushControl(
                group=PushControlGroup(type="white", group_id=[]),
                user=PushControlUser(user_id=[]),
            )
        )
