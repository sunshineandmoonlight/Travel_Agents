"""
餐饮推荐师 (Agent C3)

职责: 推荐午餐晚餐区域和特色美食
输入: 地区 + 每日景点位置
输出: 餐饮区域推荐 + 特色菜品
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger('travel_agents')


# ==================== 真实API数据获取 ====================

def _search_restaurants_with_tool(
    destination: str,
    area: str = "",
    budget_level: str = "medium",
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    使用餐厅搜索工具API获取餐厅数据

    Args:
        destination: 目的地
        area: 区域（可选）
        budget_level: 预算等级
        limit: 返回数量限制

    Returns:
        餐厅列表
    """
    try:
        from tradingagents.tools.travel_tools import get_restaurant_search_tool

        restaurant_tool = get_restaurant_search_tool()
        restaurants = restaurant_tool.search_restaurants(
            city=destination,
            area=area,
            limit=limit
        )

        if restaurants and len(restaurants) > 0:
            logger.info(f"[餐饮推荐师] 成功获取{len(restaurants)}家餐厅")
            return restaurants
        else:
            return []

    except Exception as e:
        logger.warning(f"[餐饮推荐师] 餐厅搜索API调用失败: {e}")
        return []


def _get_real_restaurants(destination: str, budget_level: str) -> List[Dict[str, Any]]:
    """
    使用真实API获取餐厅数据（兼容旧接口）

    Args:
        destination: 目的地
        budget_level: 预算等级

    Returns:
        餐厅列表
    """
    # 调用餐厅搜索工具
    return _search_restaurants_with_tool(destination, "", budget_level, limit=10)


# ==================== 静态美食数据库 ====================

