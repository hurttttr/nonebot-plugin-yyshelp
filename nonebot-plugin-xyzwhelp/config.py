from pydantic import BaseModel, Extra
from pathlib import Path


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    xyzwhelp_apikey: str = ''


DATA_PATH = Path.cwd() / "temp"  #临时图片存放路径
#配置目录不存在自动创建
if not DATA_PATH.exists():
    DATA_PATH.mkdir(parents=True)
