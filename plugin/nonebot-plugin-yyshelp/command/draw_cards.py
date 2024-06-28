# 抽卡相关的命令

from typing import List, Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PokeNotifyEvent
from nonebot.log import logger

from ..utils.draw_card import (
    generate_id_name_dict,
    get_or_update_icon,
    list_to_dict,
    simulate_draw,
)

logger.info("抽卡模块加载")
heros_list = get_or_update_icon()
heros_dict = list_to_dict(heros_list)
id_name_dict = generate_id_name_dict(heros_list)
heros_up_id = "315"
draw_count = 440
up_count = 50
logger.info("抽卡模块加载成功")

draw = on_command("抽卡", block=True)


@draw.handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断群号是否在黑名单中
    if event.group_id in [12345678, 987654321]:
        return
    # 随机抽取一张卡片
    result, up_count = simulate_draw(heros_dict, heros_up_id, up_count, draw_count)
    # 将结果转换为字符串
    result_str = ""
    for hero_id in result:
        hero_name = id_name_dict[hero_id]
        result_str += f"{hero_name} "

    # 发送结果
    await draw.send(f"{up_count}/60内必出ssr/sp\n抽卡结果：{result_str}")