# 目的地美食数据库
DESTINATION_CUISINE_DB = {
    "北京": {
        "breakfast": ["豆汁儿", "焦圈", "煎饼果子", "小笼包"],
        "lunch": ["炸酱面", "打卤面", "褡裢火烧", "卤煮"],
        "dinner": ["北京烤鸭", "涮羊肉", "京酱肉丝", "爆肚"],
        "snacks": ["驴打滚", "艾窝窝", "糖葫芦", "芸豆卷"],
        "dining_areas": [
            {
                "area": "王府井小吃街",
                "specialties": ["各种小吃", "老字号"],
                "price_level": "medium",
                "description": "汇聚各地美食，老字号聚集"
            },
            {
                "area": "簋街",
                "specialties": ["麻辣小龙虾", "火锅"],
                "price_level": "medium",
                "description": "夜宵聚集地，热闹非凡"
            },
            {
                "area": "南锣鼓巷",
                "specialties": ["文艺小馆", "创意菜"],
                "price_level": "medium",
                "description": "文艺小馆，特色小店"
            },
            {
                "area": "三里屯",
                "specialties": ["国际料理", "酒吧"],
                "price_level": "high",
                "description": "时尚餐饮，国际美食"
            },
            {
                "area": "牛街",
                "specialties": ["清真美食", "牛羊肉"],
                "price_level": "economy",
                "description": "正宗清真料理，价格实惠"
            }
        ],
        "recommended_restaurants": [
            {"name": "全聚德", "specialty": "北京烤鸭", "price": "150-200元/人", "area": "前门/王府井"},
            {"name": "东来顺", "specialty": "涮羊肉", "price": "100-150元/人", "area": "王府井"},
            {"name": "护国寺小吃", "specialty": "老北京小吃", "price": "30-50元/人", "area": "护国寺街"},
            {"name": "海碗居", "specialty": "炸酱面", "price": "40-60元/人", "area": "多家分店"}
        ]
    },
    "上海": {
        "breakfast": ["生煎包", "小笼包", "油豆腐线粉汤", "粢饭团"],
        "lunch": ["生煎", "葱油拌面", "红烧肉", "本帮菜"],
        "dinner": ["本帮菜", "小笼包", "红烧肉", "糖醋排骨"],
        "snacks": ["蟹壳黄", "排骨年糕", "桂花糖粥"],
        "dining_areas": [
            {
                "area": "城隍庙",
                "specialties": ["传统小吃", "南翔小笼"],
                "price_level": "medium",
                "description": "老上海小吃聚集地"
            },
            {
                "area": "田子坊",
                "specialties": ["文艺餐厅", "咖啡小馆"],
                "price_level": "medium",
                "description": "文艺小资，特色小店"
            },
            {
                "area": "新天地",
                "specialties": ["国际料理", "精致餐厅"],
                "price_level": "high",
                "description": "时尚餐饮，环境优雅"
            },
            {
                "area": "云南南路",
                "specialties": ["本帮菜", "海鲜"],
                "price_level": "medium",
                "description": "美食一条街"
            }
        ],
        "recommended_restaurants": [
            {"name": "南翔馒头店", "specialty": "小笼包", "price": "50-80元/人", "area": "城隍庙"},
            {"name": "老正兴", "specialty": "本帮菜", "price": "100-150元/人", "area": "福州路"},
            {"name": "小杨生煎", "specialty": "生煎包", "price": "20-30元/人", "area": "多家分店"}
        ]
    },
    "成都": {
        "breakfast": ["担担面", "龙抄手", "钟水饺", "赖汤圆"],
        "lunch": ["麻婆豆腐", "回锅肉", "夫妻肺片", "水煮鱼"],
        "dinner": ["火锅", "串串香", "川菜", "兔头"],
        "snacks": ["三大炮", "糖油果子", "冰粉"],
        "dining_areas": [
            {
                "area": "宽窄巷子",
                "specialties": ["川菜", "小吃"],
                "price_level": "medium",
                "description": "古街美食，川味十足"
            },
            {
                "area": "锦里",
                "specialties": ["小吃", "串串"],
                "price_level": "medium",
                "description": "三国主题，小吃聚集"
            },
            {
                "area": "春熙路",
                "specialties": ["火锅", "时尚餐饮"],
                "price_level": "medium",
                "description": "繁华商圈，美食众多"
            },
            {
                "area": "建设路",
                "specialties": ["串串香", "烧烤"],
                "price_level": "economy",
                "description": "本地人爱去，价格实惠"
            }
        ],
        "recommended_restaurants": [
            {"name": "陈麻婆豆腐", "specialty": "麻婆豆腐", "price": "60-80元/人", "area": "西玉龙街"},
            {"name": "蜀九香火锅", "specialty": "火锅", "price": "100-150元/人", "area": "多家分店"},
            {"name": "龙抄手", "specialty": "抄手", "price": "30-50元/人", "area": "春熙路"}
        ]
    },
    "西安": {
        "breakfast": ["肉夹馍", "羊肉泡馍", "凉皮", "胡辣汤"],
        "lunch": ["biangbiang面", "肉夹馍", "凉皮"],
        "dinner": ["羊肉泡馍", "葫芦鸡", "水盆羊肉"],
        "snacks": ["镜糕", "柿子饼", "石榴汁"],
        "dining_areas": [
            {
                "area": "回民街",
                "specialties": ["清真美食", "小吃"],
                "price_level": "economy",
                "description": "穆斯林聚集地，美食天堂"
            },
            {
                "area": "永兴坊",
                "specialties": ["陕西各地美食"],
                "price_level": "medium",
                "description": "陕西美食聚集地"
            },
            {
                "area": "大唐不夜城",
                "specialties": ["高端餐饮", "主题餐厅"],
                "price_level": "high",
                "description": "盛唐文化，精致餐饮"
            }
        ],
        "recommended_restaurants": [
            {"name": "老孙家", "specialty": "羊肉泡馍", "price": "50-80元/人", "area": "回民街"},
            {"name": "子午路张记", "specialty": "肉夹馍", "price": "20-30元/人", "area": "多家分店"},
            {"name": "同盛祥", "specialty": "牛羊肉泡馍", "price": "60-100元/人", "area": "钟楼"}
        ]
    },
    "杭州": {
        "breakfast": ["小笼包", "片儿川", "葱包桧"],
        "lunch": ["西湖醋鱼", "东坡肉", "龙井虾仁"],
        "dinner": ["杭帮菜", "西湖醋鱼", "叫化鸡"],
        "snacks": ["定胜糕", "葱包桧", "西湖藕粉"],
        "dining_areas": [
            {
                "area": "河坊街",
                "specialties": ["杭帮菜", "小吃"],
                "price_level": "medium",
                "description": "古街美食，传统风味"
            },
            {
                "area": "西湖周边",
                "specialties": ["杭帮菜", "茶馆"],
                "price_level": "high",
                "description": "湖景餐厅，环境优雅"
            },
            {
                "area": "胜利河美食街",
                "specialties": ["各地美食"],
                "price_level": "economy",
                "description": "平民美食，价格实惠"
            }
        ],
        "recommended_restaurants": [
            {"name": "楼外楼", "specialty": "西湖醋鱼", "price": "150-200元/人", "area": "孤山路"},
            {"name": "知味观", "specialty": "小笼包", "price": "40-60元/人", "area": "仁和路"},
            {"name": "外婆家", "specialty": "杭帮菜", "price": "60-80元/人", "area": "多家分店"}
        ]
    },
    "厦门": {
        "breakfast": ["沙茶面", "花生汤", "面线糊"],
        "lunch": ["土笋冻", "海蛎煎", "沙茶面"],
        "dinner": ["海鲜", "闽南菜", "姜母鸭"],
        "snacks": ["烧肉粽", "花生汤", "麻糍"],
        "dining_areas": [
            {
                "area": "中山路",
                "specialties": ["闽南小吃", "海鲜"],
                "price_level": "medium",
                "description": "百年老街，美食聚集"
            },
            {
                "area": "曾厝垵",
                "specialties": ["小吃", "文艺餐厅"],
                "price_level": "medium",
                "description": "文艺渔村，特色小吃"
            },
            {
                "area": "八市",
                "specialties": ["海鲜", "小吃"],
                "price_level": "economy",
                "description": "本地菜市场，新鲜海鲜"
            }
        ],
        "recommended_restaurants": [
            {"name": "黄则和", "specialty": "花生汤", "price": "20-30元/人", "area": "中山路"},
            {"name": "乌糖沙茶面", "specialty": "沙茶面", "price": "30-50元/人", "area": "民族路"},
            {"name": "小眼镜大排档", "specialty": "海鲜", "price": "100-200元/人", "area": "开元路"}
        ]
    },
    # 国际目的地美食数据库
    "日本": {
        "breakfast": ["日式煎蛋", "味噌汤", "米饭", "纳豆", "烤鱼"],
        "lunch": ["拉面", "寿司", "日式咖喱", "盖饭", "天妇罗"],
        "dinner": ["怀石料理", "寿喜烧", "烧肉", "刺身", "居酒屋料理"],
        "snacks": ["章鱼小丸子", "铜锣烧", "麻糬", "抹茶冰淇淋", "可丽饼"],
        "dining_areas": [
            {
                "area": "新宿",
                "specialties": ["拉面街", "居酒屋", "百货公司美食"],
                "price_level": "medium",
                "description": "繁华商圈，餐饮选择丰富"
            },
            {
                "area": "浅草",
                "specialties": ["传统料理", "人形烧", "雷门小吃"],
                "price_level": "economy",
                "description": "老东京风情，传统小吃"
            },
            {
                "area": "银座",
                "specialties": ["高端料理", "法式日料", "寿司店"],
                "price_level": "high",
                "description": "高端餐饮，米其林餐厅聚集"
            },
            {
                "area": "涩谷",
                "specialties": ["潮流餐厅", "咖啡厅", "国际料理"],
                "price_level": "medium",
                "description": "年轻人聚集，时尚餐饮"
            },
            {
                "area": "筑地",
                "specialties": ["新鲜寿司", "海鲜", "日式早餐"],
                "price_level": "medium",
                "description": "海鲜市场，新鲜食材"
            }
        ],
        "recommended_restaurants": [
            {"name": "一兰拉面", "specialty": "博多拉面", "price": "60-80元/人", "area": "新宿/涉谷"},
            {"name": " Sukiyabashi Jiro", "specialty": "寿司", "price": "500-800元/人", "area": "银座"},
            {"name": "松阪牛烧肉", "specialty": "和牛烧肉", "price": "200-400元/人", "area": "新桥"},
            {"name": "蟹道乐", "specialty": "螃蟹料理", "price": "150-250元/人", "area": "银座/新宿"}
        ]
    },
    "瑞士": {
        "breakfast": ["瑞士麦片", "面包", "奶酪", "咖啡", "果酱"],
        "lunch": ["芝士火锅", "香肠", "烤奶酪", "德式料理"],
        "dinner": ["瑞士火锅", "烤肉", "法式料理", "意式料理"],
        "snacks": ["瑞士巧克力", "马卡龙", "可丽饼", "奶油卷"],
        "dining_areas": [
            {
                "area": "苏黎世老城",
                "specialties": ["传统瑞士菜", "湖景餐厅", "咖啡厅"],
                "price_level": "high",
                "description": "湖景餐厅，环境优雅"
            },
            {
                "area": "因特拉肯",
                "specialties": ["山地料理", "奶酪火锅", "传统餐厅"],
                "price_level": "medium",
                "description": "阿尔卑斯山下的美食小镇"
            },
            {
                "area": "琉森",
                "specialties": ["湖鲜料理", "瑞士菜", "国际料理"],
                "price_level": "medium",
                "description": "湖畔餐厅，风景优美"
            },
            {
                "area": "日内瓦",
                "specialties": ["法式料理", "高端餐饮", "湖景餐厅"],
                "price_level": "high",
                "description": "国际化都市，美食丰富"
            }
        ],
        "recommended_restaurants": [
            {"name": "Zeughauskeller", "specialty": "传统瑞士菜", "price": "120-180元/人", "area": "苏黎世"},
            {"name": "Fondue House", "specialty": "芝士火锅", "price": "150-200元/人", "area": "因特拉肯"},
            {"name": "Café du Centre", "specialty": "瑞士料理", "price": "100-150元/人", "area": "琉森"}
        ]
    },
    "泰国": {
        "breakfast": ["泰式炒粉", "椰子糕", "芒果糯米饭", "咖啡"],
        "lunch": ["冬阴功汤", "泰式炒河粉", "绿咖喱鸡", "芒果沙拉"],
        "dinner": ["冬阴功", "泰式火锅", "咖喱蟹", "椰子鸡汤"],
        "snacks": ["香蕉煎饼", "椰子冰淇淋", "泰式奶茶", "炸昆虫"],
        "dining_areas": [
            {
                "area": "考山路",
                "specialties": ["街头小吃", "泰式炒面", "水果沙冰"],
                "price_level": "economy",
                "description": "背包客天堂，小吃聚集"
            },
            {
                "area": "暹罗广场",
                "specialties": ["商场美食", "泰式料理", "国际料理"],
                "price_level": "medium",
                "description": "现代化商圈，选择丰富"
            },
            {
                "area": "唐人街",
                "specialties": ["海鲜", "中式泰式融合", "夜市小吃"],
                "price_level": "medium",
                "description": "夜市美食，热闹非凡"
            },
            {
                "area": "素坤逸路",
                "specialties": ["高端泰式料理", "国际餐厅"],
                "price_level": "high",
                "description": "高端餐饮，精致料理"
            },
            {
                "area": "湄南河畔",
                "specialties": ["河景餐厅", "泰式料理", "海鲜"],
                "price_level": "high",
                "description": "河景餐厅，环境浪漫"
            }
        ],
        "recommended_restaurants": [
            {"name": "MK火锅", "specialty": "泰式火锅", "price": "50-80元/人", "area": "各大商场"},
            {"name": "建兴酒家", "specialty": "咖喱蟹", "price": "100-150元/人", "area": "暹罗/素坤逸"},
            {"name": "Greyhound Cafe", "specialty": "融合泰式料理", "price": "80-120元/人", "area": "暹罗广场"},
            {"name": "Thipsamai", "specialty": "泰式炒河粉", "price": "30-50元/人", "area": "大皇宫附近"}
        ]
    },
    "韩国": {
        "breakfast": ["韩式拌饭", "大酱汤", "泡菜", "米饭"],
        "lunch": ["石锅拌饭", "韩式烤肉", "冷面", "部队锅"],
        "dinner": ["韩式烤肉", "韩式炸鸡", "参鸡汤", "韩式火锅"],
        "snacks": ["辣炒年糕", "鱼饼串", "鸡蛋卷", "韩式煎饼"],
        "dining_areas": [
            {
                "area": "明洞",
                "specialties": ["韩式料理", "炸鸡", "街头小吃"],
                "price_level": "medium",
                "description": "繁华商圈，美食聚集"
            },
            {
                "area": "弘大",
                "specialties": ["年轻时尚餐厅", "酒吧", "夜宵"],
                "price_level": "medium",
                "description": "年轻人聚集，夜生活丰富"
            },
            {
                "area": "东大门",
                "specialties": ["24小时餐厅", "烤肉", "夜市小吃"],
                "price_level": "medium",
                "description": "不夜城，随时可以用餐"
            },
            {
                "area": "仁寺洞",
                "specialties": ["传统韩式料理", "韩定食"],
                "price_level": "high",
                "description": "传统韩国文化，精致料理"
            },
            {
                "area": "江南",
                "specialties": ["高端韩式料理", "国际料理"],
                "price_level": "high",
                "description": "高端餐饮，时尚精致"
            }
        ],
        "recommended_restaurants": [
            {"name": "校村炸鸡", "specialty": "韩式炸鸡", "price": "60-100元/人", "area": "明洞/弘大"},
            {"name": "姜虎东白丁", "specialty": "韩式烤肉", "price": "100-150元/人", "area": "明洞/江南"},
            {"name": "全州中央会馆", "specialty": "全州石锅拌饭", "price": "50-80元/人", "area": "明洞"},
            {"name": "明洞饺子", "specialty": "韩式饺子", "price": "30-50元/人", "area": "明洞"}
        ]
    },
    "新加坡": {
        "breakfast": ["海南鸡饭", "咖椰吐司", "肉骨茶", "椰浆饭"],
        "lunch": ["海南鸡饭", "叻沙", "炒粿条", "辣椒螃蟹"],
        "dinner": ["辣椒螃蟹", "黑胡椒螃蟹", "肉骨茶", "海南鸡饭"],
        "snacks": ["咖椰吐司", "榴莲", "豆花", "冰淇淋三明治"],
        "dining_areas": [
            {
                "area": "牛车水",
                "specialties": ["中式料理", "小吃", "肉骨茶"],
                "price_level": "economy",
                "description": "唐人街，传统美食"
            },
            {
                "area": "小印度",
                "specialties": ["印度料理", "咖喱", "香蕉叶饭"],
                "price_level": "economy",
                "description": "印度风情，香料浓郁"
            },
            {
                "area": "芽笼",
                "specialties": ["地道新加坡菜", "烧烤", "夜宵"],
                "price_level": "medium",
                "description": "本地人聚集，地道美食"
            },
            {
                "area": "克拉码头",
                "specialties": ["河景餐厅", "酒吧", "国际料理"],
                "price_level": "medium",
                "description": "河畔餐饮，夜生活丰富"
            },
            {
                "area": "滨海湾",
                "specialties": ["高端餐厅", "赌场美食", "景观餐厅"],
                "price_level": "high",
                "description": "高端餐饮，环境优雅"
            }
        ],
        "recommended_restaurants": [
            {"name": "天天海南鸡饭", "specialty": "海南鸡饭", "price": "20-30元/人", "area": "牛车水"},
            {"name": "无招牌海鲜", "specialty": "辣椒螃蟹", "price": "100-150元/人", "area": "滨海湾/克拉码头"},
            {"name": "松发肉骨茶", "specialty": "肉骨茶", "price": "30-50元/人", "area": "牛车水/芽笼"},
            {"name": "328 Katong Laksa", "specialty": "叻沙", "price": "20-30元/人", "area": "加东"}
        ]
    },
    "马来西亚": {
        "breakfast": ["椰浆饭", "肉骨茶", "炒粿条", " Roti Canai"],
        "lunch": ["椰浆饭", "炒粿条", "叻沙", "海南鸡饭"],
        "dinner": ["肉骨茶", "辣椒螃蟹", "马来烧烤", "娘惹菜"],
        "snacks": ["煎蕊", "榴莲", "香蕉煎饼", "红豆冰"],
        "dining_areas": [
            {
                "area": "吉隆坡茨厂街",
                "specialties": ["中式料理", "小吃", "肉骨茶"],
                "price_level": "economy",
                "description": "唐人街，美食聚集"
            },
            {
                "area": "阿罗街",
                "specialties": ["烧烤", "海鲜", "夜市小吃"],
                "price_level": "medium",
                "description": "夜市美食，热闹非凡"
            },
            {
                "area": "柏威年广场",
                "specialties": ["商场美食", "国际料理"],
                "price_level": "medium",
                "description": "现代化商圈，选择丰富"
            },
            {
                "area": "马六甲古城",
                "specialties": ["娘惹菜", "葡萄牙料理", "小吃"],
                "price_level": "medium",
                "description": "古城风情，融合料理"
            },
            {
                "area": "槟城乔治市",
                "specialties": ["福建面", "炒粿条", "小吃"],
                "price_level": "economy",
                "description": "美食天堂，地道小吃"
            }
        ],
        "recommended_restaurants": [
            {"name": "新峰肉骨茶", "specialty": "肉骨茶", "price": "30-50元/人", "area": "吉隆坡"},
            {"name": "黄亚华小食店", "specialty": "烤鸡翅", "price": "30-50元/人", "area": "阿罗街"},
            {"name": "海南鸡饭粒", "specialty": "鸡饭粒", "price": "20-30元/人", "area": "马六甲"},
            {"name": "槟城炒粿条", "specialty": "炒粿条", "price": "20-30元/人", "area": "槟城"}
        ]
    },
    "法国": {
        "breakfast": ["牛角包", "咖啡", "可颂", "欧姆蛋"],
        "lunch": ["法式三明治", "法式汤", "沙拉", " crepe"],
        "dinner": ["法式大餐", "法式蜗牛", "鹅肝", "牛排"],
        "snacks": ["马卡龙", "可丽饼", "冰淇淋", "法式糕点"],
        "dining_areas": [
            {
                "area": "香榭丽舍大街",
                "specialties": ["高端法式料理", "米其林餐厅"],
                "price_level": "high",
                "description": "世界知名，高端餐饮"
            },
            {
                "area": "蒙马特",
                "specialties": ["传统法式小馆", "咖啡厅"],
                "price_level": "medium",
                "description": "艺术家聚集，浪漫氛围"
            },
            {
                "area": "玛莱区",
                "specialties": ["时尚餐厅", "小酒馆", "犹太料理"],
                "price_level": "medium",
                "description": "潮流街区，美食丰富"
            },
            {
                "area": "塞纳河左岸",
                "specialties": ["文学咖啡厅", "传统法式"],
                "price_level": "medium",
                "description": "文艺气息，历史悠久的咖啡厅"
            }
        ],
        "recommended_restaurants": [
            {"name": "Le Comptoir", "specialty": "传统法式", "price": "150-250元/人", "area": "圣日耳曼"},
            {"name": "L'as du Fallafel", "specialty": "法拉费", "price": "30-50元/人", "area": "玛莱区"},
            {"name": "Café de Flore", "specialty": "咖啡厅", "price": "80-120元/人", "area": "圣日耳曼"}
        ]
    },
    "意大利": {
        "breakfast": ["意式咖啡", "牛角包", "意式饼干"],
        "lunch": ["披萨", "意面", "意式三明治", " risotto"],
        "dinner": ["意式大餐", "海鲜意面", "牛排", "提拉米苏"],
        "snacks": ["意式冰淇淋", "意式小吃", "咖啡"],
        "dining_areas": [
            {
                "area": "罗马西班牙广场",
                "specialties": ["传统意式", "咖啡厅"],
                "price_level": "medium",
                "description": "历史中心，美食丰富"
            },
            {
                "area": "米兰大教堂附近",
                "specialties": ["高端意式", "时尚餐厅"],
                "price_level": "high",
                "description": "时尚之都，精致餐饮"
            },
            {
                "area": "威尼斯里亚托桥",
                "specialties": ["海鲜", "传统意式"],
                "price_level": "medium",
                "description": "水城风情，浪漫用餐"
            },
            {
                "area": "佛罗伦萨",
                "specialties": ["托斯卡纳料理", "牛排"],
                "price_level": "medium",
                "description": "文艺复兴，美食天堂"
            }
        ],
        "recommended_restaurants": [
            {"name": "Da Enzo", "specialty": "罗马菜", "price": "100-150元/人", "area": "罗马"},
            {"name": "Trattoria Mario", "specialty": "托斯卡纳菜", "price": "80-120元/人", "area": "佛罗伦萨"},
            {"name": "Gelateria La Romana", "specialty": "意式冰淇淋", "price": "20-30元/人", "area": "多个城市"}
        ]
    },
    "英国": {
        "breakfast": ["英式早餐", "煎蛋", "培根", "豆子"],
        "lunch": ["炸鱼薯条", "英式三明治", "肉派"],
        "dinner": ["英式烤肉", "炸鱼薯条", "哈吉斯", "牛肉派"],
        "snacks": ["英式下午茶", "司康饼", "奶油茶"],
        "dining_areas": [
            {
                "area": "伦敦苏豪区",
                "specialties": ["各式料理", "酒吧"],
                "price_level": "medium",
                "description": "美食丰富，选择多样"
            },
            {
                "area": "伦敦金融城",
                "specialties": ["高端餐厅", "商务餐"],
                "price_level": "high",
                "description": "商务区，高端餐饮"
            },
            {
                "area": "伦敦唐人街",
                "specialties": ["中式料理", "亚洲料理"],
                "price_level": "medium",
                "description": "亚洲美食聚集"
            },
            {
                "area": "海德公园附近",
                "specialties": ["传统英式下午茶", "高级餐厅"],
                "price_level": "high",
                "description": "优雅环境，下午茶"
            }
        ],
        "recommended_restaurants": [
            {"name": "The English Grill", "specialty": "英式烤肉", "price": "200-300元/人", "area": "伦敦"},
            {"name": "Poppies Fish & Chips", "specialty": "炸鱼薯条", "price": "80-120元/人", "area": "伦敦"},
            {"name": "Fortnum & Mason", "specialty": "英式下午茶", "price": "150-250元/人", "area": "伦敦"}
        ]
    },
    "美国": {
        "breakfast": ["美式早餐", "煎饼", "华夫饼", "咖啡"],
        "lunch": ["汉堡", "三明治", "沙拉", "美式BBQ"],
        "dinner": ["牛排", "美式海鲜", "BBQ", "纽约披萨"],
        "snacks": ["热狗", " pretzel", "冰淇淋", "甜甜圈"],
        "dining_areas": [
            {
                "area": "纽约时代广场",
                "specialties": ["美式料理", "国际料理", "快餐"],
                "price_level": "medium",
                "description": "繁华商圈，选择丰富"
            },
            {
                "area": "纽约曼哈顿",
                "specialties": ["高端美式", "法式", "意大利式"],
                "price_level": "high",
                "description": "高端餐饮，米其林餐厅"
            },
            {
                "area": "洛杉矶比弗利山庄",
                "specialties": ["高端美式", "健康料理"],
                "price_level": "high",
                "description": "明星聚集，高端餐饮"
            },
            {
                "area": "旧金山渔人码头",
                "specialties": ["海鲜", "酸面包", " clam chowder"],
                "price_level": "medium",
                "description": "海滨美食，新鲜海鲜"
            }
        ],
        "recommended_restaurants": [
            {"name": "Peter Luger", "specialty": "牛排", "price": "300-500元/人", "area": "纽约"},
            {"name": "Shake Shack", "specialty": "汉堡", "price": "50-80元/人", "area": "多城市"},
            {"name": "Joe's Pizza", "specialty": "纽约披萨", "price": "30-50元/人", "area": "纽约"}
        ]
    },
    "澳大利亚": {
        "breakfast": ["澳式早餐", " flat white", "牛油果吐司"],
        "lunch": ["海鲜", "澳式肉派", "汉堡", "沙拉"],
        "dinner": ["澳式牛排", "海鲜", "袋鼠肉", " barbecue"],
        "snacks": [" Tim Tam", "澳式蛋糕", "冰淇淋"],
        "dining_areas": [
            {
                "area": "悉尼达令港",
                "specialties": ["海鲜", "河景餐厅"],
                "price_level": "high",
                "description": "海港景观，新鲜海鲜"
            },
            {
                "area": "悉尼岩石区",
                "specialties": ["澳式料理", "国际料理"],
                "price_level": "medium",
                "description": "历史区，美食丰富"
            },
            {
                "area": "墨尔本巷弄",
                "specialties": ["咖啡厅", "时尚餐厅"],
                "price_level": "medium",
                "description": "咖啡文化，潮流餐厅"
            },
            {
                "area": "布里斯班",
                "specialties": ["澳式海鲜", "烧烤"],
                "price_level": "medium",
                "description": "海滨城市，新鲜海鲜"
            }
        ],
        "recommended_restaurants": [
            {"name": "Quay", "specialty": "澳式高级料理", "price": "400-600元/人", "area": "悉尼"},
            {"name": "Harry's Cafe de Wheels", "specialty": "澳式肉派", "price": "20-30元/人", "area": "悉尼"},
            {"name": "Pancakes on the Rocks", "specialty": "煎饼", "price": "50-80元/人", "area": "悉尼"}
        ]
    },
    "新西兰": {
        "breakfast": ["新鲜烘焙", "咖啡", "吐司"],
        "lunch": ["海鲜", "汉堡", " pie"],
        "dinner": ["新西兰羊排", "海鲜", "鹿肉"],
        "snacks": ["新西兰冰淇淋", "蜂蜜", "饼干"],
        "dining_areas": [
            {
                "area": "皇后镇",
                "specialties": ["新西兰料理", "湖景餐厅"],
                "price_level": "medium",
                "description": "湖景小镇，美食丰富"
            },
            {
                "area": "奥克兰",
                "specialties": ["海鲜", "国际料理"],
                "price_level": "medium",
                "description": "最大城市，选择多样"
            },
            {
                "area": "罗托鲁瓦",
                "specialties": ["毛利料理", "地热烧烤"],
                "price_level": "medium",
                "description": "毛利文化，特色料理"
            },
            {
                "area": "但尼丁",
                "specialties": ["海鲜", "苏格兰风格料理"],
                "price_level": "economy",
                "description": "苏格兰风情，实惠美食"
            }
        ],
        "recommended_restaurants": [
            {"name": "Fergburger", "specialty": "汉堡", "price": "50-80元/人", "area": "皇后镇"},
            {"name": "The Bathhouse", "specialty": "海鲜", "price": "100-150元/人", "area": "罗托鲁瓦"}
        ]
    },
    "冰岛": {
        "breakfast": ["面包", "奶酪", "酸奶", "咖啡"],
        "lunch": ["冰岛热狗", "汤", "三明治"],
        "dinner": ["冰岛羊肉", "鱼", "鲨鱼肉"],
        "snacks": ["冰岛酸奶", "巧克力"],
        "dining_areas": [
            {
                "area": "雷克雅未克市中心",
                "specialties": ["冰岛料理", "海鲜"],
                "price_level": "high",
                "description": "首都中心，美食聚集"
            },
            {
                "area": "旧港",
                "specialties": ["海鲜", "河景餐厅"],
                "price_level": "medium",
                "description": "海港区域，新鲜海鲜"
            }
        ],
        "recommended_restaurants": [
            {"name": "Bæjarins Beztu Pylsur", "specialty": "冰岛热狗", "price": "30-50元/人", "area": "雷克雅未克"},
            {"name": "Dill", "specialty": "新北欧料理", "price": "200-300元/人", "area": "雷克雅未克"}
        ]
    },
    "挪威": {
        "breakfast": ["面包", "奶酪", "烟熏三文鱼", "咖啡"],
        "lunch": ["挪威三明治", "汤", "沙拉"],
        "dinner": ["挪威三文鱼", "驯鹿肉", "海鲜"],
        "snacks": ["挪威曲奇", "巧克力"],
        "dining_areas": [
            {
                "area": "奥斯陆市中心",
                "specialties": ["挪威料理", "海鲜"],
                "price_level": "high",
                "description": "首都中心，高端餐饮"
            },
            {
                "area": "奥斯陆峡湾",
                "specialties": ["海鲜", "峡湾景观餐厅"],
                "price_level": "high",
                "description": "峡湾景观，浪漫用餐"
            }
        ],
        "recommended_restaurants": [
            {"name": "Maaemo", "specialty": "挪威高级料理", "price": "400-600元/人", "area": "奥斯陆"},
            {"name": "Fiskeriet Youngstorget", "specialty": "海鲜", "price": "100-150元/人", "area": "奥斯陆"}
        ]
    },
    "希腊": {
        "breakfast": ["希腊酸奶", "蜂蜜", "坚果", "咖啡"],
        "lunch": ["希腊沙拉", " gyro", " moussaka"],
        "dinner": ["希腊海鲜", "羊肉", " grilled fish"],
        "snacks": ["希腊甜点", " baklava", "冰淇淋"],
        "dining_areas": [
            {
                "area": "雅典普拉卡",
                "specialties": ["传统希腊菜", " gyro"],
                "price_level": "medium",
                "description": "老城区，传统美食"
            },
            {
                "area": "圣托里尼",
                "specialties": ["海鲜", "日落餐厅"],
                "price_level": "high",
                "description": "浪漫日落，精致用餐"
            },
            {
                "area": "米科诺斯",
                "specialties": ["海鲜", "海滩餐厅"],
                "price_level": "high",
                "description": "海岛风情，新鲜海鲜"
            }
        ],
        "recommended_restaurants": [
            {"name": "Ergon House", "specialty": "希腊料理", "price": "80-120元/人", "area": "雅典"},
            {"name": "Sunset Ammoudi", "specialty": "海鲜", "price": "150-250元/人", "area": "圣托里尼"}
        ]
    },
    "西班牙": {
        "breakfast": ["西班牙油条", "咖啡", "吐司"],
        "lunch": ["西班牙海鲜饭", " tapas", "沙拉"],
        "dinner": ["西班牙海鲜饭", " tapas", " jamón"],
        "snacks": [" churros", "西班牙甜点"],
        "dining_areas": [
            {
                "area": "马德里",
                "specialties": ["西班牙料理", " tapas"],
                "price_level": "medium",
                "description": "首都中心，美食丰富"
            },
            {
                "area": "巴塞罗那兰布拉",
                "specialties": [" tapas", "海鲜"],
                "price_level": "medium",
                "description": "步行街，热闹非凡"
            },
            {
                "area": "塞维利亚",
                "specialties": ["安达卢西亚料理", "海鲜"],
                "price_level": "medium",
                "description": "南部风情，热情美食"
            }
        ],
        "recommended_restaurants": [
            {"name": "Sobrino de Botín", "specialty": "烤乳猪", "price": "150-250元/人", "area": "马德里"},
            {"name": "Can Culleretes", "specialty": "加泰罗尼亚菜", "price": "100-150元/人", "area": "巴塞罗那"}
        ]
    },
    "德国": {
        "breakfast": ["德式面包", "香肠", "奶酪", "咖啡"],
        "lunch": ["德式香肠", "德国猪肘", " schnitzel"],
        "dinner": ["德国猪肘", "香肠", "酸菜"],
        "snacks": ["德国 pretzel", "德国蛋糕"],
        "dining_areas": [
            {
                "area": "慕尼黑",
                "specialties": ["巴伐利亚料理", "啤酒花园"],
                "price_level": "medium",
                "description": "啤酒之都，巴伐利亚美食"
            },
            {
                "area": "柏林",
                "specialties": ["德国料理", "国际料理"],
                "price_level": "medium",
                "description": "首都中心，美食多样"
            }
        ],
        "recommended_restaurants": [
            {"name": "Hofbräuhaus", "specialty": "巴伐利亚料理", "price": "80-120元/人", "area": "慕尼黑"},
            {"name": "Curry 36", "specialty": "咖喱香肠", "price": "20-30元/人", "area": "柏林"}
        ]
    },
    "印度": {
        "breakfast": ["印度饼", "咖喱", "酸奶", "茶"],
        "lunch": ["印度咖喱", " butter chicken", " biryani"],
        "dinner": ["印度咖喱", " tandori", "海鲜"],
        "snacks": [" samosa", "印度甜点"],
        "dining_areas": [
            {
                "area": "德里",
                "specialties": ["北印度菜", " moghlai"],
                "price_level": "economy",
                "description": "北印风情，咖喱之都"
            },
            {
                "area": "孟买",
                "specialties": ["海鲜", "街头小吃"],
                "price_level": "medium",
                "description": "海滨城市，美食天堂"
            }
        ],
        "recommended_restaurants": [
            {"name": "Karim's", "specialty": " moghlai", "price": "30-50元/人", "area": "德里"},
            {"name": "Leopold Cafe", "specialty": "印度菜", "price": "50-80元/人", "area": "孟买"}
        ]
    },
    "尼泊尔": {
        "breakfast": ["尼泊尔早餐饼", "奶茶", "酸奶"],
        "lunch": [" dal bhat", " momo"],
        "dinner": ["尼泊尔咖喱", " momo"],
        "snacks": ["尼泊尔小吃", "奶茶"],
        "dining_areas": [
            {
                "area": "加德满都泰米尔区",
                "specialties": ["尼泊尔菜", "国际料理"],
                "price_level": "economy",
                "description": "旅游区，美食聚集"
            },
            {
                "area": "博卡拉",
                "specialties": ["尼泊尔菜", "湖景餐厅"],
                "price_level": "economy",
                "description": "湖景小镇，悠闲用餐"
            }
        ],
        "recommended_restaurants": [
            {"name": "Third Pole Restaurant", "specialty": "尼泊尔菜", "price": "30-50元/人", "area": "加德满都"},
            {"name": "Moon Dance Cafe", "specialty": "国际料理", "price": "40-60元/人", "area": "博卡拉"}
        ]
    },
    "越南": {
        "breakfast": ["越南河粉", "越南法棍", "咖啡"],
        "lunch": ["越南河粉", "春卷", "越南咖喱"],
        "dinner": ["越南烧烤", "海鲜", "越南火锅"],
        "snacks": ["越南春卷", "越南咖啡", "水果"],
        "dining_areas": [
            {
                "area": "河内老城区",
                "specialties": ["越南菜", "街头小吃"],
                "price_level": "economy",
                "description": "老城区，地道美食"
            },
            {
                "area": "胡志明市",
                "specialties": ["越南菜", "法式越南融合"],
                "price_level": "medium",
                "description": "最大城市，选择丰富"
            },
            {
                "area": "会安古镇",
                "specialties": ["中部越南菜", "小吃"],
                "price_level": "economy",
                "description": "古镇风情，实惠美食"
            }
        ],
        "recommended_restaurants": [
            {"name": "Pho 10", "specialty": "越南河粉", "price": "15-25元/人", "area": "河内"},
            {"name": "Banh Mi 25", "specialty": "越南法棍", "price": "10-20元/人", "area": "胡志明市"}
        ]
    },
    "柬埔寨": {
        "breakfast": ["柬埔寨 noodle soup", "咖啡"],
        "lunch": [" amok", " lok lak"],
        "dinner": ["柬埔寨咖喱", " amok"],
        "snacks": ["柬埔寨小吃", "热带水果"],
        "dining_areas": [
            {
                "area": "暹粒",
                "specialties": ["柬埔寨菜", "国际料理"],
                "price_level": "economy",
                "description": "吴哥窟所在地，美食聚集"
            },
            {
                "area": "金边",
                "specialties": ["柬埔寨菜", "法式柬埔寨融合"],
                "price_level": "medium",
                "description": "首都中心，美食丰富"
            }
        ],
        "recommended_restaurants": [
            {"name": "Chanrey Tree", "specialty": "柬埔寨菜", "price": "50-80元/人", "area": "暹粒"},
            {"name": "Malis Restaurant", "specialty": "高端柬埔寨菜", "price": "100-150元/人", "area": "金边"}
        ]
    },
    "印度尼西亚": {
        "breakfast": ["印尼炒饭", "印尼煎饼", "咖啡"],
        "lunch": [" nasi goreng", " satay", " rendang"],
        "dinner": ["印尼海鲜", "巴厘岛烤猪", " rendang"],
        "snacks": ["印尼小吃", "热带水果", "巧克力"],
        "dining_areas": [
            {
                "area": "巴厘岛乌布",
                "specialties": ["印尼菜", "素食"],
                "price_level": "medium",
                "description": "艺术小镇，美食丰富"
            },
            {
                "area": "巴厘岛库塔",
                "specialties": ["海鲜", "国际料理"],
                "price_level": "medium",
                "description": "海滩区域，选择多样"
            },
            {
                "area": "雅加达",
                "specialties": ["印尼菜", "中印尼融合"],
                "price_level": "medium",
                "description": "首都中心，美食天堂"
            }
        ],
        "recommended_restaurants": [
            {"name": "Locavore", "specialty": "印尼菜", "price": "100-150元/人", "area": "乌布"},
            {"name": "Warung Babi Guling", "specialty": "巴厘岛烤猪", "price": "30-50元/人", "area": "巴厘岛"}
        ]
    },
    "菲律宾": {
        "breakfast": ["菲律宾早餐", "咖啡"],
        "lunch": [" adobo", " sisig"],
        "dinner": ["菲律宾烧烤", "海鲜", " lechon"],
        "snacks": ["菲律宾小吃", "热带水果"],
        "dining_areas": [
            {
                "area": "马尼拉",
                "specialties": ["菲律宾菜", "国际料理"],
                "price_level": "medium",
                "description": "首都中心，美食丰富"
            },
            {
                "area": "宿务",
                "specialties": ["海鲜", "菲律宾菜"],
                "price_level": "economy",
                "description": "海岛城市，新鲜海鲜"
            },
            {
                "area": "长滩岛",
                "specialties": ["海鲜", "海滩餐厅"],
                "price_level": "medium",
                "description": "海滩度假，浪漫用餐"
            }
        ],
        "recommended_restaurants": [
            {"name": "Manila Hotel", "specialty": "菲律宾菜", "price": "100-150元/人", "area": "马尼拉"},
            {"name": "Paradise Beach Restaurant", "specialty": "海鲜", "price": "80-120元/人", "area": "长滩岛"}
        ]
    },
    "马尔代夫": {
        "breakfast": ["国际早餐", "热带水果", "咖啡"],
        "lunch": ["海鲜", "国际料理"],
        "dinner": ["海鲜烧烤", "马尔代夫咖喱"],
        "snacks": ["热带水果", "冰淇淋"],
        "dining_areas": [
            {
                "area": "度假村餐厅",
                "specialties": ["海鲜", "国际料理"],
                "price_level": "high",
                "description": "度假村内，精致用餐"
            },
            {
                "area": "马累",
                "specialties": ["马尔代夫菜", "海鲜"],
                "price_level": "medium",
                "description": "首都中心，美食聚集"
            }
        ],
        "recommended_restaurants": [
            {"name": "Ithaa Undersea Restaurant", "specialty": "海鲜", "price": "500-800元/人", "area": "度假村"},
            {"name": "Sea House", "specialty": "马尔代夫菜", "price": "100-150元/人", "area": "马累"}
        ]
    }
}


