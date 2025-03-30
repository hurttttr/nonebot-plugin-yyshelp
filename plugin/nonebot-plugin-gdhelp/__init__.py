from __future__ import annotations

from config import GdConfig
from config import init as config_init
from nonebot import get_driver
from nonebot.config import Config
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from . import __main__ as __main__
from .utils.config_load_save_help import save_config

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-gdhhelp",
    description="挂刀助手",
    usage="",
    config=Config,
)

config: GdConfig = config_init()


async def shutdown():
    """
    关闭调用的函数，用于保存配置文件
    """


# global_config = get_driver().config
# config = Config.parse_obj(global_config)
# logger.info("nonebot-plugin-xyzwhelp加载")
