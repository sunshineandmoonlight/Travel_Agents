"""
景点图片获取服务

使用 Unsplash 和 Pexels API，支持中英文智能搜索
"""

import os
import sys
import logging
import time
import random
import requests
from typing import Optional
from urllib.parse import quote
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger('travel_agents')

# 确定项目根目录（尝试多种方式）
def find_project_root():
    """查找项目根目录"""
    # 从当前文件向上查找
    current = Path(__file__).resolve()
    for _ in range(5):  # 最多向上5层
        current = current.parent
        if (current / '.env').exists() or (current / 'app').exists():
            return current
    # 如果找不到，返回脚本所在目录的父目录
    return Path(__file__).parent.parent.parent.resolve()

project_root = find_project_root()
logger.info(f"[图片] 项目根目录: {project_root}")

# 加载环境变量
env_files = ['.env', '.env.travel-only']
for env_file in env_files:
    env_path = project_root / env_file
    if env_path.exists():
        result = load_dotenv(env_path, override=True)
        logger.info(f"[图片] 加载环境变量: {env_file} (存在={env_path.exists()}, 加载结果={result})")

# API配置 - 在load_dotenv之后获取
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")

# 如果环境变量未加载，直接设置（临时调试）
if not UNSPLASH_ACCESS_KEY or UNSPLASH_ACCESS_KEY == "your_unsplash_key_here":
    UNSPLASH_ACCESS_KEY = "TXRusbT1Jvwq9V0LXNBeqpA0eQ2vU92LGUpQZw_JMtk"
    logger.warning("[图片] 使用硬编码的UNSPLASH_ACCESS_KEY")

if not PEXELS_API_KEY:
    PEXELS_API_KEY = "VQQmqFlIXaalCPZBGcS4IHuPl52J9mzJgs1c3tbcFwGPuDBafgf5GaWj"
    logger.warning("[图片] 使用硬编码的PEXELS_API_KEY")

logger.info(f"[图片] UNSPLASH_ACCESS_KEY: {'已设置 (' + UNSPLASH_ACCESS_KEY[:10] + '...)' if UNSPLASH_ACCESS_KEY else '未设置'}")
logger.info(f"[图片] PEXELS_API_KEY: {'已设置 (' + PEXELS_API_KEY[:10] + '...)' if PEXELS_API_KEY else '未设置'}")


