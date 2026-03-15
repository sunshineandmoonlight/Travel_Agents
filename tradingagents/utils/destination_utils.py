"""
目的地名称标准化工具

处理英文名称到中文名称的映射
"""

# 英文名称到中文名称的映射
DESTINATION_NAME_MAP = {
    # 国家名称映射
    "japan": "日本", "Japan": "日本",
    "thailand": "泰国", "Thailand": "泰国",
    "singapore": "新加坡", "Singapore": "新加坡",
    "korea": "韩国", "south korea": "韩国", "South Korea": "韩国",
    "vietnam": "越南", "Vietnam": "越南",
    "cambodia": "柬埔寨", "Cambodia": "柬埔寨",
    "indonesia": "印度尼西亚", "Indonesia": "印度尼西亚",
    "philippines": "菲律宾", "Philippines": "菲律宾",
    "malaysia": "马来西亚", "Malaysia": "马来西亚",
    "maldives": "马尔代夫", "Maldives": "马尔代夫",
    "france": "法国", "France": "法国",
    "italy": "意大利", "Italy": "意大利",
    "uk": "英国", "united kingdom": "英国", "United Kingdom": "英国",
    "spain": "西班牙", "Spain": "西班牙",
    "germany": "德国", "Germany": "德国",
    "switzerland": "瑞士", "Switzerland": "瑞士",
    "greece": "希腊", "Greece": "希腊",
    "usa": "美国", "united states": "美国", "United States": "美国",
    "australia": "澳大利亚", "Australia": "澳大利亚",
    "new zealand": "新西兰", "New Zealand": "新西兰",
    "india": "印度", "India": "印度",
    "nepal": "尼泊尔", "Nepal": "尼泊尔",
    "iceland": "冰岛", "Iceland": "冰岛",
    "norway": "挪威", "Norway": "挪威",

    # 城市名称映射
    "tokyo": "东京", "Tokyo": "东京",
    "kyoto": "京都", "Kyoto": "京都",
    "osaka": "大阪", "Osaka": "大阪",
    "bangkok": "曼谷", "Bangkok": "曼谷",
    "phuket": "普吉岛", "Phuket": "普吉岛",
    "chiang mai": "清迈", "Chiang Mai": "清迈",
    "seoul": "首尔", "Seoul": "首尔",
    "hanoi": "河内", "Hanoi": "河内",
    "ho chi minh": "胡志明市", "Ho Chi Minh": "胡志明市",
    "siem reap": "暹粒", "Siem Reap": "暹粒",
    "angkor wat": "吴哥窟", "Angkor Wat": "吴哥窟",
    "bali": "巴厘岛", "Bali": "巴厘岛",
    "manila": "马尼拉", "Manila": "马尼拉",
    "cebu": "宿务", "Cebu": "宿务",
    "kuala lumpur": "吉隆坡", "Kuala Lumpur": "吉隆坡",
    "paris": "巴黎", "Paris": "巴黎",
    "rome": "罗马", "Rome": "罗马",
    "venice": "威尼斯", "Venice": "威尼斯",
    "florence": "佛罗伦萨", "Florence": "佛罗伦萨",
    "milan": "米兰", "Milan": "米兰",
    "london": "伦敦", "London": "伦敦",
    "barcelona": "巴塞罗那", "Barcelona": "巴塞罗那",
    "madrid": "马德里", "Madrid": "马德里",
    "berlin": "柏林", "Berlin": "柏林",
    "munich": "慕尼黑", "Munich": "慕尼黑",
    "zurich": "苏黎世", "Zurich": "苏黎世",
    "geneva": "日内瓦", "Geneva": "日内瓦",
    "athens": "雅典", "Athens": "雅典",
    "santorini": "圣托里尼", "Santorini": "圣托里尼",
    "new york": "纽约", "New York": "纽约",
    "los angeles": "洛杉矶", "Los Angeles": "洛杉矶",
    "san francisco": "旧金山", "San Francisco": "旧金山",
    "sydney": "悉尼", "Sydney": "悉尼",
    "melbourne": "墨尔本", "Melbourne": "墨尔本",
    "auckland": "奥克兰", "Auckland": "奥克兰",
    "queenstown": "皇后镇", "Queenstown": "皇后镇",
    "delhi": "德里", "Delhi": "德里",
    "mumbai": "孟买", "Mumbai": "孟买",
    "kathmandu": "加德满都", "Kathmandu": "加德满都",
    "reykjavik": "雷克雅未克", "Reykjavik": "雷克雅未克",
    "oslo": "奥斯陆", "Oslo": "奥斯陆"
}


def normalize_destination_name(name: str) -> str:
    """
    标准化目的地名称（英文转中文）

    Args:
        name: 原始名称（可能是英文或中文）

    Returns:
        标准化后的中文名称
    """
    if not name:
        return name

    # 直接匹配
    if name in DESTINATION_NAME_MAP:
        return DESTINATION_NAME_MAP[name]

    # 模糊匹配（不区分大小写）
    name_lower = name.lower()
    for en_name, cn_name in DESTINATION_NAME_MAP.items():
        if en_name.lower() == name_lower:
            return cn_name

    # 如果是中文，直接返回
    if any('\u4e00' <= c <= '\u9fff' for c in name):
        return name

    # 如果找不到映射，返回原名称
    return name


