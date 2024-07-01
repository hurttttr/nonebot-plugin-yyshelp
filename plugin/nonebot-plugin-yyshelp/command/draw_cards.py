# 抽卡相关的命令

from typing import List, Union

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PokeNotifyEvent
from nonebot.log import logger
from pydantic import BaseModel

from ..utils.config_load_save_help import load_config, save_config
from ..utils.draw_card import (
    generate_id_name_dict,
    get_or_update_icon,
    list_to_dict,
    simulate_draw,
)


class User(BaseModel):
    user_id: int
    group_id: int
    up_count: int
    draw_count: int

    def __eq__(self, other):
        # 比较全部属性
        return self.user_id == other


DRAW_PATH = r"data/draw_card/user.json"

heros_list = []
heros_dict = {}
id_name_dict = {}
heros_up_id = ""
draw_count = 0
up_count = 0
user_list: List[User] = []


def draw_init():
    logger.info("抽卡模块加载")
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list = get_or_update_icon()
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    logger.info("抽卡模块加载成功")
    if load_config(User, DRAW_PATH, user_list):
        logger.info("加载用户数据成功")
    else:
        logger.info("加载用户数据失败")


draw = on_command("抽卡", block=True)


@draw.handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断群号是否在黑名单中
    if event.get_type() == "group" and event.group_id in [12345678, 987654321]:
        return
    # 判读是否存在抽卡记录
    if event.user_id in user_list:
        user = user_list[user_list.index(event.user_id)]
    else:
        user = User(
            user_id=event.user_id, group_id=event.group_id, up_count=0, draw_count=0
        )
        user_list.append(user)

    result, user.up_count = simulate_draw(
        heros_dict, heros_up_id, user.up_count, user.draw_count
    )
    user.draw_count += 10
    # 将结果转换为字符串
    result_str = ""
    for hero_id in result:
        hero_name = id_name_dict[hero_id]
        result_str += f"{hero_name} "

    # 发送结果
    await draw.send(
        f"{user.up_count}/60 内必出ssr/sp 当前累计抽卡{user.draw_count}次\n抽卡结果：\n{result_str}"
    )
