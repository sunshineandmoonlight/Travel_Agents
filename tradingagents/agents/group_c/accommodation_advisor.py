"""
住宿顾问 (Agent C4)

职责: 建议每日住宿区域和酒店类型
输入: 行程安排 + 预算等级
输出: 住宿区域建议 + 酒店类型
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger('travel_agents')


# 目的地住宿数据库
DESTINATION_ACCOMMODATION_DB = {
    "北京": {
        "accommodation_areas": [
            {
                "area": "王府井/建国门",
                "advantages": ["交通便利", "地铁枢纽", "购物方便", "餐饮丰富"],
                "nearby_attractions": ["故宫", "天安门", "王府井大街"],
                "price_range": {"economy": "200-350", "medium": "400-800", "luxury": "1000+"},
                "recommended_hotels": {
                    "economy": ["汉庭酒店(王府井店)", "如家酒店(建国门店)", "7天酒店"],
                    "medium": ["北京王府井希尔顿酒店", "北京国际饭店", "首都大酒店"],
                    "luxury": ["北京王府井文华东方酒店", "北京华尔道夫酒店", "半岛酒店"]
                }
            },
            {
                "area": "前门/崇文门",
                "advantages": ["靠近天安门", "老北京风味", "交通便利"],
                "nearby_attractions": ["天安门", "前门大街", "大栅栏"],
                "price_range": {"economy": "150-300", "medium": "350-600", "luxury": "800+"},
                "recommended_hotels": {
                    "economy": ["如家快捷酒店(前门店)", "速8酒店"],
                    "medium": ["北京崇文门饭店", "前门建国酒店"],
                    "luxury": ["北京饭店", "前门皇家驿栈"]
                }
            },
            {
                "area": "西单/西四",
                "advantages": ["购物天堂", "美食众多", "年轻人聚集"],
                "nearby_attractions": ["西单商场", "北海公园"],
                "price_range": {"economy": "200-300", "medium": "400-700", "luxury": "900+"},
                "recommended_hotels": {
                    "economy": ["汉庭酒店(西单店)", "布丁酒店"],
                    "medium": ["西单美爵酒店", "北京西单大悦城酒店"],
                    "luxury": ["北京金融街威斯汀酒店"]
                }
            },
            {
                "area": "三里屯/工体",
                "advantages": ["时尚潮流", "夜生活丰富", "国际美食"],
                "nearby_attractions": ["三里屯", "工人体育场"],
                "price_range": {"economy": "250-400", "medium": "500-900", "luxury": "1200+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(三里屯店)", "99旅馆"],
                    "medium": ["北京三里屯CHAO酒店", "怡亨酒店"],
                    "luxury": ["北京三里屯洲际酒店", "瑰丽酒店"]
                }
            }
        ]
    },
    "上海": {
        "accommodation_areas": [
            {
                "area": "人民广场/南京路",
                "advantages": ["市中心", "购物方便", "地铁枢纽"],
                "nearby_attractions": ["人民广场", "南京路步行街", "外滩"],
                "price_range": {"economy": "250-400", "medium": "500-900", "luxury": "1200+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(人民广场店)", "汉庭酒店"],
                    "medium": ["上海扬子精品酒店", "上海苏宁宝丽嘉酒店"],
                    "luxury": ["上海外滩华尔道夫酒店", "上海半岛酒店"]
                }
            },
            {
                "area": "外滩/黄浦江",
                "advantages": ["江景房", "夜景优美", "历史建筑"],
                "nearby_attractions": ["外滩", "南京路", "豫园"],
                "price_range": {"economy": "300-500", "medium": "600-1000", "luxury": "1500+"},
                "recommended_hotels": {
                    "economy": ["汉庭酒店(外滩店)"],
                    "medium": ["上海外滩浦华大酒店", "上海外滩茂悦酒店"],
                    "luxury": ["上海外滩W酒店", "上海外滩英迪格酒店"]
                }
            },
            {
                "area": "静安寺/淮海路",
                "advantages": ["高端购物", "美食聚集", "时尚潮流"],
                "nearby_attractions": ["静安寺", "淮海路", "新天地"],
                "price_range": {"economy": "250-400", "medium": "500-900", "luxury": "1200+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(静安寺店)", "全季酒店"],
                    "medium": ["上海静安香格里拉酒店", "上海璞丽酒店"],
                    "luxury": ["上海静安瑞吉酒店", "上海静安嘉里中心酒店"]
                }
            }
        ]
    },
    "成都": {
        "accommodation_areas": [
            {
                "area": "春熙路/太古里",
                "advantages": ["市中心", "购物天堂", "美食众多"],
                "nearby_attractions": ["春熙路", "太古里", "IFS"],
                "price_range": {"economy": "150-250", "medium": "300-600", "luxury": "800+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(春熙路店)", "汉庭酒店"],
                    "medium": ["成都春熙宾馆", "成都帝盛酒店"],
                    "luxury": ["成都博舍酒店", "成都尼依格罗酒店"]
                }
            },
            {
                "area": "宽窄巷子/人民公园",
                "advantages": ["文化氛围", "老成都风貌", "交通便利"],
                "nearby_attractions": ["宽窄巷子", "人民公园", "天府广场"],
                "price_range": {"economy": "150-250", "medium": "300-500", "luxury": "700+"},
                "recommended_hotels": {
                    "economy": ["成都宽窄巷子汉庭酒店", "7天酒店"],
                    "medium": ["成都浣花宾馆", "成都加州花园酒店"],
                    "luxury": ["成都钓鱼台精品酒店", "成都瑞吉酒店"]
                }
            },
            {
                "area": "锦里/武侯祠",
                "advantages": ["三国文化", "夜景美丽", "小吃聚集"],
                "nearby_attractions": ["锦里", "武侯祠"],
                "price_range": {"economy": "120-200", "medium": "250-450", "luxury": "600+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(武侯祠店)", "布丁酒店"],
                    "medium": ["成都武侯祠酒店", "成都锦江宾馆"],
                    "luxury": ["成都首座万丽酒店"]
                }
            }
        ]
    },
    "西安": {
        "accommodation_areas": [
            {
                "area": "钟楼/鼓楼",
                "advantages": ["市中心", "交通便利", "美食聚集"],
                "nearby_attractions": ["钟楼", "鼓楼", "回民街"],
                "price_range": {"economy": "150-250", "medium": "300-600", "luxury": "800+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(钟楼店)", "汉庭酒店"],
                    "medium": ["西安钟楼饭店", "西安民生大酒店"],
                    "luxury": ["西安豪享来温德姆酒店", "西安君乐城堡酒店"]
                }
            },
            {
                "area": "大雁塔/曲江",
                "advantages": ["新区环境好", "靠近大唐不夜城", "高端酒店多"],
                "nearby_attractions": ["大雁塔", "大唐不夜城", "曲江池"],
                "price_range": {"economy": "200-300", "medium": "400-700", "luxury": "1000+"},
                "recommended_hotels": {
                    "economy": ["汉庭酒店(大雁塔店)"],
                    "medium": ["西安曲江饭店", "西安唐华华邑酒店"],
                    "luxury": ["西安威斯汀酒店", "西安W酒店"]
                }
            },
            {
                "area": "回民街/北门",
                "advantages": ["美食聚集", "老城区", "价格实惠"],
                "nearby_attractions": ["回民街", "城墙"],
                "price_range": {"economy": "120-200", "medium": "250-400", "luxury": "600+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(回民街店)", "7天酒店"],
                    "medium": ["西安回民街宾馆", "西安天朗时代酒店"],
                    "luxury": ["西安索菲特人民大厦"]
                }
            }
        ]
    },
    "杭州": {
        "accommodation_areas": [
            {
                "area": "西湖周边",
                "advantages": ["湖景房", "风景优美", "散步方便"],
                "nearby_attractions": ["西湖", "断桥", "雷峰塔"],
                "price_range": {"economy": "250-400", "medium": "500-900", "luxury": "1200+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(西湖店)"],
                    "medium": ["杭州西湖国宾馆", "杭州香格里拉酒店"],
                    "luxury": ["杭州西子湖四季酒店", "杭州西湖法云安缦"]
                }
            },
            {
                "area": "河坊街/南宋御街",
                "advantages": ["老街风情", "美食聚集", "价格实惠"],
                "nearby_attractions": ["河坊街", "南宋御街", "胡庆余堂"],
                "price_range": {"economy": "150-250", "medium": "300-600", "luxury": "800+"},
                "recommended_hotels": {
                    "economy": ["汉庭酒店(河坊街店)", "布丁酒店"],
                    "medium": ["杭州南宋御街酒店", "杭州维多利亚酒店"],
                    "luxury": ["杭州凯悦酒店"]
                }
            },
            {
                "area": "湖滨/延安路",
                "advantages": ["市中心", "购物方便", "交通便利"],
                "nearby_attractions": ["西湖", "湖滨路"],
                "price_range": {"economy": "200-350", "medium": "400-800", "luxury": "1000+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(湖滨店)", "全季酒店"],
                    "medium": ["杭州JW万豪酒店", "杭州黄龙饭店"],
                    "luxury": ["杭州君悦酒店", "杭州四季酒店"]
                }
            }
        ]
    },
    "厦门": {
        "accommodation_areas": [
            {
                "area": "思明区/中山路",
                "advantages": ["市中心", "交通便利", "美食众多"],
                "nearby_attractions": ["中山路", "鼓浪屿码头"],
                "price_range": {"economy": "150-250", "medium": "300-600", "luxury": "800+"},
                "recommended_hotels": {
                    "economy": ["如家酒店(中山路店)", "汉庭酒店"],
                    "medium": ["厦门鹭江宾馆", "厦门华侨大厦"],
                    "luxury": ["厦门康莱德酒店", "厦门瑞颐大酒店"]
                }
            },
            {
                "area": "曾厝垵",
                "advantages": ["文艺渔村", "靠近环岛路", "价格实惠"],
                "nearby_attractions": ["曾厝垵", "环岛路", "胡里山炮台"],
                "price_range": {"economy": "100-200", "medium": "250-450", "luxury": "600+"},
                "recommended_hotels": {
                    "economy": ["厦门曾厝垵民宿", "青年旅舍"],
                    "medium": ["厦门海港英迪格酒店", "厦门康莱德酒店"],
                    "luxury": ["厦门七尚酒店"]
                }
            },
            {
                "area": "鼓浪屿",
                "advantages": ["岛上住宿", "宁静悠闲", "别墅风格"],
                "nearby_attractions": ["鼓浪屿全景", "日光岩"],
                "price_range": {"economy": "200-350", "medium": "400-700", "luxury": "900+"},
                "recommended_hotels": {
                    "economy": ["鼓浪屿民宿", "家庭旅馆"],
                    "medium": ["鼓浪屿林氏府", "鼓浪屿Miryam老别墅酒店"],
                    "luxury": ["鼓浪屿林氏府公馆酒店", "鼓浪屿百年老旧别墅酒店"]
                }
            }
        ]
    }
}


def _generate_accommodation_area_explanation(
    area: str,
    advantages: List[str],
    nearby_attractions: List[str],
    price_range: str,
    destination: str,
    llm=None
) -> str:
    """
    为住宿区域推荐生成LLM解释说明（保留用于兼容和降级）

    Args:
        area: 住宿区域名称
        advantages: 区域优势列表
        nearby_attractions: 附近景点
        price_range: 价格范围
        destination: 城市名称
        llm: LLM实例

    Returns:
        LLM生成的解释文本
    """
    # 默认解释（不调用LLM，使用模板）
    advantages_text = '、'.join(advantages[:2])
    return f"推荐住在{area}，因为这里{advantages_text}，出行游玩非常便利，{price_range}价位性价比高。"


def _batch_generate_accommodation_content(
    destination: str,
    recommended_area: Dict,
    hotel_list: List[str],
    budget_level: str,
    total_cost: int,
    days: int,
    llm=None
) -> Dict[str, str]:
    """
    批量生成住宿区域解释和整体描述（性能优化版本）

    将区域解释和整体描述合并为一次LLM调用，从2次减少到1次。

    Args:
        destination: 目的地
        recommended_area: 推荐区域信息
        hotel_list: 推荐酒店列表
        budget_level: 预算等级
        total_cost: 总费用
        days: 天数
        llm: LLM实例

    Returns:
        包含 area_explanation 和 llm_description 的字典
    """
    result = {}

    if llm:
        try:
            area = recommended_area.get("area", "市中心")
            advantages = recommended_area.get("advantages", [])
            nearby = recommended_area.get("nearby_attractions", [])
            price_range = recommended_area.get("price_range", {}).get(budget_level, "待查")

            prompt = f"""请为以下住宿推荐生成两部分内容：

