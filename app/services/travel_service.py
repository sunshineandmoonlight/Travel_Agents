"""
旅行规划服务

提供旅行规划的业务逻辑处理
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.models.travel import (
    TravelGuide, UserBookmark, GuideReview, GuideLike,
    Attraction, GuideTemplate, GuideRecommendation
)

logger = logging.getLogger(__name__)


class TravelPlanService:
    """旅行规划服务"""

    def __init__(self, llm_provider: str = "deepseek", llm_model: str = "deepseek-chat"):
        self.llm_provider = llm_provider
        self.llm_model = llm_model

    def generate_plan(
        self,
        destination: str,
        days: int,
        budget: str,
        travelers: int,
        interest_type: str = "",
        selected_style: str = ""
    ) -> Dict[str, Any]:
        """
        生成旅行规划

        Args:
            destination: 目的地
            days: 天数
            budget: 预算级别
            travelers: 人数
            interest_type: 兴趣类型
            selected_style: 选择的风格

        Returns:
            包含完整旅行规划的字典
        """
        logger.info(f"[TravelPlanService] 生成规划: {destination}, {days}天, {budget}预算")

        try:
            from tradingagents.graph.travel_graph_with_llm import create_travel_graph_with_llm

            # 创建旅行规划图
            graph = create_travel_graph_with_llm(
                llm_provider=self.llm_provider,
                llm_model=self.llm_model
            )

            # 生成规划
            result = graph.plan(
                destination=destination,
                days=days,
                budget=budget,
                travelers=travelers,
                interest_type=interest_type,
                selected_style=selected_style
            )

            # 格式化返回数据
            return self._format_plan_result(result, destination, days, budget, travelers, selected_style)

        except Exception as e:
            logger.error(f"[TravelPlanService] 生成失败: {e}")
            raise

    def _format_plan_result(
        self,
        result: Dict,
        destination: str,
        days: int,
        budget: str,
        travelers: int,
        selected_style: str
    ) -> Dict[str, Any]:
        """格式化规划结果 - 支持分阶段旅行规划图输出"""
        logger.info(f"[TravelPlanService] 格式化规划结果: {destination}")

        # 优先尝试从 detailed_guide (分阶段规划图输出) 获取数据
        detailed_guide = result.get("detailed_guide", {})
        if detailed_guide:
            return self._format_detailed_guide_result(
                detailed_guide, result, destination, days, budget, travelers, selected_style
            )

        # 降级：尝试从旧版 detailed_itinerary 获取数据
        detailed_itinerary = result.get("detailed_itinerary", {})
        budget_breakdown = result.get("budget_breakdown", {})
        attractions_data = result.get("attractions", {})

        # 提取每日行程
        daily_itinerary = detailed_itinerary.get("daily_itinerary", [])
        if not daily_itinerary:
            # 如果没有详细行程，生成基础结构
            daily_itinerary = self._generate_basic_itinerary(destination, days, budget)

        return {
            "destination": destination,
            "destination_type": result.get("destination_type", "domestic"),
            "days": days,
            "budget": budget,
            "travelers": travelers,
            "travel_style": selected_style or "exploration",
            "interest_tags": [],  # 可以从 user_portrait 提取
            "daily_itinerary": daily_itinerary,
            "budget_breakdown": budget_breakdown,
            "attractions": attractions_data.get("recommended", []),
            "weather_forecast": result.get("weather_forecast", {}),
            "transport_info": result.get("transport_info", {}),
            "recommendations": budget_breakdown.get("recommendations", []),
            "money_saving_tips": budget_breakdown.get("money_saving_tips", [])
        }

    def _format_detailed_guide_result(
        self,
        detailed_guide: Dict,
        result: Dict,
        destination: str,
        days: int,
        budget: str,
        travelers: int,
        selected_style: str
    ) -> Dict[str, Any]:
        """
        格式化分阶段规划图的详细攻略输出

        将LLM生成的详细攻略转换为前端期望的格式
        """
        logger.info(f"[TravelPlanService] 格式化详细攻略输出")

        # 从 detailed_guide 提取每日行程 (注意: daily_itineraries 是复数)
        daily_itineraries = detailed_guide.get("daily_itineraries", [])

        # 如果没有 daily_itineraries，尝试从 scheduled_attractions 构建
        if not daily_itineraries:
            scheduled_attractions = result.get("scheduled_attractions", [])
            if scheduled_attractions:
                daily_itineraries = self._transform_scheduled_attractions_to_frontend_format(
                    scheduled_attractions,
                    result.get("dining_plan", {}),
                    result.get("transport_plan", {}),
                    result.get("accommodation_plan", {})
                )
            else:
                # 最后降级：生成基础结构
                daily_itineraries = self._generate_basic_itinerary(destination, days, budget)

        # 构建预算明细
        budget_breakdown = detailed_guide.get("budget_breakdown", {})
        if not budget_breakdown:
            budget_breakdown = self._build_budget_breakdown(
                result, days, budget, travelers
            )

        # 构建摘要信息
        summary = self._build_guide_summary(
            detailed_guide, daily_itineraries, budget_breakdown
        )

        # 构建住宿信息
        accommodation = self._build_accommodation_info(
            result.get("accommodation_plan", {})
        )

        # 构建交通概览
        transportation = self._build_transportation_overview(
            result.get("transport_plan", {})
        )

        # 构建实用信息
        essentials = self._build_essentials_info(
            detailed_guide, destination
        )

        return {
            "destination": destination,
            "destination_type": result.get("destination_type", "domestic"),
            "days": days,
            "total_days": days,
            "budget": budget,
            "travelers": travelers,
            "travel_style": selected_style or detailed_guide.get("style_type", "exploration"),
            "interest_tags": [],  # 可以从 user_portrait 提取
            "daily_itineraries": daily_itineraries,
            "daily_itinerary": daily_itineraries,  # 兼容旧版
            "budget_breakdown": budget_breakdown,
            "summary": summary,
            "accommodation": accommodation,
            "transportation": transportation,
            "essentials": essentials,
            "overview": detailed_guide.get("overview", ""),
            "travel_tips": detailed_guide.get("travel_tips", []),
            "packing_list": detailed_guide.get("packing_list", []),
            "attractions": result.get("scheduled_attractions", []),
            "weather_forecast": result.get("weather_forecast", {}),
            "transport_info": result.get("transport_plan", {}),
            "recommendations": detailed_guide.get("travel_tips", []),
            "money_saving_tips": detailed_guide.get("travel_tips", [])
        }

    def _transform_scheduled_attractions_to_frontend_format(
        self,
        scheduled_attractions: List[Dict],
        dining_plan: Dict,
        transport_plan: Dict,
        accommodation_plan: Dict
    ) -> List[Dict[str, Any]]:
        """
        将 Group C 智能体的输出转换为前端期望的格式

        前端期望的每日行程格式:
        {
            "day": 1,
            "title": "...",
            "date": "...",
            "theme": "...",
            "pace": "...",
            "daily_budget": 500,
            "schedule": [
                {
                    "time_range": "09:00-12:00",
                    "period": "morning",
                    "activity": "游览故宫",
                    "attraction_name": "故宫",
                    "location": "故宫",
                    "description": "详细描述...",
                    "highlights": ["必看1", "必看2"],
                    "practical_info": { "address": "...", "opening_hours": "..." },
                    "transportation": { "method": "...", "route": "...", "cost": 50 },
                    "estimated_cost": 100
                }
            ]
        }
        """
        logger.info(f"[TravelPlanService] 转换景点日程为前端格式: {len(scheduled_attractions)}天")

        frontend_days = []
        daily_dining = dining_plan.get("daily_dining", [])
        daily_transport = transport_plan.get("daily_transport", [])

        for day_index, day_schedule in enumerate(scheduled_attractions):
            day_num = day_schedule.get("day", day_index + 1)
            date = day_schedule.get("date", f"第{day_num}天")
            title = day_schedule.get("title", f"第{day_num}天：探索精彩旅程")
            theme = day_schedule.get("theme", f"探索目的地特色")
            pace = day_schedule.get("pace", "适中")
            daily_budget = day_schedule.get("daily_budget", 500)

            # 转换当天的 schedule
            schedule_items = []
            raw_schedule = day_schedule.get("schedule", [])

            for item in raw_schedule:
                period = item.get("period", "")
                activity = item.get("activity", "")

                # 基础字段
                frontend_item = {
                    "time_range": item.get("time_range", ""),
                    "period": period,
                    "activity": activity,
                    "location": item.get("location", activity),
                    "description": item.get("description", ""),
                    "estimated_cost": item.get("estimated_cost", 0)
                }

                # 上午/下午景点：添加详细信息
                if period in ["morning", "afternoon"]:
                    frontend_item["attraction_name"] = activity

                    # 添加 highlights (从 agent 输出提取)
                    if item.get("highlights"):
                        frontend_item["highlights"] = item.get("highlights", [])
                    else:
                        # 生成默认 highlights
                        frontend_item["highlights"] = [
                            f"探索{activity}的主要景点",
                            "体验当地文化特色",
                            "拍摄精彩照片留念"
                        ]

                    # 添加 practical_info
                    if item.get("practical_info"):
                        frontend_item["practical_info"] = item["practical_info"]
                    else:
                        frontend_item["practical_info"] = {
                            "address": f"{activity}景区",
                            "opening_hours": "09:00-17:00",
                            "ticket_price": "¥50-100",
                            "recommended_duration": "2-3小时",
                            "best_time_to_visit": "上午开馆时人最少"
                        }

                    # 添加 transportation
                    if item.get("transportation"):
                        frontend_item["transportation"] = item["transportation"]
                    elif day_index < len(daily_transport):
                        day_transport = daily_transport[day_index]
                        if period == "morning":
                            route = day_transport.get("morning_route", {})
                        else:
                            route = day_transport.get("afternoon_route", {})

                        frontend_item["transportation"] = {
                            "method": route.get("method", "地铁/公交"),
                            "route": route.get("route", "前往景点"),
                            "duration": route.get("duration", "约30分钟"),
                            "cost": route.get("cost", 20),
                            "tips": route.get("tips", "建议避开早晚高峰")
                        }

                # 午餐/晚餐：添加餐饮信息
                elif period in ["lunch", "dinner"]:
                    meal_key = "lunch" if period == "lunch" else "dinner"
                    if day_index < len(daily_dining):
                        day_dining = daily_dining[day_index]
                        meal_info = day_dining.get(meal_key)

                        if meal_info:
                            frontend_item["recommendations"] = {
                                "restaurant": meal_info.get("recommended_restaurant", "当地特色餐厅"),
                                "address": meal_info.get("address", "景区附近"),
                                "opening_hours": meal_info.get("opening_hours", "11:00-21:00"),
                                "signature_dishes": meal_info.get("signature_dishes", [
                                    {"name": "特色菜1", "price": 60},
                                    {"name": "特色菜2", "price": 50}
                                ]),
                                "average_cost": meal_info.get("estimated_cost", 80),
                                "tips": meal_info.get("tips", "建议提前预订"),
                                "recommended_reason": meal_info.get("recommended_reason", "当地人气餐厅")
                            }

                schedule_items.append(frontend_item)

            frontend_day = {
                "day": day_num,
                "date": date,
                "title": title,
                "theme": theme,
                "pace": pace,
                "daily_budget": daily_budget,
                "schedule": schedule_items
            }

            # 添加天气信息（如果有）
            if day_schedule.get("weather"):
                frontend_day["weather"] = day_schedule["weather"]

            # 添加当天小贴士（如果有）
            if day_schedule.get("tips"):
                frontend_day["tips"] = day_schedule["tips"]

            frontend_days.append(frontend_day)

        logger.info(f"[TravelPlanService] 转换完成: {len(frontend_days)}天行程")
        return frontend_days

    def _build_budget_breakdown(
        self,
        result: Dict,
        days: int,
        budget: str,
        travelers: int
    ) -> Dict[str, Any]:
        """构建预算明细"""
        # 预算级别对应的日均费用
        budget_daily = {
            "low": 300,
            "medium": 500,
            "high": 1000
        }

        daily_budget = budget_daily.get(budget, 500)
        total_budget = daily_budget * days * travelers

        # 从各计划中提取费用
        dining_plan = result.get("dining_plan", {})
        transport_plan = result.get("transport_plan", {})
        accommodation_plan = result.get("accommodation_plan", {})

        meal_cost = dining_plan.get("estimated_meal_cost", {})
        dining_cost = meal_cost.get("per_day", 150) * days * travelers

        transport_cost = transport_plan.get("total_transport_cost", 50 * days)

        accommodation_cost = accommodation_plan.get("accommodation_cost", {})
        accommodation_total = accommodation_cost.get("total_cost", 300 * days)

        # 景点费用（从 scheduled_attractions 提取）
        attraction_cost = 0
        scheduled_attractions = result.get("scheduled_attractions", [])
        for day in scheduled_attractions:
            for item in day.get("schedule", []):
                ticket = item.get("ticket", {})
                if isinstance(ticket, dict):
                    attraction_cost += ticket.get("price", 0)

        return {
            "total_budget": total_budget,
            "attractions": attraction_cost,
            "dining": dining_cost,
            "transport": transport_cost,
            "accommodation": accommodation_total,
            "miscellaneous": total_budget - attraction_cost - dining_cost - transport_cost - accommodation_total,
            "recommendations": [
                f"提前预订景点门票可享受折扣",
                f"选择当地特色餐厅体验地道美食",
                f"使用公共交通工具节省交通费用"
            ],
            "money_saving_tips": [
                "避开旅游旺季可节省住宿费用",
                "学生携带证件可享受门票优惠",
                "选择口碑好的街头小吃体验当地风味"
            ]
        }

    def _build_guide_summary(
        self,
        detailed_guide: Dict,
        daily_itineraries: List,
        budget_breakdown: Dict
    ) -> Dict[str, Any]:
        """构建攻略摘要"""
        # 统计景点数量
        total_attractions = 0
        for day in daily_itineraries:
            for item in day.get("schedule", []):
                if item.get("period") in ["morning", "afternoon"]:
                    total_attractions += 1

        # 获取住宿区域
        accommodation_area = "市中心区域"
        if detailed_guide.get("accommodation_plan"):
            acc_plan = detailed_guide["accommodation_plan"]
            if acc_plan.get("recommended_area"):
                accommodation_area = acc_plan["recommended_area"]

        budget_per_day = budget_breakdown.get("total_budget", 0) // len(daily_itineraries) if daily_itineraries else 500

        return {
            "total_attractions": total_attractions,
            "total_attractions_en": total_attractions,
            "budget_per_day": budget_per_day,
            "accommodation_area": accommodation_area,
            "accommodation_area_en": accommodation_area,
            "transportation_overview": "市内交通建议使用地铁、公交或打车",
            "transportation_overview_en": "Use metro, bus or taxi for city transportation"
        }

    def _build_accommodation_info(self, accommodation_plan: Dict) -> Dict[str, Any]:
        """构建住宿信息"""
        if not accommodation_plan:
            return {
                "recommendation": "建议入住市中心酒店，交通便利",
                "recommendation_en": "Recommended to stay in downtown hotel with convenient transportation",
                "options": []
            }

        recommendations = accommodation_plan.get("recommendations", [])
        options = []
        for rec in recommendations[:3]:  # 最多3个选项
            options.append({
                "name": rec.get("name", "推荐酒店"),
                "name_en": rec.get("name_en", "Recommended Hotel"),
                "location": rec.get("location", "市中心"),
                "price_range": rec.get("price_range", "¥300-600/晚"),
                "reason": rec.get("reason", "地理位置优越，交通便利"),
                "reason_en": rec.get("reason_en", "Great location, convenient transportation")
            })

        return {
            "recommendation": accommodation_plan.get("recommended_area", "建议入住市中心"),
            "recommendation_en": accommodation_plan.get("recommended_area_en", "Recommended downtown area"),
            "options": options
        }

    def _build_transportation_overview(self, transport_plan: Dict) -> Dict[str, Any]:
        """构建交通概览"""
        daily_transport = transport_plan.get("daily_transport", [])

        daily_details = []
        for idx, day_transport in enumerate(daily_transport):
            day_num = idx + 1
            suggestion = day_transport.get("suggestion", f"第{day_num}天交通便捷")
            daily_details.append({
                "day": day_num,
                "suggestion": suggestion
            })

        return {
            "overview": transport_plan.get("overview", "市内交通指南"),
            "daily_details": daily_details
        }

    def _build_essentials_info(self, detailed_guide: Dict, destination: str) -> Dict[str, Any]:
        """构建实用信息"""
        travel_tips = detailed_guide.get("travel_tips", [])
        packing_list = detailed_guide.get("packing_list", [])

        return {
            "weather_advice": f"建议提前关注{destination}天气预报，根据天气准备衣物",
            "weather_advice_en": f"Check {destination} weather forecast in advance and prepare accordingly",
            "packing_list": packing_list if packing_list else [
                "身份证/护照等重要证件",
                "手机、充电器、充电宝",
                "舒适的步行鞋",
                "防晒霜、遮阳帽/雨伞",
                "常用药品（感冒药、肠胃药等）",
                "换洗衣物（根据天数准备）",
                "洗漱用品（牙刷、牙膏等）",
                "少量现金和银行卡"
            ],
            "emergency_contacts": [
                "报警：110",
                "急救：120",
                "消防：119"
            ],
            "useful_apps": travel_tips if travel_tips else [
                "使用地图APP导航",
                "关注景区官方信息",
                "注意保管随身物品"
            ]
        }

    def _generate_basic_itinerary(
        self,
        destination: str,
        days: int,
        budget: str
    ) -> List[Dict[str, Any]]:
        """生成基础行程结构"""
        itinerary = []
        for day in range(1, days + 1):
            itinerary.append({
                "day": day,
                "theme": f"第{day}天探索",
                "morning": {
                    "time": "09:00-12:00",
                    "activity": "游览景点",
                    "description": f"探索{destination}的精华景点"
                },
                "lunch": {
                    "time": "12:00-13:30",
                    "activity": "午餐",
                    "description": "品尝当地特色美食"
                },
                "afternoon": {
                    "time": "14:00-17:00",
                    "activity": "继续游览",
                    "description": "深度体验当地文化"
                },
                "dinner": {
                    "time": "18:00-20:00",
                    "activity": "晚餐",
                    "description": "享用丰盛晚餐"
                },
                "evening": {
                    "time": "20:00-22:00",
                    "activity": "自由活动",
                    "description": "夜游或休息"
                }
            })
        return itinerary


class GuideService:
    """攻略服务"""

    @staticmethod
    def create_guide_from_plan(
        db: Session,
        plan_data: Dict[str, Any],
        user_id: int,
        title: str,
        description: str = None
    ) -> TravelGuide:
        """
        从规划数据创建攻略

        Args:
            db: 数据库会话
            plan_data: 规划数据
            user_id: 用户ID
            title: 攻略标题
            description: 攻略描述

        Returns:
            创建的攻略对象
        """
        from app.models.travel import User

        # 获取用户信息
        user = db.query(User).filter(User.id == user_id).first()
        username = user.username if user else f"user_{user_id}"

        # 生成slug
        slug = GuideService._generate_slug(title)

        # 创建攻略
        guide = TravelGuide(
            title=title,
            description=description or f"AI生成的{plan_data['destination']}{plan_data['days']}天旅行规划",
            destination=plan_data["destination"],
            destination_type=plan_data.get("destination_type", "domestic"),
            days=plan_data["days"],
            budget_level=plan_data["budget"],
            total_budget=plan_data["budget_breakdown"].get("total_budget"),
            travelers_count=plan_data["travelers"],
            travel_style=plan_data.get("travel_style"),
            interest_tags=plan_data.get("interest_tags", []),
            itinerary={"daily_itinerary": plan_data.get("daily_itinerary", [])},
            budget_breakdown=plan_data.get("budget_breakdown", {}),
            attractions=plan_data.get("attractions", []),
            generation_method="ai",
            generation_config={
                "llm_provider": "deepseek",
                "generated_at": datetime.utcnow().isoformat()
            },
            slug=slug,
            user_id=user_id,
            username=username,
            status="draft"
        )

        db.add(guide)
        db.commit()
        db.refresh(guide)

        # 更新用户攻略计数
        if user:
            user.guides_count += 1
            db.commit()

        logger.info(f"[GuideService] 创建攻略: ID={guide.id}, Title={title}")
        return guide

    @staticmethod
    def _generate_slug(title: str) -> str:
        """生成URL友好的slug"""
        import re
        import uuid
        slug = re.sub(r'[^\w\u4e00-\u9fff]+', '-', title.lower())
        slug = slug.strip('-')
        # 确保唯一性
        return f"{slug}-{uuid.uuid4().hex[:8]}"

    @staticmethod
    def publish_guide(db: Session, guide_id: int, user_id: int) -> TravelGuide:
        """发布攻略"""
        guide = db.query(TravelGuide).filter(
            and_(TravelGuide.id == guide_id, TravelGuide.user_id == user_id)
        ).first()

        if not guide:
            raise ValueError("攻略不存在或无权限")

        guide.status = "published"
        guide.published_at = datetime.utcnow()

        db.commit()
        db.refresh(guide)

        return guide

    @staticmethod
    def get_similar_guides(
        db: Session,
        guide_id: int,
        limit: int = 5
    ) -> List[TravelGuide]:
        """获取相似攻略"""
        guide = db.query(TravelGuide).filter(TravelGuide.id == guide_id).first()
        if not guide:
            return []

        # 查找相似攻略
        query = db.query(TravelGuide).filter(
            and_(
                TravelGuide.id != guide_id,
                TravelGuide.status == "published",
                or_(
                    TravelGuide.destination == guide.destination,
                    TravelGuide.days == guide.days,
                    TravelGuide.budget_level == guide.budget_level,
                    TravelGuide.travel_style == guide.travel_style
                )
            )
        ).order_by(desc(TravelGuide.rating_avg))

        return query.limit(limit).all()


class SearchService:
    """搜索服务"""

    @staticmethod
    def search_guides(
        db: Session,
        keyword: str = "",
        destination: str = "",
        destination_type: str = "",
        days_min: int = None,
        days_max: int = None,
        budget_level: str = "",
        travel_style: str = "",
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        搜索攻略

        Returns:
            包含total, page, page_size, total_pages, items的字典
        """
        # 构建查询
        query = db.query(TravelGuide).filter(TravelGuide.status == "published")

        # 应用筛选条件
        if keyword:
            query = query.filter(
                or_(
                    TravelGuide.title.ilike(f"%{keyword}%"),
                    TravelGuide.description.ilike(f"%{keyword}%"),
                    TravelGuide.destination.ilike(f"%{keyword}%")
                )
            )

        if destination:
            query = query.filter(TravelGuide.destination.ilike(f"%{destination}%"))

        if destination_type:
            query = query.filter(TravelGuide.destination_type == destination_type)

        if days_min:
            query = query.filter(TravelGuide.days >= days_min)

        if days_max:
            query = query.filter(TravelGuide.days <= days_max)

        if budget_level:
            query = query.filter(TravelGuide.budget_level == budget_level)

        if travel_style:
            query = query.filter(TravelGuide.travel_style == travel_style)

        # 排序
        order_column = getattr(TravelGuide, sort_by, TravelGuide.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)

        # 分页
        total = query.count()
        total_pages = (total + page_size - 1) // page_size
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "items": items
        }


