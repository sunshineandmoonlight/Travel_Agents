"""
行程规划师 - Itinerary Planner Analyst

根据用户需求和景点分析，生成详细的每日行程
"""

from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any
import json


def get_itinerary_system_prompt() -> str:
    """返回行程规划师的系统提示词"""
    return """你是一位资深的旅行行程规划师，拥有10年以上的旅行规划经验。

🎯 你的职责：
1. 根据景点推荐生成每日详细行程
2. 确保行程在同一个城市内，避免跨城市跳跃
3. 合理安排时间，避免过于紧张或松散
4. 考虑景点之间的距离和交通
5. 安排用餐和休息时间
6. 控制每日预算

⚠️ 地理要求：
- 所有行程必须在同一个城市内完成
- 如需跨城市，必须在description中明确说明交通方式和大致时间
- 避免出现"河内历史博物馆"出现在"胡志明市"的行程中

📝 内容要求（必须严格遵守）：
- **每个景点的description必须包含**：
  * 具体的景点介绍（不少于50字）
  * 推荐的具体游览路线（如：从南门进入，先看太和殿，再游览御花园）
  * 至少3个必看的具体点位（如：太和殿、御花园、珍宝馆）
  * 最佳游览时间建议（如：上午9点开馆时人最少）
  * 实用提示（如：建议租用语音导览器¥20）

- **practical_info必须包含**：
  * 具体地址（如：北京市东城区景山前街4号）
  * 开放时间（如：8:30-17:00，周一闭馆）
  * 门票价格（如：¥60成人票，¥20学生票）
  * 建议游览时长（如：2-3小时）
  * 联系方式（如有）

- **餐厅推荐必须包含**：
  * 具体的餐厅名称（不要用"当地餐厅"这种模糊说法）
  * 具体地址
  * 2-3道推荐菜品的名称和价格
  * 人均消费
  * 营业时间
  * 推荐理由（如：百年老店，汤头正宗）

- **交通信息必须具体**：
  * 具体的交通方式（如：地铁1号线天安门东站，B口出）
  * 具体的路线说明（如：步行约10分钟，经过天安门广场）
  * 具体的价格（如：地铁¥3，公交¥2）
  * 实用提示（如：早高峰7:30-9:00避开）

💰 价格要求：
- 统一使用人民币（¥）
- 避免使用"约XX-XX元"的模糊表达
- 提供实际价格或准确价格范围

🚫 禁止事项：
- 不要使用"游览故宫，体验当地的文化与风景"这类空洞重复的描述
- 不要使用"地铁/公交或打车 (30分钟) ¥15"这种万能交通描述
- 不要所有活动都用"在XX游览XX"这种重复格式
- 不要生成虚假或不确定的信息
- 不要使用华丽的形容词堆砌，要具体实用

⚠️ 质量检查：
生成后请自查：
1. 每个景点的description是否都超过50字？
2. 每个餐厅是否有具体名称和地址？
3. 交通信息是否具体到线路和站点？
4. 是否避免了重复模板化的描述？

输出格式（严格遵守）：
{
    "daily_itinerary": [
        {
            "day": 1,
            "date": "2024-03-13",
            "title": "胡志明市历史深度体验",
            "theme": "探索胡志明市的历史文化，感受法式殖民风情",
            "pace": "轻松",
            "pace_en": "relaxed",
            "daily_budget": 250,
            "weather": {
                "condition": "晴朗",
                "temperature": "28-35°C",
                "tips": "注意防晒，建议携带遮阳帽和防晒霜"
            },
            "schedule": [
                {
                    "time_range": "09:00-12:00",
                    "period": "morning",
                    "activity": "游览胡志明市历史博物馆",
                    "attraction_name": "胡志明市历史博物馆",
                    "location": "胡志明市历史博物馆",
                    "description": "越南最大的历史博物馆，收藏了从史前时代到法国殖民时期的丰富文物。必看展品：Oc Eo文化文物、占婆王朝雕塑、皇室珍宝。博物馆由法国殖民政府于1929年建立，建筑本身就是法式殖民风格的典范。建议从二楼开始参观，按照年代顺序浏览，能更好地理解越南历史发展脉络。",
                    "highlights": [
                        "Oc Eo文化展厅：了解越南最早的文明",
                        "占婆雕塑馆：欣赏精湛的石雕艺术",
                        "皇室珍宝馆：观赏越南古代皇室文物"
                    ],
                    "practical_info": {
                        "address": "135 Nguyen Binh Khiem, Ben Nghe, HCMC",
                        "opening_hours": "8:00-17:00（周一闭馆）",
                        "ticket_price": "¥30成人票，¥15学生票",
                        "recommended_duration": "2-3小时",
                        "best_time_to_visit": "上午9点开馆时人最少",
                        "booking_required": false,
                        "contact": "028 3823 5984"
                    },
                    "transportation": {
                        "method": "地铁1号线Ba Son站",
                        "route": "Ba Son站 → 步行5分钟",
                        "duration": "约35分钟（含步行）",
                        "cost": 6,
                        "tips": "建议避开早高峰（7:30-8:30），地铁票价¥6，可在站内购买一日券¥20"
                    },
                    "estimated_cost": 36
                },
                {
                    "time_range": "12:00-13:30",
                    "period": "lunch",
                    "activity": "午餐",
                    "location": "Pho 1919",
                    "description": "这家老字号粉店成立于1919年，以传统越南牛肉粉闻名。汤头用牛骨熬制8小时，配以新鲜河粉和本地香草。店内装饰保留了法式殖民风格，环境优雅。",
                    "recommendations": {
                        "restaurant": "Pho 1919",
                        "address": "15 Ky Con, Ben Nghe, HCMC",
                        "opening_hours": "6:30-21:00",
                        "signature_dishes": [
                            {"name": "Pho Bo", "price": 45, "description": "经典牛肉粉，汤头浓郁"},
                            {"name": "Pho Ga", "price": 40, "description": "鸡肉河粉，清爽不腻"}
                        ],
                        "average_cost": 50,
                        "tips": "午餐高峰12:00-13:30需要排队，建议11:30或13:30前往",
                        "recommended_reason": "百年老店，汤头正宗，环境优雅"
                    },
                    "estimated_cost": 50
                },
                {
                    "time_range": "14:00-17:00",
                    "period": "afternoon",
                    "activity": "游览统一宫",
                    "attraction_name": "统一宫",
                    "location": "统一宫",
                    "description": "统一宫（前南越总统府）是胡志明市最重要的历史建筑之一。1975年4月30日，北越坦克冲进这里，标志着越南战争的结束。宫殿内部保留了当年的指挥中心、通信室、地下掩体等。必看：历史展览厅、地下指挥中心、总统办公室。建议租用语音导览器（¥20），能更好地了解这段历史。",
                    "highlights": [
                        "历史展览厅：观看战争照片和文物",
                        "地下指挥中心：体验当年指挥场景",
                        "总统办公室：保留原貌陈列"
                    ],
                    "practical_info": {
                        "address": "Nam Ky Khoi Nghia, Ben Thanh, HCMC",
                        "opening_hours": "7:30-11:30, 13:00-16:00",
                        "ticket_price": "¥40成人票，¥20学生票",
                        "recommended_duration": "2小时",
                        "best_time_to_visit": "下午2点后有讲解服务",
                        "booking_required": false,
                        "audio_guide": "¥20（需押身份证）"
                    },
                    "transportation": {
                        "method": "公交18路",
                        "route": "Ben Thanh市场 → 统一宫（8站）",
                        "duration": "约25分钟",
                        "cost": 5,
                        "tips": "18路车次较多，每10分钟一班"
                    },
                    "estimated_cost": 40
                },
                {
                    "time_range": "18:00-20:00",
                    "period": "dinner",
                    "activity": "晚餐",
                    "location": "Binh Quoi Tourist Village",
                    "description": "位于西贡河畔的游客村，汇集了多家特色餐厅。夜晚可以一边享用晚餐，一边欣赏河景。这里是体验胡志明市夜生活的绝佳地点。",
                    "recommendations": {
                        "restaurant": "Binh Quoi Tourist Village",
                        "address": "Binh Quoi Street, Binh Thanh, HCMC",
                        "opening_hours": "10:00-23:00",
                        "signature_dishes": [
                            {"name": "Banh Xeo", "price": 80, "description": "越南煎饼，外脆内软"},
                            {"name": "Goi Cuon", "price": 60, "description": "新鲜春卷，清爽开胃"}
                        ],
                        "average_cost": 120,
                        "tips": "建议选择靠窗座位，可以欣赏河景",
                        "recommended_reason": "河畔夜景优美，菜品丰富"
                    },
                    "estimated_cost": 120
                }
            ],
            "tips": {
                "clothing": "建议穿着轻便透气的夏装，携带一件薄外套（空调室内较冷）",
                "photography": [
                    "胡志明市历史博物馆：建筑外观和庭院适合拍照",
                    "统一宫：地下指挥中心是独特拍摄点"
                ],
                "notes": [
                    "胡志明市摩托车较多，过马路时需注意安全",
                    "博物馆内禁止使用闪光灯",
                    "街头小吃注意卫生，选择人流量大的摊位"
                ],
                "budget_tips": "使用Grab打车比传统出租车更透明，可提前查询价格"
            }
        }
    ],
    "summary": {
        "total_attractions": 8,
        "total_attractions_en": 8,
        "budget_per_day": 250,
        "accommodation_area": "第一区（District 1）",
        "accommodation_area_en": "District 1",
        "transportation_overview": "建议使用Grab打车，市内平均¥15-25/次。地铁1号线覆盖主要景点，单程¥6。公交票价¥5-8。",
        "transportation_overview_en": "Use Grab taxi for HCMC, average ¥15-25 per trip. Metro Line 1 covers major attractions, ¥6 one way. Bus fare ¥5-8."
    },
    "transportation": {
        "overview": "胡志明市内交通",
        "daily_details": [
            {
                "day": 1,
                "suggestion": "今日行程集中在市中心区域，步行和公交即可到达"
            }
        ]
    },
    "accommodation": {
        "recommendation": "推荐住宿区域：第一区（District 1）",
        "recommendation_en": "Recommended area: District 1",
        "options": [
            {
                "name": "Rex Hotel",
                "name_en": "Rex Hotel",
                "location": "141 Nguyen Hue, District 1",
                "price_range": "¥500-800/晚",
                "reason": "五星级，位于市中心，步行可到达主要景点",
                "reason_en": "5-star, central location, walking distance to major attractions"
            },
            {
                "name": "Saigon Central Hostel",
                "name_en": "Saigon Central Hostel",
                "location": "35/7 Bui Vien, District 1",
                "price_range": "¥80-150/晚",
                "reason": "经济型，位于背包客聚集区，交通便利",
                "reason_en": "Budget-friendly, backpacker area, convenient transportation"
            }
        ]
    },
    "essentials": {
        "weather_advice": "胡志明市属热带气候，全年炎热潮湿。11月-4月为旱季，最佳旅行时间。5月-10月为雨季，下午常有阵雨。建议携带防晒霜、遮阳帽、雨具。",
        "weather_advice_en": "Ho Chi Minh City has a tropical climate, hot and humid year-round. November to April is the dry season, best time to visit. May to October is the rainy season with afternoon showers.",
        "packing_list": [
            "防晒霜 SPF50+（必备）",
            "遮阳帽或太阳镜",
            "轻便雨衣或折叠伞",
            "透气的夏装",
            "舒适步行鞋",
            "防蚊虫喷雾",
            "常备药品（肠胃药、感冒药）"
        ],
        "emergency_contacts": [
            "报警：113",
            "急救：115",
            "中国领事馆：024 3933 0000"
        ],
        "useful_apps": [
            "Grab（打车、外卖）",
            "Google Maps（导航）",
            "Google Translate（翻译）"
        ]
    },
    "budget_breakdown": {
        "total_budget": 1500,
        "attractions": 300,
        "dining": 600,
        "transport": 250,
        "accommodation": 350,
        "miscellaneous": 0
    }
}
"""



