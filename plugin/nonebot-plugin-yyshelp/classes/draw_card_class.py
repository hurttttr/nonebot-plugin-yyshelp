from pydantic import BaseModel


class Heros:
    def __init__(self, heroid, name, rarity):
        self.heroid = heroid
        self.name = name
        self.rarity = rarity

    def __str__(self):
        return self.name


class DrawCardUser(BaseModel):
    user_id: int  # qq号
    group_id: int  # 群号
    up_count: int  # up累计次数
    draw_count: int  # 抽卡累计次数
    get_up_count: int = 0  # 获得本期up次数，0代表未获得

    def __eq__(self, other):
        # 比较全部属性
        return self.user_id == other
