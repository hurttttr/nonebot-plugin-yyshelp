from __future__ import annotations

from pathlib import Path

from .core_utils import OsEnvTypes


class OSEnv:
    """系统环境变量"""

    """数据目录"""
    DATA_DIR = OsEnvTypes.Str("DATA_DIR", default=(Path.cwd() / "data"))

    """配置文件目录"""
    CONFIG_DIR = OsEnvTypes.Str("CONFIG_DIR", default=(Path.cwd() / "config"))