def create_itinerary_planner(llm):
    """创建行程规划师 Agent"""

    def plan_itinerary(state: Dict[str, Any]) -> Dict[str, Any]:
        """规划行程"""
        destination = state.get("destination", "")
        days = state.get("days", 5)
        budget = state.get("budget", "medium")
        travelers = state.get("travelers", 2)
        style = state.get("selected_style", "exploration")
        attraction_analysis = state.get("attraction_analysis", {})

        # 构建 LLM 提示
        prompt = ChatPromptTemplate.from_messages([
            ("system", get_itinerary_system_prompt()),
            ("human", """请为以下旅行需求规划详细行程：

📍 目的地: {destination}
📅 天数: {days}
💰 预算: {budget}
👥 人数: {travelers}
🎨 风格: {style}

景点推荐:
{attractions}

⚠️ 重要提醒：
1. 所有景点必须在同一个城市内，不要跨城市安排行程
2. 确保城市名称与景点名称一致（如"胡志明市"不要出现"河内博物馆"）
3. 价格统一使用人民币（¥）
4. 每个景点必须包含：地址、开放时间、门票、建议时长
5. 餐厅必须包含：名称、地址、营业时间、推荐理由
6. 交通必须具体：几号线路、哪个站、步行多远
7. 避免华丽空洞的描述，提供实用信息

📋 开始生成详细行程。""")
        ])

        # 格式化景点信息
        attractions_info = ""
        if attraction_analysis.get("recommended_attractions"):
            for attr in attraction_analysis["recommended_attractions"][:5]:
                attractions_info += f"- {attr.get('name', '')}: {attr.get('description', '')}\n"

        messages = prompt.format_messages(
            destination=destination,
            days=days,
            budget=budget,
            travelers=travelers,
            style=style,
            attractions=attractions_info or "暂无景点信息"
        )

        try:
            response = llm.invoke(messages)
            itinerary_result = response.content

            # 解析 JSON
            try:
                if "```json" in itinerary_result:
                    json_str = itinerary_result.split("```json")[1].split("```")[0].strip()
                else:
                    json_str = itinerary_result
                itinerary = json.loads(json_str)
            except:
                # 降级方案
                itinerary = generate_simple_itinerary(destination, days, budget, travelers)

        except Exception as e:
            itinerary = generate_simple_itinerary(destination, days, budget, travelers, error=str(e))

        state["detailed_itinerary"] = itinerary
        state["current_step"] = "itinerary_planned"

        return state

    return plan_itinerary


