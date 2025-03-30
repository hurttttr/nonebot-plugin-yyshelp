from __future__ import annotations

import nonebot.adapters
from nonebot import get_driver
from nonebot.plugin import PluginMetadata, require
from nonebot_plugin_saa import enable_auto_select_bot

from . import __main__ as __main__
from .entities.draw_cards import DRAW_PATH, draw_init, user_list
from .utils.config_load_save_help import save_config

require("nonebot_plugin_saa")


enable_auto_select_bot()
__plugin_meta__ = PluginMetadata(
    name="yyshelp",
    description="阴阳师助手",
    usage="没什么用",
    type="application",
    # config=Config,
    extra={},
)


async def shutdown():
    # 保存用户数据
    save_config(DRAW_PATH, user_list)
    # 输出日志
    nonebot.log.logger.info("抽卡数据保存完毕")


draw_init()

driver = get_driver()
driver.on_shutdown(shutdown)
