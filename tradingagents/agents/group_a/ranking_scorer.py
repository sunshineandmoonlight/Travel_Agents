"""
排序评分智能体 (Agent A3)

综合评分，返回TOP 4推荐目的地

阶段3: 推荐地区
"""

from typing import Dict, Any, List
from langchain_core.messages import AIMessage, HumanMessage
import logging

# 导入Group A的其他智能体
from .destination_matcher import match_destinations
from .user_requirement_analyst import create_user_portrait

logger = logging.getLogger('travel_agents')


def _batch_generate_recommendation_reasons(
    top_candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    llm
) -> Dict[str, str]:
    """
    批量生成推荐理由（性能优化版本）

    一次性为所有TOP目的地生成推荐理由，而不是逐个调用LLM。
    将4次LLM调用（~8-10秒）优化为1次批量调用（~2-3秒）。

    Args:
        top_candidates: TOP候选目的地列表
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        目的地名称 -> 推荐理由 的字典
    """
    from tradingagents.utils.destination_utils import normalize_destination_name

    # 准备目的地信息
    destinations_info = []
    for candidate in top_candidates:
        dest_name = candidate["destination"]
        dest_data = candidate["raw_data"]
        dest_name_cn = normalize_destination_name(dest_name)
        match_score = candidate["match_score"]

        highlights = dest_data.get("highlights", [])[:3]
        destinations_info.append({
            "name": dest_name_cn,
            "highlights": highlights,
            "score": match_score
        })

    # 构建批量生成prompt
    user_interests = user_portrait.get("primary_interests", [])
    budget_level_map = {"economy": "经济型", "medium": "舒适型", "luxury": "品质型"}

    prompt = f"""请为以下{len(destinations_info)}个目的地各生成一句推荐理由（每句不超过50字）。

【用户信息】
兴趣：{', '.join(user_interests) if user_interests else '未指定'}
预算：{budget_level_map.get(user_portrait.get('budget', 'medium'), '舒适型')}

【目的地列表】
{_format_destinations_for_batch_reasons(destinations_info)}

【要求】
1. 每个推荐理由不超过50字
2. 突出该目的地与用户兴趣的匹配点
3. 简洁有力，有吸引力
4. 包含具体特色或景点

【输出格式】
请严格按照以下JSON格式输出，不要包含任何其他文字：
{{
  "reasons": [
    {{"destination": "城市名", "reason": "推荐理由"}},
    {{"destination": "城市名", "reason": "推荐理由"}},
    ...
  ]
}}"""

    try:
        logger.info(f"[批量推荐理由] 开始为{len(destinations_info)}个目的地批量生成推荐理由...")

        from langchain_core.messages import HumanMessage
        response = llm.invoke([HumanMessage(content=prompt)])
        response_text = response.content.strip()

        logger.info(f"[批量推荐理由] LLM响应长度: {len(response_text)}字符")

        # 解析LLM返回的JSON
        import json
        import re

        # 尝试提取JSON部分
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)

            # 构建返回字典
            reasons_dict = {}
            for item in result.get("reasons", []):
                reasons_dict[item["destination"]] = item["reason"]

            logger.info(f"[批量推荐理由] 批量生成完成，获得{len(reasons_dict)}个推荐理由")
            return reasons_dict

        else:
            logger.warning(f"[批量推荐理由] 无法从响应中提取JSON，使用规则生成")
            raise ValueError("无法解析LLM响应")

    except Exception as e:
        logger.warning(f"[批量推荐理由] 批量LLM生成失败: {e}，回退到规则生成")

        # 回退到规则生成
        reasons_dict = {}
        for candidate in top_candidates:
            dest_name = candidate["destination"]
            dest_data = candidate["raw_data"]
            from tradingagents.utils.destination_utils import normalize_destination_name
            dest_name_cn = normalize_destination_name(dest_name)
            reason = _generate_rule_based_reason(dest_name_cn, dest_data, user_portrait)
            reasons_dict[dest_name_cn] = reason
        return reasons_dict


