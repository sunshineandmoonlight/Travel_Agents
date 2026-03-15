"""
LLM攻略写作师 (Agent C5增强版)

职责: 使用LLM生成真正详细、具体的攻略内容
输入: 景点安排 + 交通 + 餐饮 + 住宿 + 天气
输出: LLM生成的详细攻略文本（不是简单格式化）

与普通GuideFormatter的区别：
- 普通版：只做格式化，拼接其他智能体的结果
- LLM版：调用LLM生成连贯、详细、有体验感的攻略文本
"""

from typing import Dict, Any, List
import logging
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger('travel_agents')


def write_detailed_guide_with_llm(
    destination: str,
    style_proposal: Dict[str, Any],
    scheduled_attractions: List[Dict[str, Any]],
    transport_plan: Dict[str, Any],
    dining_plan: Dict[str, Any],
    accommodation_plan: Dict[str, Any],
    user_requirements: Dict[str, Any],
    llm=None
) -> Dict[str, Any]:
    """
    使用LLM生成真正详细的攻略

    LLM会生成：
    1. 每个景点的详细介绍和游览建议
    2. 连贯的行程描述，不是简单的信息堆砌
    3. 实用的旅行贴士和注意事项
    4. 有温度的攻略文本，像真人写的

    Args:
        destination: 目的地名称
        style_proposal: 风格方案
        scheduled_attractions: 景点日程安排
        transport_plan: 交通计划
        dining_plan: 餐饮计划
        accommodation_plan: 住宿计划
        user_requirements: 用户需求
        llm: LLM实例（必需）

    Returns:
        LLM生成的详细攻略
    """
    if not llm:
        logger.warning("[LLM攻略写作师] 没有LLM实例，回退到普通格式化")
        from .guide_formatter import format_detailed_guide
        return format_detailed_guide(
            destination, style_proposal, scheduled_attractions,
            transport_plan, dining_plan, accommodation_plan,
            user_requirements, llm
        )

    logger.info(f"[LLM攻略写作师] 为{destination}生成LLM详细攻略")

    # 第一步：生成整体攻略概览
    overview = _generate_overview_with_llm(
        destination,
        style_proposal,
        scheduled_attractions,
        user_requirements,
        llm
    )

    # 第二步：逐天生成详细行程（使用LLM增强）
    enhanced_daily_itineraries = []
    for day_schedule in scheduled_attractions:
        enhanced_day = _generate_enhanced_day_with_llm(
            destination,
            day_schedule,
            dining_plan,
            transport_plan,
            style_proposal,
            llm
        )
        enhanced_daily_itineraries.append(enhanced_day)

    # 第三步：生成实用的旅行贴士
    travel_tips = _generate_travel_tips_with_llm(
        destination,
        style_proposal,
        user_requirements,
        llm
    )

    # 第四步：生成打包清单
    packing_list = _generate_packing_list_with_llm(
        destination,
        style_proposal,
        user_requirements,
        llm
    )

    # 计算总预算
    total_budget = _calculate_total_budget(
        style_proposal, transport_plan, dining_plan, accommodation_plan
    )

    detailed_guide = {
        "destination": destination,
        "style_type": style_proposal.get("style_type"),
        "style_name": style_proposal.get("style_name"),
        "total_days": len(scheduled_attractions),
        "start_date": user_requirements.get("start_date", datetime.now().strftime("%Y-%m-%d")),

        # LLM生成的内容
        "overview": overview,
        "daily_itineraries": enhanced_daily_itineraries,
        "travel_tips": travel_tips,
        "packing_list": packing_list,

        # 预算明细
        "budget_breakdown": {
            "total_budget": total_budget,
            "attractions": _calculate_attraction_cost(scheduled_attractions),
            "transport": transport_plan.get("total_transport_cost", 0),
            "dining": dining_plan.get("estimated_meal_cost", {}).get("per_day", 200) * len(scheduled_attractions),
            "accommodation": accommodation_plan.get("accommodation_cost", {}).get("total_cost", 0)
        },

        # 元数据
        "generated_by": "LLM Guide Writer",
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data_source": "llm_generated"
    }

    logger.info(f"[LLM攻略写作师] LLM详细攻略生成完成")

    return detailed_guide


