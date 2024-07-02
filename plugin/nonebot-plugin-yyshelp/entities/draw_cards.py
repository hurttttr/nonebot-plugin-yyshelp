# 抽卡相关的命令

from turtle import update
from typing import List, Union

from nonebot import on, on_command
from nonebot.adapters.onebot.v11 import Bot, MessageEvent, PokeNotifyEvent
from nonebot.log import logger
from nonebot_plugin_saa import (Text)
from pydantic import BaseModel
from ..classes.draw_card_class import DrawCardUser, Heros
from ..config import yyshelp_config

from ..utils.config_load_save_help import load_config, save_config
from ..utils.draw_card import (
    generate_id_name_dict,
    get_or_update_icon,
    list_to_dict,
    simulate_draw,
)


DRAW_PATH = r"data/draw_card/user.json"

heros_list: List[Heros] = []
heros_dict = {}
id_name_dict = {}
heros_up_id = "569"
draw_count = 0
up_count = 0
user_list: List[DrawCardUser] = []


def draw_init():
    logger.info("抽卡模块加载")
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list, update_text = get_or_update_icon()
    if len(heros_list) == 0:
        logger.info("无式神更新")
    else:
        logger.info(f"更新式神\n{update_text}")
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    logger.info("抽卡模块加载成功")
    if load_config(DrawCardUser, DRAW_PATH, user_list):
        logger.info("加载用户数据成功")
    else:
        logger.info("加载用户数据失败")


draw = on_command("抽卡", block=True)


@draw.handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断群号是否在黑名单中
    if event.get_type() == "group" and event.group_id in [12345678, 987654321]:
        return
    # 判断是否存在抽卡记录
    if event.user_id in user_list:
        user = user_list[user_list.index(event.user_id)]
    else:
        user = DrawCardUser(
            user_id=event.user_id, group_id=event.group_id, up_count=0, draw_count=0
        )
        user_list.append(user)

    result = simulate_draw(
        heros_dict, yyshelp_config.draw_card_up_id, user)
    user.draw_count += 10
    # 将结果转换为字符串
    result_str = ""
    for hero_id in result:
        hero_name = id_name_dict[hero_id][0]
        hero_rarity = id_name_dict[hero_id][1]
        result_str += f"{hero_rarity}:{hero_name} "

    if user.get_up_count > 0:
        send_text = f"""当期up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n{
            user.up_count}/60 内必出ssr/sp up已结束\n抽卡结果：\n{result_str}\n当前累计抽卡{user.draw_count}次"""
    else:
        send_text = f"""当期up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n{user.up_count}/60 内必出ssr/sp up概率：{10 + (
            (user.draw_count-10)//50)*10}\n抽卡结果：\n{result_str}\n当前累计抽卡{user.draw_count}次"""

    # 发送结果
    await draw.send(send_text)


@on_command("抽卡帮助", block=True).handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    await Text("""抽卡帮助：
1. 发送“抽卡”命令，即可进行十连抽卡。         
2. 累计抽卡次数达到60次后，必得ssr/sp。
3. 当期up初始概率为10%，每抽50次增加10%概率，抽出后概率加成消失。
4. 每次抽卡up维持12天
5. 依照官方公布概率 r:78.25% sr:10% ssr:1% sp:0.25%""").send()


@on_command("抽卡记录", block=True).handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断是否存在抽卡记录
    if event.user_id in user_list:
        user = user_list[user_list.index(event.user_id)]
        if user.get_up_count > 0:
            send_text = f"""抽卡记录：\n当前累计抽卡{
                user.draw_count}次\n本期up{user.up_count}次抽出"""
        else:
            send_text = f"""抽卡记录：\n当前累计抽卡{user.draw_count}次\本期up尚未抽出"""
    else:
        send_text = "您还没有抽卡记录"
    # 发送结果
    await Text(send_text).send()


@on_command("抽卡更新", block=True).handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list, update_text = get_or_update_icon()
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    if len(heros_list) == 0:
        await Text("无式神更新").send()
    else:
        heros_list.sort(key=lambda x: x.heroid, reverse=True)
        yyshelp_config.draw_card_up_id = heros_list[0].heroid
        await Text(f"更新式神\n{update_text}\n当前up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}").send()
