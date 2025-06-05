from __future__ import annotations

import nonebot
from nonebot.config import Config
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from .core.config import save_config

nonebot.load_plugins("plugins")

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-gdhhelp",
    description="挂刀助手",
    usage="",
    config=Config,
)


async def shutdown():
    """
    关闭调用的函数，用于保存配置文件
    """
    save_config()
    logger.info("nonebot-plugin-gdhhelp 配置已成功保存")