def _format_destinations_for_batch_reasons(destinations_info: List[Dict]) -> str:
    """格式化目的地列表用于批量生成推荐理由"""
    lines = []
    for i, dest in enumerate(destinations_info, 1):
        highlights_str = '、'.join(dest['highlights'][:2])
        lines.append(f"{i}. {dest['name']}({dest['score']}分) - 特色:{highlights_str}")
    return '\n'.join(lines)


def generate_recommendation_reason(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    match_score: int,
    llm=None
) -> str:
    """
    生成推荐理由

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        match_score: 匹配分数
        llm: LLM实例（可选）

    Returns:
        推荐理由文本
    """
    # 如果有LLM，使用LLM生成
    if llm:
        try:
            prompt = f"""
请为以下目的地推荐生成2-3句推荐理由（不超过80字）：

目的地: {destination}
特色: {', '.join(dest_data.get('highlights', [])[:3])}
用户画像: {user_portrait.get('description', '')}
匹配分数: {match_score}/100

要求：
1. 突出目的地与用户需求的匹配点
2. 简洁有力，有吸引力
3. 包含具体特色或景点
"""

            response = llm.invoke([HumanMessage(content=prompt)])
            reason = response.content.strip()
            if reason and len(reason) > 10:
                return reason
        except Exception as e:
            logger.warning(f"[排序评分] LLM生成理由失败: {e}")

    # 降级：使用规则生成
    return _generate_rule_based_reason(destination, dest_data, user_portrait)


def _generate_rule_based_reason(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any]
) -> str:
    """基于规则生成推荐理由"""
    # 使用城市景点数据库获取正确的景点名称
    city_attractions = {
        "成都": ["大熊猫繁育研究基地", "宽窄巷子", "锦里古街"],
        "重庆": ["洪崖洞民俗风貌区", "李子坝轻轨", "解放碑步行街"],
        "广州": ["广州塔", "白云山", "越秀公园"],
        "长沙": ["橘子洲风景区", "岳麓山", "湖南省博物馆"],
        "北京": ["故宫博物院", "万里长城", "天坛公园"],
        "上海": ["外滩", "东方明珠", "南京路步行街"],
        "西安": ["秦始皇兵马俑", "大雁塔", "西安古城墙"],
        "杭州": ["西湖", "雷峰塔", "灵隐寺"],
        "南京": ["中山陵", "夫子庙秦淮风光带", "南京总统府"],
        "武汉": ["黄鹤楼", "东湖", "湖北省博物馆"],
        "厦门": ["鼓浪屿", "南普陀寺", "厦门大学"],
        "三亚": ["亚龙湾", "天涯海角", "南山文化旅游区"],
        "丽江": ["丽江古城", "玉龙雪山", "束河古镇"],
        "桂林": ["漓江", "象鼻山", "七星公园"]
    }

    # 城市特色描述
    city_features = {
        "成都": "美食之都，悠闲慢生活",
        "重庆": "山城夜景，火锅美食",
        "广州": "早茶文化，花城广场",
        "长沙": "星城娱乐，湘菜美食",
        "北京": "古都风韵，历史沉淀",
        "上海": "魔都风情，现代都市",
        "西安": "十三朝古都，丝路起点",
        "杭州": "人间天堂，江南水乡",
        "南京": "六朝古都，民国风情",
        "武汉": "江城风光，楚文化",
        "厦门": "海上花园，文艺小资",
        "三亚": "热带海滨，度假天堂",
        "丽江": "古城时光，雪山美景",
        "桂林": "山水甲天下，诗画田园"
    }

    highlights = city_attractions.get(destination, dest_data.get("highlights", [])[:3])
    tags = dest_data.get("tags", [])[:3]
    user_interests = user_portrait.get("primary_interests", [])

    # 构建理由
    parts = []

    # 第一句：核心亮点
    if highlights:
        parts.append(f"{highlights[0]}等精华景点")
    else:
        parts.append(city_features.get(destination, "精彩景点"))

    # 第二句：与兴趣的匹配
    if user_interests:
        for interest in user_interests:
            interest_lower = interest.lower()
            # 美食兴趣匹配美食城市
            if "美食" in interest_lower and destination in ["成都", "重庆", "广州", "长沙", "武汉"]:
                parts.append(f"完美契合您的{interest}偏好")
                break
            # 历史文化兴趣匹配历史城市
            elif "历史" in interest_lower and destination in ["北京", "西安", "南京"]:
                parts.append(f"完美契合您的{interest}偏好")
                break
            # 自然风光兴趣匹配自然城市
            elif "自然" in interest_lower and destination in ["杭州", "桂林", "三亚", "厦门"]:
                parts.append(f"完美契合您的{interest}偏好")
                break
            # 购物兴趣匹配购物城市
            elif "购物" in interest_lower and destination in ["上海", "广州"]:
                parts.append(f"完美契合您的{interest}偏好")
                break

    # 第三句：特色描述（如果没有匹配到兴趣）
    if len(parts) < 2:
        parts.append(city_features.get(destination, "值得一游"))

    # 组合
    if len(parts) == 1:
        return f"{destination}拥有{parts[0]}，值得一游。"
    elif len(parts) == 2:
        return f"{parts[0]}，{parts[1]}。"
    else:
        return f"{parts[0]}，{parts[1]}，{parts[2]}。"


