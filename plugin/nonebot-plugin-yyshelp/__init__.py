from nonebot.plugin import PluginMetadata
from nonebot import require

require("nonebot_plugin_saa")

from . import __main__ as __main__
from nonebot_plugin_saa import enable_auto_select_bot

enable_auto_select_bot()
__plugin_meta__ = PluginMetadata(
    name="yyshelp",
    description="阴阳师助手",
    usage="没什么用",
    type="application",
    # config=Config,
    extra={},
)
