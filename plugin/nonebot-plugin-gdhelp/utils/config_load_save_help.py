from __future__ import annotations

import json
import os

import yaml
from nonebot.log import logger
from pydantic import BaseModel


# 传入对象类型，文件路径，数据列表，从文件中读取数据生成对象存入数据列表，成功返回True，失败返回False
def load_config(obj_type: type, file_path: str, data_list: list) -> bool:
    """
    传入对象类型，文件路径，数据列表，从文件中读取数据生成对象存入数据列表，成功返回True，失败返回False

    Args:
        obj_type (type): 对象类型
        file_path (str): 文件路径
        data_list (list): 数据列表

    Returns:
        bool: 成功返回True，失败返回False
    """
    # 判断文件是否存在
    if not os.path.exists(file_path):
        return False

    # 判断文件类型
    if file_path.endswith(".yaml"):
        # 读取yaml文件
        with open(file_path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
    # 如果是json文件
    elif file_path.endswith(".json"):
        # 读取json文件
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
    else:
        logger.log("ERROR", "文件类型不支持")
        return False

    # 判断yaml数据是否为空
    if not data:
        logger.log("ERROR", f"文件{file_path}数据为空")
        return False

    # 遍历yaml数据，生成对象存入数据列表
    data_list.extend([obj_type(**x) for x in data])

    return True


# 传入文件路径，数据列表，将数据列表写入yaml文件，成功返回True，失败返回False
def save_config(file_path: str, data_list: list) -> bool:
    """
    传入文件路径，数据列表，将数据列表写入yaml文件，成功返回True，失败返回False

    Args:
        file_path (str): 文件路径
        data_list (list): 数据列表

    Returns:
        bool: 成功返回True，失败返回False
    """

    # 判断数据列表是否为空
    if not data_list:
        logger.log("ERROR", f"文件{file_path}数据为空")
        return False
    # 判断文件路径是否存在
    if not os.path.exists(os.path.dirname(file_path)):
        # 获取父目录路径
        parent_path = os.path.dirname(file_path)
        # 创建父目录
        os.makedirs(parent_path)
    # 判断文件是否存在，不存在则创建，存在则清空
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("")
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.truncate()

    # 将数据列表转换为字典列表
    data: list = [x.dict() for x in data_list]

    # 判断文件类型
    if file_path.endswith(".yaml"):
        # 写入yaml文件
        with open(file_path, "a", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True)
    # 如果是json文件
    elif file_path.endswith(".json"):
        # 写入json文件
        with open(file_path, "a", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
    else:
        logger.log("ERROR", "文件类型不支持")
        return False

    return True
