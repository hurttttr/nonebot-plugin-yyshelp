from dataclasses import dataclass
from operator import ge
from typing import List

import requests


@dataclass
class Item:
    zh_name: str
    eng_name: str
    item_nameid: int
    price: float


def get_item_price_from_sterm_by_item_nameid(item_nameid: int) -> float:
    """ "
    获取物品在steam商城的价格
    :param item_nameid: 物品的nameid
    :return: 物品的价格
    """
    headers = {
        "sec-ch-ua-platform": '"Windows"',
        "Referer": f"https://steamcommunity.com/market/listings/730",
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
    )
    return response.json()["sell_order_graph"][0][0]


def get_case_list_from_hangknife(last24Volume: str = "5000") -> List[Item]:
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
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }

    json_data = {
        "closable": "false",
        "id": "weaponCase",
        "filterName": "武器箱",
        "wearType": "",
        "quality": "",
        "rarity": "Common",
        "weaponType": "",
        "weaponCase": [],
        "stickerCapsule": [],
        "orderBy": "minPrice / steamBuyerPrice,ascending",
        "name": "Case",
        "minPrice": "",
        "maxPrice": "",
        "limit": 50,
        "last24Volume": last24Volume,
        "totalVolume": "",
        "offset": 1,
        "platform": [
            "c5",
            "igxe",
            "uupin",
            "v5Item",
            "skinPort",
            "bitSkins",
            "dmarket",
            "halo",
            "eco",
            "waxpeer",
        ],
        "game": "csgo",
        "total": 25,
    }

    response = requests.post(
        "https://www.hangknife.com/api/steam/queryItemList",
        headers=headers,
        json=json_data,
    )

    response = requests.post(
        "https://www.hangknife.com/api/steam/queryItemList",
        headers=headers,
        json=json_data,
    )
    data = response.json()
    temp_list = []
    for item in data["data"]:
        temp = Item(
            zh_name=item["staffName"],
            eng_name=item["engName"],
            item_nameid=item["steamNameId"],
            price=item["steamSellerPrice"],
        )
        temp_list.append(temp)
    return temp_list


if __name__ == "__main__":
    # print(get_item_price_from_sterm_by_item_nameid(175999886))
    print(get_case_list_from_hangknife())
    sorted_list = sorted(
        get_case_list_from_hangknife(), key=lambda x: x.price, reverse=True
    )
    print(sorted_list)