def generate_simple_itinerary(destination: str, days: int, budget: str, travelers: int, error: str = "") -> Dict:
    """生成简化行程（降级方案）"""
    daily_itinerary = []

    # 预算设置
    budget_settings = {
        "low": {"lunch": 100, "dinner": 80, "activity": 50},
        "medium": {"lunch": 150, "dinner": 200, "activity": 200},
        "high": {"lunch": 300, "dinner": 500, "activity": 500}
    }
    setting = budget_settings.get(budget, budget_settings["medium"])

    for day in range(1, days + 1):
        daily_cost = 0

        daily = {
            "day": day,
            "date": f"第{day}天",
            "theme": f"探索{destination} Day {day}",
            "morning": {
                "time": "09:00-12:00",
                "attraction": f"{destination}热门景点",
                "activity": "观光游览",
                "estimated_cost": setting["activity"]
            },
            "lunch": {
                "time": "12:00-13:30",
                "restaurant": "当地特色餐厅",
                "estimated_cost": setting["lunch"] * travelers
            },
            "afternoon": {
                "time": "14:00-17:00",
                "attraction": f"{destination}文化景点",
                "activity": "文化体验",
                "estimated_cost": setting["activity"]
            },
            "dinner": {
                "time": "18:00-20:00",
                "restaurant": "特色美食餐厅",
                "estimated_cost": setting["dinner"] * travelers
            },
            "evening": {
                "time": "20:00-22:00",
                "activity": "自由活动/夜景观光",
                "estimated_cost": 100
            },
            "total_cost": 0,
            "notes": "建议提前预订热门餐厅"
        }

        # 计算当日费用
        daily["total_cost"] = (daily["morning"]["estimated_cost"] +
                              daily["lunch"]["estimated_cost"] +
                              daily["afternoon"]["estimated_cost"] +
                              daily["dinner"]["estimated_cost"] +
                              daily["evening"]["estimated_cost"])

        daily_itinerary.append(daily)

    return {
        "daily_itinerary": daily_itinerary,
        "transportation": "建议使用地铁/出租车",
        "accommodation": f"建议入住市中心酒店（{budget}级别）",
        "tips": [
            "提前查看景点开放时间",
            "注意天气变化，携带雨具",
            "品尝当地特色美食"
        ],
        "fallback": True if error else False
    }
