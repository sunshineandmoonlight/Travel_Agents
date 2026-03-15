"""
地区匹配智能体 (Agent A2)

根据用户画像匹配目的地数据库
优先调用工具API获取实时数据增强匹配结果

阶段3: 推荐地区
"""

from typing import Dict, Any, List, Set
import logging
import re

logger = logging.getLogger('travel_agents')


# ============================================================
# 英文名称到中文名称的映射
# ============================================================

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


def _extract_destinations_from_special_requests(special_requests: str, llm=None) -> Set[str]:
    """
    🔥 新增：从特殊需求中提取城市名称

    支持多种表达方式：
    - "我想去三亚"
    - "想去三亚玩"
    - "目的地是三亚"
    - "三亚旅游"
    - "包括三亚、曼谷"

    🔥 支持否定表达：
    - "不想去三亚" → 三亚会被排除
    - "不要去北京" → 北京会被排除

    Args:
        special_requests: 特殊需求文本
        llm: LLM实例（用于智能解析）

    Returns:
        识别到的城市名称集合（中文）
    """
    if not special_requests:
        return set()

    # 🔥 优先使用LLM智能解析
    if llm:
        result = _extract_destinations_with_llm(special_requests, llm)
        if result:  # 如果LLM成功解析，返回结果
            return result

    preferred_cities = set()

    # 构建所有可能的城市名称列表（中文）
    all_cities = set()
    # 从DOMESTIC_DESTINATIONS_DB获取国内城市
    all_cities.update(DOMESTIC_DESTINATIONS_DB.keys())
    # 从INTERNATIONAL_DESTINATIONS_DB获取国际城市
    all_cities.update(INTERNATIONAL_DESTINATIONS_DB.keys())
    # 添加英文名称映射
    for en_name, cn_name in DESTINATION_NAME_MAP.items():
        if cn_name in all_cities:
            all_cities.add(en_name)

    # 排序：优先匹配长城市名（避免"三亚"被"三"匹配）
    sorted_cities = sorted(all_cities, key=len, reverse=True)

    # 🔥 先检查否定表达
    negative_patterns = ['不想去', '不要去', '避免', '排除', '不想', '不要', '不去']
    is_negative = any(pattern in special_requests for pattern in negative_patterns)

    # 如果是否定表达，不提取城市（或返回排除列表）
    if is_negative:
        logger.info(f"[地区匹配] 检测到否定表达，跳过城市提取: {special_requests}")
        return set()

    # 直接匹配城市名称
    for city in sorted_cities:
        if city in special_requests:
            preferred_cities.add(city)
            logger.debug(f"[地区匹配] 识别到城市（直接匹配）: {city}")

    # 匹配"我想去X"模式
    pattern1 = rf'我想去([{"".join(sorted_cities)}]+)'
    matches1 = re.findall(pattern1, special_requests)
    for match in matches1:
        preferred_cities.add(match)
        logger.debug(f"[地区匹配] 识别到城市（我想去X）: {match}")

    # 匹配"想去X"模式
    pattern2 = rf'想去([{"".join(sorted_cities)}]+)'
    matches2 = re.findall(pattern2, special_requests)
    for match in matches2:
        preferred_cities.add(match)
        logger.debug(f"[地区匹配] 识别到城市（想去X）: {match}")

    # 匹配"目的地是X"模式
    pattern3 = rf'目的地是([{"".join(sorted_cities)}]+)'
    matches3 = re.findall(pattern3, special_requests)
    for match in matches3:
        preferred_cities.add(match)
        logger.debug(f"[地区匹配] 识别到城市（目的地是X）: {match}")

    # 将英文城市名转换为中文
    normalized_cities = set()
    for city in preferred_cities:
        normalized = normalize_destination_name(city)
        if normalized:
            normalized_cities.add(normalized)

    if normalized_cities:
        logger.info(f"[地区匹配] 从特殊需求提取到城市: {normalized_cities}")

    return normalized_cities


def _extract_destinations_with_llm(special_requests: str, llm) -> Set[str]:
    """
    🔥 新增：使用LLM智能解析特殊需求

    能够处理：
    1. 否定表达："不想去三亚"
    2. 复杂语义："靠近西藏的地方"、"看海的城市"
    3. 地理推理："云南周边"、"广东以北"

    Args:
        special_requests: 特殊需求文本
        llm: LLM实例

    Returns:
        preferred_destinations: 用户想去的城市集合
    """
    from langchain_core.messages import HumanMessage

    # 构建所有可用的城市列表
    all_cities = list(DOMESTIC_DESTINATIONS_DB.keys()) + list(INTERNATIONAL_DESTINATIONS_DB.keys())

    prompt = f"""分析用户的旅行特殊需求，提取城市名称并理解用户意图。

用户需求: {special_requests}

可用城市列表: {', '.join(all_cities[:50])}...

请按以下要求分析：

1. **明确提到的城市**：提取用户明确说想去的城市名
   - 例如："我想去三亚" → ["三亚"]
   - 例如："包括北京和上海" → ["北京", "上海"]

2. **否定表达**：如果用户说"不想去"某个城市，不要提取
   - 例如："不想去三亚" → [] (空列表，不要提取三亚)
   - 例如："不要去拉萨" → [] (空列表，不要提取拉萨)

3. **复杂语义理解**：根据地理位置和特征推断城市
   - "靠近西藏的地方" → ["成都", "昆明", "西宁"] (西藏周边的省会)
   - "看海的城市" → ["三亚", "厦门", "青岛", "大连"] (海滨城市)
   - "云南周边" → ["贵阳", "成都", "桂林"]
   - "广东以北" → ["长沙", "武汉", "北京"]

4. **地理特征匹配**：
   - "有雪山的城市" → ["成都", "丽江", "迪庆"]
   - "有古城的" → ["西安", "丽江", "大理"]
   - "美食多的" → ["成都", "广州", "长沙"]

请以JSON格式返回结果：
{{
    "preferred": ["城市1", "城市2"],
    "excluded": ["不想去的城市"],
    "reasoning": "简要说明分析逻辑"
}}

只返回JSON，不要其他内容。"""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 解析JSON响应
        import json
        result = json.loads(content)

        preferred = set(result.get("preferred", []))
        excluded = set(result.get("excluded", []))
        reasoning = result.get("reasoning", "")

        logger.info(f"[地区匹配] LLM分析特殊需求: {special_requests}")
        logger.info(f"[地区匹配] 推荐城市: {preferred}")
        logger.info(f"[地区匹配] 排除城市: {excluded}")
        logger.info(f"[地区匹配] 分析逻辑: {reasoning}")

        return preferred

    except Exception as e:
        logger.warning(f"[地区匹配] LLM解析失败，使用规则提取: {e}")
        # 回退到规则提取（递归调用但不传llm）
        return _extract_destinations_from_special_requests(special_requests, llm=None)


# ============================================================
# 目的地数据库
# ============================================================