class RecommendationService:
    """推荐服务"""

    @staticmethod
    def get_personalized_recommendations(
        db: Session,
        user_id: int,
        limit: int = 10
    ) -> List[TravelGuide]:
        """
        获取个性化推荐

        基于用户的浏览历史、收藏、点赞等行为推荐
        """
        # 获取用户收藏的攻略
        bookmarks = db.query(UserBookmark).filter(
            UserBookmark.user_id == user_id
        ).all()

        if not bookmarks:
            # 如果没有收藏，返回热门攻略
            return db.query(TravelGuide).filter(
                TravelGuide.status == "published"
            ).order_by(
                desc(TravelGuide.view_count)
            ).limit(limit).all()

        # 提取用户偏好的目的地和风格
        guide_ids = [b.guide_id for b in bookmarks]
        bookmarked_guides = db.query(TravelGuide).filter(
            TravelGuide.id.in_(guide_ids)
        ).all()

        # 获取推荐
        recommendations = []
        for guide in bookmarked_guides:
            similar = GuideService.get_similar_guides(db, guide.id, limit=2)
            recommendations.extend(similar)

        # 去重并排序
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec.id not in seen and rec.id not in guide_ids:
                seen.add(rec.id)
                unique_recommendations.append(rec)

        return unique_recommendations[:limit]

    @staticmethod
    def get_trending_guides(
        db: Session,
        limit: int = 10
    ) -> List[TravelGuide]:
        """获取热门攻略"""
        return db.query(TravelGuide).filter(
            TravelGuide.status == "published"
        ).order_by(
            desc(TravelGuide.view_count),
            desc(TravelGuide.like_count)
        ).limit(limit).all()

    @staticmethod
    def get_featured_guides(
        db: Session,
        limit: int = 10
    ) -> List[TravelGuide]:
        """获取精选攻略"""
        return db.query(TravelGuide).filter(
            and_(
                TravelGuide.status == "published",
                or_(
                    TravelGuide.is_featured == True,
                    TravelGuide.is_editor_pick == True
                )
            )
        ).order_by(
            desc(TravelGuide.created_at)
        ).limit(limit).all()


