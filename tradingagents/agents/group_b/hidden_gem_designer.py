"""
小众宝藏方案设计师 (Agent B4)

设计理念: 避开人流，发现隐秘景点，独特体验

特点:
- 每日2-3个小众景点
- 寻找游客少但有特色的地方
- 独特体验，与众不同
- 适合探险爱好者、喜欢发现的旅行者
- 使用SerpAPI和OpenTripMap获取实时数据
- 使用LLM生成个性化描述
"""

from typing import Dict, Any, List
import logging
import asyncio
import os

logger = logging.getLogger('travel_agents')

# 导入API工具
from .api_tools.serpapi_tool import SerpAPITool
from .api_tools.opentripmap_tool import OpenTripMapTool


def _search_hidden_gems(destination: str, days: int) -> List[Dict[str, Any]]:
    """
    使用新的API工具搜索小众景点

    小众宝藏设计师需要找到不那么热门但有特色的景点

    Args:
        destination: 目的地名称
        days: 天数

    Returns:
        景点列表
    """
    all_attractions = []

    # 优先使用SerpAPI搜索小众景点
    if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
        try:
            serpapi_tool = SerpAPITool()

            # 搜索可能有小众景点的地方
            hidden_keywords = ["老街", "巷", "小众", "文化", "艺术", "创意", "古镇", "公园", "市场"]

            for keywords in hidden_keywords[:4]:  # 限制搜索次数
                serp_results = asyncio.run(serpapi_tool.search_attractions(
                    destination=destination,
                    keywords=keywords,
                    days=days,
                    style="hidden_gem"
                ))

                if serp_results:
                    all_attractions.extend(serp_results)

            # 去重
            seen_names = set()
            unique_attractions = []
            for attr in all_attractions:
                name = attr.get("name", "")
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_attractions.append(attr)

            if unique_attractions:
                logger.info(f"[小众宝藏设计师] SerpAPI搜索到 {len(unique_attractions)} 个景点")
                return unique_attractions[:days * 3]  # 每天最多3个

        except Exception as e:
            logger.warning(f"[小众宝藏设计师] SerpAPI搜索失败: {e}")

    # 补充OpenTripMap数据
    if len(all_attractions) < days * 3 and os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
        try:
            opentripmap_tool = OpenTripMapTool()
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords="historic",
                days=days,
                style="hidden_gem"
            ))

            if otm_results:
                # 去重
                existing_names = {a.get("name", "") for a in all_attractions}
                for otm_attr in otm_results:
                    if otm_attr.get("name", "") not in existing_names:
                        all_attractions.append(otm_attr)

                logger.info(f"[小众宝藏设计师] OpenTripMap补充 {len(otm_results)} 个景点")
        except Exception as e:
            logger.warning(f"[小众宝藏设计师] OpenTripMap搜索失败: {e}")

    if all_attractions:
        logger.info(f"[小众宝藏设计师] 总共获取 {len(all_attractions)} 个实时景点")
        # 返回前 days*3 个
        seen_names = set()
        unique_attractions = []
        for attr in all_attractions:
            name = attr.get("name", "")
            if name and name not in seen_names:
                seen_names.add(name)
                unique_attractions.append(attr)
                if len(unique_attractions) >= days * 3:
                    break
        return unique_attractions
    else:
        logger.warning("[小众宝藏设计师] 未获取到实时景点数据")
        return []


