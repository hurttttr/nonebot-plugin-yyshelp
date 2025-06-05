from __future__ import annotations

from datetime import datetime
from typing import List, Tuple, Union

from core.config import (
    ControlType,
    config,
    data,
    reload_config,
    save_config,
    save_data,
)
from nonebot import on_command
from nonebot.adapters import Bot, Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageEvent
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg

from ..schemas import Record, User
from ..services.price_service import get_price_data
from ..tool.onebot_util import (
    ChatType,
    get_chat_info,
    get_user_name,
)


async def command_guard(
    event: Union[MessageEvent, GroupMessageEvent],
    bot: Bot,
    arg: Message,
    matcher: Matcher,
) -> Tuple[str, str, str, ChatType]:
    """指令执行前处理"""
    username = await get_user_name(event=event, bot=bot, user_id=event.get_user_id())
    # 判断是否是管理员
    if event.get_user_id() not in config.SUPER_USERS:
        logger.warning(f"用户 {username} 不在允许的管理用户中")
        if config.ENABLE_COMMAND_UNAUTHORIZED_OUTPUT:
            await matcher.finish(
                "用户 [{event.get_user_id()}]{username} 不在允许的管理用户中"
            )
        else:
            await matcher.finish()

    cmd_content: str = arg.extract_plain_text().strip()
    chat_key, chat_type = await get_chat_info(event=event)
    return username, cmd_content, chat_key, chat_type


async def command_gropu_guard(
    event: GroupMessageEvent,
    bot: Bot,
    arg: Message,
    matcher: Matcher,
) -> Tuple[str, str, str]:
    """群组指令执行前处理"""
    chat_key, chat_type = await get_chat_info(event=event)
    username = await get_user_name(event=event, bot=bot, user_id=event.get_user_id())
    if chat_type != ChatType.GROUP:
        logger.warning("非群聊消息，无法执行群组命令")
        await matcher.finish("非群聊消息，无法执行群组命令")
    if (event.get_user_id() not in config.SUPER_USERS) or (
        event.sender.role not in ["owner", "admin"]
    ):
        logger.warning(f"用户 {event.sender.card} 不在允许的管理用户中")
        if config.ENABLE_COMMAND_UNAUTHORIZED_OUTPUT:
            await matcher.finish(f"用户 {username} 不在允许的管理用户中")
        else:
            await matcher.finish()
    cmd_content: str = arg.extract_plain_text().strip()
    chat_key, chat_type = await get_chat_info(event=event)
    return username, cmd_content, chat_key


async def command_add_guard(
    event: GroupMessageEvent,
    bot: Bot,
    arg: Message,
    matcher: Matcher,
) -> Tuple[str, str, str, ChatType]:
    """添加挂刀推送指令执行前处理"""
    # 判断是否开启推送
    if not config.PUSH_ON:
        logger.warning("挂刀助手推送功能未开启")
        await matcher.finish("挂刀助手推送功能未开启")
    chat_key, chat_type = await get_chat_info(event=event)
    # 根据消息类别判断是否允许推送
    if chat_type == ChatType.GROUP:
        if (
            config.GROUP_CONTROL_TYPE == ControlType.BLACK
            and chat_key in config.GROUP_ID
        ) or (
            config.GROUP_CONTROL_TYPE == ControlType.WHITE
            and chat_key not in config.GROUP_ID
        ):
            logger.warning(f"群 {chat_key} 不在允许的推送群中")
            await matcher.finish(f"群 {chat_key} 不在允许的推送群中")
    else:
        username = await get_user_name(
            event=event, bot=bot, user_id=event.get_user_id()
        )
        if (
            config.USER_CONTROL_TYPE == ControlType.BLACK and username in config.USER_ID
        ) or (
            config.USER_CONTROL_TYPE == ControlType.WHITE
            and username not in config.USER_ID
        ):
            logger.warning(f"用户 {username} 不在允许的推送用户中")
            await matcher.finish(f"用户 {username} 不在允许的推送用户中")
    cmd_content: str = arg.extract_plain_text().strip()
    return username, cmd_content, chat_key, chat_type