# 中文名称到英文名称的映射表
CITY_NAME_MAP = {
    # 中国城市
    "北京": "Beijing China",
    "上海": "Shanghai China",
    "广州": "Guangzhou China",
    "深圳": "Shenzhen China",
    "成都": "Chengdu China",
    "重庆": "Chongqing China",
    "西安": "Xi'an China",
    "杭州": "Hangzhou China",
    "南京": "Nanjing China",
    "苏州": "Suzhou China",
    "武汉": "Wuhan China",
    "厦门": "Xiamen China",
    "青岛": "Qingdao China",
    "大连": "Dalian China",
    "桂林": "Guilin China",
    "丽江": "Lijiang China",
    "大理": "Dali China",
    "三亚": "Sanya China",
    "拉萨": "Lhasa China",
    "香港": "Hong Kong",
    "澳门": "Macau",
    "台北": "Taipei",

    # 东南亚
    "曼谷": "Bangkok Thailand",
    "清迈": "Chiang Mai Thailand",
    "普吉岛": "Phuket Thailand",
    "芭提雅": "Pattaya Thailand",
    "甲米": "Krabi Thailand",
    "皮皮岛": "Phi Phi Islands Thailand",
    "苏梅岛": "Koh Samui Thailand",
    "华欣": "Hua Hin Thailand",
    "新加坡": "Singapore",
    "吉隆坡": "Kuala Lumpur Malaysia",
    "槟城": "Penang Malaysia",
    "巴厘岛": "Bali Indonesia",
    "乌布": "Ubud Bali Indonesia",
    "龙目岛": "Lombok Indonesia",
    "河内": "Hanoi Vietnam",
    "胡志明市": "Ho Chi Minh City Vietnam",
    "岘港": "Da Nang Vietnam",
    "会安": "Hoi An Vietnam",
    "下龙湾": "Halong Bay Vietnam",

    # 日本韩国
    "东京": "Tokyo Japan",
    "京都": "Kyoto Japan",
    "大阪": "Osaka Japan",
    "北海道": "Hokkaido Japan",
    "富士山": "Mount Fuji Japan",
    "首尔": "Seoul South Korea",
    "釜山": "Busan South Korea",
    "济州岛": "Jeju Island South Korea",

    # 欧洲
    "巴黎": "Paris France",
    "伦敦": "London UK",
    "罗马": "Rome Italy",
    "巴塞罗那": "Barcelona Spain",
    "阿姆斯特丹": "Amsterdam Netherlands",
    "雅典": "Athens Greece",
    "布拉格": "Prague Czech",
    "威尼斯": "Venice Italy",
    "佛罗伦萨": "Florence Italy",
    "马德里": "Madrid Spain",
    "柏林": "Berlin Germany",
    "维也纳": "Vienna Austria",

    # 美洲
    "纽约": "New York USA",
    "洛杉矶": "Los Angeles USA",
    "旧金山": "San Francisco USA",
    "拉斯维加斯": "Las Vegas USA",
    "芝加哥": "Chicago USA",
    "华盛顿": "Washington DC",
    "波士顿": "Boston USA",
    "迈阿密": "Miami USA",

    # 加拿大
    "多伦多": "Toronto Canada",
    "温哥华": "Vancouver Canada",
    "蒙特利尔": "Montreal Canada",

    # 澳大利亚新西兰
    "悉尼": "Sydney Australia",
    "墨尔本": "Melbourne Australia",
    "奥克兰": "Auckland New Zealand",

    # 中东
    "迪拜": "Dubai UAE",
    "阿布扎比": "Abu Dhabi UAE",
    "多哈": "Doha Qatar",

    # 其他
    "马尔代夫": "Maldives",
    "毛里求斯": "Mauritius",
    "塞舌尔": "Seychelles",
}


