"""
交通规划师 (Agent C2)

职责: 规划景点间交通方式，估算交通时间和费用
输入: 景点位置安排
输出: 交通建议（地铁/打车/步行）
- 调用交通规划工具API获取实时路线信息
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger('travel_agents')


def _plan_route_with_tool(
    from_location: str,
    to_location: str,
    destination: str
) -> Dict[str, Any]:
    """
    调用交通工具规划路线

    Args:
        from_location: 出发地
        to_location: 目的地
        destination: 城市

    Returns:
        路线信息
    """
    try:
        from tradingagents.tools.travel_tools import get_transport_tool

        transport_tool = get_transport_tool()
        route = transport_tool.plan_route(
            from_location=from_location,
            to_location=to_location,
            city=destination
        )

        if route:
            return {
                "method": route.get("recommended_method", "地铁/公交"),
                "route": route.get("description", f"从{from_location}到{to_location}"),
                "duration": route.get("duration", "约30分钟"),
                "cost": route.get("cost", 5),
                "data_source": "realtime_api"
            }
        else:
            # 工具返回空，使用降级估算
            return None

    except Exception as e:
        logger.warning(f"[交通规划师] 路线规划失败: {e}")
        return None


def _estimate_transport_segment(
    from_location: str,
    to_location: str,
    destination: str,
    budget_level: str,
    llm=None,
    batch_mode: bool = True
) -> Dict[str, Any]:
    """
    估算交通路段信息（降级方法）

    优先调用工具API，失败时使用规则估算

    Args:
        batch_mode: 批量模式，True时不立即生成LLM解释（性能优化）
    """

    # 1. 尝试调用工具API
    route_info = _plan_route_with_tool(from_location, to_location, destination)
    if route_info:
        # 批量模式：不立即生成LLM解释，返回原始数据供后续批量处理
        if batch_mode:
            route_info["_explanation_data"] = {
                "method": route_info.get("method", ""),
                "from": from_location,
                "to": to_location,
                "cost": route_info.get("cost", 0),
                "duration": route_info.get("duration", ""),
                "destination": destination
            }
        else:
            # 兼容旧逻辑：立即生成解释
            route_info["ai_explanation"] = _generate_transport_segment_explanation(
                route_info.get("method", ""),
                from_location,
                to_location,
                route_info.get("cost", 0),
                route_info.get("duration", ""),
                destination,
                llm
            )
        return route_info

    # 2. 降级：使用规则估算
    logger.info(f"[交通规划师] 使用估算: {from_location}→{to_location}")

    # 简单估算逻辑
    distance_km = 5  # 默认假设5公里

    # 根据预算推荐方式
    if budget_level == "economy":
        method = "地铁/公交"
        cost = 5
        duration = "40分钟"
    elif budget_level == "luxury":
        method = "打车"
        cost = 30
        duration = "20分钟"
    else:  # medium
        method = "地铁/公交或打车"
        cost = 15
        duration = "30分钟"

    segment = {
        "method": method,
        "route": f"从{from_location}到{to_location}",
        "duration": duration,
        "cost": cost,
        "data_source": "estimated",
        "_explanation_data": {
            "method": method,
            "from": from_location,
            "to": to_location,
            "cost": cost,
            "duration": duration,
            "destination": destination
        }
    }

    # 批量模式：不立即生成LLM解释
    if not batch_mode:
        segment["ai_explanation"] = _generate_transport_segment_explanation(
            method, from_location, to_location, cost, duration, destination, llm
        )

    return segment


def plan_transport(
    destination: str,
    scheduled_attractions: List[Dict[str, Any]],
    budget_level: str = "medium",
    llm=None
) -> Dict[str, Any]:
    """
    规划交通方式

    优先调用工具API获取实时路线，失败时使用估算

    Args:
        destination: 目的地名称
        scheduled_attractions: 已安排的景点日程
        budget_level: 预算等级 (economy/medium/luxury)
        llm: LLM实例（可选）

    Returns:
        交通规划信息
    """
    logger.info(f"[交通规划师] 为{destination}规划交通方式")

    transport_plan = {
        "destination": destination,
        "daily_transport": [],
        "total_transport_cost": 0,
        "transport_recommendations": []
    }

    # 为每天规划交通
    total_cost = 0
    api_call_count = 0
    all_segments = []  # 收集所有路段用于批量生成解释

    for day_schedule in scheduled_attractions:
        day_num = day_schedule.get("day", 1)
        schedule_items = day_schedule.get("schedule", [])

        day_transport = {
            "day": day_num,
            "transport_segments": []
        }

        # 分析当天的活动顺序，规划交通
        prev_location = "酒店"

        for item in schedule_items:
            period = item.get("period", "")
            activity = item.get("activity", "")
            location = item.get("location", activity)

            # 跳过用餐时段的交通规划（餐饮推荐师会处理）
            if period in ["lunch", "dinner"]:
                continue

            # 规划到该地点的交通
            if location and location != "待定":
                transport_segment = _estimate_transport_segment(
                    prev_location,
                    location,
                    destination,
                    budget_level,
                    llm,
                    batch_mode=True  # 使用批量模式
                )

                if transport_segment.get("data_source") == "realtime_api":
                    api_call_count += 1

                day_transport["transport_segments"].append(transport_segment)
                all_segments.append(transport_segment)  # 收集用于批量处理
                total_cost += transport_segment["cost"]

                prev_location = location

        transport_plan["daily_transport"].append(day_transport)

    transport_plan["total_transport_cost"] = total_cost
    transport_plan["transport_recommendations"] = _get_transport_recommendations(destination, budget_level)
    transport_plan["api_used"] = api_call_count > 0

    # 🚀 性能优化：批量生成所有路段的LLM解释
    if all_segments and llm:
        batch_explanations = _batch_generate_transport_explanations(all_segments, llm)

        # 应用批量生成的解释，未生成到的使用模板
        for i, segment in enumerate(all_segments):
            exp_data = segment.get("_explanation_data")
            if exp_data:
                if i in batch_explanations:
                    segment["ai_explanation"] = batch_explanations[i]
                else:
                    # 使用模板生成
                    segment["ai_explanation"] = _generate_transport_segment_explanation(
                        exp_data["method"],
                        exp_data["from"],
                        exp_data["to"],
                        exp_data["cost"],
                        exp_data["duration"],
                        exp_data["destination"],
                        None  # 使用模板，不调用LLM
                    )
                # 清理临时数据
                del segment["_explanation_data"]

    # 生成LLM描述文本
    transport_plan["llm_description"] = _generate_transport_description(
        destination,
        transport_plan,
        budget_level,
        llm
    )

    logger.info(f"[交通规划师] 完成交通规划，总费用: {total_cost}元，API调用: {api_call_count}次，批量优化路段解释")

    return transport_plan


def _recommend_first_trip_method(budget_level: str) -> str:
    """推荐从酒店出发的交通方式"""
    if budget_level == "economy":
        return "地铁/公交"
    elif budget_level == "luxury":
        return "专车/出租车"
    else:  # medium
        return "地铁/打车结合"


def _recommend_transport_method(from_loc: str, to_loc: str, budget_level: str) -> str:
    """推荐两地之间的交通方式"""

    # 判断距离
    distance = _estimate_distance(from_loc, to_loc)

    if distance < 1:  # 1公里内
        return "步行"

    if distance < 3:  # 3公里内
        if budget_level == "economy":
            return "共享单车/步行"
        else:
            return "步行/打车"

    if distance < 10:  # 10公里内
        if budget_level == "economy":
            return "地铁/公交"
        elif budget_level == "luxury":
            return "专车"
        else:
            return "地铁/打车"

    # 10公里以上
    if budget_level == "economy":
        return "地铁"
    elif budget_level == "luxury":
        return "专车"
    else:
        return "地铁/专车结合"


def _estimate_distance(from_loc: str, to_loc: str) -> float:
    """估算两地距离（公里）"""

    # 同一景点内
    if from_loc == to_loc:
        return 0

    # 常见景点距离参考（以北京为例）
    distance_map = {
        ("故宫", "长城"): 60,
        ("故宫", "颐和园"): 15,
        ("故宫", "天坛"): 8,
        ("故宫", "胡同"): 2,
        ("长城", "颐和园"): 50,
        ("西湖", "灵隐寺"): 10,
        ("外滩", "东方明珠"): 3,
    }

    # 尝试直接匹配
    key = (from_loc, to_loc)
    if key in distance_map:
        return distance_map[key]

    # 反向匹配
    key_reverse = (to_loc, from_loc)
    if key_reverse in distance_map:
        return distance_map[key_reverse]

    # 默认中等距离
    return 5


def _estimate_duration(from_loc: str, to_loc: str, destination: str) -> str:
    """估算交通时间"""

    distance = _estimate_distance(from_loc, to_loc)

    if distance < 1:
        return "10分钟"
    elif distance < 3:
        return "20-30分钟"
    elif distance < 10:
        return "40-60分钟"
    elif distance < 30:
        return "1-1.5小时"
    else:
        return "1.5-2小时"


def _estimate_transport_cost(from_loc: str, to_loc: str, budget_level: str) -> int:
    """估算交通费用（元）"""

    distance = _estimate_distance(from_loc, to_loc)

    if distance < 1:
        return 0  # 步行

    if distance < 3:
        if budget_level == "economy":
            return 5  # 共享单车
        elif budget_level == "luxury":
            return 25  # 打车
        else:
            return 15  # 打车/单车

    if distance < 10:
        if budget_level == "economy":
            return 4  # 地铁
        elif budget_level == "luxury":
            return 50  # 专车
        else:
            return 30  # 打车/地铁

    # 10公里以上
    if budget_level == "economy":
        return 8  # 地铁
    elif budget_level == "luxury":
        return 100  # 专车
    else:
        return 60  # 专车


def _batch_generate_transport_explanations(
    segments: List[Dict[str, Any]],
    llm=None
) -> Dict[str, str]:
    """
    批量生成所有交通路段的LLM解释说明（性能优化版本）

    将所有路段一次性发送给LLM进行解释生成，而不是逐个调用。
    这样可以将6-9次LLM调用优化为1次批量调用。

    Args:
        segments: 交通路段列表（每个路段包含_explanation_data）
        llm: LLM实例

    Returns:
        路段ID到解释文本的映射字典
    """
    if not llm or not segments:
        return {}

    try:
        # 提取所有路段的解释数据
        segments_data = []
        for i, segment in enumerate(segments):
            exp_data = segment.get("_explanation_data", {})
            if exp_data:
                segments_data.append({
                    "id": i,
                    "from": exp_data.get("from", ""),
                    "to": exp_data.get("to", ""),
                    "method": exp_data.get("method", ""),
                    "cost": exp_data.get("cost", 0),
                    "duration": exp_data.get("duration", ""),
                    "destination": exp_data.get("destination", "")
                })

        if not segments_data:
            return {}

        # 构建批量提示
        segments_text = "\n".join([
            f"[{s['id']}] {s['from']} → {s['to']} | 方式: {s['method']} | 费用: {s['cost']}元 | 耗时: {s['duration']}"
            for s in segments_data
        ])

        prompt = f"""请为以下{len(segments_data)}个交通路段各生成一句推荐理由（每条不超过50字）：