@on_command("挂刀帮助", priority=5, block=True).handle()
async def gd_help(matcher: Matcher, event: MessageEvent, bot: Bot):
    """显示挂刀帮助"""
    await matcher.finish(
        """欢迎使用挂刀帮助，数据有延迟具体以steam官方为准
开启挂刀推送:在本群开启挂刀推送，私聊不支持
开启/关闭挂刀日报:在本群开启/关闭挂刀日报推送，私聊不支持
添加挂刀 {name}|{price}:添加挂刀推送
注：自行替换{}内的内容，不要保留{}，中间的空格保留，默认7天后开始推送
查询挂刀 {name|可选}：查询挂刀，默认返回推送列表的所有纪录，输入商品名称时只查询该记录
删除挂刀推送 {name}:删除添加的挂刀推送"""
    )


@on_command("开启挂刀日报", priority=5, block=True).handle()
async def gd_start_push(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """开启挂刀日报推送"""
    username, cmd_content, chat_key = await command_gropu_guard(
        event=event, bot=bot, arg=arg, matcher=matcher
    )
    if not config.PUSH_ON:
        await matcher.finish("挂刀助手已关闭推送功能,请联系管理员开启")
    # 白名单控制方式处理
    if (
        config.GROUP_CONTROL_TYPE == ControlType.WHITE
        and chat_key not in config.GROUP_ID
    ):
        config.GROUP_ID.append(chat_key)
        save_config()
        logger.info(f"群 {chat_key} 已添加到白名单")
        await matcher.finish(f"群 {chat_key} 已开启挂刀日报推送")
    # 黑名单控制方式处理
    elif config.GROUP_CONTROL_TYPE == ControlType.BLACK and chat_key in config.GROUP_ID:
        config.GROUP_ID.remove(chat_key)
        save_config()
        logger.info(f"群 {chat_key} 已从黑名单中移除")
        await matcher.finish(f"群 {chat_key} 已关闭挂刀日报推送")
    else:
        await matcher.finish(f"群 {chat_key} 已开启挂刀日报推送,请勿重复开启")


@on_command("关闭挂刀日报", priority=5, block=True).handle()
async def gd_stop_push(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """关闭挂刀日报推送"""
    username, cmd_content, chat_key = await command_gropu_guard(
        event=event, bot=bot, arg=arg, matcher=matcher
    )
    # 白名单控制方式处理
    if config.GROUP_CONTROL_TYPE == ControlType.WHITE and chat_key in config.GROUP_ID:
        config.GROUP_ID.remove(chat_key)
        save_config()
        logger.info(f"群 {chat_key} 已从白名单中移除")
        await matcher.finish(f"群 {chat_key} 已关闭挂刀日报推送")
    # 黑名单控制方式处理
    elif (
        config.GROUP_CONTROL_TYPE == ControlType.BLACK
        and chat_key not in config.GROUP_ID
    ):
        config.GROUP_ID.append(chat_key)
        save_config()
        logger.info(f"群 {chat_key} 已添加到黑名单")
        await matcher.finish(f"群 {chat_key} 已开启挂刀日报推送")
    else:
        await matcher.finish(f"群 {chat_key} 已关闭挂刀日报推送,请勿重复关闭")


@on_command("开启挂刀推送", priority=5, block=True).handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """开启挂刀推送"""
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )
    config.PUSH_ON = True
    save_config()
    logger.info("已成功开启挂刀推送")
    await matcher.finish("已成功开启挂刀推送")


@on_command("关闭挂刀推送", priority=5, block=True).handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """关闭挂刀推送"""
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )
    config.PUSH_ON = False
    save_config()
    logger.info("已成功关闭挂刀推送")
    await matcher.finish("已成功关闭挂刀推送")


@on_command("conf_show", aliases={"conf-show"}, priority=5, block=True).handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )

    if not cmd_content:
        modifiable_config_key: List[str] = []
        for _key, _value in config.model_dump().items():
            if isinstance(_value, (int, float, bool, str)):
                modifiable_config_key.append(_key)
        sep = "\n"
        await matcher.finish(
            f"当前支持动态修改配置：\n{sep.join([f'- {k} ({str(type(getattr(config, k)))[8:-2]})' for k in modifiable_config_key])}"
        )
    else:
        if config.model_dump().get(cmd_content):
            await matcher.finish(
                message=f"当前配置：\n{cmd_content}={getattr(config, cmd_content)}"
            )
        else:
            await matcher.finish(message=f"未知配置 `{cmd_content}`")


