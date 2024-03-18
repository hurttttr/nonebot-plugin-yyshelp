def calculate(wooden: int = 0,
              silver: int = 0,
              gold: int = 0,
              platinum: int = 0,
              pre_code: int = 0) -> str:
    """
    计算积分数和完成轮数。
    
    参数:
    - wooden: 木头积分数，默认为0。
    - silver: 银色积分数，默认为0。
    - gold: 金色积分数，默认为0。
    - platinum: 铂金积分数，默认为0。
    - pre_code: 当前累计积分数，默认为0。
    
    返回值:
    - 返回一个包含可完成轮数、当前总积分、完成下一轮所需积分和需闯关数的字符串。
    """
    need_code = 3340  # 一轮积分数
    code = 0  # 总积分
    bout = 0  # 轮数
    surplus = 0  # 还需积分数

    # 根据不同材料计算总积分
    code = wooden + silver * 10 + gold * 20 + platinum * 50

    # 根据预设积分数调整，计算剩余积分数
    if pre_code >= 2000:
        if pre_code >= 6000:
            pre_code -= 6000
            pre_code = 860 - int(pre_code / 25 * 12)
        elif pre_code >= 4000:
            pre_code -= 4000
            pre_code = 1720 - int(pre_code / 25 * 12)
        else:
            pre_code -= 2000
            pre_code = 2580 - int(pre_code / 25 * 12)
    else:
        if pre_code >= 1000:
            pre_code -= 1000
            pre_code = 480 - int(pre_code / 25 * 12) + 2580
        elif pre_code > 0:
            pre_code = 380 - int(pre_code / 25 * 12) + 480 + 2580
        else:
            pre_code = 3440

    # 判断是否可以完成一轮，并计算剩余所需积分或剩余轮数
    if code >= pre_code:
        code -= pre_code
        bout = code // need_code
        surplus = need_code - (code - bout * need_code) + 100
        bout += 1
        code += pre_code
    else:
        surplus = pre_code - code
        bout = 0

    # 返回计算结果
    return f"木头箱子数量：{wooden:<4} 白银箱子数量：{silver:<4}\n黄金箱子数量：{gold:<4} 铂金箱子数量：{platinum:<4}\n可完成轮数：{bout}\n当总积分：{code}\n完成下一轮还需：{surplus}\n需闯关：{surplus/2.5:.1f}\n请检查木头箱子数量是否正确，推荐选中钻石箱子再进行截图"