def recommend_dining(
    destination: str,
    scheduled_attractions: List[Dict[str, Any]],
    budget_level: str = "medium",
    llm=None
) -> Dict[str, Any]:
    """
    推荐餐饮

    Args:
        destination: 目的地名称
        scheduled_attractions: 已安排的景点日程
        budget_level: 预算等级
        llm: LLM实例（可选）

    Returns:
        餐饮推荐信息
    """
    logger.info(f"[餐饮推荐师] 为{destination}推荐餐饮")

    # 首先尝试使用真实API数据
    real_restaurants = _get_real_restaurants(destination, budget_level)

    cuisine_db = DESTINATION_CUISINE_DB.get(destination, {})
    if not cuisine_db:
        # 根据目的地类型使用合适的默认推荐
        # 检查是否是国际目的地
        from tradingagents.agents.group_a import INTERNATIONAL_DESTINATIONS_DB
        is_international = destination in INTERNATIONAL_DESTINATIONS_DB

        if is_international:
            # 国际目的地默认推荐
            cuisine_db = {
                "breakfast": ["当地特色早餐", "面包", "咖啡", "新鲜水果"],
                "lunch": ["当地特色菜", "简餐", "海鲜"],
                "dinner": ["当地特色菜", "海鲜", "烧烤"],
                "snacks": ["当地特色小吃", "热带水果", "冰淇淋"],
                "dining_areas": [
                    {
                        "area": "市中心商圈",
                        "specialties": ["国际料理", "当地特色"],
                        "price_level": "medium",
                        "description": "繁华商圈，餐饮选择丰富"
                    },
                    {
                        "area": "旅游景点区",
                        "specialties": ["当地特色菜", "小吃"],
                        "price_level": "medium",
                        "description": "景区周边，特色餐厅"
                    }
                ],
                "recommended_restaurants": [
                    {"name": "当地特色餐厅", "specialty": "当地特色菜", "price": "100-200元/人", "area": "市中心"}
                ]
            }
        else:
            # 国内目的地默认推荐
            cuisine_db = {
                "breakfast": ["当地早餐", "包子", "粥", "豆浆"],
                "lunch": ["当地特色菜", "简餐"],
                "dinner": ["当地特色菜", "海鲜"],
                "snacks": ["当地小吃"],
                "dining_areas": [],
                "recommended_restaurants": []
            }

    # 合并真实餐厅数据和静态数据
    all_recommended_restaurants = []

    # 添加真实餐厅数据（优先）
    if real_restaurants:
        # 选择评分最高的几家
        sorted_restaurants = sorted(
            real_restaurants,
            key=lambda r: r.get("recommendation_score", 0),
            reverse=True
        )
        all_recommended_restaurants.extend(sorted_restaurants[:8])

    # 添加静态推荐餐厅（补充）
    static_restaurants = cuisine_db.get("recommended_restaurants", [])
    for static_rest in static_restaurants:
        # 检查是否已在真实列表中
        existing_names = [r.get("name", "") for r in all_recommended_restaurants]
        if static_rest.get("name") not in existing_names:
            all_recommended_restaurants.append(static_rest)

    dining_plan = {
        "destination": destination,
        "daily_dining": [],
        "special_dishes": {
            "breakfast": cuisine_db.get("breakfast", []),
            "lunch": cuisine_db.get("lunch", []),
            "dinner": cuisine_db.get("dinner", []),
            "snacks": cuisine_db.get("snacks", [])
        },
        "recommended_restaurants": all_recommended_restaurants,
        "real_restaurants_count": len(real_restaurants),  # 真实数据数量
        "dining_tips": _get_dining_tips(destination, budget_level),
        "estimated_meal_cost": _estimate_meal_cost(budget_level),
        "data_source": "realtime_api" if real_restaurants and len(real_restaurants) > 0 else "fallback"
    }

    # 🚀 性能优化：收集所有用餐推荐，批量生成LLM解释
    all_meal_recommendations = []  # 收集所有用餐推荐
    api_used_count = 0

    for day_schedule in scheduled_attractions:
        day_num = day_schedule.get("day", 1)
        schedule_items = day_schedule.get("schedule", [])

        day_dining = {
            "day": day_num,
            "lunch": None,
            "dinner": None
        }

        # 根据当天的活动位置推荐用餐区域
        for item in schedule_items:
            period = item.get("period")
            location = item.get("location", "")

            if period == "lunch":
                lunch_rec = _recommend_meal(
                    destination,
                    location,
                    "lunch",
                    budget_level,
                    cuisine_db,
                    real_restaurants,
                    None  # 批量模式：不立即生成LLM解释
                )
                day_dining["lunch"] = lunch_rec
                if lunch_rec.get("data_source") == "realtime_api":
                    api_used_count += 1
                # 收集用于批量生成解释
                if "_explanation_data" in lunch_rec:
                    all_meal_recommendations.append(lunch_rec)

            elif period == "dinner":
                dinner_rec = _recommend_meal(
                    destination,
                    location,
                    "dinner",
                    budget_level,
                    cuisine_db,
                    real_restaurants,
                    None  # 批量模式：不立即生成LLM解释
                )
                day_dining["dinner"] = dinner_rec
                if dinner_rec.get("data_source") == "realtime_api":
                    api_used_count += 1
                # 收集用于批量生成解释
                if "_explanation_data" in dinner_rec:
                    all_meal_recommendations.append(dinner_rec)

        dining_plan["daily_dining"].append(day_dining)

    # 🚀 批量生成所有餐厅推荐的LLM解释
    if all_meal_recommendations and llm:
        batch_explanations = _batch_generate_restaurant_explanations(all_meal_recommendations, llm)

        # 应用批量生成的解释，未生成到的使用模板
        for i, rec in enumerate(all_meal_recommendations):
            exp_data = rec.get("_explanation_data")
            if exp_data:
                if i in batch_explanations:
                    rec["ai_explanation"] = batch_explanations[i]
                else:
                    # 使用模板生成
                    rec["ai_explanation"] = _generate_restaurant_explanation(
                        exp_data["restaurant_name"],
                        exp_data["specialty"],
                        exp_data["area"],
                        exp_data["price_range"],
                        exp_data["destination"],
                        None  # 使用模板，不调用LLM
                    )
                # 清理临时数据
                del rec["_explanation_data"]

    dining_plan["api_calls_count"] = api_used_count

    # 生成LLM描述文本
    dining_plan["llm_description"] = _generate_dining_description(
        destination,
        dining_plan,
        budget_level,
        llm
    )

    logger.info(f"[餐饮推荐师] 完成{len(dining_plan['daily_dining'])}天餐饮推荐，API调用: {api_used_count}次，批量优化餐厅解释")

    return dining_plan


