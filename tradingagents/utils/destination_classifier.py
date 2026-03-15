"""
目的地分类器 - 自动识别目的地类型（国内/国际）
"""

from typing import Dict, Literal


class DestinationClassifier:
    """目的地分类器"""

    # 国内城市列表（100+热门城市）
    DOMESTIC_CITIES = {
        # 直辖市
        "北京", "上海", "天津", "重庆",
        # 省会及热门城市
        "广州", "深圳", "成都", "杭州", "西安", "南京", "武汉", "长沙",
        "郑州", "沈阳", "大连", "青岛", "宁波", "厦门", "苏州", "无锡",
        "福州", "济南", "石家庄", "太原", "合肥", "南昌", "南宁", "海口",
        "贵阳", "昆明", "拉萨", "兰州", "西宁", "银川", "乌鲁木齐", "呼和浩特",
        "长春", "哈尔滨",
        # 热门旅游城市
        "三亚", "丽江", "大理", "桂林", "张家界", "九寨沟", "黄山",
        "五台山", "峨眉山", "武夷山", "庐山", "敦煌", "嘉峪关",
        "延吉", "呼伦贝尔", "漠河", "伊犁", "喀什", "林芝", "日喀则",
        # 港澳台
        "香港", "澳门", "台北"
    }

    # 国际国家列表
    INTERNATIONAL_DESTINATIONS = {
        # 亚洲
        "日本", "韩国", "朝鲜", "蒙古", "泰国", "新加坡", "马来西亚",
        "越南", "柬埔寨", "老挝", "缅甸", "菲律宾", "印尼", "文莱",
        "印度", "尼泊尔", "孟加拉", "巴基斯坦", "斯里兰卡", "马尔代夫",
        # 欧洲
        "法国", "英国", "意大利", "西班牙", "葡萄牙", "希腊",
        "德国", "瑞士", "奥地利", "荷兰", "比利时", "捷克", "匈牙利",
        # 大洋洲
        "澳大利亚", "新西兰",
        # 北美
        "美国", "加拿大", "墨西哥",
        # 其他
        "土耳其", "埃及", "南非", "阿联酋", "迪拜", "巴西", "阿根廷"
    }

    # 城市别名映射
    CITY_ALIASES = {
        # 中文别名
        "帝都": "北京",
        "魔都": "上海",
        "羊城": "广州",
        "蓉城": "成都",
        # 英文别名 - 国内城市
        "Beijing": "北京",
        "Shanghai": "上海",
        "Guangzhou": "广州",
        "Shenzhen": "深圳",
        "Chengdu": "成都",
        "Xian": "西安",
        "Tianjin": "天津",
        "Chongqing": "重庆",
        "Hangzhou": "杭州",
        "Nanjing": "南京",
        "Wuhan": "武汉",
        "Changsha": "长沙",
        "Zhengzhou": "郑州",
        "Shenyang": "沈阳",
        "Dalian": "大连",
        "Qingdao": "青岛",
        "Ningbo": "宁波",
        "Xiamen": "厦门",
        "Suzhou": "苏州",
        "Fuzhou": "福州",
        "Jinan": "济南",
        "Hefei": "合肥",
        "Nanchang": "南昌",
        "Nanning": "南宁",
        "Haikou": "海口",
        "Guiyang": "贵阳",
        "Kunming": "昆明",
        "Lhasa": "拉萨",
        "Lanzhou": "兰州",
        "Urumqi": "乌鲁木齐",
        "Hohhot": "呼和浩特",
        "Changchun": "长春",
        "Harbin": "哈尔滨",
        "Sanya": "三亚",
        "Lijiang": "丽江",
        "Dali": "大理",
        "Guilin": "桂林",
        "Zhangjiajie": "张家界",
        "Huangshan": "黄山",
        "Hong Kong": "香港",
        "Macau": "澳门",
        "Taipei": "台北",
        # 英文别名 - 国际热门城市
        "Tokyo": "日本",
        "Paris": "法国",
        "London": "英国",
        "New York": "美国",
        "Los Angeles": "美国",
        "San Francisco": "美国",
        "Bangkok": "泰国",
        "Seoul": "韩国",
        "Singapore": "新加坡",
        "Dubai": "阿联酋",
        "Sydney": "澳大利亚",
        "Rome": "意大利",
        "Barcelona": "西班牙",
        "Amsterdam": "荷兰",
        "Berlin": "德国",
        "Vienna": "奥地利",
        # 英文别名 - 国际国家
        "Japan": "日本",
        "Korea": "韩国",
        "North Korea": "朝鲜",
        "Mongolia": "蒙古",
        "Thailand": "泰国",
        "Singapore": "新加坡",
        "Malaysia": "马来西亚",
        "Vietnam": "越南",
        "Cambodia": "柬埔寨",
        "Laos": "老挝",
        "Myanmar": "缅甸",
        "Philippines": "菲律宾",
        "Indonesia": "印尼",
        "Brunei": "文莱",
        "India": "印度",
        "Nepal": "尼泊尔",
        "Bangladesh": "孟加拉",
        "Pakistan": "巴基斯坦",
        "Sri Lanka": "斯里兰卡",
        "Maldives": "马尔代夫",
        "France": "法国",
        "UK": "英国",
        "United Kingdom": "英国",
        "Italy": "意大利",
        "Spain": "西班牙",
        "Portugal": "葡萄牙",
        "Greece": "希腊",
        "Germany": "德国",
        "Switzerland": "瑞士",
        "Austria": "奥地利",
        "Netherlands": "荷兰",
        "Belgium": "比利时",
        "Czech": "捷克",
        "Hungary": "匈牙利",
        "Australia": "澳大利亚",
        "New Zealand": "新西兰",
        "USA": "美国",
        "United States": "美国",
        "Canada": "加拿大",
        "Mexico": "墨西哥",
        "Turkey": "土耳其",
        "Egypt": "埃及",
        "South Africa": "南非",
        "UAE": "阿联酋",
        "Dubai": "迪拜",
        "Brazil": "巴西",
        "Argentina": "阿根廷",
    }

    @classmethod
    def classify(cls, destination: str) -> Dict:
        """
        分类目的地

        Args:
            destination: 目的地名称（城市或国家）

        Returns:
            {
                "type": "domestic" | "international" | "unknown",
                "normalized_name": "标准化名称",
                "confidence": 置信度 0.0-1.0,
                "matched_by": "exact" | "alias" | "fuzzy" | "unknown"
            }
        """
        if not destination:
            return {
                "type": "unknown",
                "normalized_name": "",
                "confidence": 0.0,
                "matched_by": "unknown"
            }

        dest = destination.strip()

        # 1. 精确匹配 - 国内城市
        if dest in cls.DOMESTIC_CITIES:
            return {
                "type": "domestic",
                "normalized_name": dest,
                "confidence": 1.0,
                "matched_by": "exact"
            }

        # 2. 精确匹配 - 国际国家
        if dest in cls.INTERNATIONAL_DESTINATIONS:
            return {
                "type": "international",
                "normalized_name": dest,
                "confidence": 1.0,
                "matched_by": "exact"
            }

        # 3. 别名匹配
        if dest in cls.CITY_ALIASES:
            canonical = cls.CITY_ALIASES[dest]
            if canonical in cls.DOMESTIC_CITIES:
                return {
                    "type": "domestic",
                    "normalized_name": canonical,
                    "confidence": 0.9,
                    "matched_by": "alias"
                }
            elif canonical in cls.INTERNATIONAL_DESTINATIONS:
                return {
                    "type": "international",
                    "normalized_name": canonical,
                    "confidence": 0.9,
                    "matched_by": "alias"
                }

        # 4. 模糊匹配（包含）
        for city in cls.DOMESTIC_CITIES:
            if city in dest or dest in city:
                return {
                    "type": "domestic",
                    "normalized_name": city,
                    "confidence": 0.7,
                    "matched_by": "fuzzy"
                }

        for country in cls.INTERNATIONAL_DESTINATIONS:
            if country in dest or dest in country:
                return {
                    "type": "international",
                    "normalized_name": country,
                    "confidence": 0.7,
                    "matched_by": "fuzzy"
                }

        # 5. 无法识别（需要用户确认或LLM辅助）
        return {
            "type": "unknown",
            "normalized_name": dest,
            "confidence": 0.0,
            "matched_by": "unknown",
            "need_user_confirm": True
        }

    @classmethod
    def is_domestic(cls, destination: str) -> bool:
        """快速判断是否为国内目的地"""
        result = cls.classify(destination)
        return result["type"] == "domestic"

    @classmethod
    def is_international(cls, destination: str) -> bool:
        """快速判断是否为国际目的地"""
        result = cls.classify(destination)
        return result["type"] == "international"
