import json
import yaml

from nonebot.log import logger
from nonebot import get_driver
from pydantic import BaseModel
from pathlib import Path
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

ALLOWED_SUFFIXES = (".json", ".yml", ".yaml")  #允许的文件后缀
DATA_PATH = Path.cwd() / "data" / "yyshelp"  #配置存放路径
#配置目录不存在自动创建
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
    number: int = 10
    user: str
    option: List[Literal["bvinfo"]] = [""]  #暂不使用


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


def load_config(path: Path) -> List[ReplyEntryModel]:
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


def reload_replies() -> Tuple[int, int]:
    replies.clear()

    success = 0
    fail = 0

    for path in iter_config_path():
        file_name = path.name
        print(file_name)

        try:
            replies.extend(load_config(path))

        except Exception:
            logger.opt(colors=True).exception(
                f"加载回复配置 <y>{file_name}</y> <l><r>失败</r></l>", )
            fail += 1

        else:
            logger.opt(colors=True).info(
                f"加载回复配置 <y>{file_name}</y> <l><g>成功</g></l>")
            success += 1

    replies.sort(key=lambda x: x.priority)
    logger.opt(colors=True).info(
        f"加载回复配置完毕，<l>成功 <g>{success}</g> 个，失败 <r>{fail}</r> 个</l>", )
    return success, fail


replies: List[ReplyEntryModel] = []
reload_replies()
# for i in replies:
#     print(i)