def _generate_restaurant_explanation(
    restaurant_name: str,
    specialty: str,
    area: str,
    price_range: str,
    destination: str,
    llm=None
) -> str:
    """
    为餐厅推荐生成LLM解释说明（保留用于兼容和降级）

    Args:
        restaurant_name: 餐厅名称
        specialty: 招牌菜
        area: 所在区域
        price_range: 价格范围
        destination: 城市名称
        llm: LLM实例

    Returns:
        LLM生成的解释文本
    """
    # 如果有LLM，使用LLM生成解释
    if llm:
        try:
            prompt = f"""请用2-3句话介绍为什么推荐这家餐厅（不超过80字）：

餐厅：{restaurant_name}
招牌菜：{specialty}
所在区域：{area}
价格：{price_range}
城市：{destination}

要求：
1. 突出餐厅特色或招牌菜优势
2. 解释为什么值得尝试
3. 简洁有力，有吸引力

请直接输出解释文字。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            explanation = response.content.strip()
            if explanation and len(explanation) > 10:
                return explanation
        except Exception as e:
            logger.warning(f"[餐饮推荐师] LLM生成餐厅解释失败: {e}")

    # 默认解释
    if specialty and price_range:
        return f"{restaurant_name}是{area}的知名餐厅，招牌{specialty}地道美味，{price_range}性价比高，值得一试。"
    else:
        return f"{restaurant_name}是{area}口碑不错的餐厅，口味正宗，价格合理。"


def _batch_generate_restaurant_explanations(
    meal_recommendations: List[Dict[str, Any]],
    llm=None
) -> Dict[int, str]:
    """
    批量生成所有餐厅推荐的LLM解释说明（性能优化版本）

    将所有用餐推荐一次性发送给LLM进行解释生成，而不是逐个调用。
    这样可以将6次LLM调用优化为1-2次批量调用。

    Args:
        meal_recommendations: 用餐推荐列表（每个包含_explanation_data）
        llm: LLM实例

    Returns:
        索引到解释文本的映射字典
    """
    if not llm or not meal_recommendations:
        return {}

    try:
        # 提取所有用餐推荐的解释数据
        recommendations_data = []
        for i, rec in enumerate(meal_recommendations):
            exp_data = rec.get("_explanation_data", {})
            if exp_data:
                recommendations_data.append({
                    "id": i,
                    "restaurant": exp_data.get("restaurant_name", ""),
                    "specialty": exp_data.get("specialty", ""),
                    "area": exp_data.get("area", ""),
                    "price": exp_data.get("price_range", ""),
                    "destination": exp_data.get("destination", "")
                })

        if not recommendations_data:
            return {}

        # 构建批量提示
        recommendations_text = "\n".join([
            f"[{r['id']}] {r['restaurant']} | 区域: {r['area']} | 招牌: {r['specialty']} | 价格: {r['price']}"
            for r in recommendations_data
        ])

        prompt = f"""请为以下{len(recommendations_data)}个餐厅推荐各生成一段介绍（每段不超过80字）：

