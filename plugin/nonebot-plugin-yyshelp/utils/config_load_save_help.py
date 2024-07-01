import json
import os

import yaml
from click import group
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
        with open(file_path, "r", encoding="utf-8") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    # 如果是json文件
    elif file_path.endswith(".json"):
        # 读取json文件
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        logger.log("error", f"文件类型不支持")
        return False

    # 判断yaml数据是否为空
    if not data:
        logger.log("error", f"文件{file_path}数据为空")
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
        logger.log("error", f"文件{file_path}数据为空")
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
        logger.log("error", f"文件类型不支持")
        return False

    return True


if __name__ == "__main__":

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

    class JsonTestModel(BaseModel):
        user_id: int
        group_id: int
        up_count: int
        draw_count: int

    # # 测试读取yaml文件
    # data_list: list[DailyWorkModel] = []
    # file_path = r"e:\HQ\Documents\Code\dailywork.yaml"

    # load_config(DailyWorkModel, file_path, data_list)
    # print(data_list)

    # # 尝试写入yaml文件
    # data_list[0].qh = 10
    # save_config(file_path, data_list)

    # 测试读取json文件
    data_list: list[JsonTestModel] = []
    file_path = r"e:\HQ\Documents\Code\json_test.json"
    load_config(JsonTestModel, file_path, data_list)
    print(data_list)

    # 尝试写入json文件
    # data_list.append(JsonTestModel(user_id=123, group_id=456,
    #                  up_count=789, draw_count=114514))
    # save_config(file_path, data_list)