def _generate_overview_with_llm(
    destination: str,
    style_proposal: Dict,
    scheduled_attractions: List[Dict],
    user_requirements: Dict,
    llm
) -> str:
    """使用LLM生成攻略概览（集成天行数据真实景点信息）"""

    # 提取关键信息
    style_name = style_proposal.get("style_name", "")
    style_desc = style_proposal.get("style_description", "")
    days = len(scheduled_attractions)

    # 🔥 新增：获取真实景点列表（天行数据）
    real_attractions_info = _get_real_attractions_context(destination)

    # 统计景点
    attractions = []
    for day in scheduled_attractions:
        for item in day.get("schedule", []):
            activity = item.get("activity", "")
            if activity and item.get("period") not in ["lunch", "dinner"]:
                attractions.append(activity)

    unique_attractions = list(set(attractions))[:5]  # 前5个不重复的景点

    # 构建提示词
    attractions_str = ', '.join(unique_attractions[:3]) if unique_attractions else "精彩景点"

    prompt = f"""请为以下旅行计划生成一个吸引人的概览介绍（150-200字）：

目的地：{destination}
旅行天数：{days}天
旅行风格：{style_name} - {style_desc}

主要景点：{attractions_str}等

{real_attractions_info}

要求：
1. 开头要吸引人，突出目的地特色
2. 介绍这次旅行的核心体验
3. ⚠️ 基于真实景点信息生成，不要编造不存在的景点
4. 语言生动有感染力，让读者期待这次旅行
5. 150-200字左右

请直接输出概览文本，不要其他内容："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        overview = response.content.strip()
        if overview and len(overview) > 50:
            logger.info(f"[LLM攻略写作师] 概览生成成功: {len(overview)}字")
            return overview
    except Exception as e:
        logger.warning(f"[LLM攻略写作师] 概览生成失败: {e}")

    # 降级：规则生成
    return f"""欢迎来到{destination}！这是一个{style_name}的{days}天之旅。

{style_desc}

在这次旅程中，您将探索{attractions_str if attractions_str else '精彩景点'}等著名地标，
体验当地独特的文化与美食，创造难忘的旅行回忆。

