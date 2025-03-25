from nonebot import get_driver
from nonebot.config import Config
from nonebot.log import logger
from nonebot.plugin import PluginMetadata

from . import __main__ as __main__

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-gdhhelp",
    description="挂刀助手",
    usage="",
    config=Config,
)

# global_config = get_driver().config
# config = Config.parse_obj(global_config)
# logger.info("nonebot-plugin-xyzwhelp加载")
