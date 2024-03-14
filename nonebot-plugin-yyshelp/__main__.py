from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

from nonebot import require, on_command, on_message, on_notice
from nonebot.params import CommandArg
from nonebot.rule import to_me
from nonebot.adapters import Message
from nonebot_plugin_saa import Text, Image, MessageFactory, AggregatedMessageFactory
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
    PokeNotifyEvent,
)

from .utils.rss import RssData, get_rssdataList
from .config import (config, replies, reload_replies)

require("nonebot_plugin_saa")


def match_str(word: str, match_list: List[str]) -> bool:
    if not word or not match_list:
        return False
    match_set = set(match_list)
    return word in match_set


async def message_checker(
    event: Union[MessageEvent, PokeNotifyEvent],
    state: T_State,
) -> bool:

    state_reply: list[RssData] = []
    for reply in replies:
        if match_str(str(event.get_message()), reply.matches):  #进行回复词匹配
            state_reply.append(await get_rssdataList(reply.user,
                                                     reply.keyword))
            break

    state["reply"] = state_reply
    return bool(state_reply)


message_matcher = on_message(
    rule=message_checker,
    block=config.autoreply_block,
    priority=config.autoreply_priority,
)
poke_matcher = on_notice(
    rule=message_checker,
    block=config.autoreply_block,
    priority=config.autoreply_priority,
)


@message_matcher.handle()
@poke_matcher.handle()
async def _(bot: Bot, event: Union[MessageEvent, PokeNotifyEvent],
            state: T_State):
    """
    异步处理函数，用于根据会话状态回复信息。
    
    参数:
    - bot: Bot对象，代表机器人本身。
    - event: Union[MessageEvent, PokeNotifyEvent]，代表触发的事件，可以是消息事件或戳一戳通知事件。
    - state: T_State，代表当前会话的状态，用于获取储存的回复信息。
    
    无返回值。
    """

    # 从会话状态中获取待回复的数据
    reply: List[RssData] = state["reply"][0]

    if len(reply) == 0:  # 如果待回复数据为空，则发送未查询到相关记录的消息
        await Text("未查询到相关记录！").finish()
    elif len(reply) == 1:  # 如果待回复数据为一条，则根据其中的图片数量分别处理
        src_links = reply[0].src_links

        if len(src_links) == 0:  # 如果无图片，仅发送文本消息
            await Text(format(reply[0])).finish()
        elif len(src_links) > 1:  # 如果有多个图片，发送文本消息加图片聚合消息
            image_list = [Image(i) for i in src_links]
            await Text(format(reply[0])).send()
            await AggregatedMessageFactory(image_list).finish()
        else:  # 如果有一个图片，发送文本消息加单个图片消息
            await Text(format(reply[0])).send()
            await Image(src_links[0]).finish()
    else:  # 如果待回复数据多于一条，逐条发送并聚合
        msg_list: list[MessageFactory] = []
        for i in reply:
            # 对每条数据，创建包含文本和图片的消息工厂对象
            msg_list.append(
                MessageFactory([Text(format(i))] +
                               [Image(j) for j in i.src_links]))
        await AggregatedMessageFactory(msg_list).finish()


rss = on_command("rss", rule=to_me(), priority=10, block=True)


@rss.handle()
async def get_rss(args: Message = CommandArg()):
    # 提取参数纯文本作为rss链接，并判断是否有效
    if rss_link := args.extract_plain_text():
        result = await get_rssdataList(rss_link, '秘闻竞速')
        # logger.opt(colors=True).info(len(result))
        if len(result) == 0:  #记录为0
            await Text("未查询到相关记录！").finish()
        elif len(result) == 1:  #记录为1
            src_links = result[0].src_links
            if len(src_links) == 0:  # 无图片
                await Text(format(result[0])).finish()
            elif len(src_links) > 1:  # 图片数>1
                image_list = [Image(i) for i in src_links]
                await Text(format(result[0])).send()
                await AggregatedMessageFactory(image_list).finish()
            else:  # 图片数==1
                await Text(format(result[0])).send()
                await Image(src_links[0]).finish()
        else:  #记录大于1
            msg_list: list[MessageFactory] = []
            for i in result:
                msg_list.append(
                    MessageFactory([Text(format(i))] +
                                   [Image(j) for j in i.src_links]))
            await AggregatedMessageFactory(msg_list).finish()
    else:
        await Text("请输入要查询的rss链接").finish()


reload_matcher = on_command("重载自动回复", permission=SUPERUSER)


@reload_matcher.handle()
async def _():
    """重载自动回复
    """
    success, fail = reload_replies()
    await Text(f"重载回复配置完毕~\n成功 {success} 个，失败 {fail} 个").finish()