class StatsService:
    """统计服务"""

    @staticmethod
    def get_global_stats(db: Session) -> Dict[str, Any]:
        """获取全局统计数据"""
        total_guides = db.query(TravelGuide).count()
        published_guides = db.query(TravelGuide).filter(
            TravelGuide.status == "published"
        ).count()

        # 热门目的地
        top_destinations = db.query(
            TravelGuide.destination,
            func.count(TravelGuide.id).label('count')
        ).filter(
            TravelGuide.status == "published"
        ).group_by(
            TravelGuide.destination
        ).order_by(
            desc('count')
        ).limit(10).all()

        return {
            "total_guides": total_guides,
            "published_guides": published_guides,
            "total_views": db.query(func.sum(TravelGuide.view_count)).scalar() or 0,
            "total_likes": db.query(func.sum(TravelGuide.like_count)).scalar() or 0,
            "total_bookmarks": db.query(func.count(UserBookmark.id)).scalar() or 0,
            "top_destinations": [
                {"destination": d[0], "count": d[1]} for d in top_destinations
            ]
        }

    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict[str, Any]:
        """获取用户统计数据"""
        from app.models.travel import User

        user = db.query(User).filter(User.id == user_id).first()

        guides_count = db.query(TravelGuide).filter(
            TravelGuide.user_id == user_id
        ).count()

        bookmarks_count = db.query(UserBookmark).filter(
            UserBookmark.user_id == user_id
        ).count()

        likes_count = db.query(GuideLike).filter(
            GuideLike.user_id == user_id
        ).count()

        reviews_count = db.query(GuideReview).filter(
            GuideReview.user_id == user_id
        ).count()

        total_views = db.query(func.sum(TravelGuide.view_count)).filter(
            TravelGuide.user_id == user_id
        ).scalar() or 0

        return {
            "guides_count": guides_count,
            "bookmarks_count": bookmarks_count,
            "likes_count": likes_count,
            "reviews_count": reviews_count,
            "total_views": total_views,
            "nickname": user.nickname if user else None,
            "avatar_url": user.avatar_url if user else None
        }