让我们开始这段精彩的旅程吧！"""


def _generate_enhanced_day_with_llm(
    destination: str,
    day_schedule: Dict,
    dining_plan: Dict,
    transport_plan: Dict,
    style_proposal: Dict,
    llm
) -> Dict[str, Any]:
    """使用LLM增强单天的行程"""

    day_num = day_schedule.get("day", 1)
    date = day_schedule.get("date", "")
    title = day_schedule.get("title", f"第{day_num}天")
    schedule_items = day_schedule.get("schedule", [])

    # 提取当天的景点和活动
    morning_attractions = []
    afternoon_attractions = []
    for item in schedule_items:
        activity = item.get("activity", "")
        period = item.get("period", "")
        description = item.get("description", "")

        if period == "morning" and activity:
            morning_attractions.append({
                "name": activity,
                "description": description,
                "time_range": item.get("time_range", ""),
                "ticket": item.get("ticket", {})
            })
        elif period == "afternoon" and activity:
            afternoon_attractions.append({
                "name": activity,
                "description": description,
                "time_range": item.get("time_range", ""),
                "ticket": item.get("ticket", {})
            })

    # 生成当天的详细描述
    day_description = _generate_day_description_with_llm(
        destination,
        day_num,
        morning_attractions,
        afternoon_attractions,
        style_proposal,
        llm
    )

    # 为每个景点生成详细介绍
    enhanced_schedule = []
    for item in schedule_items:
        enhanced_item = item.copy()

        # 为景点添加详细介绍和验证信息
        if item.get("period") not in ["lunch", "dinner"]:
            attraction_name = item.get("activity", "")
            if attraction_name:
                # 🔥 新增：验证景点是否存在于天行数据
                is_verified = _verify_attraction_from_tianapi(attraction_name, destination)

                # 生成详细介绍
                enhanced_item["detailed_description"] = _generate_attraction_description_with_llm(
                    destination,
                    attraction_name,
                    item.get("description", ""),
                    llm
                )

                # 添加验证标记
                enhanced_item["attraction_verified"] = is_verified
                enhanced_item["data_source"] = "tianapi_verified" if is_verified else "llm_generated"

                # 如果有子景点信息，添加到item中
                sub_attractions = _get_attraction_sub_attractions_list(attraction_name, destination)
                if sub_attractions:
                    enhanced_item["sub_attractions"] = sub_attractions

        # 处理餐饮信息
        if item.get("period") == "lunch":
            enhanced_item["dining"] = _get_dining_for_meal("lunch", dining_plan, day_num - 1)
        elif item.get("period") == "dinner":
            enhanced_item["dining"] = _get_dining_for_meal("dinner", dining_plan, day_num - 1)

        enhanced_schedule.append(enhanced_item)

    return {
        "day": day_num,
        "date": date,
        "title": title,
        "description": day_description,
        "schedule": enhanced_schedule,
        "pace": day_schedule.get("pace", "适中"),
        "daily_budget": day_schedule.get("daily_budget", 500)
    }


def _generate_day_description_with_llm(
    destination: str,
    day_num: int,
    morning_attractions: List[Dict],
    afternoon_attractions: List[Dict],
    style_proposal: Dict,
    llm
) -> str:
    """生成单天的行程描述（集成天行数据）"""

    style_type = style_proposal.get("style_type", "immersive")

    # 🔥 增强：为景点添加真实描述和子景点信息
    enhanced_morning = []
    for attr in morning_attractions[:2]:
        name = attr["name"]
        real_desc = _get_real_attraction_description(name, destination)
        sub_attractions = _get_attraction_sub_attractions(name, destination)

        desc = real_desc if real_desc else attr.get("description", "")
        enhanced_morning.append({
            "name": name,
            "description": desc,
            "sub_attractions": sub_attractions
        })

    enhanced_afternoon = []
    for attr in afternoon_attractions[:2]:
        name = attr["name"]
        real_desc = _get_real_attraction_description(name, destination)
        sub_attractions = _get_attraction_sub_attractions(name, destination)

        desc = real_desc if real_desc else attr.get("description", "")
        enhanced_afternoon.append({
            "name": name,
            "description": desc,
            "sub_attractions": sub_attractions
        })

    morning_str = "、".join([a["name"] + a["sub_attractions"] for a in enhanced_morning])
    afternoon_str = "、".join([a["name"] + a["sub_attractions"] for a in enhanced_afternoon])

    # 如果没有景点，使用简单格式
    if not morning_str and not afternoon_str:
        morning_str = "、".join([a["name"] for a in morning_attractions[:2]])
        afternoon_str = "、".join([a["name"] for a in afternoon_attractions[:2]])

    prompt = f"""请为以下行程生成一天的精彩描述（100-150字）：

第{day_num}天行程：
上午：{morning_str if morning_str else '自由活动'}
下午：{afternoon_str if afternoon_str else '自由活动'}

旅行风格：{style_proposal.get('style_name', '')}

要求：
1. 描述要生动有感染力
2. 突出当天的亮点和体验
3. ⚠️ 基于真实景点信息生成
4. 语言要流畅自然
5. 100-150字

请直接输出描述文本："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        description = response.content.strip()
        if description and len(description) > 30:
            return description
    except Exception as e:
        logger.warning(f"[LLM攻略写作师] 第{day_num}天描述生成失败: {e}")

    # 降级：规则生成
    morning_names = "、".join([a["name"] for a in morning_attractions[:2]])
    afternoon_names = "、".join([a["name"] for a in afternoon_attractions[:2]])

    if morning_names and afternoon_names:
        return f"今天上午游览{morning_names}，感受{destination}的独特魅力。下午继续探索{afternoon_names}，深入体验当地文化。"
    elif morning_names:
        return f"今天上午游览{morning_names}，开启精彩的一天。"
    else:
        return f"第{day_num}天，享受悠闲的旅行时光。"


