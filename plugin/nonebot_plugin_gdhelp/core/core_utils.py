from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class ConfigBase(BaseModel):

    @classmethod
    def load_config(cls, file_path: Path):
        """加载配置文件"""
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            return cls()
        content: str = file_path.read_text(encoding="utf-8")
        if file_path.suffix == ".json":
            return cls.model_validate_json(content)
        if file_path.suffix in [".yaml", ".yml"]:
            return cls.model_validate(yaml.safe_load(content))
        raise ValueError(f"Unsupported file type: {file_path}")

    def dump_config(self, file_path: Path) -> None:
        """保存配置文件"""
        if file_path.suffix == ".json":
            file_path.write_text(self.model_dump_json())
        elif file_path.suffix in [".yaml", ".yml"]:
            yaml_str = yaml.dump(
                data=self.model_dump(),
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True,
            )
            file_path.write_text(yaml_str, encoding="utf-8")
        else:
            raise ValueError(f"Unsupported file type: {file_path}")


class OsEnvTypes:

    @staticmethod
    def _use_env(env_key: str, default: Any = None) -> Any:
        return os.environ.get(f"GD_{env_key.upper()}", default)

    @staticmethod
    def Str(key: str, default: str = "") -> str:
        return str(OsEnvTypes._use_env(key, default))

    @staticmethod
    def Int(key: str, default: int = 0) -> int:
        return int(OsEnvTypes._use_env(key, default))

    @staticmethod
    def Float(key: str, default: float = 0.0) -> float:
        return float(OsEnvTypes._use_env(key, default))

    @staticmethod
    def Bool(key: str) -> bool:
        return str(OsEnvTypes._use_env(key, "false")).lower() == "true"