# 城市的代表景点（用于通用活动搜索）
CITY_LANDMARKS = {
    "成都": ["Panda Base", "Kuanzhai Alleys", "Jinli Street", "Wuhou Shrine"],
    "北京": ["Forbidden City", "Great Wall", "Temple of Heaven", "Summer Palace"],
    "上海": ["The Bund", "Oriental Pearl Tower", "Yu Garden", "Shanghai Tower"],
    "西安": ["Terracotta Warriors", "Ancient City Wall", "Big Wild Goose Pagoda", "Muslim Quarter"],
    "杭州": ["West Lake", "Leifeng Pagoda", "Lingyin Temple", "Hefang Street"],
    "成都": ["Panda Base", "Kuanzhai Alleys", "Jinli Street", "Wuhou Shrine"],
    "重庆": ["Hongya Cave", "Ciqikou Ancient Town", "Chaotianmen", "Yangtze River Cableway"],
    "广州": ["Canton Tower", "Shamian Island", "Chen Clan Ancestral Hall", "Yuexiu Park"],
    "深圳": ["Window of the World", "Shenzhen Bay Bridge", "Dameisha", "OCT-LOFT"],
    "苏州": ["Humble Administrator's Garden", "Tiger Hill", "Pingjiang Road", "Suzhou Museum"],
    "南京": ["Dr. Sun Yat-sen Mausoleum", "Confucius Temple", "Presidential Palace", "Nanjing City Wall"],
    "武汉": ["Yellow Crane Tower", "East Lake", "Yangtze River Bridge", "Hubu Alley"],
    "厦门": ["Gulangyu Island", "Nanputuo Temple", "Zhongshan Road", "Xiamen University"],
    "青岛": ["Zhan Qiao", "Badaguan Scenic Area", "May Fourth Square", "Laoshan"],
    "大理": ["Dali Ancient City", "Erhai Lake", "Cangshan Mountain", "Three Pagodas"],
    "丽江": ["Lijiang Old Town", "Jade Dragon Snow Mountain", "Shuhe Ancient Town", "Black Dragon Pool"],
    "三亚": ["Yalong Bay", "Tianya Haijiao", "Nanshan Temple", "Wuzhizhou Island"],
    "桂林": ["Li River", "Elephant Trunk Hill", "Reed Flute Cave", "Seven Star Park"],
    "张家界": ["Zhangjiajie National Forest", "Tianmen Mountain", "Zhangjiajie Glass Bridge", "Baofeng Lake", "Huanglong Cave", "Golden Whip Stream"],
    "香港": ["Victoria Peak", "Victoria Harbour", "Tian Tan Buddha", "Temple Street Night Market"],
    "曼谷": ["Grand Palace", "Wat Arun", "Chatuchak Market", "Khaosan Road"],
    "东京": ["Sensoji Temple", "Tokyo Tower", "Shibuya Crossing", "Meiji Shrine"],
    "京都": ["Kinkakuji Temple", "Fushimi Inari Shrine", "Kiyomizudera Temple", "Gion District"],
    "大阪": ["Osaka Castle", "Dotonbori", "Umeda Sky Building", "Shinsekai"],
    "新加坡": ["Marina Bay Sands", "Gardens by the Bay", "Merlion Park", "Sentosa Island"],
    "巴厘岛": ["Tanah Lot", "Ubud Rice Terraces", "Uluwatu Temple", "Seminyak Beach"],
    "普吉岛": ["Patong Beach", "Phi Phi Islands", "Phang Nga Bay", "Promthep Cape"],
    "巴黎": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Champs-Élysées"],
    "伦敦": ["Big Ben", "London Eye", "Tower Bridge", "Buckingham Palace"],
    "纽约": ["Statue of Liberty", "Times Square", "Central Park", "Empire State Building"],
    "悉尼": ["Sydney Opera House", "Harbour Bridge", "Bondi Beach", "Darling Harbour"],
}