def design_hidden_gem_style(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """
    设计小众宝藏旅行方案

    优先调用工具API搜索小众景点，失败时使用静态小众景点列表

    Args:
        destination: 目的地名称
        dest_data: 目的地数据
        user_portrait: 用户画像
        days: 旅行天数
        llm: LLM实例（可选）

    Returns:
        小众宝藏风格方案
    """
    logger.info(f"[小众宝藏设计师] 为{destination}设计{days}天小众宝藏方案")

    tags = dest_data.get("tags", [])
    highlights = dest_data.get("highlights", [])

    # 1. 优先调用工具API搜索小众景点
    real_attractions = []
    data_source = "fallback"

    try:
        searched_gems = _search_hidden_gems(destination, days)

        if searched_gems and len(searched_gems) > 0:
            # 转换为小众宝藏格式
            real_attractions = []
            for attr in searched_gems:
                real_attractions.append({
                    "name": attr.get("name", ""),
                    "id": attr.get("name", ""),
                    "description": f"探索{attr.get('name', '')}的独特魅力"
                })
            data_source = "realtime_api"
            logger.info(f"[小众宝藏设计师] 使用实时API数据: {len(real_attractions)}个景点")
    except Exception as e:
        logger.warning(f"[小众宝藏设计师] 实时数据获取失败: {e}")

    # 2. 降级：使用_generate_hidden_gems函数生成小众景点
    if not real_attractions:
        logger.info(f"[小众宝藏设计师] 使用静态小众景点列表")
        hidden_gems = _generate_hidden_gems(destination, highlights, tags)
        real_attractions = hidden_gems
        data_source = "fallback"

    # 3. 每天安排2-3个小众景点
    daily_itinerary = []
    gems_per_day = max(2, len(real_attractions) // days)

    for day in range(1, days + 1):
        start_idx = (day - 1) * gems_per_day
        end_idx = min(start_idx + gems_per_day + 1, len(real_attractions))
        day_gems = real_attractions[start_idx:end_idx]

        # 生成活动安排
        activities = []
        for gem in day_gems[:3]:
            gem_name = gem.get("name", gem) if isinstance(gem, dict) else gem
            gem_desc = gem.get("description", "独特的小众体验") if isinstance(gem, dict) else "独特体验"
            gem_id = gem.get("id", "") if isinstance(gem, dict) else ""

            activities.append({
                "time": "上午" if len(activities) == 0 else "下午" if len(activities) == 1 else "晚上",
                "activity": f"探索{gem_name}",
                "description": gem_desc,
                "attraction_id": gem_id
            })

        # 添加特色活动
        if "美食" in str(tags):
            activities.append({
                "time": "晚上",
                "activity": "当地人推荐餐厅",
                "description": "避开游客区，寻找本地人常去的地方"
            })
        else:
            activities.append({
                "time": "晚上",
                "activity": "隐秘夜景点",
                "description": "发现游客少知的绝佳观景点"
            })

        day_gem_names = [gem.get("name", gem) if isinstance(gem, dict) else gem for gem in day_gems]
        daily_itinerary.append({
            "day": day,
            "title": f"第{day}天：{day_gem_names[0] if day_gem_names else destination}隐秘探索",
            "activities": activities,
            "attractions": day_gem_names,
            "pace": "中等节奏"
        })

    # 生成亮点
    highlights_desc = [
        "避开人流，发现隐秘景点",
        "独特体验，与众不同",
        "探索鲜为人知的美丽角落"
    ]

    if "自然" in str(tags):
        highlights_desc.append("避开人群的自然秘境")

    if "文化" in str(tags) or "历史" in str(tags):
        highlights_desc.append("不为人知的文化遗产")

    # 计算费用（小众宝藏可能稍高，因为需要更多探索）
    budget = dest_data.get("budget_level", {}).get("medium", 500)
    total_budget = int(budget * 1.1) * days * user_portrait.get("total_travelers", 2)

    # 获取实际使用的景点名称
    used_attractions = []
    for day_plan in daily_itinerary:
        used_attractions.extend(day_plan.get("attractions", []))

    # 跟踪API来源
    api_sources_used = []
    if data_source == "realtime_api":
        if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
            api_sources_used.append("serpapi")
        if os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
            api_sources_used.append("opentripmap")

    # 使用LLM生成方案描述
    llm_description = _generate_llm_description(
        destination,
        days,
        used_attractions[:5] if len(used_attractions) > 5 else used_attractions,
        user_portrait,
        llm
    )

    return {
        "style_name": "小众宝藏",
        "style_icon": "💎",
        "style_type": "hidden_gem",
        "style_description": "避开人流，发现隐秘景点，独特体验",
        "daily_pace": "中等节奏，每日2-3个小众景点",
        "intensity_level": 3,
        "preview_itinerary": [
            {"day": 1, "title": f"{used_attractions[0] if used_attractions else destination}探索", "attractions": [used_attractions[0]] if used_attractions else [destination]},
            {"day": 2, "title": f"{used_attractions[1] if len(used_attractions) > 1 else '周边'}发现", "attractions": [used_attractions[1]] if len(used_attractions) > 1 else [destination]}
        ],
        "estimated_cost": total_budget,
        "best_for": "探险爱好者，喜欢发现的旅行者",
        "highlights": highlights_desc[:5],
        "daily_itinerary": daily_itinerary,
        "data_source": data_source,
        "api_sources_used": api_sources_used,
        "llm_description": llm_description,
        "agent_info": {
            "name_cn": "小众宝藏设计师",
            "name_en": "HiddenGemDesigner",
            "icon": "💎",
            "group": "B",
            "llm_enabled": llm is not None
        }
    }


def _generate_hidden_gems(
    destination: str,
    highlights: List[str],
    tags: List[str]
) -> List[Dict[str, Any]]:
    """生成小众景点列表"""
    gems = []

    # 基于目的地生成小众景点
    hidden_attractions_map = {
        "北京": [
            {"name": "智化寺", "id": "bj_hidden_1", "description": "少有人知的明代古寺"},
            {"name": "杨梅竹斜斜街", "id": "bj_hidden_2", "description": "老胡同里的宁静角落"},
            {"name": "先农坛", "id": "bj_hidden_3", "description": "比天坛人少的祭坛"},
            {"name": "法源寺", "id": "bj_hidden_4", "description": "古老寺庙，丁香闻名"},
            {"name": "南锣鼓巷小巷", "id": "bj_hidden_5", "description": "避开主街的幽静胡同"},
            {"name": "景山后街", "id": "bj_hidden_6", "description": "绝美故宫后视"},
        ],
        "上海": [
            {"name": "武康路", "id": "sh_hidden_1", "description": "老洋房建筑群"},
            {"name": "多伦路文化街", "id": "sh_hidden_2", "description": "文艺小店聚集地"},
            {"name": "思南公馆", "id": "sh_hidden_3", "description": "幽静的历史公馆"},
            {"name": "1933老场坊", "id": "sh_hidden_4", "description": "创意园区"},
            {"name": "马勒别墅", "id": "sh_hidden_5", "description": "北欧风情小别墅"},
        ],
        "成都": [
            {"name": "宽窄巷子侧巷", "id": "cd_hidden_1", "description": "避开主街的清净"},
            {"name": "大慈寺", "id": "cd_hidden_2", "description": "历史悠久的古寺"},
            {"name": "文殊院", "id": "cd_hidden_3", "description": "静心禅修之地"},
            {"name": "人民公园鹤鸣茶社", "id": "cd_hidden_4", "description": "体验老成都茶文化"},
            {"name": "太古里", "id": "cd_hidden_5", "description": "文艺复古街区"},
        ],
        "西安": [
            {"name": "大唐不夜城后巷", "id": "xa_hidden_1", "description": "避开人群的小路"},
            {"name": "陕西历史博物馆", "id": "xa_hidden_2", "description": "宝库级别，人少"},
            {"name": "书院门", "id": "xa_hidden_3", "description": "老城文化体验"},
            {"name": "大唐芙蓉园夜场", "id": "xa_hidden_4", "description": "夜景更佳"},
            {"name": "回民街小巷", "id": "xa_hidden_5", "description": "避开主街的美食"},
        ],
        "杭州": [
            {"name": "九溪十八涧", "id": "hz_hidden_1", "description": "自然溪流徒步"},
            {"name": "郭庄", "id": "hz_hidden_2", "description": "水乡古镇风貌"},
            {"name": "云栖竹径", "id": "hz_hidden_3", "description": "竹林幽径"},
            {"name": "虎跑泉", "id": "hz_hidden_4", "description": "清幽的泉水"},
            {"name": "梅家坞茶文化村", "id": "hz_hidden_5", "description": "体验龙井茶"},
        ],
        "厦门": [
            {"name": "沙坡尾艺术区", "id": "xm_hidden_1", "description": "文艺聚集地"},
            {"name": "铁路文化公园", "id": "xm_hidden_2", "description": "工业遗产改造"},
            {"name": "华新路", "id": "xm_hidden_3", "description": "幽静的老别墅区"},
            {"name": "曾厝垵小巷", "id": "xm_hidden_4", "description": "避开主街"},
            {"name": "集美学村", "id": "xm_hidden_5", "description": "独特建筑群"},
        ],
    }

    # 获取对应城市的小众景点，或使用通用小众景点
    gems_data = hidden_attractions_map.get(destination, [])

    if not gems_data:
        # 通用小众景点
        gems_data = [
            {"name": f"{destination}老街小巷", "id": f"{destination}_hidden_1", "description": "避开游客区的本地生活区"},
            {"name": f"{destination}当地市场", "id": f"{destination}_hidden_2", "description": "体验当地人生活"},
            {"name": f"{destination}城市公园", "id": f"{destination}_hidden_3", "description": "本地人休闲地"},
        ]

    # 添加一些常规景点的小众角度
    for highlight in highlights[:2]:
        gems_data.append({
            "name": f"{highlight}非热门路线",
            "id": f"{destination}_alt_{highlight}",
            "description": f"避开人群的游览{highlight}"
        })

    return gems_data


def hidden_gem_designer_node(state: Dict) -> Dict:
    """小众宝藏设计师节点（用于LangGraph）"""
    destination = state.get("selected_destination")
    dest_data = state.get("selected_destination_data", {})
    user_portrait = state.get("user_portrait")
    days = state.get("days", 5)
    llm = state.get("_llm")

    if not destination or not user_portrait:
        logger.error("[小众宝藏设计师] 缺少必要数据")
        return state

    # 设计方案
    proposal = design_hidden_gem_style(destination, dest_data, user_portrait, days, llm)

    # 更新状态
    from langchain_core.messages import AIMessage
    messages = state.get("messages", [])
    messages.append(AIMessage(
        content=f"小众宝藏方案设计完成: {days}天独特体验",
        name="HiddenGemDesigner"
    ))

    if "style_proposals" not in state:
        state["style_proposals"] = []
    state["style_proposals"].append(proposal)
    state["messages"] = messages

    return state


def create_hidden_gem_proposal(
    destination: str,
    dest_data: Dict[str, Any],
    user_portrait: Dict[str, Any],
    days: int,
    llm=None
) -> Dict[str, Any]:
    """创建小众宝藏方案（独立调用）"""
    proposal = design_hidden_gem_style(destination, dest_data, user_portrait, days, llm)

    return {
        "success": True,
        "proposal": proposal,
        "agent_info": {
            "name": "HiddenGemDesigner",
            "icon": "💎",
            "description": "小众宝藏方案设计师"
        }
    }


def _generate_llm_description(
    destination: str,
    days: int,
    attractions: List[str],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    """
    使用LLM生成小众宝藏方案的自然语言描述

    Args:
        destination: 目的地
        days: 天数
        attractions: 主要景点列表
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    """
    if llm:
        try:
            travel_type = user_portrait.get("travel_type", "")
            interests = user_portrait.get("primary_interests", [])
            interests_text = "、".join(interests) if interests else "小众探索"

            prompt = f"""请为以下小众宝藏旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{destination}
旅行天数：{days}天
旅行类型：{travel_type}
用户兴趣：{interests_text}
核心景点：{', '.join(attractions[:5])}

方案特点：
- 避开热门景点的拥挤人流
- 发现鲜为人知的隐秘景点
- 独特体验，与众不同
- 适合喜欢探索和发现的旅行者

请生成一段能吸引向往独特体验的旅行者，突出小众宝藏旅行的独特魅力。

直接输出描述文字，不要标题。"""

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[HiddenGemDesigner] LLM生成描述成功: {len(description)}字")
            return description

        except Exception as e:
            logger.warning(f"[HiddenGemDesigner] LLM生成描述失败: {e}")

    # 默认描述
    return f"""这是一场独特的小众宝藏之旅，在{destination}的{days}天里，您将远离游客如织的热门景点，探索那些鲜为人知的隐秘角落。不同于大众化的观光旅行，小众宝藏之旅注重发现和探索，在{', '.join(attractions[:3])}等独特景点，您将收获专属的旅行记忆和故事。让旅行回归本质，发现那些只有少数人知道的美丽。"""