目的地：{destination}
推荐住宿区域：{area}
区域优势：{', '.join(advantages[:5])}
附近景点：{', '.join(nearby[:3])}
价格范围：{price_range}
预算等级：{budget_level}
推荐酒店：{', '.join(hotel_list[:3])}
住宿费用：{total_cost}元（{days}晚）

请按以下JSON格式输出：
{{
  "area_explanation": "2-3句话解释为什么推荐这个区域（不超过80字）",
  "overall_description": "一段自然友好的整体描述（约150-200字）"
}}

要求：
- area_explanation: 突出区域优势，解释交通便利性
- overall_description: 像朋友推荐一样亲切，提及景点便利性和预订建议

只输出JSON，不要其他内容。"""

            from langchain_core.messages import HumanMessage
            import json
            import re

            response = llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # 解析JSON响应
            json_match = re.search(r'\{[^{}]+\}', content, re.DOTALL)
            if json_match:
                content_dict = json.loads(json_match.group())

                area_exp = content_dict.get("area_explanation", "")
                overall_desc = content_dict.get("overall_description", "")

                if area_exp and len(area_exp) > 10:
                    result["area_explanation"] = area_exp
                if overall_desc and len(overall_desc) > 20:
                    result["llm_description"] = overall_desc

                if result:
                    logger.info(f"[住宿顾问] 批量生成住宿内容成功")
                    return result

        except Exception as e:
            logger.warning(f"[住宿顾问] 批量生成住宿内容失败: {e}，使用模板")

    # 失败时返回空字典，使用模板
    return {}


def recommend_accommodation(
    destination: str,
    days: int,
    budget_level: str = "medium",
    travelers: int = 2,
    llm=None
) -> Dict[str, Any]:
    """
    推荐住宿

    Args:
        destination: 目的地名称
        days: 旅行天数
        budget_level: 预算等级
        travelers: 旅行人数
        llm: LLM实例（可选）

    Returns:
        住宿推荐信息（包含LLM生成的描述文本）
    """
    logger.info(f"[住宿顾问] 为{destination}推荐住宿 ({days}天, {budget_level}预算)")

    acc_db = DESTINATION_ACCOMMODATION_DB.get(destination, {})
    accommodation_areas = acc_db.get("accommodation_areas", [])

    if not accommodation_areas:
        # 默认推荐
        accommodation_areas = [{
            "area": "市中心",
            "advantages": ["交通便利", "餐饮丰富"],
            "nearby_attractions": ["主要景点"],
            "price_range": {"economy": "150-300", "medium": "300-600", "luxury": "800+"},
            "recommended_hotels": {
                "economy": ["经济型酒店"],
                "medium": ["舒适型酒店"],
                "luxury": ["高端酒店"]
            }
        }]

    # 选择最适合的住宿区域
    recommended_area = _select_accommodation_area(accommodation_areas, budget_level)

    # 获取酒店推荐
    hotels = recommended_area.get("recommended_hotels", {})
    hotel_list = hotels.get(budget_level, [])
    price_range = recommended_area.get("price_range", {}).get(budget_level, "待查")

    # 计算住宿费用
    nightly_rate = _estimate_nightly_rate(budget_level, hotel_list)
    total_accommodation_cost = nightly_rate * days

    # 🚀 性能优化：批量生成区域解释和整体描述（从2次LLM调用减少到1次）
    area_explanation = None
    llm_description = None

    if llm:
        batch_content = _batch_generate_accommodation_content(
            destination,
            recommended_area,
            hotel_list,
            budget_level,
            total_accommodation_cost,
            days,
            llm
        )

        area_explanation = batch_content.get("area_explanation")
        llm_description = batch_content.get("llm_description")

    # 如果批量生成失败，使用模板
    if not area_explanation:
        area_explanation = _generate_accommodation_area_explanation(
            recommended_area.get("area", "市中心"),
            recommended_area.get("advantages", []),
            recommended_area.get("nearby_attractions", []),
            price_range,
            destination,
            None  # 使用模板
        )

    if not llm_description:
        llm_description = _generate_accommodation_description(
            destination,
            recommended_area,
            hotel_list,
            budget_level,
            total_accommodation_cost,
            days,
            None  # 使用模板
        )

    accommodation_plan = {
        "destination": destination,
        "recommended_area": {
            "area": recommended_area.get("area"),
            "reason": f"{' '.join(recommended_area.get('advantages', [])[:3])}",
            "advantages": recommended_area.get("advantages", []),
            "nearby_attractions": recommended_area.get("nearby_attractions", []),
            "ai_explanation": area_explanation  # LLM解释
        },
        "hotel_recommendations": {
            "budget_level": budget_level,
            "hotels": hotel_list[:5] if hotel_list else ["待查"],
            "price_range": price_range
        },
        "accommodation_cost": {
            "nightly_rate": nightly_rate,
            "nights": days,
            "total_cost": total_accommodation_cost,
            "per_person": total_accommodation_cost // travelers if travelers > 0 else total_accommodation_cost
        },
        "accommodation_tips": _get_accommodation_tips(destination, budget_level),
        "llm_description": llm_description  # 整体描述
    }

    logger.info(f"[住宿顾问] 完成住宿推荐，总费用: {total_accommodation_cost}元，批量优化LLM调用")

    return accommodation_plan


def _select_accommodation_area(areas: List[Dict], budget_level: str) -> Dict:
    """选择最适合的住宿区域"""

    # 根据预算优先选择
    if budget_level == "economy":
        # 优先选择价格实惠的
        return areas[0] if areas else {}
    elif budget_level == "luxury":
        # 优先选择高端的
        return areas[-1] if areas else {}
    else:
        # 中等预算，选择综合性价比高的
        return areas[len(areas) // 2] if len(areas) > 1 else (areas[0] if areas else {})


def _estimate_nightly_rate(budget_level: str, hotel_list: List[str]) -> int:
    """估算每晚房价"""

    if not hotel_list:
        base_rates = {"economy": 200, "medium": 500, "luxury": 1000}
        return base_rates.get(budget_level, 400)

    # 根据酒店列表估算
    if budget_level == "economy":
        return 250
    elif budget_level == "luxury":
        return 1200
    else:
        return 500


def _generate_accommodation_description(
    destination: str,
    recommended_area: Dict,
    hotel_list: List[str],
    budget_level: str,
    total_cost: int,
    days: int,
    llm=None
) -> str:
    """
    使用LLM生成住宿推荐的自然语言描述

    Args:
        destination: 目的地
        recommended_area: 推荐区域信息
        hotel_list: 推荐酒店列表
        budget_level: 预算等级
        total_cost: 总费用
        days: 天数
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    area = recommended_area.get("area", "市中心")
    advantages = recommended_area.get("advantages", [])
    nearby = recommended_area.get("nearby_attractions", [])

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
            prompt = f"""请为以下住宿推荐生成一段自然、友好的描述文字（约150-200字）：

目的地：{destination}
推荐住宿区域：{area}
区域优势：{', '.join(advantages[:5])}
附近景点：{', '.join(nearby[:3])}
预算等级：{budget_level}
推荐酒店：{', '.join(hotel_list[:3])}
住宿费用：{total_cost}元（{days}晚）

描述要求：
1. 用亲切自然的语气，像朋友推荐一样
2. 突出该区域的住宿优势
3. 提及附近景点的便利性
4. 给出实用的预订建议
5. 语言要生动有趣，不要像官方说明

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[住宿顾问] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[住宿顾问] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述（无LLM或LLM失败时）
    advantages_text = '、'.join(advantages[:3])
    nearby_text = '、'.join(nearby[:2])

    description = f"""为您推荐住在{area}区域，这里{advantages_text}，住宿体验非常棒。