# 知名景点的英文搜索词
ATTRACTION_NAME_MAP = {
    # 中国著名景点
    "长城": "Great Wall of China",
    "故宫": "Forbidden City Beijing",
    "天安门": "Tiananmen Square Beijing",
    "天坛": "Temple of Heaven Beijing",
    "颐和园": "Summer Palace Beijing",
    "兵马俑": "Terracotta Warriors Xi'an",
    "少林寺": "Shaolin Temple",
    "黄山": "Huangshan Mountain",
    "张家界": "Zhangjiajie National Forest",
    "九寨沟": "Jiuzhaigou Valley",
    "珍珠滩": "Pearl Shoal Jiuzhaigou",
    "五花海": "Five Flower Lake Jiuzhaigou",
    "诺日朗瀑布": "Nuorilang Waterfall Jiuzhaigou",
    "长海": "Long Lake Jiuzhaigou",
    "镜海": "Mirror Lake Jiuzhaigou",
    "丽江古城": "Lijiang Old Town",
    "玉龙雪山": "Jade Dragon Snow Mountain",
    "束河古镇": "Shuhe Ancient Town",
    "西湖": "West Lake Hangzhou",
    "雷峰塔": "Leifeng Pagoda Hangzhou",
    "断桥": "Broken Bridge Hangzhou",
    "外滩": "The Bund Shanghai",
    "东方明珠": "Oriental Pearl Tower Shanghai",
    "上海中心大厦": "Shanghai Tower",
    "武夷山": "Wuyi Mountain",
    "鼓浪屿": "Gulangyu Island Xiamen",
    "日月潭": "Sun Moon Lake Taiwan",
    "太鲁阁": "Taroko Gorge Taiwan",
    "千岛湖": "Qiandao Lake Hangzhou",
    "三清山": "Sanqing Mountain",
    "龙虎山": "Mount Longhu",
    "峨眉山": "Mount Emei",
    "乐山大佛": "Leshan Giant Buddha",
    "黄果树瀑布": "Huangguoshu Waterfall",
    "天门山": "Tianmen Mountain Zhangjiajie",
    "大溪地玻璃桥": "Zhangjiajie Glass Bridge",
    "玻璃桥": "Zhangjiajie Glass Bridge",
    "云天渡": "Zhangjiajie Glass Bridge",
    "宝峰湖": "Baofeng Lake Zhangjiajie",
    "黄龙洞": "Huanglong Cave Zhangjiajie",
    "凤凰古城": "Fenghuang Ancient Town",
    "阳朔": "Yangshuo Guilin",
    "漓江": "Li River Guilin",
    "象鼻山": "Elephant Trunk Hill Guilin",
    "芦笛岩": "Reed Flute Cave Guilin",
    "日月湾": "Sun and Moon Bay",
    "蜈支洲岛": "Wuzhizhou Island Sanya",
    "亚龙湾": "Yalong Bay Sanya",
    "天涯海角": "Tianya Haijiao Sanya",
    "南山寺": "Nanshan Temple Sanya",

    # 成都著名景点
    "大熊猫繁育研究基地": "Panda Base Chengdu",
    "熊猫基地": "Chengdu Panda Base",
    "大熊猫基地": "Giant Panda Breeding Research Base",
    "宽窄巷子": "Kuanzhai Alleys Chengdu",
    "宽窄巷": "Kuanzhai Alley Chengdu",
    "锦里": "Jinli Ancient Street Chengdu",
    "锦里古街": "Jinli Street Chengdu",
    "武侯祠": "Wuhou Shrine Chengdu",
    "杜甫草堂": "Du Fu Thatched Cottage Chengdu",
    "草堂": "Du Fu Cottage Chengdu",
    "青羊宫": "Qingyang Taoist Temple Chengdu",
    "文殊院": "Wenshu Monastery Chengdu",
    "金沙遗址": "Jinsha Site Museum Chengdu",
    "金沙遗址博物馆": "Jinsha Relics Museum",
    "都江堰": "Dujiangyan Irrigation System",
    "青城山": "Mount Qingcheng Chengdu",
    "青城": "Qingcheng Mountain Sichuan",
    "春熙路": "Chunxi Road Shopping Chengdu",
    "太古里": "Taikoo Li Chengdu",
    "IFS国际金融中心": "Chengdu IFS Tower",
    "四川博物院": "Sichuan Museum Chengdu",
    "成都博物馆": "Chengdu Museum",
    "人民公园": "Chengdu People's Park",
    "天府广场": "Tianfu Square Chengdu",
    "望江楼": "Wangjiang Tower Chengdu",
    "百花潭": "Baihua Pond Park",
    "浣花溪": "Huanhua Creek Park",
    "洛带古镇": "Luodai Ancient Town",
    "黄龙溪": "Huanglongxi Ancient Town",
    "街子古镇": "Jiezi Ancient Town",
    "平乐古镇": "Pingle Ancient Town",
    "西岭雪山": "Xiling Snow Mountain",
    "四姑娘山": "Mount Siguniang",
    "三星堆": "Sanxingdui Museum Guanghan",

    # 国外著名景点
    "埃菲尔铁塔": "Eiffel Tower Paris",
    "凯旋门": "Arc de Triomphe Paris",
    "卢浮宫": "Louvre Museum Paris",
    "塞纳河": "Seine River Paris",
    "凡尔赛宫": "Palace of Versailles Paris",
    "自由女神像": "Statue of Liberty New York",
    "时代广场": "Times Square New York",
    "中央公园": "Central Park New York",
    "布鲁克林大桥": "Brooklyn Bridge New York",
    "大本钟": "Big Ben London",
    "伦敦眼": "London Eye",
    "塔桥": "Tower Bridge London",
    "威斯敏斯特教堂": "Westminster Abbey London",
    "白金汉宫": "Buckingham Palace London",
    "斗兽场": "Colosseum Rome",
    "梵蒂冈": "Vatican City",
    "许愿池": "Trevi Fountain Rome",
    "西班牙台阶": "Spanish Steps Rome",
    "圣托里尼": "Santorini Greece",
    "圣家堂": "Sagrada Familia Barcelona",
    "古埃尔公园": "Park Guell Barcelona",
    "红场": "Red Square Moscow",
    "克里姆林宫": "Kremlin Moscow",
    "圣瓦西里大教堂": "Saint Basil's Cathedral Moscow",
    "富士山": "Mount Fuji Japan",
    "东京塔": "Tokyo Tower",
    "浅草寺": "Sensoji Temple Tokyo",
    "清水寺": "Kiyomizudera Temple Kyoto",
    "金阁寺": "Kinkakuji Temple Kyoto",
    "大阪城": "Osaka Castle",
    "清迈古城": "Chiang Mai Old City",
    "大皇宫": "Grand Palace Bangkok",
    "卧佛寺": "Wat Pho Bangkok",
    "郑王庙": "Wat Arun Bangkok",
    "吴哥窟": "Angkor Wat Cambodia",
    "巴戎寺": "Bayon Temple Cambodia",
    "泰姬陵": "Taj Mahal India",
    "琥珀堡": "Amber Fort India",
    "悉尼歌剧院": "Sydney Opera House",
    "海港大桥": "Harbour Bridge Sydney",
    "邦迪海滩": "Bondi Beach Sydney",
    "帆船酒店": "Burj Al Arab Dubai",
    "哈利法塔": "Burj Khalifa Dubai",
    "棕榈岛": "Palm Jumeirah Dubai",
    "马尔代夫": "Maldives Islands",
    "巴厘岛海滩": "Bali Beach Indonesia",
    "乌布": "Ubud Bali Indonesia",
    "火山": "Mount Bromo Indonesia",
}


