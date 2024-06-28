from nonebot.plugin import PluginMetadata, require

require("nonebot_plugin_saa")

from nonebot_plugin_saa import enable_auto_select_bot

from . import __main__ as __main__

enable_auto_select_bot()
__plugin_meta__ = PluginMetadata(
    name="yyshelp",
    description="阴阳师助手",
    usage="没什么用",
    type="application",
    # config=Config,
    extra={},
)
