import json

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Message, MessageEvent
from nonebot.params import Arg, CommandArg
from nonebot.typing import T_State

from .utils.get import get_image_and_cut, get_return_str

test = on_command("宝箱周")


@test.handle()
async def _(event: MessageEvent, state: T_State, tu: Message = CommandArg()):
    if tu:  # 如果tu存在，则将其保存到状态字典中
        state["tu"] = tu


# 定义一个命令，用于触发图片处理
@test.got("tu", prompt="请发送识别图片,建议选择钻石箱子截图")
async def process_image(bot: Bot, event: MessageEvent, msg: Message = Arg("tu")):
    try:
        if msg[0].type == "image":
            await bot.send(event=event, message="正在处理图片")
            url = msg[0].data["url"]  # 图片链接
            print(url)
            get_image_and_cut(url)
            await bot.send(event=event, message=get_return_str())
    except IndexError:
        await bot.finish("参数错误")