def get_destination_highlights(destination_name: str, dest_type: str = "综合") -> list:
    """
    获取目的地的特色景点（根据名称和类型）

    Args:
        destination_name: 目的地名称（中文）
        dest_type: 目的地类型

    Returns:
        特色景点列表
    """
    # 国际目的地景点映射
    international_highlights = {
        "日本": ["东京塔", "富士山", "京都清水寺", "大阪城", "北海道雪景"],
        "韩国": ["首尔塔", "景福宫", "济州岛", "明洞", "釜山海鲜市场"],
        "泰国": ["大皇宫", "普吉岛海滩", "清迈古城", "芭提雅", "水上市场"],
        "新加坡": ["滨海湾花园", "圣淘沙", "鱼尾狮", "牛车水", "克拉码头"],
        "马来西亚": ["双子塔", "槟城乔治市", "沙巴仙本那", "马六甲古城", "云顶高原"],
        "瑞士": ["阿尔卑斯山", "少女峰", "琉森湖", "日内瓦湖", "因特拉肯"],
        "法国": ["埃菲尔铁塔", "卢浮宫", "凯旋门", "塞纳河", "凡尔赛宫"],
        "意大利": ["罗马斗兽场", "威尼斯运河", "佛罗伦萨大教堂", "比萨斜塔", "庞贝古城"],
        "英国": ["大本钟", "伦敦塔桥", "大英博物馆", "白金汉宫", "巨石阵"],
        "西班牙": ["圣家堂", "普拉多博物馆", "阿尔罕布拉宫", "兰布拉大道", "塞维利亚大教堂"],
        "德国": ["勃兰登堡门", "新天鹅堡", "科隆大教堂", "黑森林", "慕尼黑啤酒节"],
        "希腊": ["雅典卫城", "圣托里尼日落", "米科诺斯岛", "德尔菲遗址", "克里特岛"],
        "冰岛": ["蓝湖温泉", "黄金圈", "北极光", "冰川徒步", "间歇泉"],
        "挪威": ["奥斯陆峡湾", "盖朗厄尔峡湾", "维京船博物馆", "北角", "卑尔根"],
        "美国": ["自由女神像", "大峡谷", "黄石公园", "迪士尼乐园", "时代广场"],
        "澳大利亚": ["悉尼歌剧院", "大堡礁", "乌鲁鲁巨石", "大洋路", "考拉"],
        "新西兰": ["米尔福德峡湾", "皇后镇极限运动", "奥克兰天空塔", "罗托鲁瓦地热", "霍比特村"],
        "印度": ["泰姬陵", "恒河", "琥珀堡", "喀拉拉邦回水", "孟买宝莱坞"],
        "尼泊尔": ["珠峰大本营", "博卡拉费瓦湖", "加德满都杜巴广场", "巴德岗古城", "蓝毗尼"],
        "越南": ["下龙湾", "会安古镇", "顺化皇城", "美奈海滩", "胡志明市战争遗迹博物馆"],
        "柬埔寨": ["吴哥窟", "巴戎寺", "女王宫", "洞里萨湖", "金边皇宫"],
        "印度尼西亚": ["巴厘岛梯田", "婆罗浮屠", "科莫多公园", "日惹皇宫", "龙目岛"],
        "菲律宾": ["长滩岛", "薄荷岛巧克力山", "马尼拉西班牙王城", "杜马盖地", "巴拉望"],
        "马尔代夫": ["水上别墅", "珊瑚礁潜水", "马累渔市", "沙滩日落", "海豚巡游"]
    }

    # 首先尝试精确匹配
    if destination_name in international_highlights:
        return international_highlights[destination_name]

    # 如果找不到精确匹配，根据类型返回通用景点
    type_highlights = {
        "海滨": ["阳光沙滩", "海岛风光", "海上活动", "海鲜美食", "日落美景"],
        "海滩": ["热带海滩", "水上运动", "沙滩酒吧", "海景日落", "潜水"],
        "历史": ["历史遗迹", "古建筑", "博物馆", "文化遗址", "历史街区"],
        "文化": ["文化体验", "传统艺术", "民俗表演", "文化街区", "手工艺品"],
        "都市": ["城市地标", "购物中心", "美食街", "夜生活", "摩天大楼"],
        "自然": ["自然风光", "国家公园", "山脉景色", "湖泊河流", "森林徒步"],
        "综合": ["著名景点", "当地特色", "文化体验", "美食探索", "购物娱乐"]
    }

    if dest_type in type_highlights:
        return type_highlights[dest_type]

    # 默认返回通用景点
    return ["著名景点", "当地美食", "文化体验", "自然风光", "购物娱乐"]
