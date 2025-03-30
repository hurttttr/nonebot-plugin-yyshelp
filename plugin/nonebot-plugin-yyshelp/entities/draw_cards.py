# 抽卡相关的命令
from __future__ import annotations

import os
from typing import List, Union

from nonebot import get_bot, get_driver, on_command
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import (
    Bot,
    Event,
    MessageEvent,
    PokeNotifyEvent,
)
from nonebot.log import logger
from nonebot.params import CommandArg
from nonebot.permission import SUPERUSER
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_saa import Image, MessageFactory, TargetQQPrivate, Text

from ..classes.draw_card_class import DrawCardUser, Heros
from ..config import CONFIG_PATH, yyshelp_config
from ..utils.config_load_save_help import load_config, save_config
from ..utils.draw_card import (
    generate_binary_image,
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


async def is_group_blacklisted(event: Event) -> bool:
    """
    黑名单功能，判断群号是否在黑名单中
    """
    if (
        event.get_type() == "group"
        and event.group_id in yyshelp_config.draw_card_black_groups
    ):
        return False
    return True


def draw_init():
    logger.info("抽卡模块加载")
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list, update_text = get_or_update_icon()
    if len(update_text) == 0:
        logger.info("无式神更新")
    else:
        logger.info(f"更新式神\n{update_text}")
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    logger.info("抽卡模块加载成功")
    # 判断用户数据文件是否存在，不存在创建,
    if not os.path.exists(DRAW_PATH):
        save_config(
            DRAW_PATH,
            [
                DrawCardUser(
                    user_id=12345678,
                    group_id=12345678,
                    up_count=0,
                    draw_count=0,
                ),
            ],
        )
        logger.info("创建用户数据文件")
        user_list = []
    elif load_config(DrawCardUser, DRAW_PATH, user_list):
        logger.info("加载用户数据成功")
    else:
        logger.info("加载用户数据失败，建议删除文件后重启")


draw = on_command("抽卡", rule=is_group_blacklisted, block=True)


@draw.handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断群号是否在黑名单中
    if event.get_type() == "group":
        return
    # 判断是否存在抽卡记录
    if event.user_id in user_list:
        user = user_list[user_list.index(event.user_id)]
    else:
        user = DrawCardUser(
            user_id=event.user_id,
            group_id=event.group_id,
            up_count=0,
            draw_count=0,
        )
        user_list.append(user)

    result = simulate_draw(heros_dict, yyshelp_config.draw_card_up_id, user)
    user.draw_count += 10
    # 将结果转换为图片
    result_image = generate_binary_image(result, id_name_dict)
    if user.get_up_count > 0:
        send_text = f"当期up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n{user.up_count}/60 内必出ssr/sp up已结束\n当前累计抽卡{user.draw_count}次\n抽卡结果：\n"

    else:
        send_text = f"当期up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n{user.up_count}/60 内必出ssr/sp up概率：{10 + ((user.draw_count-10)//50)*10}\n当前累计抽卡{user.draw_count}次\n抽卡结果：\n"

    # 发送结果,并@发送者
    await MessageFactory([Text(send_text), Image(result_image)]).finish(at_sender=True)


@on_command("抽卡帮助", rule=is_group_blacklisted, block=True).handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    await Text(
        """抽卡帮助：
1. 发送“抽卡”命令，即可进行十连抽卡。
2. 累计抽卡次数达到60次后，必得ssr/sp。
3. 当期up初始概率为10%，每抽50次增加10%概率，抽出后概率加成消失。
4. 每次抽卡up维持12天
5. 依照官方公布概率 r:78.25% sr:10% ssr:1% sp:0.25%""",
    ).send()


@on_command("抽卡记录", rule=is_group_blacklisted, block=True).handle()
async def _(event: Union[MessageEvent, PokeNotifyEvent]):
    # 判断是否存在抽卡记录
    if event.user_id in user_list:
        user = user_list[user_list.index(event.user_id)]
        if user.get_up_count > 0:
            send_text = f"""抽卡记录：\n当前累计抽卡{
                user.draw_count}次\n本期up{user.get_up_count}次抽出"""
        else:
            send_text = (
                f"""抽卡记录：\n当前累计抽卡{user.draw_count}次\n本期up尚未抽出"""
            )
    else:
        send_text = "您还没有抽卡记录"
    # 发送结果,并@发送者
    await Text(send_text).send(at_sender=True)


@on_command("抽卡更新", block=True, permission=SUPERUSER).handle()
async def _(bot: Bot, event: Union[MessageEvent, PokeNotifyEvent]):
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list, update_text = get_or_update_icon()
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    if len(update_text) == 0:
        await Text("无式神更新").send()
    else:
        heros_list.sort(key=lambda x: x.heroid, reverse=True)
        yyshelp_config.draw_card_up_id = heros_list[0].heroid
        # 重置抽卡记录
        for user in user_list:
            user.up_count = 0
            user.draw_count = 0
            user.get_up_count = 0
        # 保存抽卡记录
        save_config(CONFIG_PATH, [yyshelp_config])
        update_text = f"""更新式神\n{update_text}\n当前up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n已重置抽卡次数"""
        # 发送更新信息
        group_list = await bot.get_group_list()
        for group in group_list:
            await bot.send_group_msg(group_id=group["group_id"], message=update_text)


@on_command("抽卡UP", block=True, permission=SUPERUSER).handle()
async def _(args: Message = CommandArg()):
    up_id = args.extract_plain_text()
    # 检验id是否为3个数字组成
    if not up_id.isdigit() or len(up_id) != 3:
        await Text("请输入正确的式神id").send(at_sender=True)
    else:
        yyshelp_config.draw_card_up_id = up_id
        save_config(CONFIG_PATH, [yyshelp_config])
        await Text(f"已设置当前up：{id_name_dict[up_id][0]}").send(at_sender=True)


@on_command("抽卡重置", block=True, permission=SUPERUSER).handle()
async def _(bot: Bot):
    # 重置抽卡记录
    for user in user_list:
        user.up_count = 0
        user.draw_count = 0
        user.get_up_count = 0
    # 保存抽卡记录
    save_config(CONFIG_PATH, [yyshelp_config])
    message = "已重置抽卡次数"
    # 发送更新信息
    group_list = await bot.get_group_list()
    for group in group_list:
        await bot.send_group_msg(group_id=group["group_id"], message=message)


# 定时任务，每周3中午12点执行抽卡更新
@scheduler.scheduled_job("cron", day_of_week=2, hour=12, id="update_draw_card")
async def update_draw_card():
    global heros_list, heros_dict, id_name_dict, user_list
    heros_list, update_text = get_or_update_icon()
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    bot: Bot = get_bot()
    if len(update_text) == 0:
        try:
            for user in get_driver().config.superusers:
                await Text("无式神更新").send_to(
                    target=TargetQQPrivate(user_id=user),
                    bot=bot,
                )
        except:
            logger.error("[draw_card]:定时任务发送失败,请配置超级管理员账号")
    else:
        heros_list.sort(key=lambda x: x.heroid, reverse=True)
        yyshelp_config.draw_card_up_id = heros_list[0].heroid
        # 重置抽卡记录
        for user in user_list:
            user.up_count = 0
            user.draw_count = 0
            user.get_up_count = 0
        # 保存抽卡记录
        save_config(CONFIG_PATH, [yyshelp_config])
        update_text = f"""更新式神\n{update_text}\n当前up：{id_name_dict[yyshelp_config.draw_card_up_id][0]}\n已重置抽卡次数"""
        # 发送更新信息
        try:
            for user in get_driver().config.superusers:
                bot.send_private_msg(user_id=user, message=update_text)
        except:
            logger.error("[draw_card]:定时任务发送失败,请配置超级管理员账号")
        group_list = await bot.get_group_list()
        for group in group_list:
            if group not in yyshelp_config.draw_card_black_groups:
                await bot.send_group_msg(
                    group_id=group["group_id"],
                    message=update_text,
                )
