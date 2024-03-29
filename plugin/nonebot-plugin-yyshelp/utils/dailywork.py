from typing import Literal
import requests
import json
import datetime

from ..config import DailyWorkModel

# headers = {
#     'User-Agent':
#     'Mozilla/5.0 (Linux; Android 12; 22021211RC Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/91.0.4472.114 Mobile Safari/537.36 Godlike/3.71.2 UEPay/com.netease.gl/android7.11.4',
#     'Accept': 'application/json, text/plain, */*',
#     'gl-version': '3.71.2',
#     'gl-source': 'URS',
#     'gl-deviceid': 'ec31b65b85164b53acc66d1d5c11471a',
#     'gl-token': '28165f9d58b14bbd8c69a7abfda09259',
#     'gl-clienttype': '50',
#     'gl-uid': '0cfe4201bf4342e89b401c525398906c',
# }


def get_tasks_data(model: DailyWorkModel,
                   taskType: str = "liao30",
                   logDate: str = "",
                   type=Literal["daily", "weekly"]) -> list[str]:

    # 当未提供logDate时，使用当前日期
    if not logDate:
        logDate = datetime.datetime.now().date().strftime('%Y%m%d')

    # 准备请求的JSON数据
    json_data = {
        'taskType': taskType,
        'logDate': logDate,
    }

    # 根据任务类型选择请求的URL
    if type == "weekly":
        url = 'https://god.gameyw.netease.com/v1/app/gameData/g37/org/report/getFinishTaskMemberList'
    else:
        url = 'https://god.gameyw.netease.com/v1/app/gameData/g37/org/report/getDailyTaskInfo'

    # 发送POST请求并获取响应
    response = requests.post(
        url=url,
        headers=model.get_headers(),
        json=json_data,
    )

    # 解析响应结果，提取数据
    try:
        data = json.loads(response.text)['result']['memberList']
    except KeyError:
        print("请求失败")
        return []
    return [i['roleId'] for i in data]


def get_users_dict(model: DailyWorkModel) -> dict[str:str]:
    """
    从服务器获取公会成员信息，并以字典形式返回，键为成员id，值为成员名称。
    
    参数:
    - model: DailyWorkModel 实例，包含请求所需的所有信息，如角色id、服务器编号和公会id。
    
    返回值:
    - 一个字典，键为公会成员的id，值为成员的名称。
    """

    # 准备请求数据
    json_data = {
        'appKey': 'g37',
        'roleId': model.roleId,
        'server': model.server,
        'guildId': model.guildId,
    }

    # 发送请求并获取响应
    response = requests.post(
        'https://god.gameyw.netease.com/v1/app/gameRole/guild/members/cache',
        headers=model.get_headers(),
        json=json_data)

    # 尝试解析响应体中的JSON数据
    try:
        data = json.loads(response.text)['result']
    except KeyError:
        print("请求失败")
        return {}

    # 初始化并更新用户信息字典
    user_dict = {}
    for i in data:
        user_dict.update({i['roleId']: i['roleName']})

    return user_dict


def not_do_liao30(model: DailyWorkModel) -> list[str]:
    """
    获取当日寮30未完成任务的用户字典。

    参数:
    - model: DailyWorkModel 实例，包含请求所需的所有信息，如角色id、服务器编号和公会id。

    返回值:
        list[str]: 未完成的用户名列表。
    """
    # 获取当前日期，并格式化为YYYYMMDD形式
    date_time = datetime.datetime.now().date().strftime('%Y%m%d')
    # 获取所有用户字典
    user_dict = get_users_dict(model)
    # 获取当前日期的任务数据
    date30 = get_tasks_data(model=model, logDate=date_time)
    user_list = []
    # 将未完成的用户的用户名加入列表
    for i in user_dict:
        if i not in date30:
            user_list.append(user_dict[i])
    return user_list


def not_do_weekly(model: DailyWorkModel) -> list[str]:
    """
    获取周贡献为0的用户列表。

    参数:
    - model: DailyWorkModel 实例，包含请求所需的所有信息，如角色id、服务器编号和公会id。

    返回值:
        list[str]: 一个列表，包含周贡献为0的用户名称。
    """
    kill_list = []
    user_dict: dict = get_users_dict(model)
    liao30: list = get_tasks_data(model=model,
                                  taskType="liao30",
                                  type='weekly')
    fengmo: list = get_tasks_data(model=model,
                                  taskType="fengmo",
                                  type='weekly')
    xianshi: list = get_tasks_data(model=model,
                                   taskType="xianshi",
                                   type='weekly')
    daoguan: list = get_tasks_data(model=model,
                                   taskType="daoguan",
                                   type='weekly')
    for i in user_dict:
        if (i not in liao30) and (i not in fengmo) and (i not in xianshi) and (
                i not in daoguan):
            kill_list.append(user_dict[i])
    return kill_list