@on_command("conf_set", aliases={"conf-set"}, priority=5, block=True).handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )

    try:
        key, value = cmd_content.strip().split("=", 1)
        assert key and value
    except ValueError:
        await matcher.finish(message="参数错误，请使用 `conf_set key=value` 的格式")
        return

    if config.model_dump().get(key) is not None:
        _c_type = type(getattr(config, key))
        _c_value = getattr(config, key)
        if isinstance(_c_value, (int, float)):
            setattr(config, key, _c_type(value))
        elif isinstance(_c_value, bool):
            if value.lower() in ["true", "1", "yes"]:
                setattr(config, key, True)
            elif value.lower() in ["false", "0", "no"]:
                setattr(config, key, False)
            else:
                await matcher.finish(
                    message=f"布尔值只能是 `true` 或 `false`，请检查 `{key}` 的值"
                )
        elif isinstance(_c_value, str):
            setattr(config, key, _c_type(value))
        else:
            await matcher.finish(message=f"不支持动态修改的配置类型 `{_c_type}`")
        await matcher.finish(message=f"已设置 `{key}` 的值为 `{value}`")
    else:
        await matcher.finish(message=f"未知配置: `{key}`")


@on_command("conf_reload", aliases={"conf-reload"}, priority=5, block=True).handle()
async def _(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    try:
        reload_config()
    except Exception as e:
        await matcher.finish(message=f"重载配置失败：{e}")
    else:
        await matcher.finish(message="重载配置成功")


@on_command("添加挂刀", priority=5, block=True).handle()
async def gd_add_push(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """添加挂刀"""
    username, cmd_content, chat_key, chat_type = await command_add_guard(
        event, bot, arg, matcher
    )
    try:
        name, price = cmd_content.strip().split("|")
        assert name and price
    except ValueError:
        await matcher.finish(message="参数错误，请使用 `添加挂刀 name|price` 的格式")
        return
    if get_price_data(name)["status"] == 500:
        await matcher.finish(message=f"未找到商品：{name}")
        return
    price = float(price)
    if price < 0:
        await matcher.finish(message=f"价格不能为负数：{price}")
        return
    if chat_type == ChatType.GROUP:
        record = Record(
            name=name,
            price=price,
            time=datetime.now(),
            type="gropu",
            group=chat_key,
        )
    else:
        record = Record(
            name=name,
            price=price,
            time=datetime.now(),
            type="private",
        )
    # 遍历data，如何发现存在username相同的记录，则更新，不存在则新增
    for _record in data:
        if _record.user == username:
            _record.add_record(record)
    else:
        data.append(User(user=username, record=[record]))
    save_data()
    logger.info(f"已添加挂刀：{name} {price}")
    await matcher.finish(message=f"已添加挂刀：{name} {price}")


@on_command("查询挂刀", priority=5, block=True).handle()
async def gd_query_push(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """查询挂刀"""
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )
    if not cmd_content:
        # 遍历data，如何发现存在username相同的记录，则更新，不存在则新增
        for _record in data:
            if _record.user == username:
                await matcher.finish(message=f"查询结果：\n{_record.record}")
                return
        else:
            await matcher.finish(message="未查询到挂刀记录")
    else:
        # 遍历data，如何发现存在username相同的记录，则更新，不存在则新增
        for _record in data:
            if _record.user == username:
                for _r in _record.record:
                    if _r.name == cmd_content:
                        await matcher.finish(message=f"查询结果：\n{_r}")
                        return
        else:
            await matcher.finish(message="未查询到挂刀记录")


@on_command("删除挂刀", priority=5, block=True).handle()
async def gd_del_push(
    matcher: Matcher, event: MessageEvent, bot: Bot, arg: Message = CommandArg()
):
    """删除挂刀"""
    username, cmd_content, chat_key, chat_type = await command_guard(
        event, bot, arg, matcher
    )
    if not cmd_content:
        await matcher.finish(message="参数错误，请使用 `删除挂刀 name` 的格式")
        return
    # 遍历data，如何发现存在username相同的记录，则更新，不存在则新增
    for _record in data:
        if _record.user == username:
            for _r in _record.record:
                if _r.name == cmd_content:
                    _record.record.remove(_r)
                    save_data()
                    logger.info(f"已删除挂刀：{cmd_content}")
                    await matcher.finish(message=f"已删除挂刀：{cmd_content}")
                    return
    else:
        await matcher.finish(message="未查询到挂刀记录")
