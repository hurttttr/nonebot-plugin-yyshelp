from nonebot import get_driver
from nonebot.plugin import PluginMetadata
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.params import CommandArg, Arg
from nonebot.log import logger
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    PrivateMessageEvent,
)

from PIL import Image, ImageEnhance
from io import BytesIO
import easyocr
import re
import requests

from .utils.calculate import calculate

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-xyzwhelp",
    description="咸鱼之王帮助",
    usage="",
    # config=Config,
)

# global_config = get_driver().config
# config = Config.parse_obj(global_config)
reader_ch = easyocr.Reader(['ch_sim', 'en'], gpu=False)
reader_en = easyocr.Reader(['en'], gpu=False)
test = on_command("宝箱周")


@test.handle()
async def _(event: MessageEvent, state: T_State, tu: Message = CommandArg()):
    if tu:
        state["tu"] = tu


# 定义一个命令，用于触发图片处理
@test.got("tu", prompt="请发送识别图片")
async def process_image(bot: Bot,
                        event: MessageEvent,
                        msg: Message = Arg('tu')):
    try:
        if msg[0].type == "image":
            await bot.send(event=event, message="正在处理图片")
            url = msg[0].data["url"]  # 图片链接
            image: Image = await process_image_from_url(url)
            width, height = image.size
            cut1 = image.crop(
                (0, height * 0.23, width, height * 0.3)).save('cut1.jpg')
            cut2 = image.crop((0, height * 0.75, width, height * 0.87))
            # 创建一个对比度增强器对象
            enhancer = ImageEnhance.Contrast(cut2)
            # 增强图像对比度
            cut2 = enhancer.enhance(2).save('cut2.jpg')
            result1 = reader_ch.readtext('cut1.jpg', detail=0)
            result2 = reader_en.readtext('cut2.jpg', detail=0)
            pre_code = int(
                re.findall(r'\d+/\d+', result1[-1])[0].split('/')[0])
            wooden = int(result2[0][1:])
            silver = int(result2[1][1:])
            gold = int(result2[2][1:])
            platinum = int(result2[3][1:])
            await bot.send(event=event,
                           message=calculate(wooden=wooden,
                                             silver=silver,
                                             gold=gold,
                                             platinum=platinum,
                                             pre_code=pre_code))
    except (IndexError):
        await bot.finish("参数错误")


async def process_image_from_url(url) -> Image:
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    return image
