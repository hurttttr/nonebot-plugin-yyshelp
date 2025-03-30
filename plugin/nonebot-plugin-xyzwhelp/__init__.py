from __future__ import annotations

from nonebot import get_driver
from nonebot.config import Config
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from . import __main__ as __main__

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-xyzwhelp",
    description="咸鱼之王帮助",
    usage="计算宝箱周",
    config=Config,
)

global_config = get_driver().config
config = Config.parse_obj(global_config)
logger.info("nonebot-plugin-xyzwhelp加载")
