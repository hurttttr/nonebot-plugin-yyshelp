import requests
import parsel
import json

from datetime import datetime

######暂时不继续开发

headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


class BVData:

    def __init__(
        self,
        author,
        bvid,
        rid,
        times,
    ) -> None:
        self.author = author
        self.bvid = bvid
        self.rid = rid
        self.times = times


async def get_bvinfo(bvid: str) -> str:
    """返回BV号对应视频的视频简介

    Args:
        bvid (str): bv号

    Returns:
        str: 视频简介
    """
    url = f'https://www.bilibili.com/video/{bvid}'

    html = requests.get(url=url, headers=headers).text
    selector = parsel.Selector(html)
    text = selector.xpath('//*[@id="v_desc"]/div[1]/span/text()').get()
    return text


def get_videolist(uid: str, keyword: str = ' ', num: int = 1) -> list[BVData]:
    """获得指定up主指定关键词的视频投稿信息，可以指定返回数量

    Args:
        uid (str): up主uid
        keyword (str): 关键词,必填，默认为空格
        num (int, optional): 返回数量 Defaults to 1.

    Returns:
        list[BVData]: 视频信息列表
    """
    url = f'https://api.bilibili.com/x/space/dynamic/search?keyword={keyword}&pn=1&ps=10&mid={uid}'

    data = json.loads(requests.get(url=url,
                                   headers=headers).text)['data']['cards']
    index = 0
    videoList: list[BVData] = []
    while index < num:  #控制返回数量
        bvid = data[index]['desc']['bvid']  #bv号
        times = datetime.fromtimestamp(
            data[index]['desc']['timestamp']).strftime(
                '%Y-%m-%d %H:%M:%S')  #更新时间,并将时间戳转换成标准时间
        rid = data[index]['desc']['rid']  #视频rid，方便取评论，不一定有用
        author = data[index]['desc']['user_profile']['info']['uname']  #作者
        videoList.append(BVData(author, bvid, rid, times))
        index += 1
    return videoList


# get_videolist('40403050', '秘闻', 3)
