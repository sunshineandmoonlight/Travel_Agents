"""
热门旅行目的地配置
用于预加载和推荐
"""

# 热门城市列表（按地区分组）
POPULAR_DESTINATIONS = {
    # 中国热门城市
    "china": [
        "北京", "上海", "广州", "深圳", "成都", "重庆",
        "西安", "杭州", "南京", "苏州", "武汉", "厦门",
        "青岛", "大连", "桂林", "丽江", "大理", "三亚",
        "拉萨", "香港", "澳门", "台北"
    ],

    # 东南亚
    "southeast_asia": [
        "曼谷", "清迈", "普吉岛", "芭提雅", "新加坡",
        "吉隆坡", "槟城", "巴厘岛", "河内", "胡志明市",
        "岘港", "马尼拉", "长滩岛"
    ],

    # 日韩
    "east_asia": [
        "东京", "京都", "大阪", "奈良", "富士山", "冲绳",
        "首尔", "釜山", "济州岛"
    ],

    # 欧洲
    "europe": [
        "巴黎", "伦敦", "罗马", "威尼斯", "巴塞罗那",
        "阿姆斯特丹", "雅典", "圣托里尼", "布拉格", "维也纳",
        "里斯本", "马德里", "柏林", "慕尼黑"
    ],

    # 美洲
    "americas": [
        "纽约", "洛杉矶", "旧金山", "拉斯维加斯",
        "芝加哥", "迈阿密", "多伦多", "温哥华",
        "里约热内卢", "布宜诺斯艾利斯"
    ],

    # 澳大利亚新西兰
    "oceania": [
        "悉尼", "墨尔本", "奥克兰", "皇后镇",
        "大堡礁", "珀斯"
    ],

    # 中东
    "middle_east": [
        "迪拜", "阿布扎比", "伊斯坦布尔", "多哈",
        "耶路撒冷", "佩特拉"
    ]
}

# 最热门的TOP 20城市（用于首页预加载）
TOP_DESTINATIONS = [
    "三亚", "曼谷", "东京", "巴黎", "纽约",
    "新加坡", "迪拜", "悉尼", "伦敦", "罗马",
    "巴厘岛", "首尔", "京都", "巴塞罗那", "洛杉矶",
    "清迈", "普吉岛", "阿姆斯特丹", "布拉格", "威尼斯"
]

# 所有热门城市扁平列表（用于API返回）
ALL_POPULAR_DESTINATIONS = []
for cities in POPULAR_DESTINATIONS.values():
    ALL_POPULAR_DESTINATIONS.extend(cities)

# 去重并排序
ALL_POPULAR_DESTINATIONS = sorted(list(set(ALL_POPULAR_DESTINATIONS)))


def get_popular_destinations(limit: int = None, region: str = None) -> list:
    """
    获取热门城市列表

    Args:
        limit: 返回数量限制
        region: 地区筛选 (china, southeast_asia, east_asia, europe, americas, oceania, middle_east)

    Returns:
        城市列表
    """
    if region:
        cities = POPULAR_DESTINATIONS.get(region, [])
    else:
        cities = ALL_POPULAR_DESTINATIONS

    if limit:
        return cities[:limit]
    return cities


def get_top_destinations(limit: int = 20) -> list:
    """获取TOP热门城市"""
    return TOP_DESTINATIONS[:limit]


def is_popular_destination(city: str) -> bool:
    """检查城市是否是热门目的地"""
    return city in ALL_POPULAR_DESTINATIONS