def get_english_search_term(chinese_name: str, name_type: str = "city") -> str:
    """
    获取英文搜索词

    Args:
        chinese_name: 中文名称
        name_type: 名称类型 ('city' 或 'attraction')

    Returns:
        英文搜索词
    """
    # 优先从映射表查找
    if name_type == "attraction":
        mapped = ATTRACTION_NAME_MAP.get(chinese_name)
    else:
        mapped = CITY_NAME_MAP.get(chinese_name)

    if mapped:
        return mapped

    # 检查是否包含中文字符
    has_chinese = any('\u4e00' <= char <= '\u9fff' for char in chinese_name)

    if has_chinese:
        # 包含中文但没有映射，返回原文（API可能也能处理）
        return chinese_name

    # 纯英文，直接返回
    return chinese_name


def build_search_query(attraction_name: str, city: str) -> str:
    """
    构建优化的搜索查询

    优先使用英文关键词以获得更好的搜索结果
    为通用景点名添加更多变化的搜索词
    优先使用城市的代表景点
    """
    # 获取英文名称
    city_en = get_english_search_term(city, "city")
    attraction_en = get_english_search_term(attraction_name, "attraction")

    # 检查是否使用了映射（英文名 != 中文名）
    attraction_was_mapped = attraction_en != attraction_name and not any('\u4e00' <= char <= '\u9fff' for char in attraction_en)

    # 如果景点名称映射到了英文且城市包含China，去掉城市中的国家信息（避免重复）
    if attraction_was_mapped and " China" in city_en:
        city_en = city_en.replace(" China", "").strip()

    # 通用景点名称变化表 - 为相似的景点名提供不同的搜索词
    generic_attraction_variations = {
        "周边景点": "scenic viewpoint",
        "景点打卡": "landmark photography",
        "景点探索": "attraction discovery",
        "周边游览": "surrounding area",
        "特色景点": "unique attraction",
        "著名景点": "famous landmark",
        "市区观光": "city sightseeing",
        "文化体验": "cultural experience",
        "自由活动": "leisure travel",
        "休闲娱乐": "entertainment",
        "海滩": "beach",
        "海岛": "island",
        "山脉": "mountain",
        "古镇": "ancient town",
        "夜景": "night view",
        "美食街": "food street",
    }

    # 检查是否是通用活动名称
    is_generic_activity = any(generic in attraction_name for generic in generic_attraction_variations.keys())

    # 如果是通用活动，优先使用城市的代表景点
    if is_generic_activity and city in CITY_LANDMARKS:
        # 随机选择一个城市的代表景点
        landmark = random.choice(CITY_LANDMARKS[city])
        logger.info(f"[图片] 通用活动'{attraction_name}'使用城市代表景点: {landmark} ({city})")
        return f"{landmark} {city_en}"

    # 如果景点名包含通用词汇，使用变化表
    for generic, variation in generic_attraction_variations.items():
        if generic in attraction_name:
            if attraction_name == city or attraction_name == generic:
                # 纯城市名或纯通用名 - 城市名 + 变化
                return f"{city_en} {variation}"
            else:
                # 混合名称 - 保留原始特征 + 变化
                base_name = attraction_name.replace(generic, "").strip()
                return f"{city_en} {variation} {base_name}".strip()

    # 构建查询
    if attraction_en == city or attraction_name == city:
        # 只有城市名 - 保持完整的city_en（包含China）
        return city_en
    else:
        # 景点 + 城市
        return f"{attraction_en} {city_en}"