def _generate_attraction_description_with_llm(
    destination: str,
    attraction_name: str,
    basic_description: str,
    llm
) -> str:
    """为景点生成详细介绍（集成天行数据）"""

    # 🔥 新增：尝试从天行数据获取真实景点描述
    real_description = _get_real_attraction_description(attraction_name, destination)

    # 如果有天行数据，使用真实描述作为基础
    base_desc = real_description if real_description else basic_description

    prompt = f"""请为以下景点生成详细介绍（80-120字）：

目的地：{destination}
景点名称：{attraction_name}
真实描述：{base_desc}

要求：
1. 基于真实景点描述生成内容
2. 介绍景点的特色和亮点
3. 提供实用的游览建议
4. 语言生动，让读者想去游览
5. ⚠️ 不要编造不存在的信息
6. 80-120字

请直接输出介绍文本："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        description = response.content.strip()
        if description and len(description) > 20:
            logger.info(f"[LLM攻略写作师] {attraction_name}介绍生成成功")
            return description
    except Exception as e:
        logger.warning(f"[LLM攻略写作师] {attraction_name}介绍生成失败: {e}")

    # 降级：返回基础描述
    return base_desc or f"{attraction_name}是{destination}的著名景点，值得一游。"


def _get_dining_for_meal(
    meal_type: str,
    dining_plan: Dict,
    day_index: int
) -> Dict:
    """获取餐饮信息"""
    daily_dining = dining_plan.get("daily_dining", [])
    if day_index < len(daily_dining):
        day_dining = daily_dining[day_index]
        meal = day_dining.get(meal_type)
        if meal:
            return meal

    # 默认餐饮信息
    return {
        "recommended_restaurant": "待定",
        "cuisine_type": "当地特色",
        "estimated_cost": 80 if meal_type == "lunch" else 120,
        "area": "待定区域"
    }


def _generate_travel_tips_with_llm(
    destination: str,
    style_proposal: Dict,
    user_requirements: Dict,
    llm
) -> List[str]:
    """生成旅行贴士"""

    style_type = style_proposal.get("style_type", "immersive")
    days = user_requirements.get("days", 5)
    budget = user_requirements.get("budget", "medium")

    prompt = f"""请为以下旅行生成5-8条实用贴士：

目的地：{destination}
旅行天数：{days}天
旅行风格：{style_proposal.get('style_name', '')}
预算：{budget}

要求：
1. 贴分类型：交通、餐饮、住宿、购物、安全、文化等
2. 每条贴士简洁实用，10-20字
3. 基于目的地特点给出针对性建议
4. 5-8条贴士

请直接输出贴士列表，每条一行："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        tips_text = response.content.strip()

        # 解析贴士
        tips = []
        for line in tips_text.split('\n'):
            line = line.strip()
            if line and not line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '•', '-')):
                tips.append(line)
            elif line.startswith(('1', '2', '3', '4', '5', '6', '7', '8')):
                # 去掉序号
                clean_line = line.lstrip('12345678. •-')
                if clean_line:
                    tips.append(clean_line.strip())

        if tips and len(tips) >= 3:
            return tips[:8]

    except Exception as e:
        logger.warning(f"[LLM攻略写作师] 贴士生成失败: {e}")

    # 降级：规则生成
    return [
        f"提前了解{destination}的文化习俗，尊重当地传统",
        "建议提前预订热门景点的门票，避免排队",
        "注意保管好随身物品，特别是在人多的地方",
        "尝试当地特色美食，体验地道风味",
        "携带常用药品，以备不时之需"
    ]


def _generate_packing_list_with_llm(
    destination: str,
    style_proposal: Dict,
    user_requirements: Dict,
    llm
) -> List[str]:
    """生成打包清单"""

    days = user_requirements.get("days", 5)
    style_type = style_proposal.get("style_type", "immersive")
    budget = user_requirements.get("budget", "medium")

    prompt = f"""请为以下旅行生成打包清单（8-12项）：

目的地：{destination}
旅行天数：{days}天
旅行风格：{style_proposal.get('style_name', '')}

要求：
1. 包含：衣物、证件、电子设备、日用品、药品等
2. 每项简洁明了，5-10字
3. 根据目的地特点添加必要物品
4. 8-12项

请直接输出清单，每项一行："""

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        items_text = response.content.strip()

        # 解析清单
        items = []
        for line in items_text.split('\n'):
            line = line.strip()
            if line and not line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '•', '-')):
                items.append(line)
            elif line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9')):
                clean_line = line.lstrip('123456789. •-')
                if clean_line:
                    items.append(clean_line.strip())

        if items and len(items) >= 5:
            return items[:12]

    except Exception as e:
        logger.warning(f"[LLM攻略写作师] 清单生成失败: {e}")

    # 降级：规则生成
    return [
        "身份证/护照等重要证件",
        "手机、充电器、充电宝",
        "舒适的步行鞋",
        "防晒霜、遮阳帽/雨伞",
        "常用药品（感冒药、肠胃药等）",
        "换洗衣物（根据天数准备）",
        "洗漱用品（牙刷、牙膏等）",
        "少量现金和银行卡"
    ]