def rank_and_select_top(
    candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    top_n: int = 4,
    llm=None
) -> Dict[str, Any]:
    """
    排序并选择TOP N推荐

    Args:
        candidates: 候选目的地列表
        user_portrait: 用户画像
        top_n: 返回前N个
        llm: LLM实例（可选）

    Returns:
        包含TOP N推荐目的地卡片和LLM描述的字典
    """
    logger.info(f"[排序评分] 开始排序，选择TOP {top_n}")

    # 取前top_n个（已经按分数排序）
    top_candidates = candidates[:top_n]

    # 🔧 性能优化: 批量生成所有推荐理由，而不是逐个调用LLM
    # 将4次LLM调用（~8-10秒）优化为1次批量调用（~2-3秒）
    if llm:
        batch_reasons = _batch_generate_recommendation_reasons(top_candidates, user_portrait, llm)
    else:
        # 如果没有LLM，使用规则生成
        batch_reasons = {}
        for candidate in top_candidates:
            dest_name = candidate["destination"]
            dest_data = candidate["raw_data"]
            match_score = candidate["match_score"]
            from tradingagents.utils.destination_utils import normalize_destination_name
            dest_name_cn = normalize_destination_name(dest_name)
            reason = _generate_rule_based_reason(dest_name_cn, dest_data, user_portrait)
            batch_reasons[dest_name_cn] = reason

    # 生成推荐卡片
    destination_cards = []

    for candidate in top_candidates:
        dest_name = candidate["destination"]
        dest_data = candidate["raw_data"]
        match_score = candidate["match_score"]

        # 标准化目的地名称（英文转中文）
        from tradingagents.utils.destination_utils import normalize_destination_name
        dest_name_cn = normalize_destination_name(dest_name)

        # 从批量结果中获取推荐理由
        reason = batch_reasons.get(dest_name_cn, _generate_rule_based_reason(dest_name_cn, dest_data, user_portrait))

        # 构建卡片
        # 优先使用dest_data中的images数组，如果不存在则使用Unsplash搜索
        image_url = ""
        if dest_data.get("images") and len(dest_data.get("images", [])) > 0:
            image_url = dest_data["images"][0]
        elif dest_data.get("image_url"):
            image_url = dest_data["image_url"]
        else:
            # 使用Unsplash搜索图片（使用中文名称）
            try:
                from tradingagents.tools.travel_tools import get_destination_search_tool
                search_tool = get_destination_search_tool()
                image_url = search_tool._get_destination_image(dest_name_cn)
            except Exception as e:
                logger.warning(f"[排序评分] 获取图片失败: {e}")

        # 获取正确的highlights（使用城市景点数据库）
        city_attractions = {
            "成都": ["大熊猫繁育研究基地", "宽窄巷子", "锦里古街", "武侯祠", "都江堰", "青城山", "杜甫草堂", "春熙路"],
            "重庆": ["洪崖洞民俗风貌区", "李子坝轻轨穿楼观景平台", "解放碑步行街", "磁器口古镇", "长江索道", "重庆人民大礼堂", "南山一棵树观景台"],
            "广州": ["广州塔", "白云山", "越秀公园", "陈家祠", "沙面岛", "北京路步行街", "长隆旅游度假区", "珠江夜游"],
            "长沙": ["橘子洲风景区", "岳麓山", "湖南省博物馆", "五一广场", "黄兴路步行街", "天心阁", "爱晚亭", "太平老街"],
            "北京": ["故宫博物院", "万里长城", "天坛公园", "颐和园", "天安门广场", "南锣鼓巷", "什刹海", "北海公园"],
            "上海": ["外滩", "东方明珠", "南京路步行街", "豫园", "城隍庙", "新天地", "田子坊", "迪士尼乐园"],
            "西安": ["秦始皇兵马俑", "大雁塔", "西安古城墙", "华清宫", "大唐不夜城", "回民街", "大雁塔音乐喷泉", "小雁塔"],
            "杭州": ["西湖", "雷峰塔", "灵隐寺", "西溪湿地", "宋城", "千岛湖", "河坊街", "断桥"],
            "南京": ["中山陵", "明孝陵", "夫子庙秦淮风光带", "南京总统府", "玄武湖", "中华门城堡", "南京长江大桥", "侵华日军南京大屠杀遇难同胞纪念馆"],
            "武汉": ["黄鹤楼", "东湖", "湖北省博物馆", "长江大桥", "户部巷", "武汉光谷", "归元寺", "昙华林"],
            "厦门": ["鼓浪屿", "南普陀寺", "厦门大学", "曾厝垵", "环岛路", "日光岩", "菽庄花园", "胡里山炮台"],
            "三亚": ["亚龙湾", "天涯海角", "南山文化旅游区", "亚特兰蒂斯", "蜈支洲岛", "槟榔谷", "三亚湾", "大小洞天"],
            "丽江": ["丽江古城", "玉龙雪山", "蓝月谷", "束河古镇", "白沙古镇", "拉市海", "虎跳峡", "黑龙潭"],
            "桂林": ["漓江", "象鼻山", "七星公园", "芦笛岩", "两江四湖", "阳朔西街", "月亮山", "遇龙河"]
        }

        # 使用城市景点数据库获取highlights
        highlights = city_attractions.get(dest_name_cn, dest_data.get("highlights", []))

        # 如果数据库中没有，且dest_data也没有，使用默认
        if not highlights:
            from tradingagents.utils.destination_utils import get_destination_highlights
            dest_type = dest_data.get("tags", ["旅游"])[0] if dest_data.get("tags") else "旅游"
            highlights = get_destination_highlights(dest_name_cn, dest_type)
            logger.info(f"[排序评分] 为{dest_name_cn}生成highlights: {highlights[:3]}")

        # 城市特色标签（用于suitable_for）
        city_suitable_for = {
            "成都": ["美食爱好者", "文化探索者", "休闲度假", "亲子家庭"],
            "重庆": ["美食爱好者", "夜景摄影", "探险爱好者", "年轻情侣"],
            "广州": ["美食爱好者", "购物达人", "都市观光", "商务旅行"],
            "长沙": ["美食爱好者", "夜生活爱好者", "年轻游客", "学生党"],
            "北京": ["历史文化爱好者", "首次到访者", "家庭出游", "学习考察"],
            "上海": ["购物达人", "都市观光", "商务旅行", "现代都市爱好者"],
            "西安": ["历史文化爱好者", "古都探索者", "摄影爱好者", "学习考察"],
            "杭州": ["自然风光爱好者", "休闲度假", "情侣出游", "摄影爱好者"],
            "南京": ["历史文化爱好者", "都市观光", "学生党", "周末短途游"],
            "武汉": ["美食爱好者", "都市观光", "学生党", "家庭出游"],
            "厦门": ["海滨度假", "情侣出游", "摄影爱好者", "休闲度假"],
            "三亚": ["海滨度假", "蜜月旅行", "休闲度假", "海滨运动"],
            "丽江": ["文艺青年", "情侣出游", "摄影爱好者", "古镇探索"],
            "桂林": ["自然风光爱好者", "摄影爱好者", "家庭出游", "休闲度假"]
        }

        # 获取suitable_for
        suitable_for = city_suitable_for.get(dest_name_cn, dest_data.get("best_for", ["旅行者"]))

        # 获取best_season
        city_best_season = {
            "成都": "四季皆宜，春秋最佳（3-5月，9-11月）",
            "重庆": "四季皆宜，春秋最佳（4-5月，9-10月）",
            "广州": "四季皆宜，秋冬最佳（10-12月）",
            "长沙": "四季皆宜，春秋最佳（3-5月，9-11月）",
            "北京": "四季皆宜，春秋最佳（4-5月，9-10月）",
            "上海": "四季皆宜，春秋最佳（4-5月，9-11月）",
            "西安": "四季皆宜，春秋最佳（4-5月，9-10月）",
            "杭州": "四季皆宜，春秋最佳（3-5月，9-11月）",
            "南京": "四季皆宜，春秋最佳（3-5月，10-11月）",
            "武汉": "四季皆宜，春秋最佳（3-5月，9-11月）",
            "厦门": "四季皆宜，春秋最佳（4-6月，9-11月）",
            "三亚": "秋冬最佳（11-4月），避开台风季",
            "丽江": "春夏最佳（3-5月，9-11月）",
            "桂林": "四季皆宜，春秋最佳（4-5月，9-11月）"
        }

        best_season = city_best_season.get(dest_name_cn, dest_data.get("best_season", "四季皆宜"))

        card = {
            "destination": dest_name_cn,  # 使用中文名称
            "imageUrl": image_url,
            "image_url": image_url,
            "match_score": match_score,
            "recommendation_reason": reason,
            "ai_explanation": reason,  # 统一字段名，与其他智能体保持一致
            "estimated_budget": candidate["estimated_budget"],
            "best_season": best_season,
            "suitable_for": suitable_for,
            "highlights": highlights[:5]
        }

        destination_cards.append(card)

    # 生成LLM描述
    llm_description = _generate_ranking_description(destination_cards, user_portrait, llm)

    logger.info(f"[排序评分] 生成{len(destination_cards)}个推荐卡片")

    return {
        "destination_cards": destination_cards,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "排序评分专家",
            "name_en": "RankingScorer",
            "icon": "📊",
            "group": "A"
        }
    }