{recommendations_text}

要求：
1. 突出餐厅特色或招牌菜优势
2. 解释为什么值得尝试
3. 简洁有力，有吸引力

请严格按照以下JSON格式输出：
{{
  "0": "第0个餐厅的介绍",
  "1": "第1个餐厅的介绍",
  ...
}}

只输出JSON，不要其他内容。"""

        from langchain_core.messages import HumanMessage
        import json
        import re

        response = llm.invoke([HumanMessage(content=prompt)])
        content = response.content.strip()

        # 解析JSON响应
        json_match = re.search(r'\{[^{}]+\}', content)
        if json_match:
            explanations = json.loads(json_match.group())

            # 验证并构建返回字典
            result = {}
            for i, rec in enumerate(meal_recommendations):
                exp_data = rec.get("_explanation_data", {})
                if exp_data:
                    explanation = explanations.get(str(i), "")
                    if explanation and len(explanation) > 5:
                        result[i] = explanation

            if result:
                logger.info(f"[餐饮推荐师] 批量生成{len(result)}条餐厅解释成功")
                return result

    except Exception as e:
        logger.warning(f"[餐饮推荐师] 批量生成餐厅解释失败: {e}，使用模板")

    # 失败时返回空字典，后续会使用模板
    return {}


def _recommend_meal(
    destination: str,
    location: str,
    meal_type: str,
    budget_level: str,
    cuisine_db: Dict,
    real_restaurants: List[Dict] = None,
    llm=None,
    batch_mode: bool = True
) -> Dict[str, Any]:
    """
    推荐单次用餐

    优先调用餐厅搜索工具API获取实时餐厅数据

    Args:
        batch_mode: 批量模式，True时不立即生成LLM解释（性能优化）
    """

    # 查找附近餐饮区域
    nearby_area = None
    dining_areas = cuisine_db.get("dining_areas", [])
    if dining_areas and location:
        # 尝试匹配位置附近的餐饮区
        for area in dining_areas:
            if location in area.get("area", "") or area.get("area", "") in location:
                nearby_area = area
                break

    # 1. 尝试调用餐厅搜索工具API
    try:
        area_restaurants = _search_restaurants_with_tool(
            destination,
            area=location if location and location != "待定" else "",
            budget_level=budget_level,
            limit=3
        )

        if area_restaurants and len(area_restaurants) > 0:
            # 使用API搜索到的餐厅
            recommended = area_restaurants[0]
            restaurant_name = recommended.get("name", "当地餐厅")
            area_name = recommended.get("area", location)
            specialty = recommended.get("specialty", "当地特色菜")
            estimated_cost = recommended.get("estimated_cost", 80)

            result = {
                "meal_type": meal_type,
                "recommended_area": area_name,
                "restaurant_name": restaurant_name,
                "specialty": specialty,
                "dishes": [specialty],
                "estimated_cost": estimated_cost,
                "data_source": "realtime_api"
            }

            # 批量模式：存储解释数据供后续批量处理
            if batch_mode:
                result["_explanation_data"] = {
                    "restaurant_name": restaurant_name,
                    "specialty": specialty,
                    "area": area_name,
                    "price_range": f"{estimated_cost}元/人",
                    "destination": destination
                }
            else:
                # 兼容旧逻辑：立即生成解释
                result["ai_explanation"] = _generate_restaurant_explanation(
                    restaurant_name, specialty, area_name,
                    f"{estimated_cost}元/人", destination, llm
                )

            return result

    except Exception as e:
        logger.warning(f"[餐饮推荐师] 实时餐厅搜索失败: {e}")

    # 2. 降级：使用传入的真实餐厅数据
    recommended = None
    dishes = []

    if real_restaurants:
        # 根据预算筛选真实餐厅
        suitable_restaurants = []
        for r in real_restaurants:
            cost = r.get("estimated_cost", 100)
            if budget_level == "economy" and cost <= 80:
                suitable_restaurants.append(r)
            elif budget_level == "medium" and 50 <= cost <= 200:
                suitable_restaurants.append(r)
            elif budget_level == "luxury" and cost >= 150:
                suitable_restaurants.append(r)
            elif budget_level == "medium":
                suitable_restaurants.append(r)

        if suitable_restaurants:
            # 选择评分最高的
            recommended = max(
                suitable_restaurants,
                key=lambda r: r.get("recommendation_score", 0)
            )

    # 如果没有找到合适的真实餐厅，使用静态数据
    if not recommended:
        restaurants = cuisine_db.get("recommended_restaurants", [])
        if restaurants:
            if budget_level == "economy":
                recommended = min(restaurants, key=lambda r: _parse_price(r.get("price", "")))
            elif budget_level == "luxury":
                recommended = max(restaurants, key=lambda r: _parse_price(r.get("price", "")))
            else:
                recommended = restaurants[0]

    # 获取特色菜品
    if nearby_area:
        dishes = nearby_area.get("specialties", [])

    restaurant_name = recommended.get("name", "当地餐厅") if recommended else "当地餐厅"
    specialty = recommended.get("specialty", "当地特色菜") if recommended else (dishes[0] if dishes else "当地特色菜")
    area_name = nearby_area.get("area", location) if nearby_area else location
    price_range = recommended.get("price", "100元/人") if recommended else "100元/人"

    result = {
        "meal_type": meal_type,
        "time": "12:00-13:30" if meal_type == "lunch" else "18:00-20:00",
        "recommended_area": nearby_area.get("area", "周边餐厅") if nearby_area else "周边餐厅",
        "area_description": nearby_area.get("description", "") if nearby_area else "",
        "special_dishes": dishes[:3] if dishes else [],
        "recommended_restaurant": recommended,
        "estimated_cost": _estimate_meal_cost_by_type(meal_type, budget_level)
    }

    # 批量模式：存储解释数据供后续批量处理
    if batch_mode:
        result["_explanation_data"] = {
            "restaurant_name": restaurant_name,
            "specialty": specialty,
            "area": area_name,
            "price_range": price_range,
            "destination": destination
        }
    else:
        # 兼容旧逻辑：立即生成解释
        result["ai_explanation"] = _generate_restaurant_explanation(
            restaurant_name, specialty, area_name, price_range, destination, llm
        )

    return result


def _parse_price(price_str: str) -> int:
    """解析价格字符串，返回平均值"""
    try:
        import re
        numbers = re.findall(r'\d+', price_str)
        if numbers:
            return sum(map(int, numbers)) // len(numbers)
    except:
        pass
    return 100  # 默认中等价格


def _estimate_meal_cost_by_type(meal_type: str, budget_level: str) -> int:
    """估算单次用餐费用"""
    base_cost = {
        "economy": {"lunch": 40, "dinner": 60},
        "medium": {"lunch": 80, "dinner": 120},
        "luxury": {"lunch": 150, "dinner": 250}
    }
    return base_cost.get(budget_level, {}).get(meal_type, 80)


def _estimate_meal_cost(budget_level: str) -> Dict[str, int]:
    """估算总体餐饮费用"""
    daily_cost = {
        "economy": 100,  # 40+60
        "medium": 200,  # 80+120
        "luxury": 400  # 150+250
    }
    return {
        "per_day": daily_cost.get(budget_level, 200),
        "per_meal_lunch": _estimate_meal_cost_by_type("lunch", budget_level),
        "per_meal_dinner": _estimate_meal_cost_by_type("dinner", budget_level)
    }


def _get_dining_tips(destination: str, budget_level: str) -> List[str]:
    """获取用餐建议"""
    tips = []

    if destination == "北京":
        tips.extend([
            "北京烤鸭建议提前预约",
            "老字号餐厅人多，建议错峰用餐",
            "回民街清真美食，注意饮食习惯"
        ])
    elif destination == "上海":
        tips.extend([
            "本帮菜偏甜，不习惯可提前说明",
            "小笼包要趁热吃，小心烫嘴",
            "城隍庙人多，可考虑周边替代"
        ])
    elif destination == "成都":
        tips.extend([
            "川菜辣度可要求调整",
            "火锅底料可选微辣",
            "串串香按签子结账，注意数量"
        ])
    else:
        tips.append("建议提前网上查看餐厅评价")

    if budget_level == "economy":
        tips.append("为节省费用，可选择当地小吃街")
    elif budget_level == "luxury":
        tips.append("高端餐厅建议提前预订")

    return tips


def _generate_dining_description(
    destination: str,
    dining_plan: Dict[str, Any],
    budget_level: str,
    llm=None
) -> str:
    """
    使用LLM生成餐饮推荐的自然语言描述

    Args:
        destination: 目的地
        dining_plan: 餐饮计划
        budget_level: 预算等级
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    special_dishes = dining_plan.get("special_dishes", {})
    breakfast = ', '.join(special_dishes.get("breakfast", [])[:4])
    lunch = ', '.join(special_dishes.get("lunch", [])[:4])
    dinner = ', '.join(special_dishes.get("dinner", [])[:4])
    snacks = ', '.join(special_dishes.get("snacks", [])[:4])

    restaurants = dining_plan.get("recommended_restaurants", [])
    top_restaurants = [r.get("name", "推荐餐厅") for r in restaurants[:3]]

    meal_cost = dining_plan.get("estimated_meal_cost", {})
    daily_cost = meal_cost.get("daily_total", 200)

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
            prompt = f"""请为以下餐饮推荐生成一段自然、诱人的描述文字（约150-200字）：

目的地：{destination}
特色美食：
• 早餐：{breakfast}
• 午餐：{lunch}
• 晚餐：{dinner}
• 小吃：{snacks}

推荐餐厅：{', '.join(top_restaurants)}
预算等级：{budget_level}
预计餐饮费用：约{daily_cost}元/天

描述要求：
1. 用诱人美食的语气，让人看了就想去尝试
2. 突出当地特色美食的吸引力
3. 介绍美食体验和文化背景
4. 给出实用的用餐建议
5. 语言要生动有趣，有画面感

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[餐饮推荐师] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[餐饮推荐师] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述（无LLM或LLM失败时）
    description = f"""来{destination}，开启一场舌尖上的美味之旅！🍽️

🌅 早餐推荐：{breakfast}
中午不妨尝尝当地特色{lunch}，晚餐必点{dinner}。别忘了品尝{snacks}等特色小吃，每一口都是地道的{destination}风味！

🍴 推荐餐厅：{', '.join(top_restaurants)}
这些餐厅都是当地人气之选，口碑极佳。

💰 预算参考：餐饮约{daily_cost}元/天

💡 实用小贴士：
• 热门餐厅建议提前预约，避免排队
• 正餐时间当地人较多，错峰用餐体验更佳
• 尝试街边小店，往往有意想不到的美味
• 注意饮食卫生和当地饮食习惯

准备好让味蕾尽情享受吧！🎉"""

    return description


# LangGraph 节点函数
def dining_recommender_node(state: Dict) -> Dict:
    """餐饮推荐节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")
    llm = state.get("_llm")

    if not destination:
        logger.error("[餐饮推荐师] 缺少目的地信息")
        return state

    # 推荐餐饮
    dining_plan = recommend_dining(
        destination,
        scheduled_attractions,
        budget_level,
        llm
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"餐饮推荐完成: 包含当地特色美食",
        name="DiningRecommender"
    ))

    state["dining_plan"] = dining_plan
    state["messages"] = messages

    return state
