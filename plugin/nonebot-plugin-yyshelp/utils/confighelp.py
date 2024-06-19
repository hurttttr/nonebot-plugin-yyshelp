import json
import yaml
from typing import List

"""
配置文件帮助类

该类用于加载和保存配置文件，目前支持json，yml和yaml格式。

"""

def load_Config(object:object,filepath:str,dataList:List) -> bool:
    """
    加载配置文件
    :param object: 配置对象
    :param filename: 配置文件名
    :param dataList: 数据列表
    :return: bool   
    """

    # 清空数据列表
    dataList.clear()

    try:
        # 读取文件内容
        content = filepath.read_text(encoding="u8")

        # 根据文件后缀选择相应的解析方式
        if filepath.suffix in (".yml", ".yaml"):
            obj: list = yaml.load(content, Loader=yaml.FullLoader)
        else:
            obj: list = json.loads(content)

        # 将解析后的数据转换为对象并添加到数据列表中
        dataList.extend([object(**x) for x in obj])
        # logger.opt(colors=True).info(f"<g>加载日常任务配置完毕</g>")
    except Exception:
        # 若出现异常则记录日志并返回 False
        # logger.opt(colors=True).exception(f"<r>加载日常任务配置失败</r>")
        return False
    # 若没有出现异常则返回 True
    return True

def save_Config(object:object,filepath:str,dataList:List) -> bool:
    """ 
    保存配置文件
    :param object: 配置对象
    :param filename: 配置文件名
    :param dataList: 数据列表
    :param dataList: 数据列表
    :return: bool   
    """

    # 将数据列表转换为字典列表
    obj: list = [x.dict() for x in dataList]

    # 根据文件后缀选择相应的序列化方式  

  
    if filepath.suffix in (".yml", ".yaml"):
        content = yaml.dump(obj, allow_unicode=True)
    else:
        content = json.dumps(obj, ensure_ascii=False, indent=4)

    # 写入文件内容
    try:
        filepath.write_text(content, encoding="u8")
        # logger.opt(colors=True).info(f"<g>保存日常任务配置完毕</g>")
    except Exception:
        # 若出现异常则记录日志并返回 False
        # logger.opt(colors=True).exception(f"<r>保存日常任务配置失败</r>")
        return False
    # 若没有出现异常则返回 True
    return True