{segments_text}

要求：
1. 简洁有力，突出每种方式的优势
2. 解释为什么推荐该方式
3. 强调便捷性或经济性

请严格按照以下JSON格式输出：
{{
  "0": "第0条的解释",
  "1": "第1条的解释",
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
            for i, segment in enumerate(segments):
                exp_data = segment.get("_explanation_data", {})
                if exp_data:
                    explanation = explanations.get(str(i), "")
                    if explanation and len(explanation) > 5:
                        result[i] = explanation

            if result:
                logger.info(f"[交通规划师] 批量生成{len(result)}条路段解释成功")
                return result

    except Exception as e:
        logger.warning(f"[交通规划师] 批量生成路段解释失败: {e}，使用模板")

    # 失败时返回空字典，后续会使用模板
    return {}


def _generate_transport_segment_explanation(
    method: str,
    from_loc: str,
    to_loc: str,
    cost: int,
    duration: str,
    destination: str,
    llm=None
) -> str:
    """
    为单个交通路段生成LLM解释说明（保留用于兼容和降级）

    Args:
        method: 交通方式
        from_loc: 出发地
        to_loc: 目的地
        cost: 费用
        duration: 耗时
        destination: 城市名称
        llm: LLM实例

    Returns:
        LLM生成的解释文本
    """
    # 如果有LLM，使用LLM生成解释
    if llm:
        try:
            prompt = f"""请用一句话解释为什么推荐这个交通方式（不超过50字）：

路线：{from_loc} → {to_loc}
城市：{destination}
推荐方式：{method}
费用：{cost}元
耗时：{duration}

要求：
1. 简洁有力，突出优势
2. 解释为什么推荐这种方式
3. 强调便捷性或经济性

请直接输出解释文字。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            explanation = response.content.strip()
            if explanation and len(explanation) > 5:
                return explanation
        except Exception as e:
            logger.warning(f"[交通规划师] LLM生成路段解释失败: {e}")

    # 默认解释
    if "地铁" in method:
        return f"选择{method}是因为{destination}地铁系统发达，准时可靠，且{cost}元性价比极高。"
    elif "打车" in method or "专车" in method:
        return f"推荐{method}是因为直达{to_loc}最便捷，节省时间，费用{cost}元合理。"
    elif "步行" in method:
        return f"推荐步行是因为距离很近，沿途可以欣赏{destination}街景，免费又健康。"
    else:
        return f"选择{method}便捷经济，{duration}即可到达，是最优出行选择。"


def _get_transport_recommendations(destination: str, budget_level: str) -> List[str]:
    """获取交通建议"""

    recommendations = []

    # 通用建议
    recommendations.append("建议下载当地交通APP（如：高德地图、百度地图）")

    if destination == "北京":
        recommendations.extend([
            "北京地铁发达，建议优先选择地铁出行",
            "早高峰(7-9点)避开三环内主要路段",
            "去长城建议乘坐S2线或包车"
        ])
    elif destination == "上海":
        recommendations.extend([
            "上海地铁网络完善，推荐地铁出行",
            "外滩、南京路步行街建议地铁到达后步行",
            "去迪士尼可乘坐地铁11号线"
        ])
    elif destination == "成都":
        recommendations.extend([
            "市区景点相对集中，打车比较便宜",
            "去周边景点(如都江堰)可动车/大巴"
        ])
    elif destination == "杭州":
        recommendations.extend([
            "西湖周边建议步行或共享单车",
            "市区地铁1、2号线覆盖主要景点"
        ])
    else:
        recommendations.append("建议提前查询当地交通路线")

    # 根据预算建议
    if budget_level == "economy":
        recommendations.append("为节省费用，优先选择公共交通")
    elif budget_level == "luxury":
        recommendations.append("为节省时间，可考虑专车接送")

    return recommendations


def _generate_transport_description(
    destination: str,
    transport_plan: Dict[str, Any],
    budget_level: str,
    llm=None
) -> str:
    """
    使用LLM生成交通规划的自然语言描述

    Args:
        destination: 目的地
        transport_plan: 交通计划
        budget_level: 预算等级
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    total_cost = transport_plan.get("total_transport_cost", 0)
    daily_transport = transport_plan.get("daily_transport", [])
    recommendations = transport_plan.get("transport_recommendations", [])

    # 统计主要交通方式
    transport_methods = []
    for day in daily_transport:
        for segment in day.get("transport_segments", []):
            method = segment.get("method", "")
            if method and method not in transport_methods:
                transport_methods.append(method)

    # 如果有LLM，使用LLM生成描述
    if llm:
        try:
            methods_text = '、'.join(transport_methods[:5])
            recommendations_text = '\n'.join(recommendations[:3])

            prompt = f"""请为以下交通规划生成一段自然、实用的描述文字（约150-200字）：

目的地：{destination}
主要交通方式：{methods_text}
预算等级：{budget_level}
总交通费用：约{total_cost}元
交通建议：
{recommendations_text}

描述要求：
1. 用实用建议的语气，帮助用户高效出行
2. 突出当地交通特点和优势
3. 给出具体的交通方式和路线建议
4. 包含省时省费的小技巧
5. 语言要实用具体，有操作性

请直接输出描述文字，不要标题和格式符号。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[交通规划师] LLM生成描述成功: {len(description)}字")
            return description
        except Exception as e:
            logger.warning(f"[交通规划师] LLM生成描述失败: {e}，使用默认描述")

    # 默认描述（无LLM或LLM失败时）
    methods_text = '、'.join(transport_methods[:4]) if transport_methods else "地铁、公交、步行"

    description = f"""在{destination}出行，交通非常便利！🚇🚕

推荐主要交通方式：{methods_text}

预计总交通费用约{total_cost}元，平均每天出行很经济实惠。

💡 出行小贴士：
• 建议下载当地交通APP，如高德地图/百度地图，实时导航很方便
• {methods_text.split('、')[0] if methods_text else '地铁'}是最可靠的出行方式，不易堵车
• 早晚高峰时段尽量错峰出行，节省时间
• 买一张交通卡或使用手机扫码，乘车更便捷
{''.join([f'\n• {rec}' for rec in recommendations[:3]])}

祝您出行顺利！🎯"""

    return description


def enhance_schedule_with_transport(
    scheduled_attractions: List[Dict[str, Any]],
    transport_plan: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """将交通信息整合到日程安排中"""

    enhanced = []

    for day_schedule in scheduled_attractions:
        day_num = day_schedule.get("day", 1)

        # 找到对应的交通信息
        day_transport = next(
            (dt for dt in transport_plan.get("daily_transport", []) if dt.get("day") == day_num),
            {"transport_segments": []}
        )

        # 将交通信息添加到日程项中
        transport_segments = day_transport.get("transport_segments", [])
        segment_index = 0

        enhanced_schedule = []

        for item in day_schedule.get("schedule", []):
            # 添加交通信息到活动项
            if item.get("period") not in ["lunch", "dinner"] and segment_index < len(transport_segments):
                item["transport"] = transport_segments[segment_index]
                segment_index += 1

            enhanced_schedule.append(item)

        enhanced.append({
            "day": day_schedule.get("day"),
            "date": day_schedule.get("date"),
            "title": day_schedule.get("title"),
            "schedule": enhanced_schedule,
            "pace": day_schedule.get("pace")
        })

    return enhanced


# LangGraph 节点函数
def transport_planner_node(state: Dict) -> Dict:
    """交通规划节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    scheduled_attractions = state.get("scheduled_attractions", [])
    user_portrait = state.get("user_portrait", {})
    budget_level = user_portrait.get("budget_level", "medium")
    llm = state.get("_llm")

    if not destination or not scheduled_attractions:
        logger.error("[交通规划师] 缺少必要数据")
        return state

    # 规划交通
    transport_plan = plan_transport(
        destination,
        scheduled_attractions,
        budget_level,
        llm
    )

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"交通规划完成: 总费用{transport_plan['total_transport_cost']}元",
        name="TransportPlanner"
    ))

    state["transport_plan"] = transport_plan
    state["messages"] = messages

    return state