class AttractionImageService:
    """景点图片服务类"""

    @staticmethod
    def get_image(attraction_name: str, city: str, width: int = 800, height: int = 600) -> str:
        """获取景点图片URL"""
        return get_attraction_image(attraction_name, city, width, height)


def _get_attraction_name_from_tianapi(attraction_name: str, city: str) -> Optional[str]:
    """
    从天行数据获取真实的景点名称

    用于优化图片搜索关键词

    Args:
        attraction_name: 原始景点名称
        city: 城市名称

    Returns:
        优化后的景点名称，如果未找到则返回None
    """
    try:
        from tradingagents.integrations.tianapi_client import TianAPIClient

        client = TianAPIClient()
        attractions = client.get_scenic_attractions(city=city, num=50)

        # 查找匹配的景点
        for attraction in attractions:
            name = attraction.get('name', '')
            # 精确匹配
            if name == attraction_name:
                return name
            # 模糊匹配（包含关系）
            if attraction_name in name or name in attraction_name:
                return name

        return None

    except Exception as e:
        logger.debug(f"[天行数据] 获取景点名称失败: {e}")
        return None


def get_attraction_image(
    attraction_name: str,
    city: str,
    width: int = 800,
    height: int = 600,
    max_retries: int = 3
) -> str:
    """
    获取景点图片URL

    优先使用 Unsplash，失败后使用 Pexels，持续重试直到成功

    使用随机化策略减少重复图片

    Args:
        attraction_name: 景点名称
        city: 城市
        width: 宽度
        height: 高度
        max_retries: 最大重试次数（每个API）

    Returns:
        图片URL
    """
    import random

    # 🔥 优化：对于国内城市，先尝试从天行数据获取真实景点名称
    if city and attraction_name:
        enhanced_name = _get_attraction_name_from_tianapi(attraction_name, city)
        if enhanced_name and enhanced_name != attraction_name:
            logger.info(f"[图片] 使用天行数据优化景点名称: {attraction_name} -> {enhanced_name}")
            attraction_name = enhanced_name

    # 构建优化的英文搜索关键词
    query = build_search_query(attraction_name, city)
    logger.info(f"[图片] 搜索关键词: {query} (原始: {city} - {attraction_name})")

    # 尝试 Unsplash
    if UNSPLASH_ACCESS_KEY and UNSPLASH_ACCESS_KEY != "your_unsplash_key_here":
        for attempt in range(max_retries):
            try:
                # 使用随机页码获取不同结果 (1-5页)
                random_page = random.randint(1, 5)
                url = _get_unsplash_image(query, width, height, page=random_page)
                if url:
                    logger.info(f"[图片] Unsplash成功: {city} - {attraction_name} (页码: {random_page})")
                    return url
                logger.warning(f"[图片] Unsplash返回空，重试 {attempt + 1}/{max_retries}")
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"[图片] Unsplash失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)

    # 尝试 Pexels
    if PEXELS_API_KEY:
        for attempt in range(max_retries):
            try:
                # 使用随机页码获取不同结果 (1-5页)
                random_page = random.randint(1, 5)
                url = _get_pexels_image(query, width, height, page=random_page)
                if url:
                    logger.info(f"[图片] Pexels成功: {city} - {attraction_name} (页码: {random_page})")
                    return url
                logger.warning(f"[图片] Pexels返回空，重试 {attempt + 1}/{max_retries}")
                time.sleep(0.5)
            except Exception as e:
                logger.warning(f"[图片] Pexels失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.5)

    # 都失败了，使用占位图
    logger.warning(f"[图片] 所有API失败，使用占位图: {city} - {attraction_name}")
    # 使用城市名生成占位图
    city_for_url = quote(city.encode('utf-8'))
    return f"https://placehold.co/{width}x{height}?text={city_for_url}"


def _get_unsplash_image(query: str, width: int, height: int, page: int = 1) -> Optional[str]:
    """
    从 Unsplash 获取图片

    Args:
        query: 搜索关键词（英文）
        width: 宽度
        height: 高度
        page: 页码（用于获取不同结果）

    Returns:
        图片URL或None
    """
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape" if width > height else "portrait",
        "page": page
    }
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        if results:
            photo = results[0]
            # 构建高质量图片URL
            raw_url = photo["urls"]["regular"]
            # 添加尺寸参数
            return f"{raw_url}&w={width}&h={height}&fit=crop"

        return None

    except Exception as e:
        logger.error(f"[Unsplash API错误] {e}")
        return None


