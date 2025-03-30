from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime

import requests


class RssData:
    """Rss信息类，包含Rss节点的信息"""

    def __init__(self, author, description, pubDate, link, href_links, src_links):
        self.author = author  # 作者
        self.description = description  # 内容
        self.pubDate = pubDate  # 更新时间
        self.link = link  # 文章链接
        self.href_links = href_links  # href链接，一般为网页，视频等
        self.src_links = src_links  # src链接，一般为图片

    def __format__(self, __format_spec: str) -> str:
        return f"@{self.author} {self.pubDate}\n{self.description}\n链接:{self.link}"


async def get_rssdataList(
    url: str, keyword: str = "", number: int = 5
) -> list[RssData]:
    """获取rss中的作者信息和内容

    Args:
        url (str): rsshub链接

    Returns:
        dict: 数据字典
    """
    root = ET.fromstring(requests.get(url=url, timeout=10).text)
    author = root[0][0].text
    get_rssdataList = []
    for elem in root[0].iter(tag="item"):  # 获取rss中item的内容
        # 如果数字小于等于0，则跳出循环
        if number <= 0:
            break
        description = elem[1].text  # 详细内容
        # 当keyword非空且不为none的情况下判断内容是否包含
        if (keyword := keyword.strip()) and keyword not in description:
            continue
        pubDate = datetime.strptime(
            elem[2].text, "%a, %d %b %Y %H:%M:%S %Z"
        )  # 更新时间，并进行格式转换
        link = elem[4].text  # 原链接

        # 获取详细内容中的链接
        href_links = re.findall(
            r'href="([^"]*)"', description
        )  # href链接，一般为网页，视频等
        src_links = re.findall(r'src="([^"]*)"', description)  # src链接，一般为图片

        # 如果存在链接去掉详细内容末尾的链接
        index: int = description.find("<")
        if index != -1:
            description = description[:index]
        description = description.rstrip()  # 去除结尾多余空格和换行
        result_dict = RssData(author, description, pubDate, link, href_links, src_links)
        get_rssdataList.append(result_dict)
        number -= 1
    return get_rssdataList


# s = get_rssdataList(
#     'https://rsshub.zzliux.cn/163/ds/06fc2d8303dd4bdcbab84e0e2443dbc4', '版本活动')
# for i in s:
#     print(format(i))
