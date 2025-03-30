from __future__ import annotations

import math
import typing
from datetime import datetime, timedelta
from typing import Dict, List

import requests

from ..entities.item import Item


def get_price_data(item_name: str) -> dict:
    """
    获取指定商品的价格数据
    :param item_name: 商品名称
    :return: 价格数据字典
    """
    headers = {
        "Referer": "https://www.hangknife.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    }

    params = {
        "engName": item_name,
    }

    response = requests.get(
        "https://www.hangknife.com/api/steam/auditDailyInfo",
        params=params,
        headers=headers,
        timeout=10,
    )
    return response.json()


def calculate_data(prices: dict, time: int) -> list:
    """
    计算指定日期内的平均价格和标准差
    :param prices: 价格字典
    :param time: 时间间隔，单位为天
    :return: 平均价格, 标准差
    """

    numbers = []
    for key, value in prices:
        # 比较时间是否在一个月内
        given_time = datetime.strptime(key, "%Y-%m-%d %H:%M:%S.%f")
        # 获取当前时间
        current_time = datetime.now()

        # 计算30天前的时间
        thirty_days_ago = current_time - timedelta(days=time)
        if given_time >= thirty_days_ago and value is not None:
            numbers.append(float(value))

    return [sum(numbers) / len(numbers), calculate_standard_deviation(numbers)]


def calculate_standard_deviation(numbers) -> float:
    """
    计算标准差
    :param numbers: 数字列表
    :return: 标准差
    """
    n = len(numbers)
    if n == 0:
        return 0

    # 计算均值
    mean = sum(numbers) / n

    # 计算方差
    variance = sum((x - mean) ** 2 for x in numbers) / n

    # 计算标准差
    standard_deviation = math.sqrt(variance)

    return standard_deviation


def calculate_knife_ratio(item_name: str) -> dict[str, typing.Any]:
    """
    计算挂刀比例并返回格式化信息
    :param item_name: 商品名称
    :return: 包含计算结果的字典
    """
    json_data = get_price_data(item_name)
    name = json_data["itemData"]["cnName"]
    thirdMinPrices = json_data["thirdMinPrices"]  # 第三方最低价格
    steamBuyerPrices = json_data["steamBuyerPrices"]  # Steam购买者价格
    platformData = json_data["platformData"]  # 平台数据

    # 计算30天和7天的第三方最低价格平均值和标准差
    thirdMinPrices_30 = calculate_data(thirdMinPrices, 30)  # 30天第三方最低价格数据
    thirdMinPrices_7 = calculate_data(thirdMinPrices, 7)  # 7天第三方最低价格数据

    # 计算30天和7天的Steam购买者价格平均值和标准差
    steamBuyerPrices_30 = calculate_data(
        steamBuyerPrices, 30
    )  # 30天Steam购买者价格数据
    steamBuyerPrices_7 = calculate_data(steamBuyerPrices, 7)  # 7天Steam购买者价格数据

    # 计算30天挂刀比例: (第三方价格/Steam价格)*1.15(Steam手续费系数)
    ratio_30d = thirdMinPrices_30[0] / steamBuyerPrices_30[0] * 1.15  # 30天挂刀比例
    ratio_7d = thirdMinPrices_7[0] / steamBuyerPrices_7[0] * 1.15  # 7天挂刀比例

    result = {
        "name": name,
        "third_price_30d": thirdMinPrices_30,
        "third_price_7d": thirdMinPrices_7,
        "steam_price_30d": steamBuyerPrices_30,
        "steam_price_7d": steamBuyerPrices_7,
        "ratio_30d": ratio_30d,
        "ratio_7d": ratio_7d,
        "message": f"""商品名称: {name}
{name} 第三方最低价格(30天): {thirdMinPrices_30[0]:.2f} 标准差: {thirdMinPrices_30[1]:.2f}
{name} 第三方最低价格(7天): {thirdMinPrices_7[0]:.2f} 标准差: {thirdMinPrices_7[1]:.2f}
{name} Steam购买者价格(30天): {steamBuyerPrices_30[0]:.2f} 标准差: {steamBuyerPrices_30[1]:.2f}
{name} Steam购买者价格(7天): {steamBuyerPrices_7[0]:.2f} 标准差: {steamBuyerPrices_7[1]:.2f}
30天平均价格挂刀比例{ratio_30d:.2f}
7天平均价格挂刀比例{ratio_7d:.2f}
https://www.hangknife.com/#/itemPage?marketHashName={item_name}""",
    }

    return result


def get_item_price_from_sterm_by_item_nameid(item_nameid: int) -> float:
    """
    获取物品在steam商城的价格
    :param item_nameid: 物品的nameid
    :return: 物品的价格
    """
    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": "https://steamcommunity.com/market/listings/730",
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
    }

    params = {
        "country": "CN",
        "language": "schinese",
        "currency": "23",
        "item_nameid": item_nameid,
    }

    response = requests.get(
        "https://steamcommunity.com/market/itemordershistogram",
        params=params,
        headers=headers,
        timeout=10,
    )
    return response.json()["sell_order_graph"][0][0]


def get_case_list_from_hangknife(last24Volume: str = "5000") -> list[Item]:
    """
    从挂刀网获取箱子列表
    :param last24Volume: 最近24小时交易量大于等于该值的箱子, 默认为5000
    :return: 箱子列表
    """
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "Origin": "https://www.hangknife.com",
        "Referer": "https://www.hangknife.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    json_data = {
        "filterName": "武器箱",
        "orderBy": "(chosenMinPrice / steamBuyerPrice),ASC",
        "name": "武器箱",
        "limit": 50,
        "offset": 1,
        "game": "csgo",
        "platform": [
            "DMarket",
            "C5Game",
            "SkinPort",
            "IGXE",
            "UUPIN",
            "V5Item",
            "CsMoney",
            "Waxpeer",
            "Eco",
            "BitSkins",
        ],
        "total": 41,
        "steamLatestTradeCount": last24Volume,
    }

    response = requests.post(
        "https://www.hangknife.com/api/steam/queryItemList/v2",
        headers=headers,
        json=json_data,
        timeout=10,
    )

    if response.status_code != 200:
        return []

    data = response.json()
    temp_list = []

    if "rows" not in data:
        return []

    for item in data["rows"]:
        temp = Item(
            zh_name=item["cnName"],
            eng_name=item["engName"],
            item_nameid=item["nameId"],
            price=item["steamSellerPrice"],
        )
        temp_list.append(temp)

    return temp_list
