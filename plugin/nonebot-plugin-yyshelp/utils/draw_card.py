import json
import os
import random

import requests

# 稀有度字典
rarity = {
    "1": "n",
    "2": "r",
    "3": "sr",
    "4": "ssr",
    "5": "sp",
}
# SSR卡：两面佛
# SR卡：万年竹、海忍、人面树
# R卡：兔丸、数珠、天井下
ban_list = [
    "258",
    "275",
    "317",
    "329",
    "289",
    "301",
    "323",
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
}

path = 'data/icon/'


class Heros:
    def __init__(self, heroid, name, rarity):
        self.heroid = heroid
        self.name = name
        self.rarity = rarity

    def __str__(self):
        return self.name


# 转换函数，输入列表，输出按照稀有度分类的字典
def list_to_dict(heros_list: list[Heros]) -> dict:
    result: dict = {"n": [], "r": [], "sr": [], "ssr": [], "sp": []}
    for i in heros_list:
        # 去掉无法抽到的式神
        if i.heroid in ban_list:
            continue
        result[i.rarity].append(i)
    return result


# 生成id与名称的映射字典
def generate_id_name_dict(heros_list: list[Heros]) -> dict:
    result = {}
    for i in heros_list:
        result[i.heroid] = i.name
    return result


def get_or_update_icon() -> list[Heros]:
    """
    获取或更新英雄图标。

    清空已有的英雄列表，然后根据稀有度从网络上获取英雄信息和对应的图标。
    如果图标文件不存在，则下载并保存图标；如果已存在，则只更新英雄列表。

    :return: list, 包含英雄对象的列表。
    """
    heros_list = []
    for key, value in rarity.items():
        # 判断文件夹是否存在
        if not os.path.exists(path + value):
            os.makedirs(path + value)  # 递归创建文件夹
            url = f"""https://g37simulator.webapp.163.com/get_heroid_list?callback=jQuery1113002988038468302756_1719390741330&rarity={
                key}&interactive=0&material_type=0&page=1&per_page=200"""
            response = requests.get(url, headers=headers, timeout=10)
            data = json.loads(response.text[43:-1])["data"]

            for heroid in data:
                # print(heroid, data[heroid]['name'])
                icon_url = f"""https://yys.res.netease.com/pc/zt/20161108171335/data/shishen/{
                    heroid}.png?v5"""
                response = requests.get(icon_url, headers=headers, timeout=10)
                heros_list.append(Heros(heroid, data[heroid]["name"], value))
                with open(f"icon/{value}/{heroid}.png", "wb") as f:
                    f.write(response.content)
        # 若存在则判断是否有更新
        else:
            url = f"""https://g37simulator.webapp.163.com/get_heroid_list?callback=jQuery1113002988038468302756_1719390741330&rarity={
                key}&interactive=0&material_type=0&page=1&per_page=200"""
            response = requests.get(url, headers=headers, timeout=10)
            data = json.loads(response.text[43:-1])["data"]

            # 遍历数据中的每个式神ID
            for heroid in data:
                heros_list.append(Heros(heroid, data[heroid]["name"], value))
                # 检查指定路径下是否存在该式神的图标文件
                if not os.path.exists(path+f"{value}/{heroid}.png"):
                    # 打印新增式神的提示信息
                    print(f"新增{value}式神{data[heroid]['name']}，ID:{heroid}")
                    # 构造图标URL
                    icon_url = f"""https://yys.res.netease.com/pc/zt/20161108171335/data/shishen/{
                        heroid}.png?v5"""
                    # 发送HTTP GET请求获取图标
                    response = requests.get(
                        icon_url, headers=headers, timeout=10)
                    # 将获取的图标保存到指定路径
                    with open(path+f"{value}/{heroid}.png", "wb") as f:
                        f.write(response.content)
    return heros_list


# 根据概率进行模拟抽卡，输入式神字典、当期up式神id、累计up次数和累计抽卡次数，输出10次抽卡结果,结果列表中包含式神id
def simulate_draw(
    heros_dict: dict, heros_up_id: str, up_count: int, draw_count: int
) -> tuple[list[str], int]:
    """
    模拟抽卡。

    根据概率进行模拟抽卡，输入式神字典、当期up式神id、累计up次数和累计抽卡次数，输出10次抽卡结果,结果列表中包含式神id。

    :param heros_dict: dict, 包含式神字典。
    :param heros_up_id: int, 当期up式神id。
    :param up_count: int, 累计up次数。
    :param draw_count: int, 累计抽卡次数。
    :return: tuple, 包含10次抽卡结果的列表和累计up次数。
    """
    result = []
    for i in range(10):
        # 如果up次数达到六十，则必出ssp或sp
        if up_count >= 59:
            random_num = round(random.uniform(98.75, 100), 2)
        else:
            # 生成0-100的含2位小数的随机数
            random_num = round(random.uniform(0, 100), 2)
        # 遍历概率字典，找到第一个大于随机数的键
        if random_num < 78.75:
            rarity_key = "r"
        elif random_num < 98.75:
            rarity_key = "sr"
        elif random_num < 99.75:
            rarity_key = "ssr"
        else:
            rarity_key = "sp"
        # 若随机数小于98.75，则累计up次数加1
        if random_num < 98.75:
            up_count += 1
        else:
            up_count = 0
        # 若抽卡次数在450内，且该次抽中ssr或者sp式神，在此进行随机判断，若随机数小于10+抽卡次数/50*10，则必出up式神
        if (
            draw_count <= 450
            and random_num >= 98.75
            and random.uniform(0, 100) < (10 + (draw_count // 50 * 10))
        ):
            result.append(heros_up_id)
        else:
            # 否则随机选取该稀有度下所有式神
            heros_list = heros_dict[rarity_key]
            # 随机选取一个式神
            heros_id = random.choice(heros_list).heroid
            result.append(heros_id)
    return result, up_count


if __name__ == "__main__":
    heros_list = get_or_update_icon()
    heros_dict = list_to_dict(heros_list)
    id_name_dict = generate_id_name_dict(heros_list)
    heros_up_id = "315"
    draw_count = 440
    up_count = 50
    result, up_count = simulate_draw(
        heros_dict, heros_up_id, up_count, draw_count)
    print(result, up_count)
    if len(result) == 1:
        print(result[0])
    else:
        for i in result:
            print(id_name_dict[i])