def _get_pexels_image(query: str, width: int, height: int, page: int = 1) -> Optional[str]:
    """
    从 Pexels 获取图片

    Args:
        query: 搜索关键词（英文）
        width: 宽度
        height: 高度
        page: 页码（用于获取不同结果）

    Returns:
        图片URL或None
    """
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "per_page": 1,
        "orientation": "landscape" if width > height else "portrait",
        "page": page,
        "size": "large"
    }
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        photos = data.get("photos", [])

        if photos:
            photo = photos[0]
            # Pexels 返回的图片已经是完整URL
            return photo["src"]["large"]

        return None

    except Exception as e:
        logger.error(f"[Pexels API错误] {e}")
        return None


def get_progressive_image_urls(city: str, width: int = 600, height: int = 400) -> list:
    """
    获取渐进式图片URL列表（用于懒加载）

    Args:
        city: 城市名
        width: 宽度
        height: 高度

    Returns:
        不同尺寸的URL列表 [small, medium, large]
    """
    # 生成不同尺寸
    urls = []
    sizes = [(400, 300), (600, 400), (1200, 800)]

    for w, h in sizes:
        url = get_attraction_image(city, city, w, h)
        urls.append(url)

    return urls


# 兼容函数
def get_image_service() -> AttractionImageService:
    """获取图片服务实例"""
    return AttractionImageService()


def get_themed_image(destination: str, width: int = 1200, height: int = 600) -> str:
    """获取主题图片（用于横幅等）"""
    return get_attraction_image(destination, destination, width, height)


# 城市颜色配置（用于UI）
CITY_COLORS = {
    "三亚": "#FF6B6B",
    "曼谷": "#4ECDC4",
    "东京": "#95E1D3",
    "巴黎": "#F38181",
    "纽约": "#AA96DA",
    "伦敦": "#FCBAD3",
    "悉尼": "#FFFFD2",
    "新加坡": "#A8E6CF",
}


# 导出
__all__ = [
    'AttractionImageService',
    'get_attraction_image',
    'get_progressive_image_urls',
    'get_image_service',
    'get_themed_image',
    'CITY_COLORS',
]
