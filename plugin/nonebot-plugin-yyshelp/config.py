import json
from pathlib import Path
from typing import Iterator, List, Literal, Tuple

import yaml
from nonebot import get_driver
from nonebot.log import logger
from pydantic import BaseModel

ALLOWED_SUFFIXES = (".json", ".yml", ".yaml")  # 允许的文件后缀
DATA_PATH = Path.cwd() / "data" / "yyshelp"  # 配置存放路径

# 配置目录不存在自动创建
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)


class ConfigModel(BaseModel):
    """控制类，控制阻塞和优先级

    Args:
        BaseModel (_type_): _description_
    """

    autoreply_block: bool = False
    autoreply_priority: int = 99


config = ConfigModel.parse_obj(get_driver().config)


class ReplyEntryModel(BaseModel):
    type: Literal["rss", "bilibili"] = "rss"
    priority: int = 1
    matches: List[str]
    keyword: str
    number: int = 5
    user: str
    option: List[Literal["bvinfo"]] = [""]  # 暂不使用


class DailyWorkModel(BaseModel):
    deviceid: str  # cookie
    token: str  # cookie
    uid: str  # 大神id
    roleId: str  # 登录账户id
    server: str  # 服务器id
    guildId: str  # 寮id
    cron: str = "0 0 21 * * 5 "  # 默认每周521点执行
    at: bool = False
    user_json: str = ""  # json对应文件路径
    qh: int

    def get_headers(self) -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; 22021211RC Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36 Godlike/3.71.2 UEPay/com.netease.gl/android7.11.4",
            "Accept": "application/json, text/plain, */*",
            # 'Accept-Encoding': 'gzip, deflate',
            "Content-Type": "application/json",
            "gl-version": "3.71.2",
            "gl-source": "URS",
            "gl-deviceid": self.deviceid,
            "gl-token": self.token,
            "gl-clienttype": "50",
            "gl-uid": self.uid,
        }


def iter_config_path(root_path: Path = DATA_PATH) -> Iterator[Path]:
    """递归遍历指定目录下的所有文件，并返回符合条件的文件路径

    Args:
        root_path (Path, optional): 表示根目录的路径，默认值为 DATA_PATH

    Yields:
        Iterator[Path]: 返回的是一个迭代器，迭代器的元素是 Path 类型的对象，表示文件路径
    """
    for path in root_path.iterdir():
        if path.is_dir():
            yield from iter_config_path(path)

        if path.is_file() and (path.suffix in ALLOWED_SUFFIXES):
            yield path


def load_rss_config(path: Path) -> List[ReplyEntryModel]:
    """从指定路径加载配置文件，并将其转换为 ReplyEntryModel 对象的列表

    Args:
        path (Path): 指定路径

    Returns:
        List[ReplyEntryModel]: 返回的是一个列表，列表的元素是 ReplyEntryModel 类型的对象
    """
    content = path.read_text(encoding="u8")

    if path.suffix in (".yml", ".yaml"):
        obj: list = yaml.load(content, Loader=yaml.FullLoader)
    else:
        obj: list = json.loads(content)

    return [ReplyEntryModel(**x) for x in obj]


def reload_rss() -> Tuple[int, int]:
    replies.clear()

    success = 0
    fail = 0
    file_name = DATA_PATH / "rss.yaml"
    try:
        replies.extend(load_rss_config(file_name))

    except Exception:
        logger.opt(colors=True).exception(
            f"加载回复配置 <y>{file_name}</y> <l><r>失败</r></l>",
        )
        fail += 1

    else:
        logger.opt(colors=True).info(
            f"加载回复配置 <y>{file_name}</y> <l><g>成功</g></l>"
        )
        success += 1

    replies.sort(key=lambda x: x.priority)
    logger.opt(colors=True).info(
        f"加载回复配置完毕，<l>成功 <g>{success}</g> 个，失败 <r>{fail}</r> 个</l>",
    )
    return success, fail


def reload_dailywork() -> bool:
    """
    重新加载每日工作配置。

    从指定的文件（支持 YAML 或 JSON 格式）中读取每日工作配置，并更新到 dailywork 的存储中。
    不接受任何参数。
    返回值为 None。
    """
    dailywork.clear()  # 清空当前的每日工作记录
    file_name = DATA_PATH / "dailywork.yaml"
    print(file_name)  # 打印文件名

    try:
        content = file_name.read_text(encoding="u8")  # 读取文件内容

        if file_name.suffix in (".yml", ".yaml"):  # 判断文件格式
            # 加载 YAML 格式的内容
            obj: list = yaml.load(content, Loader=yaml.FullLoader)
        else:
            # 加载 JSON 格式的内容
            obj: list = json.loads(content)
        # 将加载的内容转换为 DailyWorkModel 实例，并更新到 dailywork 中
        dailywork.extend([DailyWorkModel(**x) for x in obj])
        logger.opt(colors=True).info(f"<g>加载日常任务配置完毕</g>")
    except Exception:
        # 记录加载异常
        logger.opt(colors=True).exception(f"<r>加载日常任务配置失败</r>")
        return False
    return True


dailywork: List[DailyWorkModel] = []
replies: List[ReplyEntryModel] = []
reload_rss()
reload_dailywork()