# 国内城市数据库
DOMESTIC_DESTINATIONS_DB = {
    "北京": {
        "name": "北京",
        "type": "domestic",
        "tags": ["历史文化", "古迹", "博物馆", "美食", "皇家园林"],
        "best_season": "春秋两季（4-5月，9-10月）",
        "best_for": ["history", "culture", "food"],
        "highlights": ["故宫", "长城", "颐和园", "天坛", "胡同"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]
    },
    "上海": {
        "name": "上海",
        "type": "domestic",
        "tags": ["现代都市", "购物", "美食", "夜景", "外滩"],
        "best_season": "春秋两季",
        "best_for": ["shopping", "modern", "food", "nightlife"],
        "highlights": ["外滩", "东方明珠", "迪士尼", "豫园", "南京路"],
        "budget_level": {
            "economy": 400,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1548919973-5cef591cdbc9?w=800"]
    },
    "成都": {
        "name": "成都",
        "type": "domestic",
        "tags": ["美食", "休闲", "熊猫", "慢生活", "火锅"],
        "best_season": "四季皆宜",
        "best_for": ["food", "relaxation", "nature", "family"],
        "highlights": ["大熊猫基地", "宽窄巷子", "锦里", "都江堰", "青城山"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1628777065725-84f64b60e34d?w=800"]
    },
    "西安": {
        "name": "西安",
        "type": "domestic",
        "tags": ["历史文化", "古迹", "美食", "兵马俑", "碳水之都"],
        "best_season": "春秋两季",
        "best_for": ["history", "culture", "food"],
        "highlights": ["兵马俑", "大雁塔", "古城墙", "回民街", "华清宫"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 650
        },
        "images": ["https://images.unsplash.com/photo-1599974579688-8dbdd335c77f?w=800"]
    },
    "杭州": {
        "name": "杭州",
        "type": "domestic",
        "tags": ["自然风光", "古镇", "西湖", "园林", "文化"],
        "best_season": "春秋最佳",
        "best_for": ["nature", "culture", "romance", "relaxation"],
        "highlights": ["西湖", "灵隐寺", "宋城", "千岛湖", "西溪湿地"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1584467541268-b040f83be3fd?w=800"]
    },
    "重庆": {
        "name": "重庆",
        "type": "domestic",
        "tags": ["山城", "美食", "夜景", "火锅", "8D魔幻"],
        "best_season": "春秋两季",
        "best_for": ["food", "adventure", "nightlife", "modern"],
        "highlights": ["洪崖洞", "解放碑", "长江索道", "大足石刻", "武隆天生三桥"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 650
        },
        "images": ["https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=800"]
    },
    "厦门": {
        "name": "厦门",
        "type": "domestic",
        "tags": ["海滨", "文艺", "鼓浪屿", "美食", "休闲"],
        "best_season": "四季皆宜，春秋最佳",
        "best_for": ["nature", "romance", "relaxation", "food"],
        "highlights": ["鼓浪屿", "曾厝垵", "环岛路", "南普陀寺", "土楼"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1560278608-4d837701730f?w=800"]
    },
    "三亚": {
        "name": "三亚",
        "type": "domestic",
        "tags": ["海滨", "度假", "海鲜", "热带", "家庭"],
        "best_season": "10月至次年4月",
        "best_for": ["beach", "relaxation", "family", "food"],
        "highlights": ["亚龙湾", "天涯海角", "蜈支洲岛", "南山寺", "热带天堂"],
        "budget_level": {
            "economy": 400,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1559592413-7cec4d0cae2b?w=800"]
    },
    "丽江": {
        "name": "丽江",
        "type": "domestic",
        "tags": ["古镇", "自然", "雪山", "文艺", "慢生活"],
        "best_season": "四季皆宜",
        "best_for": ["nature", "culture", "romance", "relaxation"],
        "highlights": ["丽江古城", "玉龙雪山", "泸沽湖", "束河古镇", "蓝月谷"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1517722011199-e3c161974f70?w=800"]
    },
    "拉萨": {
        "name": "拉萨",
        "type": "domestic",
        "tags": ["高原", "宗教", "布达拉宫", "文化", "探险"],
        "best_season": "5-10月",
        "best_for": ["adventure", "culture", "religion", "nature"],
        "highlights": ["布达拉宫", "大昭寺", "纳木错", "羊卓雍措", "八廓街"],
        "budget_level": {
            "economy": 400,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1548018586-b999e2948319?w=800"]
    },
    "广州": {
        "name": "广州",
        "type": "domestic",
        "tags": ["美食", "现代", "早茶", "购物", "文化"],
        "best_season": "10月至次年4月",
        "best_for": ["food", "shopping", "culture", "modern"],
        "highlights": ["广州塔", "陈家祠", "沙面", "长隆", "上下九"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "南京": {
        "name": "南京",
        "type": "domestic",
        "tags": ["历史文化", "古迹", "民国", "美食", "人文"],
        "best_season": "春秋两季",
        "best_for": ["history", "culture", "food"],
        "highlights": ["中山陵", "明孝陵", "夫子庙", "秦淮河", "总统府"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1543084446-1e7882f59c24?w=800"]
    },
    "张家界": {
        "name": "张家界",
        "type": "domestic",
        "tags": ["自然风光", "山景", "探险", "摄影", "世界遗产"],
        "best_season": "4-10月",
        "best_for": ["nature", "adventure", "photography", "hiking"],
        "highlights": ["张家界国家森林公园", "天门山", "黄龙洞", "宝峰湖", "大峡谷玻璃桥"],
        "budget_level": {
            "economy": 400,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1506421660975-ea5f1aba1098?w=800"]
    },
    "桂林": {
        "name": "桂林",
        "type": "domestic",
        "tags": ["山水风光", "漓江", "喀斯特地貌", "摄影", "休闲"],
        "best_season": "4-10月",
        "best_for": ["nature", "photography", "relaxation", "scenery"],
        "highlights": ["漓江", "阳朔西街", "象鼻山", "芦笛岩", "龙脊梯田"],
        "budget_level": {
            "economy": 350,
            "medium": 550,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1558583620-f6e8ef1d1f33?w=800"]
    },
    "九寨沟": {
        "name": "九寨沟",
        "type": "domestic",
        "tags": ["自然风光", "湖泊", "彩林", "世界遗产", "摄影"],
        "best_season": "9-11月",
        "best_for": ["nature", "photography", "scenery", "hiking"],
        "highlights": ["诺日朗瀑布", "五花海", "长海", "镜海", "珍珠滩"],
        "budget_level": {
            "economy": 450,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]
    },
    "黄山": {
        "name": "黄山",
        "type": "domestic",
        "tags": ["自然风光", "山景", "云海", "日出", "世界遗产"],
        "best_season": "4-6月，9-11月",
        "best_for": ["nature", "photography", "hiking", "scenery"],
        "highlights": ["迎客松", "光明顶", "天都峰", "莲花峰", "西海大峡谷"],
        "budget_level": {
            "economy": 400,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1517722011199-e3c161974f70?w=800"]
    },
    "丽江": {
        "name": "丽江",
        "type": "domestic",
        "tags": ["古镇", "民族文化", "雪山", "休闲", "浪漫"],
        "best_season": "3-5月，9-11月",
        "best_for": ["culture", "romance", "nature", "relaxation"],
        "highlights": ["丽江古城", "玉龙雪山", "泸沽湖", "束河古镇", "蓝月谷"],
        "budget_level": {
            "economy": 350,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1548018586-b999e2948319?w=800"]
    },
    "三亚": {
        "name": "三亚",
        "type": "domestic",
        "tags": ["海滨", "度假", "水上运动", "热带", "休闲"],
        "best_season": "10月至次年4月",
        "best_for": ["beach", "resort", "water", "relaxation"],
        "highlights": ["亚龙湾", "天涯海角", "蜈支洲岛", "南山寺", "海棠湾"],
        "budget_level": {
            "economy": 400,
            "medium": 700,
            "luxury": 1500
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    # ========== 新增更多国内城市 ==========
    "苏州": {
        "name": "苏州",
        "type": "domestic",
        "tags": ["园林", "古镇", "文化", "美食", "精致"],
        "best_season": "3-5月，9-11月",
        "best_for": ["culture", "garden", "history", "romance"],
        "highlights": ["拙政园", "狮子林", "周庄", "同里", "寒山寺"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1548625361-2484861465c3?w=800"]
    },
    "青岛": {
        "name": "青岛",
        "type": "domestic",
        "tags": ["海滨", "啤酒", "欧式建筑", "海鲜", "夏季"],
        "best_season": "6-9月",
        "best_for": ["beach", "food", "modern", "family"],
        "highlights": ["栈桥", "崂山", "八大关", "啤酒博物馆", "金沙滩"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1528493775063-6d1c4e38c3df?w=800"]
    },
    "大连": {
        "name": "大连",
        "type": "domestic",
        "tags": ["海滨", "避暑", "广场", "海鲜", "浪漫"],
        "best_season": "5-10月",
        "best_for": ["beach", "romance", "family", "summer"],
        "highlights": ["星海广场", "老虎滩", "金石滩", "旅顺", "发现王国"],
        "budget_level": {
            "economy": 350,
            "medium": 550,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800"]
    },
    "哈尔滨": {
        "name": "哈尔滨",
        "type": "domestic",
        "tags": ["冰雪", "俄式建筑", "滑雪", "中央大街", "冬"],
        "best_season": "12-2月（冰雪节）",
        "best_for": ["winter", "snow", "architecture", "adventure"],
        "highlights": ["冰雪大世界", "圣索菲亚教堂", "中央大街", "太阳岛", "亚布力"],
        "budget_level": {
            "economy": 350,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1566432548212-aca84e72077b?w=800"]
    },
    "武汉": {
        "name": "武汉",
        "type": "domestic",
        "tags": ["江湖", "樱花", "美食", "历史", "英雄"],
        "best_season": "3-5月（樱花）",
        "best_for": ["nature", "food", "history", "modern"],
        "highlights": ["黄鹤楼", "东湖", "武汉大学", "长江大桥", "户部巷"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 750
        },
        "images": ["https://images.unsplash.com/photo-1548268770-66184a21657e?w=800"]
    },
    "长沙": {
        "name": "长沙",
        "type": "domestic",
        "tags": ["美食", "娱乐", "夜生活", "橘子洲", "火"],
        "best_season": "全年皆宜",
        "best_for": ["food", "nightlife", "entertainment", "modern"],
        "highlights": ["橘子洲", "岳麓山", "太平街", "湖南卫视", "文和友"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1558583620-f6e8ef1d1f33?w=800"]
    },
    "昆明": {
        "name": "昆明",
        "type": "domestic",
        "tags": ["春城", "花卉", "气候", "民族文化", "休闲"],
        "best_season": "全年皆宜",
        "best_for": ["nature", "culture", "relaxation", "weather"],
        "highlights": ["石林", "滇池", "西山", "翠湖", "民族村"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "贵阳": {
        "name": "贵阳",
        "type": "domestic",
        "tags": ["避暑", "酸汤", "山水", "气候", "美食"],
        "best_season": "5-10月",
        "best_for": ["nature", "food", "weather", "relaxation"],
        "highlights": ["青岩古镇", "黔灵山", "甲秀楼", "花溪", "天河潭"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "乌鲁木齐": {
        "name": "乌鲁木齐",
        "type": "domestic",
        "tags": ["西域", "大巴扎", "雪山", "美食", "民族"],
        "best_season": "6-9月",
        "best_for": ["culture", "food", "adventure", "nature"],
        "highlights": ["天山天池", "大巴扎", "红山", "南山", "新疆博物馆"],
        "budget_level": {
            "economy": 400,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "兰州": {
        "name": "兰州",
        "type": "domestic",
        "tags": ["牛肉面", "黄河", "西部", "丝绸之路", "美食"],
        "best_season": "5-10月",
        "best_for": ["food", "history", "culture", "nature"],
        "highlights": ["中山桥", "白塔山", "水车博览园", "甘肃省博物馆", "兴隆山"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "西宁": {
        "name": "西宁",
        "type": "domestic",
        "tags": ["夏都", "青海湖", "高原", "避暑", "藏文化"],
        "best_season": "6-9月",
        "best_for": ["nature", "culture", "weather", "adventure"],
        "highlights": ["青海湖", "塔尔寺", "东关清真大寺", "日月山", "藏医药博物馆"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "银川": {
        "name": "银川",
        "type": "domestic",
        "tags": ["西夏", "沙漠", "黄河", "葡萄", "历史"],
        "best_season": "5-10月",
        "best_for": ["history", "culture", "nature", "adventure"],
        "highlights": ["沙坡头", "镇北堡", "西夏陵", "贺兰山", "水洞沟"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 800
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "呼和浩特": {
        "name": "呼和浩特",
        "type": "domestic",
        "tags": ["草原", "蒙古文化", "烤肉", "沙漠", "风情"],
        "best_season": "6-9月",
        "best_for": ["culture", "nature", "food", "adventure"],
        "highlights": ["大召寺", "昭君墓", "内蒙古博物馆", "草原", "沙漠"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "太原": {
        "name": "太原",
        "type": "domestic",
        "tags": ["晋商", "古建", "煤炭", "面食", "历史"],
        "best_season": "5-10月",
        "best_for": ["history", "culture", "food", "architecture"],
        "highlights": ["晋祠", "双塔寺", "蒙山", "山西博物馆", "迎泽公园"],
        "budget_level": {
            "economy": 250,
            "medium": 400,
            "luxury": 700
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "济南": {
        "name": "济南",
        "type": "domestic",
        "tags": ["泉城", "趵突泉", "大明湖", "美食", "历史"],
        "best_season": "4-10月",
        "best_for": ["nature", "history", "culture", "relaxation"],
        "highlights": ["趵突泉", "大明湖", "千佛山", "黑虎泉", "芙蓉街"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 750
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "郑州": {
        "name": "郑州",
        "type": "domestic",
        "tags": ["中原", "少林寺", "黄河", "历史", "交通"],
        "best_season": "4-10月",
        "best_for": ["history", "culture", "nature", "modern"],
        "highlights": ["少林寺", "黄河风景名胜区", "嵩山", "河南博物院", "二七塔"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 750
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "南昌": {
        "name": "南昌",
        "type": "domestic",
        "tags": ["英雄城", "滕王阁", "瓷器", "美食", "革命"],
        "best_season": "4-10月",
        "best_for": ["history", "culture", "food", "modern"],
        "highlights": ["滕王阁", "八一起义纪念馆", "梅岭", "鄱阳湖", "秋水广场"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 750
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "合肥": {
        "name": "合肥",
        "type": "domestic",
        "tags": ["科技", "黄山门户", "历史", "美食", "园林"],
        "best_season": "4-10月",
        "best_for": ["culture", "nature", "modern", "food"],
        "highlights": ["三河古镇", "李鸿章故居", "巢湖", "安徽博物院", "逍遥津"],
        "budget_level": {
            "economy": 280,
            "medium": 450,
            "luxury": 750
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "福州": {
        "name": "福州",
        "type": "domestic",
        "tags": ["榕城", "三坊七巷", "海鲜", "温泉", "历史"],
        "best_season": "9月至次年5月",
        "best_for": ["culture", "food", "nature", "history"],
        "highlights": ["三坊七巷", "鼓山", "西湖公园", "马尾船政", "永泰温泉"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 850
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "海口": {
        "name": "海口",
        "type": "domestic",
        "tags": ["椰城", "免税", "海南门户", "美食", "热带"],
        "best_season": "10月至次年4月",
        "best_for": ["beach", "shopping", "food", "relaxation"],
        "highlights": ["假日海滩", "骑楼老街", "火山口公园", "东寨港", "免税店"],
        "budget_level": {
            "economy": 350,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "澳门": {
        "name": "澳门",
        "type": "domestic",
        "tags": ["赌城", "葡式建筑", "美食", "购物", "文化"],
        "best_season": "全年皆宜",
        "best_for": ["entertainment", "culture", "food", "shopping"],
        "highlights": ["威尼斯人", "大三巴牌坊", "妈阁庙", "渔人码头", "新葡京"],
        "budget_level": {
            "economy": 500,
            "medium": 1000,
            "luxury": 2000
        },
        "images": ["https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800"]
    },
    "敦煌": {
        "name": "敦煌",
        "type": "domestic",
        "tags": ["莫高窟", "沙漠", "丝绸之路", "壁画", "历史"],
        "best_season": "5-10月",
        "best_for": ["history", "culture", "adventure", "art"],
        "highlights": ["莫高窟", "鸣沙山", "月牙泉", "阳关", "玉门关"],
        "budget_level": {
            "economy": 400,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1469854524868-4f2a8d7e0a8c?w=800"]
    },
    "敦煌": {
        "name": "敦煌",
        "type": "domestic",
        "tags": ["莫高窟", "沙漠", "丝绸之路", "壁画", "历史"],
        "best_season": "5-10月",
        "best_for": ["history", "culture", "adventure", "art"],
        "highlights": ["莫高窟", "鸣沙山", "月牙泉", "阳关", "玉门关"],
        "budget_level": {
            "economy": 400,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1469854524868-4f2a8d7e0a8c?w=800"]
    },
    "桂林": {
        "name": "桂林",
        "type": "domestic",
        "tags": ["山水", "漓江", "喀斯特", "摄影", "休闲"],
        "best_season": "4-10月",
        "best_for": ["nature", "photography", "scenery", "relaxation"],
        "highlights": ["漓江", "阳朔西街", "象鼻山", "芦笛岩", "龙脊梯田"],
        "budget_level": {
            "economy": 350,
            "medium": 550,
            "luxury": 900
        },
        "images": ["https://images.unsplash.com/photo-1558583620-f6e8ef1d1f33?w=800"]
    },
    "九寨沟": {
        "name": "九寨沟",
        "type": "domestic",
        "tags": ["自然风光", "湖泊", "彩林", "世界遗产", "摄影"],
        "best_season": "9-11月",
        "best_for": ["nature", "photography", "scenery", "hiking"],
        "highlights": ["诺日朗瀑布", "五花海", "长海", "镜海", "珍珠滩"],
        "budget_level": {
            "economy": 450,
            "medium": 700,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800"]
    },
    "黄山": {
        "name": "黄山",
        "type": "domestic",
        "tags": ["自然风光", "山景", "云海", "日出", "世界遗产"],
        "best_season": "4-6月，9-11月",
        "best_for": ["nature", "photography", "hiking", "scenery"],
        "highlights": ["迎客松", "光明顶", "天都峰", "莲花峰", "西海大峡谷"],
        "budget_level": {
            "economy": 400,
            "medium": 600,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1517722011199-e3c161974f70?w=800"]
    }
}

# 国际目的地数据库
INTERNATIONAL_DESTINATIONS_DB = {
    "日本": {
        "name": "日本",
        "name_en": "Japan",
        "type": "international",
        "tags": ["文化", "美食", "购物", "动漫", "温泉"],
        "best_season": "春季（樱花）或秋季（红叶）",
        "best_for": ["culture", "food", "shopping", "nature"],
        "highlights": ["东京", "京都", "大阪", "北海道", "富士山"],
        "budget_level": {
            "economy": 800,
            "medium": 1500,
            "luxury": 3000
        },
        "images": ["https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=800"]
    },
    "泰国": {
        "name": "泰国",
        "name_en": "Thailand",
        "type": "international",
        "tags": ["海滨", "美食", "佛教", "购物", "性价比"],
        "best_season": "11月至次年2月",
        "best_for": ["beach", "food", "relaxation", "shopping"],
        "highlights": ["曼谷", "清迈", "普吉岛", "甲米", "苏梅岛"],
        "budget_level": {
            "economy": 500,
            "medium": 1000,
            "luxury": 2000
        },
        "images": ["https://images.unsplash.com/photo-1552465011-b4e21bf6e79a?w=800"]
    },
    "新加坡": {
        "name": "新加坡",
        "name_en": "Singapore",
        "type": "international",
        "tags": ["城市", "美食", "购物", "家庭", "花园城市"],
        "best_season": "全年皆宜",
        "best_for": ["city", "food", "shopping", "family"],
        "highlights": ["滨海湾", "圣淘沙", "牛车水", "乌节路", "植物园"],
        "budget_level": {
            "economy": 600,
            "medium": 1200,
            "luxury": 2500
        },
        "images": ["https://images.unsplash.com/photo-1565967511849-76a60a516170?w=800"]
    },
    "韩国": {
        "name": "韩国",
        "name_en": "Korea",
        "type": "international",
        "tags": ["文化", "购物", "美食", "韩流", "四季"],
        "best_season": "春季或秋季",
        "best_for": ["shopping", "culture", "food"],
        "highlights": ["首尔", "济州岛", "釜山", "庆州", "南怡岛"],
        "budget_level": {
            "economy": 500,
            "medium": 1000,
            "luxury": 2000
        },
        "images": ["https://images.unsplash.com/photo-1538485399081-7191377e8241?w=800"]
    },
    "马来西亚": {
        "name": "马来西亚",
        "name_en": "Malaysia",
        "type": "international",
        "tags": ["多元文化", "美食", "海滩", "自然", "性价比"],
        "best_season": "全年皆宜",
        "best_for": ["culture", "food", "beach", "nature"],
        "highlights": ["吉隆坡", "槟城", "马六甲", "沙巴", "兰卡威"],
        "budget_level": {
            "economy": 400,
            "medium": 800,
            "luxury": 1500
        },
        "images": ["https://images.unsplash.com/photo-1516216964975-62a19d762f13?w=800"]
    },
    "越南": {
        "name": "越南",
        "name_en": "Vietnam",
        "type": "international",
        "tags": ["历史", "自然", "美食", "性价比", "法式"],
        "best_season": "11月至次年4月",
        "best_for": ["history", "nature", "food", "budget"],
        "highlights": ["河内", "胡志明市", "岘港", "会安", "下龙湾"],
        "budget_level": {
            "economy": 300,
            "medium": 600,
            "luxury": 1200
        },
        "images": ["https://images.unsplash.com/photo-1505816014357-96b5ff457e9a?w=800"]
    },
    "法国": {
        "name": "法国",
        "name_en": "France",
        "type": "international",
        "tags": ["浪漫", "艺术", "美食", "历史", "奢侈品"],
        "best_season": "春季或秋季",
        "best_for": ["romance", "culture", "food", "shopping"],
        "highlights": ["巴黎", "普罗旺斯", "尼斯", "里昂", "卢瓦尔河谷"],
        "budget_level": {
            "economy": 1200,
            "medium": 2500,
            "luxury": 5000
        },
        "images": ["https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800"]
    },
    "意大利": {
        "name": "意大利",
        "name_en": "Italy",
        "type": "international",
        "tags": ["历史", "艺术", "美食", "时尚", "浪漫"],
        "best_season": "春季或秋季",
        "best_for": ["history", "culture", "food", "romance"],
        "highlights": ["罗马", "佛罗伦萨", "威尼斯", "米兰", "阿玛尔菲"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800"]
    },
    # ========== 新增更多国际目的地 ==========
    "德国": {
        "name": "德国",
        "name_en": "Germany",
        "type": "international",
        "tags": ["历史", "文化", "城堡", "啤酒", "汽车"],
        "best_season": "5-9月",
        "best_for": ["history", "culture", "nature", "modern"],
        "highlights": ["柏林", "慕尼黑", "新天鹅堡", "科隆", "黑森林"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1580537659466-95a8b2e1da99?w=800"]
    },
    "西班牙": {
        "name": "西班牙",
        "name_en": "Spain",
        "type": "international",
        "tags": ["热情", "艺术", "美食", "海滩", "足球"],
        "best_season": "5-9月",
        "best_for": ["culture", "beach", "food", "nightlife"],
        "highlights": ["马德里", "巴塞罗那", "塞维利亚", "格拉纳达", "瓦伦西亚"],
        "budget_level": {
            "economy": 900,
            "medium": 1800,
            "luxury": 3500
        },
        "images": ["https://images.unsplash.com/photo-1583422409516-2895a77efded?w=800"]
    },
    "瑞士": {
        "name": "瑞士",
        "name_en": "Switzerland",
        "type": "international",
        "tags": ["自然", "滑雪", "手表", "巧克力", "小镇"],
        "best_season": "全年皆宜",
        "best_for": ["nature", "skiing", "luxury", "scenery"],
        "highlights": ["苏黎世", "因特拉肯", "少女峰", "日内瓦", "卢塞恩"],
        "budget_level": {
            "economy": 1500,
            "medium": 3000,
            "luxury": 6000
        },
        "images": ["https://images.unsplash.com/photo-1530122037265-a5f1c4e4d2e4?w=800"]
    },
    "英国": {
        "name": "英国",
        "name_en": "United Kingdom",
        "type": "international",
        "tags": ["皇室", "历史", "文化", "足球", "博物馆"],
        "best_season": "5-9月",
        "best_for": ["history", "culture", "modern", "royal"],
        "highlights": ["伦敦", "爱丁堡", "曼彻斯特", "牛津", "温莎城堡"],
        "budget_level": {
            "economy": 1200,
            "medium": 2500,
            "luxury": 5000
        },
        "images": ["https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?w=800"]
    },
    "希腊": {
        "name": "希腊",
        "name_en": "Greece",
        "type": "international",
        "tags": ["历史", "海岛", "神话", "浪漫", "美食"],
        "best_season": "4-10月",
        "best_for": ["history", "beach", "romance", "islands"],
        "highlights": ["雅典", "圣托里尼", "米科诺斯", "克里特岛", "德尔斐"],
        "budget_level": {
            "economy": 800,
            "medium": 1500,
            "luxury": 3000
        },
        "images": ["https://images.unsplash.com/photo-1533105079780-92b9be482077?w=800"]
    },
    "荷兰": {
        "name": "荷兰",
        "name_en": "Netherlands",
        "type": "international",
        "tags": ["风车", "郁金香", "运河", "艺术", "自由"],
        "best_season": "4-10月",
        "best_for": ["culture", "nature", "romance", "modern"],
        "highlights": ["阿姆斯特丹", "海牙", "鹿特丹", "风车村", "库肯霍夫公园"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1582415321395-7aa04f6c2d3e?w=800"]
    },
    "美国": {
        "name": "美国",
        "name_en": "United States",
        "type": "international",
        "tags": ["现代", "自然", "电影", "公路旅行", "多元文化"],
        "best_season": "全年皆宜",
        "best_for": ["modern", "nature", "roadtrip", "diverse"],
        "highlights": ["纽约", "洛杉矶", "旧金山", "拉斯维加斯", "大峡谷"],
        "budget_level": {
            "economy": 1200,
            "medium": 2500,
            "luxury": 5000
        },
        "images": ["https://images.unsplash.com/photo-1501594907352-04cda38ebc29?w=800"]
    },
    "澳大利亚": {
        "name": "澳大利亚",
        "name_en": "Australia",
        "type": "international",
        "tags": ["自然", "海滩", "袋鼠", "冲浪", "大堡礁"],
        "best_season": "9月至次年5月",
        "best_for": ["nature", "beach", "wildlife", "adventure"],
        "highlights": ["悉尼", "墨尔本", "大堡礁", "乌鲁鲁", "黄金海岸"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?w=800"]
    },
    "新西兰": {
        "name": "新西兰",
        "name_en": "New Zealand",
        "type": "international",
        "tags": ["自然", "极限运动", "中土世界", "纯净", "冒险"],
        "best_season": "12月至次年5月",
        "best_for": ["nature", "adventure", "scenery", "sports"],
        "highlights": ["奥克兰", "皇后镇", "米尔福德峡湾", "罗托鲁瓦", "基督城"],
        "budget_level": {
            "economy": 1200,
            "medium": 2500,
            "luxury": 5000
        },
        "images": ["https://images.unsplash.com/photo-1507699622108-4be3abd695ad?w=800"]
    },
    "加拿大": {
        "name": "加拿大",
        "name_en": "Canada",
        "type": "international",
        "tags": ["自然", "枫叶", "极光", "冰球", "友好"],
        "best_season": "6-9月",
        "best_for": ["nature", "wildlife", "scenery", "outdoors"],
        "highlights": ["多伦多", "温哥华", "蒙特利尔", "尼亚加拉瀑布", "班夫"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1503614472-8c93d56e92b1?w=800"]
    },
    "马尔代夫": {
        "name": "马尔代夫",
        "name_en": "Maldives",
        "type": "international",
        "tags": ["海岛", "蜜月", "潜水", "奢华", "度假"],
        "best_season": "11月至次年4月",
        "best_for": ["beach", "honeymoon", "luxury", "diving"],
        "highlights": ["马累", "水上屋", "潜水", "海豚", "私人岛屿"],
        "budget_level": {
            "economy": 1500,
            "medium": 3000,
            "luxury": 8000
        },
        "images": ["https://images.unsplash.com/photo-1514282401047-d79a71a590e8?w=800"]
    },
    "菲律宾": {
        "name": "菲律宾",
        "name_en": "Philippines",
        "type": "international",
        "tags": ["海岛", "海滩", "潜水", "性价比", "英语"],
        "best_season": "12月至次年5月",
        "best_for": ["beach", "diving", "islands", "budget"],
        "highlights": ["长滩岛", "薄荷岛", "巴拉望", "马尼拉", "杜马盖地"],
        "budget_level": {
            "economy": 400,
            "medium": 800,
            "luxury": 1500
        },
        "images": ["https://images.unsplash.com/photo-1558583620-f6e8ef1d1f33?w=800"]
    },
    "柬埔寨": {
        "name": "柬埔寨",
        "name_en": "Cambodia",
        "type": "international",
        "tags": ["历史", "文化", "寺庙", "性价比", "探险"],
        "best_season": "11月至次年4月",
        "best_for": ["history", "culture", "adventure", "budget"],
        "highlights": ["吴哥窟", "金边", "西哈努克", "洞里萨湖", "暹粒"],
        "budget_level": {
            "economy": 300,
            "medium": 500,
            "luxury": 1000
        },
        "images": ["https://images.unsplash.com/photo-1567787510264-045490e3a0eb?w=800"]
    },
    "阿联酋": {
        "name": "阿联酋",
        "name_en": "United Arab Emirates",
        "type": "international",
        "tags": ["奢华", "购物", "建筑", "沙漠", "现代"],
        "best_season": "11月至次年3月",
        "best_for": ["luxury", "shopping", "modern", "architecture"],
        "highlights": ["迪拜", "阿布扎比", "沙迦", "哈利法塔", "棕榈岛"],
        "budget_level": {
            "economy": 1000,
            "medium": 2500,
            "luxury": 6000
        },
        "images": ["https://images.unsplash.com/photo-1512453979798-5ea904f22790?w=800"]
    },
    "土耳其": {
        "name": "土耳其",
        "name_en": "Turkey",
        "type": "international",
        "tags": ["历史", "文化", "热气球", "美食", "欧亚"],
        "best_season": "4-10月",
        "best_for": ["history", "culture", "romance", "adventure"],
        "highlights": ["伊斯坦布尔", "卡帕多奇亚", "安塔利亚", "棉花堡", "以弗所"],
        "budget_level": {
            "economy": 600,
            "medium": 1200,
            "luxury": 2500
        },
        "images": ["https://images.unsplash.com/photo-1524231755987-7356e59dfc61?w=800"]
    },
    "埃及": {
        "name": "埃及",
        "name_en": "Egypt",
        "type": "international",
        "tags": ["古文明", "金字塔", "历史", "探险", "尼罗河"],
        "best_season": "10月至次年4月",
        "best_for": ["history", "adventure", "ancient", "culture"],
        "highlights": ["吉萨金字塔", "卢克索", "尼罗河", "红海", "帝王谷"],
        "budget_level": {
            "economy": 500,
            "medium": 1000,
            "luxury": 2000
        },
        "images": ["https://images.unsplash.com/photo-1539650116574-8efeb43e04f7?w=800"]
    },
    "印度": {
        "name": "印度",
        "name_en": "India",
        "type": "international",
        "tags": ["文化", "宗教", "美食", "色彩", "神秘"],
        "best_season": "10月至次年3月",
        "best_for": ["culture", "religion", "spiritual", "adventure"],
        "highlights": ["泰姬陵", "德里", "孟买", "金奈", "喀拉拉"],
        "budget_level": {
            "economy": 400,
            "medium": 800,
            "luxury": 1500
        },
        "images": ["https://images.unsplash.com/photo-1524492412937-b28024a79d8e?w=800"]
    },
    "葡萄牙": {
        "name": "葡萄牙",
        "name_en": "Portugal",
        "type": "international",
        "tags": ["历史", "海滩", "美食", "性价比", "航海"],
        "best_season": "4-10月",
        "best_for": ["history", "beach", "food", "budget"],
        "highlights": ["里斯本", "波尔图", "阿尔加维", "辛特拉", "卡斯凯什"],
        "budget_level": {
            "economy": 700,
            "medium": 1400,
            "luxury": 2800
        },
        "images": ["https://images.unsplash.com/photo-1555881400-74d7acaacd8b?w=800"]
    },
    "奥地利": {
        "name": "奥地利",
        "name_en": "Austria",
        "type": "international",
        "tags": ["音乐", "艺术", "城堡", "滑雪", "咖啡"],
        "best_season": "全年皆宜",
        "best_for": ["culture", "music", "nature", "history"],
        "highlights": ["维也纳", "萨尔茨堡", "因斯布鲁克", "哈尔施塔特", "美泉宫"],
        "budget_level": {
            "economy": 1000,
            "medium": 2000,
            "luxury": 4000
        },
        "images": ["https://images.unsplash.com/photo-1516551355296-8f3d8dda6ef6?w=800"]
    },
    "墨西哥": {
        "name": "墨西哥",
        "name_en": "Mexico",
        "type": "international",
        "tags": ["文化", "美食", "玛雅", "海滩", "狂欢"],
        "best_season": "12月至次年4月",
        "best_for": ["history", "beach", "food", "culture"],
        "highlights": ["墨西哥城", "坎昆", "奇琴伊察", "瓜纳华托", "图卢姆"],
        "budget_level": {
            "economy": 600,
            "medium": 1200,
            "luxury": 2500
        },
        "images": ["https://images.unsplash.com/photo-1518105779704-91da04b3c553?w=800"]
    },
    "巴西": {
        "name": "巴西",
        "name_en": "Brazil",
        "type": "international",
        "tags": ["足球", "狂欢节", "海滩", "自然", "热情"],
        "best_season": "12月至次年3月",
        "best_for": ["beach", "culture", "nature", "festival"],
        "highlights": ["里约热内卢", "圣保罗", "伊瓜苏瀑布", "亚马逊", "萨尔瓦多"],
        "budget_level": {
            "economy": 700,
            "medium": 1400,
            "luxury": 2800
        },
        "images": ["https://images.unsplash.com/photo-1483729558449-99ef09a8c325?w=800"]
    },
    "阿根廷": {
        "name": "阿根廷",
        "name_en": "Argentina",
        "type": "international",
        "tags": ["探戈", "牛肉", "葡萄酒", "自然", "足球"],
        "best_season": "10月至次年4月",
        "best_for": ["culture", "food", "nature", "adventure"],
        "highlights": ["布宜诺斯艾利斯", "伊瓜苏瀑布", "门多萨", "巴塔哥尼亚", "冰川"],
        "budget_level": {
            "economy": 800,
            "medium": 1500,
            "luxury": 3000
        },
        "images": ["https://images.unsplash.com/photo-1568252942802-9b4b9b290c19?w=800"]
    },
    "南非": {
        "name": "南非",
        "name_en": "South Africa",
        "type": "international",
        "tags": ["野生动物", "自然", "冒险", "葡萄酒", "多元"],
        "best_season": "5-9月",
        "best_for": ["wildlife", "nature", "safari", "adventure"],
        "highlights": ["开普敦", "克鲁格国家公园", "花园大道", "太阳城", "德班"],
        "budget_level": {
            "economy": 800,
            "medium": 1500,
            "luxury": 3000
        },
        "images": ["https://images.unsplash.com/photo-1547471080-75cc6c6e87d0?w=800"]
    }
}


def _generate_matching_description(
    candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    travel_scope: str,
    llm=None
) -> str:
    """
    生成目的地匹配的LLM描述

    Args:
        candidates: 候选目的地列表
        user_portrait: 用户画像
        travel_scope: 旅行范围
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    top_candidates = candidates[:3]
    destinations_text = '、'.join([c['destination'] for c in top_candidates])
    scores_text = ', '.join([f"{c['destination']}({c['match_score']}分)" for c in top_candidates])

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
            scope_text = "国内" if travel_scope == "domestic" else "国际"

            prompt = f"""请为以下目的地推荐结果生成一段自然、吸引人的描述文字（约150-200字）：

用户偏好：{user_portrait.get('description', '热爱旅行')}
旅行范围：{scope_text}
推荐目的地：{destinations_text}
匹配分数：{scores_text}

描述要求：
1. 用热情推荐的语气，让人对这些目的地充满期待
2. 解释为什么这些目的地适合用户
3. 突出每个目的地的特色和吸引力
4. 给出选择建议
5. 语言要生动有趣，有画面感

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[目的地匹配专家] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[目的地匹配专家] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述
    scope_text = "国内" if travel_scope == "domestic" else "国际"

    description = f"""根据您的旅行偏好，我们为您精心筛选了{len(candidates)}个{scope_text}目的地！🌟

🎯 最适合您的目的地推荐：

{chr(10).join([f"• {c['destination']} - 匹配度{c['match_score']}分，{c['raw_data'].get('highlights', ['精彩景点'])[:1][0] if c['raw_data'].get('highlights') else '值得一游'}" for c in top_candidates])}

💡 推荐理由：
• 这些目的地与您的兴趣偏好高度匹配
• 预算范围符合您的{user_portrait.get('budget_level', '舒适')}预算
• 旅行节奏适合您的{user_portrait.get('pace_preference', '均衡型')}偏好

建议您根据具体时间和季节选择最适合的目的地。每个目的地都有独特的魅力，等待您去探索！✨"""

    return description


def _generate_destination_explanation(
    destination: str,
    dest_data: Dict[str, Any],
    match_score: int,
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """
    为单个目的地生成LLM解释说明

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        match_score: 匹配分数
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        LLM生成的解释文本
    """
    if not llm:
        # 返回默认解释
        tags = dest_data.get("tags", [])
        highlights = dest_data.get("highlights", [])
        return f"{destination}是一个{', '.join(tags[:3])}的热门目的地，" \
               f"拥有{highlights[0] if highlights else '精彩景点'}等著名景点。" \
               f"匹配度{match_score}分，非常符合您的{user_portrait.get('travel_type')}需求。"

    try:
        tags = dest_data.get("tags", [])
        highlights = dest_data.get("highlights", [])
        user_interests = user_portrait.get("primary_interests", [])

        prompt = f"""请用2-3句话解释为什么推荐目的地：{destination}

用户画像：
- 旅行类型：{user_portrait.get('travel_type')}
- 兴趣：{', '.join(user_interests)}
- 预算：{user_portrait.get('budget_level')}
- 节奏：{user_portrait.get('pace_preference')}

目的地信息：
- 匹配分数：{match_score}/100
- 特色：{', '.join(tags[:5])}
- 亮点：{', '.join(highlights[:3])}

要求：
1. 用热情推荐的语气
2. 解释为什么这个目的地适合用户
3. 语言简洁生动，2-3句话
4. 不要标题和格式符号

请直接输出解释文字："""

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        explanation = response.content.strip()
        logger.info(f"[目的地匹配] 为{destination}生成解释: {len(explanation)}字")
        return explanation

    except Exception as e:
        logger.warning(f"[目的地匹配] LLM解释生成失败: {e}")
        tags = dest_data.get("tags", [])
        return f"{destination}完美契合您的{user_portrait.get('travel_type')}需求，" \
               f"这里有丰富的{', '.join(user_interests)}等待您探索。"


# ============================================================
# 匹配逻辑
# ============================================================

def calculate_match_score_with_llm(
    destination: Dict[str, Any],
    user_portrait: Dict[str, Any],
    llm=None
) -> float:
    """
    使用LLM计算目的地与用户的匹配分数

    Args:
        destination: 目的地数据
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        匹配分数 0-100
    """
    dest_name = destination.get("name", "") or destination.get("destination", "")
    user_interests = user_portrait.get("primary_interests", [])
    user_budget = user_portrait.get("budget", "medium")
    travel_type = user_portrait.get("travel_type", "")
    days = user_portrait.get("days", 5)
    travelers = user_portrait.get("total_travelers", 2)

    # 如果有LLM，使用LLM生成评分
    if llm:
        try:
            logger.info(f"🤖 [LLM] 使用LLM计算 {dest_name} 的匹配分数...")
            logger.info(f"🔑 [LLM] LLM实例类型: {type(llm).__name__}")
            # 获取目的地特色
            city_features_info = _get_city_features(dest_name)

            prompt = f"""请为以下目的地和用户匹配情况评分（0-100分）：

目的地：{dest_name}
目的地特色：{city_features_info}
用户兴趣：{', '.join(user_interests) if user_interests else '未指定'}
用户预算等级：{user_budget}
旅行类型：{travel_type}
旅行天数：{days}天
出行人数：{travelers}人

评分标准：
1. 兴趣匹配度（40分）：目的地特色与用户兴趣的匹配程度
2. 预算适配度（20分）：目的地消费水平是否适合用户预算
3. 旅行类型适合度（20分）：是否适合用户的旅行类型（亲子游/情侣游/团队游）
4. 季节适宜性（10分）：当前是否是该目的地的最佳旅行时间
5. 综合吸引力（10分）：目的地的整体吸引力

【重要】请根据该目的地的具体特色进行差异化评分！
- 如果该目的地完美契合用户需求，给90-100分
- 如果该目的地比较契合用户需求，给80-89分
- 如果该目的地一般契合用户需求，给70-79分
- 如果该目的地不太契合用户需求，给60-69分
- 避免给所有目的地打相同的分数，要根据实际情况进行区分

请只返回一个0-100之间的数字，不要任何解释文字。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            score_text = response.content.strip()

            # 尝试从LLM返回中提取数字
            import re
            score_match = re.search(r'\d+', score_text)
            if score_match:
                score = float(score_match.group())
                logger.info(f"[目的地匹配] {dest_name} LLM评分: {score}分")
                return max(0, min(100, score))

        except Exception as e:
            logger.warning(f"❌ [LLM] LLM评分失败: {e}，使用规则评分")

    # 降级到规则评分
    logger.info(f"⚙️ [规则引擎] 使用规则计算 {dest_name} 的匹配分数 (LLM未配置或失败)")
    return _calculate_rule_based_score(destination, user_portrait)


def _calculate_rule_based_score(
    destination: Dict[str, Any],
    user_portrait: Dict[str, Any],
    preferred_destinations: Set[str] = None
) -> float:
    """
    基于规则的计算（LLM失败时的降级方案）

    Args:
        destination: 目的地数据
        user_portrait: 用户画像
        preferred_destinations: 用户特殊需求中提到的城市（优先推荐）

    Returns:
        匹配分数
    """
    dest_name = destination.get("name", "") or destination.get("destination", "")
    dest_tags = destination.get("tags", [])

    # 基础分根据城市热度调整
    city_base_scores = {
        # 国内一线城市
        "北京": 75, "上海": 75,
        # 热门旅游城市
        "成都": 78, "重庆": 76, "西安": 74, "杭州": 76,
        "广州": 72, "深圳": 70,
        "南京": 71, "武汉": 70, "长沙": 69,
        "厦门": 73, "三亚": 74, "丽江": 72, "桂林": 70,
        "苏州": 71, "青岛": 69, "大连": 68,
        # 国际热门目的地
        "日本": 82, "东京": 80, "京都": 79, "大阪": 78,
        "韩国": 79, "首尔": 78, "釜山": 75, "济州岛": 76,
        "泰国": 85, "曼谷": 81, "清迈": 78, "普吉岛": 82, "芭提雅": 77,
        "新加坡": 84,
        "马来西亚": 80, "吉隆坡": 78, "槟城": 76,
        "瑞士": 86, "法国": 85, "意大利": 83,
        "英国": 82, "西班牙": 81, "德国": 80,
        "希腊": 84, "冰岛": 83, "挪威": 81,
        "美国": 82, "澳大利亚": 81, "新西兰": 80,
        "越南": 78, "柬埔寨": 76, "印度尼西亚": 77,
        "菲律宾": 76, "印度": 75, "尼泊尔": 74,
    }
    score = float(city_base_scores.get(dest_name, 65))

    # 获取用户兴趣
    user_interests = user_portrait.get("primary_interests", [])
    if not user_interests:
        # 尝试从interests字段获取
        user_interests = user_portrait.get("interests", [])

    # 目的地标签
    city_tags = destination.get("tags", [])

    # 兴趣匹配加分 (最多+15分)
    interest_match_count = 0
    for interest in user_interests:
        interest_lower = interest.lower()
        # 检查是否匹配城市标签
        for tag in city_tags:
            if interest_lower in tag.lower() or tag.lower() in interest_lower:
                interest_match_count += 1
                break
        # 检查是否匹配特色
        highlights = destination.get("highlights", [])
        for highlight in highlights:
            if interest_lower in highlight.lower() or highlight.lower() in interest_lower:
                interest_match_count += 1
                break

    score += min(15, interest_match_count * 5)

    # 旅行类型加成 (最多+10分) - 扩展到国际目的地
    travel_type = user_portrait.get("travel_type", "")
    pace = user_portrait.get("pace_preference", "")

    if travel_type == "亲子游":
        # 国内+国际亲子友好目的地
        family_friendly = ["成都", "上海", "广州", "新加坡", "东京", "大阪", "香港"]
        if dest_name in family_friendly:
            score += 8
    elif travel_type == "情侣游":
        romantic_spots = ["丽江", "厦门", "三亚", "桂林", "巴黎", "普吉岛", "巴厘岛", "济州岛", "清迈"]
        if dest_name in romantic_spots:
            score += 8
    elif "休闲" in travel_type or "放松" in travel_type:
        relaxing_places = ["成都", "厦门", "三亚", "丽江", "桂林", "普吉岛", "济州岛", "巴厘岛", "冲绳"]
        if dest_name in relaxing_places:
            score += 6
    elif "文化" in travel_type or "历史" in travel_type:
        cultural_spots = ["北京", "西安", "南京", "京都", "奈良", "雅典", "罗马", "开罗", "伊斯坦布尔"]
        if dest_name in cultural_spots:
            score += 8
    elif "购物" in travel_type:
        shopping_paradise = ["上海", "香港", "东京", "大阪", "首尔", "新加坡", "迪拜"]
        if dest_name in shopping_paradise:
            score += 8
    elif "冒险" in travel_type or "户外" in travel_type:
        adventure_spots = ["瑞士", "新西兰", "挪威", "冰岛", "澳大利亚", "尼泊尔"]
        if dest_name in adventure_spots:
            score += 8

    # 节奏偏好匹配 - 扩展到国际目的地
    if pace == "慢节奏" or pace == "休闲":
        slow_places = ["成都", "厦门", "丽江", "桂林", "清迈", "巴厘岛", "普吉岛", "济州岛"]
        if dest_name in slow_places:
            score += 5
    elif pace == "快节奏" or pace == "紧凑":
        fast_places = ["北京", "上海", "西安", "东京", "香港", "新加坡", "曼谷"]
        if dest_name in fast_places:
            score += 5

    # 预算适配度调整 (根据预算等级)
    user_budget = user_portrait.get("budget", "medium")
    if user_budget == "economy" or user_budget == "low":
        # 经济型，偏好性价比高的地方
        budget_friendly = ["泰国", "越南", "马来西亚", "柬埔寨", "菲律宾", "成都", "重庆", "西安"]
        if dest_name in budget_friendly:
            score += 5
        else:
            score -= 3  # 昂贵地方降分
    elif user_budget == "luxury" or user_budget == "high":
        # 豪华型，偏好高端体验
        luxury_places = ["瑞士", "法国", "新加坡", "日本", "马尔代夫", "迪拜"]
        if dest_name in luxury_places:
            score += 5

    # 🔥 新增：特殊需求中提到的城市优先推荐加分
    if preferred_destinations and dest_name in preferred_destinations:
        bonus_score = 20  # 给予20分的额外加分，确保排名第一
        score += bonus_score
        logger.info(f"[地区匹配] {dest_name} 在特殊需求中被提到，额外加分 +{bonus_score}")

    # 添加小幅度随机变化，避免分数完全相同
    import random
    score += random.uniform(-2, 3)

    return max(50, min(98, score))


def _get_city_features(city_name: str) -> str:
    """获取城市特色描述（包含国内和国际热门目的地）"""
    city_features_db = {
        # 国内城市
        "成都": "美食之都，大熊猫基地，悠闲慢生活，茶馆文化，川菜发源地",
        "重庆": "山城夜景，火锅之都，洪崖洞，李子坝轻轨穿楼，8D魔幻城市",
        "广州": "花城，早茶文化，广州塔小蛮腰，珠江夜游，美食天堂",
        "长沙": "星城，橘子洲头，岳麓书院，湘菜美食，芒果台总部，夜生活丰富",
        "北京": "六朝古都，故宫长城，天坛颐和，胡同文化，政治文化中心",
        "上海": "魔都，外滩万国建筑群，东方明珠，南京路购物，现代都市",
        "西安": "十三朝古都，兵马俑，大雁塔，古城墙，大唐不夜城，美食古都",
        "杭州": "人间天堂，西湖美景，雷峰塔，灵隐寺，龙井茶，江南水乡",
        "南京": "六朝古都，中山陵，夫子庙，秦淮河，民国风情，鸭血粉丝汤",
        "武汉": "江城，黄鹤楼，东湖绿道，热干面，樱花胜地，九省通衢",
        "厦门": "海上花园，鼓浪屿，文艺小资，南普陀，海滨风光，曾厝垵",
        "三亚": "东方夏威夷，亚龙湾，天涯海角，海滨度假，热带天堂，海鲜美食",
        "丽江": "艳遇之城，丽江古城，玉龙雪山，束河古镇，纳西文化，慢生活",
        "桂林": "山水甲天下，漓江风光，象鼻山，阳朔西街，龙脊梯田，喀斯特地貌",

        # 国际热门目的地
        "日本": "樱花之国，富士山，京都古寺，温泉文化，动漫潮流，和风美食，购物天堂",
        "东京": "日本首都，涩谷十字路口，东京塔，秋叶原动漫街，浅草寺，现代与传统交融",
        "京都": "千年古都，清水寺，伏见稻荷大社，艺伎文化，祗园古街，传统和服体验",
        "大阪": "美食之都，大阪城，道顿堀美食街，环球影城，章鱼烧，热情好客",

        "韩国": "韩流文化，首尔塔，整容美容，化妆品购物，炸鸡啤酒，四季分明",
        "首尔": "韩国首都，景福宫，明洞购物街，弘大夜生活，江南区，韩流体验",
        "釜山": "海滨城市，海云台海滩，札嘎其市场，海鲜美食，电影节举办地",
        "济州岛": "韩国夏威夷，汉拿山，火山地貌，免税购物，蜜月胜地",

        "泰国": "微笑之国，佛教文化，热带海滩，泰式按摩，夜市美食，性价比高",
        "曼谷": "泰国首都，大皇宫，水上市场，考山路，暹罗广场，繁华都市",
        "清迈": "泰北玫瑰，古城寺庙，大象营，夜市美食，手工艺品，慢生活",
        "普吉岛": "泰国海岛，芭东海滩，皮皮岛，潜水天堂，夜生活丰富",
        "芭提雅": "海滨度假，东方巴黎，人妖表演，海滩娱乐，水上活动",

        "新加坡": "花园城市，滨海湾花园，鱼尾狮，圣淘沙，多元文化，美食天堂，干净安全",

        "马来西亚": "亚洲多元国家，双子塔，槟城美食，沙巴海岛，马六甲古城",
        "吉隆坡": "马来西亚首都，双子塔，独立广场，唐人街，美食融合",
        "槟城": "美食之都，乔治市古迹，街头艺术，小吃天堂",

        "瑞士": "阿尔卑斯山，少女峰，琉森湖，手表军刀，滑雪胜地，奶酪巧克力",
        "法国": "浪漫之都，埃菲尔铁塔，卢浮宫，红酒香水，时尚艺术",
        "意大利": "罗马帝国遗迹，威尼斯水城，佛罗伦萨艺术，美食披萨，时尚之都",

        # 更多国际目的地...
        "美国": "自由女神，大峡谷，好莱坞，迪士尼，百老汇，多元文化",
        "澳大利亚": "悉尼歌剧院，大堡礁，袋鼠考拉，海滩冲浪，自然奇观",
        "英国": "大本钟，伦敦塔桥，大英博物馆，皇室文化，下午茶",
        "德国": "慕尼黑啤酒，新天鹅堡，汽车工业，圣诞市场，严谨高效",
        "西班牙": "圣家堂，弗拉明戈舞，海鲜饭，午睡文化，热情奔放",
        "希腊": "雅典卫城，圣托里尼日落，爱琴海，神话起源，蓝白世界",
        "冰岛": "北极光，蓝湖温泉，冰川火山，极昼极夜，自然奇迹",
        "挪威": "峡湾风光，维京海盗，午夜太阳，三文鱼，高福利",
    }

    return city_features_db.get(city_name, f"{city_name}是一个独特的旅游目的地，拥有丰富的文化、美食和自然风光")


def estimate_budget_with_llm(
    city_name: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    使用LLM估算旅行预算

    Args:
        city_name: 城市名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        预算信息 {total, per_person, currency}
    """
    user_budget = user_portrait.get("budget", "medium")
    days = user_portrait.get("days", 5)
    travelers = user_portrait.get("total_travelers", 2)

    # 如果有LLM，使用LLM估算预算
    if llm:
        try:
            logger.info(f"🤖 [LLM] 使用LLM估算 {city_name} 的预算...")
            logger.info(f"🔑 [LLM] LLM实例类型: {type(llm).__name__}")
            city_features = _get_city_features(city_name)
            budget_level_map = {"economy": "经济型", "medium": "舒适型", "luxury": "品质型"}

            prompt = f"""请为以下旅行估算每日人均预算（只返回数字，不要任何文字）：

目的地：{city_name}
目的地特色：{city_features}
用户预算等级：{budget_level_map[user_budget]}
旅行天数：{days}天
出行人数：{travelers}人

预算说明：
- 经济型：青年旅舍、经济型酒店、公共交通、当地美食
- 舒适型：三星酒店、快捷酒店、出租车+地铁、特色餐厅
- 品质型：高档酒店、专车接送、网红餐厅、优质服务

请只返回一个数字，代表每日人均预算（单位：元）。

例如：成都舒适型，5天2人，返回：650"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            budget_text = response.content.strip()

            # 尝试从LLM返回中提取数字
            import re
            budget_match = re.search(r'\d+', budget_text)
            if budget_match:
                daily_budget = int(budget_match.group())
                total_budget = daily_budget * days * travelers
                logger.info(f"[目的地匹配] {city_name} LLM估算预算: {daily_budget}元/天")

                return {
                    "total": total_budget,
                    "per_person": int(total_budget / travelers),
                    "currency": "CNY"
                }

        except Exception as e:
            logger.warning(f"❌ [LLM] LLM估算预算失败: {e}，使用规则计算")

    # 降级：使用规则计算预算
    logger.info(f"⚙️ [规则引擎] 使用规则计算 {city_name} 的预算 (LLM未配置或失败)")
    return _estimate_budget_by_rules(city_name, user_budget, days, travelers)


def _estimate_budget_by_rules(
    city_name: str,
    user_budget: str,
    days: int,
    travelers: int
) -> Dict[str, Any]:
    """基于规则计算预算（LLM失败时的降级方案）"""
    # 城市基础费用
    city_base_costs = {
        # 一线城市
        "北京": {"economy": 500, "medium": 800, "luxury": 1500},
        "上海": {"economy": 500, "medium": 800, "luxury": 1500},
        "广州": {"economy": 450, "medium": 700, "luxury": 1300},
        # 新一线
        "成都": {"economy": 400, "medium": 650, "luxury": 1200},
        "重庆": {"economy": 380, "medium": 600, "luxury": 1100},
        "杭州": {"economy": 420, "medium": 680, "luxury": 1250},
        "西安": {"economy": 380, "medium": 600, "luxury": 1100},
        "南京": {"economy": 400, "medium": 650, "luxury": 1200},
        "武汉": {"economy": 380, "medium": 620, "luxury": 1150},
        "长沙": {"economy": 350, "medium": 550, "luxury": 1000},
        # 旅游城市
        "厦门": {"economy": 400, "medium": 650, "luxury": 1200},
        "三亚": {"economy": 450, "medium": 750, "luxury": 1400},
        "丽江": {"economy": 350, "medium": 550, "luxury": 1000},
        "桂林": {"economy": 320, "medium": 500, "luxury": 900},
    }

    # 获取城市费用，默认400
    daily_budget = city_base_costs.get(city_name, {}).get(user_budget, 400)

    total_budget = daily_budget * days * travelers

    return {
        "total": total_budget,
        "per_person": int(total_budget / travelers),
        "currency": "CNY"
    }


def _batch_calculate_match_scores_with_llm(
    destinations_db: Dict[str, Any],
    user_portrait: Dict[str, Any],
    llm,
    preferred_destinations: Set[str] = None
) -> List[Dict[str, Any]]:
    """
    批量使用LLM计算所有目的地的匹配分数（性能优化版本）

    将所有目的地一次性发送给LLM进行评分，而不是逐个调用。
    这样可以将14个LLM调用（~30秒）优化为1次批量调用（~3秒）。

    Args:
        destinations_db: 目的地数据库
        user_portrait: 用户画像
        llm: LLM实例
        preferred_destinations: 用户特殊需求中提到的城市（优先推荐）

    Returns:
        候选目的地列表（带匹配分数）
    """
    user_interests = user_portrait.get("primary_interests", [])
    user_budget = user_portrait.get("budget", "medium")
    travel_type = user_portrait.get("travel_type", "")
    days = user_portrait.get("days", 5)
    travelers = user_portrait.get("total_travelers", 2)

    # 构建目的地列表信息
    destinations_info = []
    for dest_name, dest_data in destinations_db.items():
        city_features = _get_city_features(dest_name)
        destinations_info.append({
            "name": dest_name,
            "features": city_features,
            "tags": dest_data.get("tags", [])
        })

    # 构建批量评分prompt
    budget_level_map = {"economy": "经济型", "medium": "舒适型", "luxury": "品质型"}

    # 🔥 新增：特殊需求说明
    special_requests_info = ""
    if preferred_destinations:
        special_requests_info = f"""
【用户特殊需求】
用户明确提到想去的城市：{', '.join(preferred_destinations)}
⚠️ 重要：这些城市应该在评分中获得显著加分（+20分），确保排在推荐列表的前列！
"""

    prompt = f"""请为以下所有目的地与用户需求进行匹配评分（0-100分）。

【用户信息】
兴趣：{', '.join(user_interests) if user_interests else '未指定'}
预算等级：{budget_level_map[user_budget]}
旅行类型：{travel_type}
旅行天数：{days}天
出行人数：{travelers}人
{special_requests_info}
【评分标准】
1. 兴趣匹配度（40分）：目的地特色与用户兴趣的匹配程度
2. 预算适配度（20分）：目的地消费水平是否适合用户预算
3. 旅行类型适合度（20分）：是否适合用户的旅行类型
4. 季节适宜性（10分）：当前是否是该目的地的最佳旅行时间
5. 综合吸引力（10分）：目的地的整体吸引力
6. 🔥 特殊需求优先级（额外+20分）：如果城市在用户特殊需求中被提到，给予额外加分

【目的地列表】
{_format_destinations_for_batch_scoring(destinations_info)}

【重要要求】
请为每个目的地给出差异化评分！
- 如果该目的地完美契合用户需求，给90-100分
- 如果该目的地比较契合用户需求，给80-89分
- 如果该目的地一般契合用户需求，给70-79分
- 如果该目的地不太契合用户需求，给60-69分
- 避免给所有目的地打相同的分数

【输出格式】
请严格按照以下JSON格式输出，不要包含任何其他文字：
{{
  "scores": [
    {{"destination": "城市名", "score": 分数}},
    {{"destination": "城市名", "score": 分数}},
    ...
  ]
}}"""

    try:
        logger.info(f"[批量LLM评分] 开始为{len(destinations_info)}个目的地批量评分...")

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()

        logger.info(f"[批量LLM评分] LLM响应长度: {len(response_text)}字符")

        # 解析LLM返回的JSON
        import json
        import re

        # 尝试提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)

            # 构建候选列表
            candidates = []
            score_dict = {item["destination"]: item["score"] for item in result.get("scores", [])}

            for dest_name, dest_data in destinations_db.items():
                match_score = score_dict.get(dest_name, 70)  # 默认70分

                # 🔥 新增：为特殊需求中的城市添加额外加分
                if preferred_destinations and dest_name in preferred_destinations:
                    match_score += 20  # 额外加分
                    logger.info(f"[批量LLM评分] {dest_name} 在用户特殊需求中提到，额外加分 +20")

                # 使用规则估算预算
                estimated_budget = _estimate_budget_rule_based(dest_name, dest_data, user_portrait)

                candidates.append({
                    "destination": dest_name,
                    "match_score": int(match_score),
                    "raw_data": dest_data,
                    "estimated_budget": estimated_budget,
                    "is_preferred": dest_name in preferred_destinations if preferred_destinations else False  # 🔥 标记为优先推荐
                })

            logger.info(f"[批量LLM评分] 批量评分完成，获得{len(candidates)}个候选目的地")
            logger.info(f"[批量LLM评分] 评分范围: {min(score_dict.values())} - {max(score_dict.values())}")

            return candidates

        else:
            logger.warning(f"[批量LLM评分] 无法从响应中提取JSON，使用规则评分")
            raise ValueError("无法解析LLM响应")

    except Exception as e:
        logger.warning(f"[批量LLM评分] 批量LLM评分失败: {e}，回退到规则评分")

        # 回退到规则评分
        candidates = []
        for dest_name, dest_data in destinations_db.items():
            match_score = _calculate_rule_based_score(dest_data, user_portrait, preferred_destinations)
            estimated_budget = _estimate_budget_rule_based(dest_name, dest_data, user_portrait)
            candidates.append({
                "destination": dest_name,
                "match_score": int(match_score),
                "raw_data": dest_data,
                "estimated_budget": estimated_budget,
                "is_preferred": dest_name in preferred_destinations if preferred_destinations else False
            })
        return candidates


def _format_destinations_for_batch_scoring(destinations_info: List[Dict]) -> str:
    """格式化目的地列表用于批量评分"""
    lines = []
    for i, dest in enumerate(destinations_info, 1):
        lines.append(f"{i}. {dest['name']} - 特色:{dest['features']}, 标签:{','.join(dest['tags'][:3])}")
    return '\n'.join(lines)


def _estimate_budget_rule_based(
    city_name: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any]
) -> Dict[str, Any]:
    """
    基于规则估算预算（性能优化版本，不调用LLM）

    Args:
        city_name: 城市名称
        dest_data: 目的地数据
        user_portrait: 用户画像

    Returns:
        预算信息 {total, per_person, currency}
    """
    user_budget = user_portrait.get("budget", "medium")
    days = user_portrait.get("days", 5)
    travelers = user_portrait.get("total_travelers", 2)

    # 直接调用已有的规则预算计算函数
    return _estimate_budget_by_rules(city_name, user_budget, days, travelers)


def match_destinations(
    user_portrait: Dict[str, Any],
    travel_scope: str,
    llm=None
) -> Dict[str, Any]:
    """
    匹配目的地（批量LLM评分版本）

    Args:
        user_portrait: 用户画像
        travel_scope: 旅行范围（domestic/international）
        llm: LLM实例（可选，用于批量评分）

    Returns:
        候选目的地列表（带匹配分数）和LLM描述
    """
    logger.info(f"[地区匹配] 开始匹配{travel_scope}目的地")

    # 🔥 新增：提取特殊需求中的城市名称，给予优先推荐
    special_requests = user_portrait.get("special_requests", "")
    preferred_destinations = _extract_destinations_from_special_requests(special_requests, llm)

    if preferred_destinations:
        logger.info(f"[地区匹配] 从特殊需求中识别到优先目的地: {preferred_destinations}")

    # 选择数据库
    if travel_scope == "domestic":
        db = DOMESTIC_DESTINATIONS_DB
    else:
        db = INTERNATIONAL_DESTINATIONS_DB

    # 🔧 性能优化: 使用批量LLM评分，一次性为所有目的地评分
    # 将14个LLM调用（~30秒）优化为1次批量调用（~3秒）
    if llm:
        logger.info(f"[地区匹配] 使用批量LLM评分（优化版本）")
        candidates = _batch_calculate_match_scores_with_llm(db, user_portrait, llm, preferred_destinations)
    else:
        logger.info(f"[地区匹配] 使用规则引擎评分（LLM未配置）")
        candidates = []
        for dest_name, dest_data in db.items():
            match_score = _calculate_rule_based_score(dest_data, user_portrait, preferred_destinations)
            estimated_budget = _estimate_budget_rule_based(dest_name, dest_data, user_portrait)
            candidates.append({
                "destination": dest_name,
                "match_score": int(match_score),
                "raw_data": dest_data,
                "estimated_budget": estimated_budget,
                "is_preferred": dest_name in preferred_destinations  # 🔥 标记为优先推荐
            })

    # 按匹配分数排序（优先推荐的会排在前面）
    candidates.sort(key=lambda x: x["match_score"], reverse=True)

    logger.info(f"[地区匹配] 匹配完成，共{len(candidates)}个候选目的地")

    # 🔧 性能优化: 不再为每个目的地单独生成LLM解释
    # 这些解释在后续流程中没有被使用，可以节省10次LLM调用（~20秒）
    # if llm:
    #     for candidate in candidates[:10]:  # 为前10个生成解释
    #         candidate["ai_explanation"] = _generate_destination_explanation(
    #             candidate["destination"],
    #             candidate["raw_data"],
    #             candidate["match_score"],
    #             user_portrait,
    #             llm
    #         )
    # else:
    #     # 没有LLM时，为前5个添加默认解释
    #     for candidate in candidates[:5]:
    #         dest_data = candidate["raw_data"]
    #         tags = dest_data.get("tags", [])
    #         highlights = dest_data.get("highlights", [])
    #         candidate["ai_explanation"] = (
    #             f"{candidate['destination']}拥有{highlights[0] if highlights else '精彩景点'}等著名景点，"
    #             f"是{', '.join(tags[:3])}的热门目的地，"
    #             f"匹配度{candidate['match_score']}分，非常符合您的需求。"
    #         )

    logger.info(f"[地区匹配] 跳过目的地解释生成（性能优化）")

    # 生成整体LLM描述
    llm_description = _generate_matching_description(
        candidates[:5],  # 前5个推荐
        user_portrait,
        travel_scope,
        llm
    )

    logger.info(f"[地区匹配] 找到{len(candidates)}个候选目的地，为其中{min(10, len(candidates))}个生成了解释")

    return {
        "candidates": candidates,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "目的地匹配专家",
            "name_en": "DestinationMatcher",
            "icon": "🗺️",
            "group": "A"
        }
    }


def destination_matcher_node(state: Dict) -> Dict:
    """
    地区匹配智能体节点（用于LangGraph）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    user_portrait = state.get("user_portrait")
    travel_scope = state.get("travel_scope")

    if not user_portrait:
        logger.error("[地区匹配] 缺少用户画像")
        state["error"] = "缺少用户画像"
        return state

    # 匹配目的地
    llm = state.get("_llm")
    matching_result = match_destinations(user_portrait, travel_scope, llm)

    candidates = matching_result.get("candidates", [])

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"地区匹配完成: 找到{len(candidates)}个候选目的地",
        name="DestinationMatcher"
    ))

    state["candidate_destinations"] = candidates
    state["matching_llm_description"] = matching_result.get("llm_description", "")
    state["messages"] = messages
    state["current_stage"] = "destinations_matched"

    return state


# ============================================================
# 独立调用函数（用于API）
# ============================================================

def find_matching_destinations(
    user_portrait: Dict[str, Any],
    travel_scope: str
) -> Dict[str, Any]:
    """
    查找匹配的目的地（独立调用）

    Args:
        user_portrait: 用户画像
        travel_scope: 旅行范围

    Returns:
        包含候选目的地的响应
    """
    candidates = match_destinations(user_portrait, travel_scope)

    return {
        "success": True,
        "candidates": candidates,
        "agent_info": {
            "name": "DestinationMatcher",
            "icon": "🗺️",
            "description": "根据用户画像匹配目的地"
        }
    }


# ============================================================
# 实时搜索版本（使用API工具）
# ============================================================

def match_destinations_realtime(
    user_portrait: Dict[str, Any],
    travel_scope: str,
    use_realtime: bool = True
) -> List[Dict[str, Any]]:
    """
    实时匹配目的地（使用API搜索工具）

    根据用户兴趣和偏好，实时搜索匹配的目的地

    Args:
        user_portrait: 用户画像
        travel_scope: 旅行范围（domestic/international）
        use_realtime: 是否使用实时搜索（默认True）

    Returns:
        候选目的地列表（带匹配分数）
    """
    logger.info(f"[地区匹配-实时] 开始实时搜索{travel_scope}目的地")

    if not use_realtime:
        # 如果不使用实时搜索，回退到数据库版本
        return match_destinations(user_portrait, travel_scope)

    # 获取用户兴趣关键词
    interests = user_portrait.get("primary_interests", [])
    interests_str = " ".join(interests) if interests else "旅游"

    try:
        # 调用目的地搜索工具
        from tradingagents.tools.travel_tools import get_destination_search_tool
        search_tool = get_destination_search_tool()

        # 根据兴趣搜索目的地
        searched_destinations = search_tool.search_destinations(
            keywords=interests_str,
            scope=travel_scope
        )

        if not searched_destinations:
            logger.warning("[地区匹配-实时] 搜索无结果，使用数据库")
            return match_destinations(user_portrait, travel_scope)

        candidates = []

        # 为搜索到的目的地生成候选卡片
        for dest in searched_destinations[:8]:  # 最多返回8个
            dest_name = dest.get("destination")
            dest_type = dest.get("type", "")

            # 标准化目的地名称（英文转中文）
            dest_name_cn = normalize_destination_name(dest_name)

            # 获取该城市的详细信息（使用搜索工具）
            from tradingagents.tools.travel_tools import get_attraction_search_tool, get_destination_search_tool
            attraction_tool = get_attraction_search_tool()
            destination_search_tool = get_destination_search_tool()

            attractions = attraction_tool.search_attractions(
                city=dest_name_cn,  # 使用中文名称搜索
                keywords="景点",
                limit=5
            )

            # 获取目的地图片（使用Unsplash）
            image_url = dest.get("image_url", "")
            if not image_url:
                try:
                    image_url = destination_search_tool._get_destination_image(dest_name_cn)
                except Exception as e:
                    logger.warning(f"[地区匹配-实时] 获取{dest_name_cn}图片失败: {e}")

            # 获取目的地的正确highlights（从数据库或根据类型生成）
            highlights = _get_destination_highlights(dest_name_cn, dest_type)

            # 构建目的地数据
            if attractions:
                highlights = [a["name"] for a in attractions[:5]]

            # 获取该城市的详细信息（使用搜索工具）
            from tradingagents.tools.travel_tools import get_attraction_search_tool, get_destination_search_tool
            attraction_tool = get_attraction_search_tool()
            destination_search_tool = get_destination_search_tool()

            attractions = attraction_tool.search_attractions(
                city=dest_name,
                keywords="景点",
                limit=5
            )

            # 获取目的地图片（使用Unsplash）
            image_url = dest.get("image_url", "")
            if not image_url:
                try:
                    image_url = destination_search_tool._get_destination_image(dest_name)
                except Exception as e:
                    logger.warning(f"[地区匹配-实时] 获取{dest_name}图片失败: {e}")

            # 构建目的地数据
            highlights = []
            if attractions:
                highlights = [a["name"] for a in attractions[:5]]

            # 计算匹配分数
            base_score = 70
            # 根据兴趣匹配加分
            for interest in interests:
                if dest_type and interest in dest_type:
                    base_score += 10

            # 计算预估费用
            user_budget = user_portrait.get("budget", "medium")
            budget_map = {"economy": 300, "medium": 500, "luxury": 800}
            daily_budget = budget_map.get(user_budget, 500)
            total_budget = daily_budget * user_portrait.get("days", 5) * user_portrait.get("total_travelers", 2)

            candidates.append({
                "destination": dest_name,
                "match_score": min(base_score, 100),
                "raw_data": {
                    "name": dest_name,
                    "type": travel_scope,
                    "tags": [dest_type] if dest_type else [],
                    "best_season": "四季皆宜",
                    "best_for": ["travel"],
                    "highlights": highlights,
                    "description": dest.get("description", f"{dest_name}特色城市"),
                    "budget_level": {
                        "economy": int(daily_budget * 0.6),
                        "medium": daily_budget,
                        "luxury": int(daily_budget * 1.5)
                    },
                    "images": [image_url] if image_url else [],
                    "image_url": image_url
                },
                "estimated_budget": {
                    "total": total_budget,
                    "per_person": int(total_budget / user_portrait.get("total_travelers", 2)),
                    "currency": "CNY"
                }
            })

        # 按匹配分数排序
        candidates.sort(key=lambda x: x["match_score"], reverse=True)

        logger.info(f"[地区匹配-实时] 实时搜索完成，找到{len(candidates)}个目的地")

        return candidates

    except Exception as e:
        logger.error(f"[地区匹配-实时] 搜索失败: {e}，使用数据库")
        return match_destinations(user_portrait, travel_scope)


# ============================================================
# 辅助函数
# ============================================================

def _get_destination_highlights(destination_name: str, dest_type: str) -> List[str]:
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
        "综合": ["热门景点", "当地特色", "文化体验", "美食探索", "购物娱乐"]
    }

    if dest_type in type_highlights:
        return type_highlights[dest_type]

    # 默认返回通用景点
    return ["著名景点", "当地美食", "文化体验", "自然风光", "购物娱乐"]