def _generate_ranking_description(
    destination_cards: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """
    生成排序推荐的LLM描述

    Args:
        destination_cards: 目的地卡片列表
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    top_destinations = [c['destination'] for c in destination_cards[:3]]
    destinations_text = '、'.join(top_destinations)

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
            scores_text = '、'.join([f"{c['destination']}({c['match_score']}分)" for c in destination_cards])

            prompt = f"""请为以下TOP目的地推荐生成一段自然、吸引人的总结描述（约150-200字）：

推荐目的地：{destinations_text}
匹配分数：{scores_text}
用户画像：{user_portrait.get('description', '热爱旅行')}

描述要求：
1. 用总结性的语气，突出推荐结果的可靠性
2. 解释这些目的地是如何被精选出来的
3. 给出选择建议
4. 语言要专业可靠，同时有吸引力

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[排序评分专家] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[排序评分专家] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述
    description = f"""经过智能算法的综合评分和多维度分析，我们为您精选出以下{len(destination_cards)}个最佳目的地！🏆

🌟 推荐结果亮点：

{chr(10).join([f"{i+1}. {c['destination']} - 综合评分{c['match_score']}分" for i, c in enumerate(destination_cards)])}

💎 评分依据：
• 兴趣匹配度：与您的偏好高度契合
• 预算适配度：符合您的{user_portrait.get('budget_level', '舒适')}预算
• 季节适宜性：当前为最佳旅行时机
• 综合价值：景点丰富度、交通便利性等综合考虑

💡 选择建议：
• 排名第一的目的地是您的最佳选择
• 其他目的地各有特色，可根据具体时间安排选择
• 所有目的地都经过精心筛选，保证旅行体验

我们已为您完成目的地筛选，接下来请选择您心仪的目的地，开始规划详细行程！✨"""

    return description


def ranking_scorer_node(state: Dict) -> Dict:
    """
    排序评分智能体节点（用于LangGraph）

    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    candidates = state.get("candidate_destinations", [])
    user_portrait = state.get("user_portrait")
    llm = state.get("_llm")

    if not candidates:
        logger.error("[排序评分] 缺少候选目的地")
        state["error"] = "缺少候选目的地"
        return state

    # 排序并选择TOP 4
    ranking_result = rank_and_select_top(
        candidates,
        user_portrait,
        top_n=4,
        llm=llm
    )

    recommended_destinations = ranking_result.get("destination_cards", [])

    # 更新状态
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"排序评分完成: 推荐TOP {len(recommended_destinations)}目的地",
        name="RankingScorer"
    ))

    state["recommended_destinations"] = recommended_destinations
    state["ranking_llm_description"] = ranking_result.get("llm_description", "")
    state["messages"] = messages
    state["current_stage"] = "destinations_ranked"

    return state


# ============================================================
# 独立调用函数（用于API）
# ============================================================

def rank_and_recommend(
    candidates: List[Dict[str, Any]],
    user_portrait: Dict[str, Any],
    top_n: int = 4,
    llm=None
) -> Dict[str, Any]:
    """
    排序并推荐目的地（独立调用）

    Args:
        candidates: 候选目的地列表
        user_portrait: 用户画像
        top_n: 返回前N个
        llm: LLM实例（可选）

    Returns:
        包含推荐目的地的响应
    """
    ranking_result = rank_and_select_top(
        candidates,
        user_portrait,
        top_n,
        llm
    )

    return {
        "success": True,
        "destinations": ranking_result.get("destination_cards", []),
        "llm_description": ranking_result.get("llm_description", ""),
        "agent_info": {
            "name": "RankingScorer",
            "icon": "📊",
            "description": "综合评分，推荐最佳目的地"
        }
    }


# ============================================================
# 完整的地区推荐流程（组A智能体联合调用）
# ============================================================

def recommend_destinations(
    requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    完整的地区推荐流程

    依次调用组A的3个智能体：
    1. UserRequirementAnalyst - 分析需求
    2. DestinationMatcher - 匹配目的地（使用实时搜索）
    3. RankingScorer - 排序推荐

    Args:
        requirements: 用户需求表单数据
        llm: LLM实例（可选）

    Returns:
        包含TOP 4推荐目的地的响应
    """
    from .user_requirement_analyst import create_user_portrait
    from .destination_matcher import match_destinations_realtime

    logger.info("[地区推荐] 开始完整推荐流程（实时搜索模式）")

    # Agent A1: 分析需求
    user_portrait = create_user_portrait(requirements, llm)

    # Agent A2: 匹配目的地（使用match_destinations以获取LLM描述）
    travel_scope = requirements.get('travel_scope', 'domestic')
    matching_result = match_destinations(user_portrait, travel_scope, llm)

    # Agent A3: 排序推荐
    ranking_result = rank_and_select_top(
        matching_result.get("candidates", []),
        user_portrait,
        top_n=4,
        llm=llm
    )

    # 构建最终结果
    destination_cards = ranking_result.get("destination_cards", [])

    result = {
        "destinations": destination_cards,
        "user_portrait": user_portrait,
        "realtime_search_enabled": True,
        # 添加LLM描述
        "user_portrait_llm_description": user_portrait.get("llm_description", ""),
        "matching_llm_description": matching_result.get("llm_description", ""),
        "ranking_llm_description": ranking_result.get("llm_description", "")
    }

    logger.info("[地区推荐] 推荐流程完成（实时搜索）")

    return result