def _calculate_total_budget(
    style_proposal: Dict,
    transport_plan: Dict,
    dining_plan: Dict,
    accommodation_plan: Dict
) -> int:
    """计算总预算"""
    base_cost = style_proposal.get("estimated_cost", 0)
    transport_cost = transport_plan.get("total_transport_cost", 0)
    accommodation_cost = accommodation_plan.get("accommodation_cost", {}).get("total_cost", 0)
    meal_cost = dining_plan.get("estimated_meal_cost", {}).get("per_day", 200)
    days = len(transport_plan.get("daily_transport", []))
    dining_cost = meal_cost * days if days > 0 else 0

    return base_cost + transport_cost + accommodation_cost + dining_cost


def _calculate_attraction_cost(scheduled_attractions: List[Dict]) -> int:
    """计算门票费用"""
    total = 0
    for day in scheduled_attractions:
        for item in day.get("schedule", []):
            ticket = item.get("ticket", {})
            if isinstance(ticket, dict):
                total += ticket.get("price", 0)
    return total


# LangGraph节点函数
def llm_guide_writer_node(state: Dict) -> Dict:
    """LLM攻略写作师节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    style_proposal = state.get("selected_style_proposal", {})
    scheduled_attractions = state.get("scheduled_attractions", [])
    transport_plan = state.get("transport_plan", {})
    dining_plan = state.get("dining_plan", {})
    accommodation_plan = state.get("accommodation_plan", {})
    user_requirements = state.get("user_requirements", {})
    llm = state.get("_llm")

    if not destination or not scheduled_attractions:
        logger.error("[LLM攻略写作师] 缺少必要数据")
        return state

    # 使用LLM生成详细攻略
    detailed_guide = write_detailed_guide_with_llm(
        destination,
        style_proposal,
        scheduled_attractions,
        transport_plan,
        dining_plan,
        accommodation_plan,
        user_requirements,
        llm
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"LLM详细攻略生成完成: {destination} {len(scheduled_attractions)}天行程",
        name="LLMGuideWriter"
    ))

    state["detailed_guide"] = detailed_guide
    state["messages"] = messages

    return state


# ============================================================
# 天行数据集成辅助函数
# ============================================================
# 天行数据优化 - 批量加载和缓存
# ============================================================

# 天行数据缓存（减少API调用）
_TIANAPI_CITY_CACHE = {}
_TIANAPI_CACHE_TIME = {}
_TIANAPI_CACHE_TTL = 3600  # 1小时缓存


def _batch_load_city_attractions(city: str, attraction_names: List[str]) -> Dict[str, Dict]:
    """
    批量加载城市景点数据（优化版）

    一次API调用获取所有景点数据，然后本地查询
    将API调用从 ~76次 减少到 ~2次

    Args:
        city: 城市名称
        attraction_names: 需要查询的景点名称列表

    Returns:
        景点数据映射 {attraction_name: {verified, description, sub_attractions}}
    """
    import time

    # 检查缓存
    if city in _TIANAPI_CITY_CACHE:
        cache_time = _TIANAPI_CACHE_TIME.get(city, 0)
        if time.time() - cache_time < _TIANAPI_CACHE_TTL:
            logger.debug(f"[LLM攻略写作师] 使用天行数据缓存: {city}")
            return _TIANAPI_CITY_CACHE[city]

    try:
        # 一次API调用获取所有景点详情
        from tradingagents.tools.travel_tools_tianapi import validate_and_enrich_attraction_names

        logger.info(f"[LLM攻略写作师] 批量加载 {city} 景点数据")

        result = validate_and_enrich_attraction_names(
            attraction_names=attraction_names,
            city=city
        )

        # 构建景点数据映射
        attraction_map = {}

        # 添加验证通过的景点
        for name in result['valid']:
            if name in result['details']:
                data = result['details'][name]
                attraction_map[name] = {
                    'verified': True,
                    'description': data.get('description', ''),
                    'sub_attractions': data.get('sub_attractions', []),
                    'province': data.get('province', ''),
                    'city': data.get('city', '')
                }

        # 添加未验证的景点
        for name in result['invalid']:
            attraction_map[name] = {
                'verified': False,
                'description': '',
                'sub_attractions': [],
                'province': '',
                'city': city
            }

        # 存入缓存
        _TIANAPI_CITY_CACHE[city] = attraction_map
        _TIANAPI_CACHE_TIME[city] = time.time()

        logger.info(f"[LLM攻略写作师] 已缓存 {len(attraction_map)} 个景点")

        return attraction_map

    except Exception as e:
        logger.warning(f"[LLM攻略写作师] 批量加载失败: {e}")
        return {}


# ============================================================

def _get_real_attractions_context(destination: str) -> str:
    """
    获取城市的真实景点列表（用于LLM提示词）

    Args:
        destination: 目的地名称

    Returns:
        格式化的景点列表文本
    """
    try:
        from tradingagents.tools.travel_tools_tianapi import (
            get_city_attractions_for_agent
        )

        attractions_text = get_city_attractions_for_agent(
            city=destination,
            limit=20,
            format_for_llm=True
        )

        if attractions_text:
            logger.info(f"[LLM攻略写作师] 已加载 {destination} 的真实景点数据")
            return f"\n\n**{destination} 真实景点列表（必须从这些景点中选择）：**\n{attractions_text}\n"
        else:
            logger.info(f"[LLM攻略写作师] {destination} 无天行数据，使用LLM生成")
            return ""

    except Exception as e:
        logger.debug(f"[LLM攻略写作师] 获取真实景点数据失败: {e}")
        return ""


def _get_real_attraction_description(attraction_name: str, city: str) -> str:
    """
    获取景点的真实描述（优化版，使用缓存）

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        真实景点描述，如果未找到则返回None
    """
    try:
        # 使用批量加载的缓存数据
        attraction_map = _batch_load_city_attractions(city, [attraction_name])

        if attraction_name in attraction_map:
            desc = attraction_map[attraction_name].get('description', '')
            if desc:
                logger.debug(f"[LLM攻略写作师] 使用天行数据: {attraction_name}")
                return desc

    except Exception as e:
        logger.debug(f"[LLM攻略写作师] 获取景点描述失败: {e}")

    return None


def _get_attraction_sub_attractions(attraction_name: str, city: str) -> str:
    """
    获取景点的子景点列表（优化版，使用缓存）

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        子景点列表字符串
    """
    try:
        # 使用批量加载的缓存数据
        attraction_map = _batch_load_city_attractions(city, [attraction_name])

        if attraction_name in attraction_map:
            sub_attractions = attraction_map[attraction_name].get('sub_attractions', [])

            if sub_attractions:
                # 选择前3个最有代表性的子景点
                top_subs = sub_attractions[:3] if len(sub_attractions) > 3 else sub_attractions
                logger.debug(f"[LLM攻略写作师] {attraction_name} 子景点: {top_subs}")
                return f"，包含{', '.join(top_subs)}等景点"

    except Exception as e:
        logger.debug(f"[LLM攻略写作师] 获取子景点失败: {e}")

    return ""


def _verify_attraction_from_tianapi(attraction_name: str, city: str) -> bool:
    """
    验证景点是否存在于天行数据（优化版，使用缓存）

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        是否验证通过
    """
    try:
        # 使用批量加载的缓存数据
        attraction_map = _batch_load_city_attractions(city, [attraction_name])

        is_valid = attraction_name in attraction_map and attraction_map[attraction_name].get('verified', False)

        if is_valid:
            logger.debug(f"[LLM攻略写作师] ✓ 景点验证通过: {attraction_name}")

        return is_valid

    except Exception as e:
        logger.debug(f"[LLM攻略写作师] 景点验证失败: {e}")
        return False


def _get_attraction_sub_attractions_list(attraction_name: str, city: str) -> List[str]:
    """
    获取景点的子景点列表（优化版，使用缓存）

    Args:
        attraction_name: 景点名称
        city: 城市名称

    Returns:
        子景点列表
    """
    try:
        # 使用批量加载的缓存数据
        attraction_map = _batch_load_city_attractions(city, [attraction_name])

        if attraction_name in attraction_map:
            return attraction_map[attraction_name].get('sub_attractions', [])

        return []

    except Exception as e:
        logger.debug(f"[LLM攻略写作师] 获取子景点列表失败: {e}")
        return []


# 导出
__all__ = [
    "write_detailed_guide_with_llm",
    "llm_guide_writer_node"
]
