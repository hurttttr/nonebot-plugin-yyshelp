from nonebot import get_driver
from io import BytesIO
from PIL import Image
import requests
import json
import re

from ..config import Config
from .calculate import calculate

config: Config = Config.parse_obj(get_driver().config)


def get_image_and_cut(url: str) -> None:
    """
    从给定的URL获取图像并进行裁剪。
    
    参数:
    url: 图像的URL地址。
    
    返回值:
    无
    """
    # 从URL获取图像响应
    response = requests.get(url)
    # 将响应内容打开为图像
    image = Image.open(BytesIO(response.content))
    # 获取图像的宽和高
    width, height = image.size

    # 裁剪图像的上部区域并保存
    image.crop((0, height * 0.23, width, height * 0.3)).save(r'temp/cut1.jpg')
    # 裁剪图像的下部区域，转换为灰度并保存
    image.crop((0, height * 0.75, width,
                height * 0.87)).convert('L').save(r'temp/cut2.jpg')


def ocr_space_file(filename,
                   overlay=False,
                   api_key=config.xyzwhelp_apikey,
                   language='eng') -> str:
    """
    使用本地文件通过OCR.space API进行请求。
    Python3.5 - 未在2.7上进行测试
    
    :param filename: 文件路径及名称。
    :param overlay: 是否在响应中需要OCR.space的叠加层。默认为False。
    :param api_key: OCR.space的API密钥。默认为'helloworld'。
    :param language: 用于OCR的语言代码。
                     可用的语言代码列表可在https://ocr.space/OCRAPI找到。
                     默认为'en'。
    :return: 返回JSON格式的结果。
    """

    # 准备请求参数
    payload = {
        'isOverlayRequired': overlay,
        'apikey': api_key,
        'language': language,
        'OCREngine': 2,
    }
    # 打开文件并使用requests库发送POST请求
    with open(filename, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={filename: f},
            data=payload,
        )
    # 返回请求内容
    return r.content


def process_data(data: str) -> int:
    """
    处理数据字符串，将其中的字符'o', 'O' 替换成 '0'，将 'l', 'L', 'I', 'i' 替换成 '1'，然后将处理后的字符串转换成整数返回。
    
    参数:
    data: str - 需要处理的数据字符串。
    
    返回值:
    int - 经过字符替换并转换为整数后的结果。
    """
    # 替换所有的'o'和'O'为'0'
    data = data.replace('o', '0').replace('O', '0')
    # 替换所有的'l', 'L', 'I', 'i'为'1'
    data = data.replace('l', '1').replace('L',
                                          '1').replace('I',
                                                       '1').replace('i', '1')
    # 将处理后的字符串转换为整数并返回
    return int(data)


def get_return_str() -> str:
    """
    从两张图片中提取信息，并根据提取的信息计算返回一个字符串结果。
    
    函数流程：
    1. 从'cut1.jpg'图片中使用OCR技术提取文本，并提取预编码（格式如：数字/数字）。
    2. 从'cut2.jpg'图片中使用OCR技术提取文本，提取四种材料的信息（wooden, silver, gold, platinum）。
    3. 对提取的材料信息进行处理。
    4. 使用预编码和处理后的材料信息进行计算，返回计算结果。
    
    返回:
    str: 计算后的字符串结果。
    """
    # 从'cut1.jpg'图片中提取预编码
    result1 = json.loads(ocr_space_file(
        r'temp/cut1.jpg', language='chs'))['ParsedResults'][0]['ParsedText']
    pre_code = re.findall(r'\d+/\d+', result1)[0].split('/')[0]

    # 从'cut2.jpg'图片中提取四种材料的信息
    result2 = re.findall(
        r'X[\da-zA-Z]+',
        json.loads(ocr_space_file(r'temp/cut2.jpg'))['ParsedResults'][0]
        ['ParsedText'])

    # 对提取的材料信息进行处理
    wooden = process_data(result2[0][1:])
    silver = process_data(result2[1][1:])
    gold = process_data(result2[2][1:])
    platinum = process_data(result2[3][1:])

    # 根据预编码和处理后的材料信息进行计算，返回计算结果
    return calculate(wooden, silver, gold, platinum, int(pre_code))
