from nonebot.plugin import PluginMetadata

from . import __main__ as __main__

__plugin_meta__ = PluginMetadata(
    name="test",
    description="这是一个示例插件",
    usage="没什么用",
    type="application",
    # config=Config,
    extra={},
)