附近有{nearby_text}等热门景点，出行游览十分便利。根据您{budget_level}预算的需求，特别推荐{', '.join(hotel_list[:3])}等酒店。

预计住宿费用约{total_cost}元（{days}晚），平均每晚{total_cost // days}元。

💡 实用小贴士：
• 建议提前网上预订，价格通常更优惠
• 查看酒店评价时，重点关注最近3个月的住客反馈
• 确认酒店到主要景点的交通方式和时间
• 了解酒店的早餐政策和周边餐饮配套

祝您住宿愉快！"""

    return description


def _get_accommodation_tips(destination: str, budget_level: str) -> List[str]:
    """获取住宿建议"""
    tips = []

    general_tips = [
        "建议提前网上预订，价格更优惠",
        "查看酒店评价，特别关注近期评价",
        "确认酒店位置与景点的距离",
        "了解酒店早餐政策和周边餐饮"
    ]

    tips.extend(general_tips)

    if destination == "北京":
        tips.extend([
            "避开旅游旺季，价格会有较大涨幅",
            "考虑选择地铁沿线酒店，出行更方便"
        ])
    elif destination == "上海":
        tips.extend([
            "外滩区域酒店价格较高，可考虑周边区域",
            "静安寺、淮海路区域性价比相对较高"
        ])
    elif destination == "厦门":
        tips.extend([
            "鼓浪屿岛上住宿需要轮渡，行李较多需考虑",
            "曾厝垵民宿较多，注意查看真实评价"
        ])

    if budget_level == "economy":
        tips.append("经济型酒店建议选择连锁品牌，品质有保障")
    elif budget_level == "luxury":
        tips.append("高端酒店建议升级房型或行政酒廊待遇")

    return tips


# LangGraph 节点函数
def accommodation_advisor_node(state: Dict) -> Dict:
    """住宿顾问节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")
    days = state.get("days", 5)
    travelers = user_portrait.get("total_travelers", 2)
    llm = state.get("_llm")

    if not destination:
        logger.error("[住宿顾问] 缺少目的地信息")
        return state

    # 推荐住宿
    accommodation_plan = recommend_accommodation(
        destination,
        days,
        budget_level,
        travelers,
        llm
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"住宿推荐完成: {accommodation_plan['recommended_area']['area']}区域",
        name="AccommodationAdvisor"
    ))

    state["accommodation_plan"] = accommodation_plan
    state["messages"] = messages

    return state
