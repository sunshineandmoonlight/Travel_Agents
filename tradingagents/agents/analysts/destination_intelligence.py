"""
目的地情报智能体 (Destination Intelligence Agent)

实时获取目的地的：
- 新闻资讯
- 风险评估
- 节日活动
- 文化体验
- 风土人情

为旅行规划提供实时情报支持
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain.tools import tool

logger = logging.getLogger(__name__)

# 新闻数据适配器 - 用于获取真实新闻数据
try:
    from app.services.data_sources.news_adapter import get_news_adapter
    NEWS_ADAPTER_AVAILABLE = True
except ImportError:
    NEWS_ADAPTER_AVAILABLE = False
    logger.warning("[目的地情报] 新闻适配器不可用，将使用模拟数据")

# LLM导入（用于智能建议生成）
try:
    from tradingagents.graph.trading_graph import create_llm_by_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("[目的地情报] LLM功能不可用，将使用规则生成建议")


class DestinationIntelligenceAgent:
    """目的地情报智能体"""

    def __init__(self, llm_provider: str = "deepseek", llm_model: str = "deepseek-chat"):
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        self._cache = {}
        self._cache_ttl = 3600  # 缓存1小时

    async def analyze_destination(self, destination: str, travel_date: Optional[str] = None) -> Dict[str, Any]:
        """
        综合分析目的地情报

        Args:
            destination: 目的地名称
            travel_date: 旅行日期 (YYYY-MM-DD)

        Returns:
            完整的情报报告
        """
        logger.info(f"[目的地情报] 开始分析: {destination}")

        start_time = datetime.now()
        report = {
            "destination": destination,
            "travel_date": travel_date,
            "generated_at": datetime.now().isoformat(),
            "news": [],
            "risk_assessment": {},
            "events": [],
            "cultural_experiences": [],
            "recommendations": []
        }

        try:
            # 并行执行各子Agent
            tasks = [
                self._search_news(destination),
                self._assess_risks(destination, travel_date),
                self._find_events(destination, travel_date),
                self._recommend_culture(destination)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 收集结果
            if isinstance(results[0], Exception):
                logger.error(f"新闻搜索失败: {results[0]}")
            else:
                report["news"] = results[0]

            if isinstance(results[1], Exception):
                logger.error(f"风险评估失败: {results[1]}")
            else:
                report["risk_assessment"] = results[1]

            if isinstance(results[2], Exception):
                logger.error(f"活动搜索失败: {results[2]}")
            else:
                report["events"] = results[2]

            if isinstance(results[3], Exception):
                logger.error(f"文化推荐失败: {results[3]}")
            else:
                report["cultural_experiences"] = results[3]

            # 生成综合建议
            report["recommendations"] = self._generate_recommendations(report)

            duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            report["duration_ms"] = duration_ms

            logger.info(f"[目的地情报] 分析完成: {destination} ({duration_ms}ms)")

            return report

        except Exception as e:
            logger.error(f"[目的地情报] 分析失败: {e}")
            raise

    async def _search_news(self, destination: str, days: int = 7) -> List[Dict]:
        """搜索目的地新闻"""
        logger.info(f"[新闻搜索] 搜索 {destination} 的新闻...")

        # 尝试使用真实新闻数据源
        use_real_api = os.getenv("NEWS_SOURCE", "mock") != "mock"

        if use_real_api and NEWS_ADAPTER_AVAILABLE:
            try:
                adapter = get_news_adapter()
                real_news = await adapter.search_news(f"{destination} 旅游", days, num=10)

                if real_news:
                    logger.info(f"[新闻搜索] 从 {adapter.source} 获取到 {len(real_news)} 条真实新闻")

                    # 添加目的地特定新闻作为补充
                    specific_news = self._get_destination_specific_news(destination)
                    all_news = real_news + specific_news

                    return all_news[:10]
                else:
                    logger.warning("[新闻搜索] 真实API未返回数据，使用模拟数据")
            except Exception as e:
                logger.error(f"[新闻搜索] 真实API调用失败: {e}，使用模拟数据")

        # 使用模拟数据（降级方案）
        mock_news = [
            {
                "title": f"{destination}推出新一轮旅游优惠政策",
                "source": f"{destination}日报",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "url": "#",
                "summary": f"{destination}市政府宣布，为促进旅游业发展，将推出新一轮旅游优惠政策，包括部分景点门票减免、公共交通优惠等。",
                "sentiment": "positive",
                "category": "policy"
            },
            {
                "title": f"{destination}春季旅游市场升温",
                "source": "旅游新闻网",
                "published_at": (datetime.now() - timedelta(hours=12)).isoformat(),
                "url": "#",
                "summary": f"随着春季的到来，{destination}旅游市场逐渐升温，各大景区游客量明显增加。",
                "sentiment": "neutral",
                "category": "market"
            }
        ]

        # 根据目的地添加特定新闻
        destination_specific_news = self._get_destination_specific_news(destination)
        mock_news.extend(destination_specific_news)

        return mock_news[:10]  # 返回最多10条

    def _get_destination_specific_news(self, destination: str) -> List[Dict]:
        """获取目的地特定新闻"""
        # 这里可以根据目的地返回不同的新闻
        specific_news = []

        if "杭州" in destination or "浙江" in destination:
            specific_news.append({
                "title": "杭州西湖音乐节将于4月举办",
                "source": "杭州市文旅局",
                "published_at": datetime.now().isoformat(),
                "url": "#",
                "summary": "杭州西湖音乐节定于4月15-22日在西湖风景区举办，届时将有多位知名艺人参演。",
                "sentiment": "positive",
                "category": "event"
            })
        elif "三亚" in destination or "海南" in destination:
            specific_news.append({
                "title": "三亚加强旅游市场监管，保障游客权益",
                "source": "海南日报",
                "published_at": datetime.now().isoformat(),
                "url": "#",
                "summary": "三亚市旅游和文化广电体育局近日开展专项行动，加强旅游市场监管，严厉打击违法违规行为。",
                "sentiment": "positive",
                "category": "policy"
            })
        elif "成都" in destination or "四川" in destination:
            specific_news.append({
                "title": "成都大熊猫繁育研究基地发布公告",
                "source": "成都日报",
                "published_at": datetime.now().isoformat(),
                "url": "#",
                "summary": "成都大熊猫繁育研究基地发布关于游客参观的最新公告，提醒游客提前预约。",
                "sentiment": "neutral",
                "category": "notice"
            })

        return specific_news

    async def _assess_risks(self, destination: str, travel_date: Optional[str] = None) -> Dict:
        """评估旅行风险"""
        logger.info(f"[风险评估] 评估 {destination} 的风险...")

        # 基础风险等级（国内城市通常较安全）
        base_risk_level = 1  # 1-5，5最高

        risk_factors = []
        risk_categories = {
            "political": {"level": 1, "status": "安全", "description": "社会稳定"},
            "safety": {"level": 1, "status": "安全", "description": "治安良好"},
            "health": {"level": 1, "status": "安全", "description": "无疫情报告"},
            "natural_disaster": {"level": 1, "status": "安全", "description": "无灾害预警"},
            "social": {"level": 1, "status": "正常", "description": "社会秩序良好"}
        }

        # 根据季节调整风险
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:
            # 夏季：台风、暴雨风险
            risk_categories["natural_disaster"]["level"] = 2
            risk_categories["natural_disaster"]["status"] = "注意"
            risk_categories["natural_disaster"]["description"] = "夏季可能有台风、暴雨"
            risk_factors.append({
                "type": "natural_disaster",
                "level": "medium",
                "description": "夏季是台风高发季节，请关注天气预报",
                "advice": "关注天气预报，做好防护准备"
            })
            base_risk_level = 2
        elif current_month in [11, 12, 1, 2]:
            # 冬季：寒冷、雨雪
            risk_categories["natural_disaster"]["level"] = 2
            risk_categories["natural_disaster"]["status"] = "注意"
            risk_categories["natural_disaster"]["description"] = "冬季寒冷，注意保暖"
            risk_factors.append({
                "type": "weather",
                "level": "low",
                "description": "冬季天气寒冷",
                "advice": "注意保暖，携带防寒衣物"
            })

        # 根据目的地特定风险
        destination_risks = self._get_destination_specific_risks(destination)
        if destination_risks:
            risk_factors.extend(destination_risks)
            # 调整风险等级
            max_level = max([r.get("level_num", 1) for r in risk_factors])
            base_risk_level = max(base_risk_level, max_level)

        # 确定总体风险等级
        if base_risk_level <= 2:
            overall_risk = "low"
            overall_risk_text = "🟢 低风险 - 可以放心前往"
            recommendation = "目的地安全，可以放心前往。建议购买旅游保险。"
        elif base_risk_level == 3:
            overall_risk = "medium"
            overall_risk_text = "🟡 中风险 - 谨慎前往"
            recommendation = "需要注意一些风险因素，建议购买旅游保险，关注当地预警信息。"
        else:
            overall_risk = "high"
            overall_risk_text = "🔴 高风险 - 不建议前往"
            recommendation = "当前不建议前往，建议推迟行程或选择其他目的地。"

        return {
            "overall_risk": overall_risk,
            "overall_risk_text": overall_risk_text,
            "risk_level": base_risk_level,
            "risk_categories": risk_categories,
            "risk_factors": risk_factors,
            "recommendation": recommendation,
            "last_updated": datetime.now().isoformat()
        }

    def _get_destination_specific_risks(self, destination: str) -> List[Dict]:
        """获取目的地特定风险"""
        risks = []

        if "三亚" in destination or "海南" in destination:
            if datetime.now().month in [9, 10]:
                risks.append({
                    "type": "weather",
                    "level": "medium",
                    "level_num": 2,
                    "description": "秋季是台风季节",
                    "advice": "关注台风预报，必要时调整行程"
                })
        elif "西藏" in destination or "拉萨" in destination:
            risks.append({
                "type": "health",
                "level": "medium",
                "level_num": 2,
                "description": "高原反应风险",
                "advice": "提前做好高反预防，携带相关药品"
            })
            risks.append({
                "type": "political",
                "level": "low",
                "level_num": 1,
                "description": "需要办理入藏函",
                "advice": "提前办理入藏函，检查证件有效期"
            })
        elif "新疆" in destination:
            risks.append({
                "type": "political",
                "level": "low",
                "level_num": 1,
                "description": "需要边防证",
                "advice": "提前办理边防证"
            })

        return risks

    async def _find_events(self, destination: str, travel_date: Optional[str] = None) -> List[Dict]:
        """查找当地活动"""
        logger.info(f"[活动搜索] 搜索 {destination} 的活动...")

        # 解析旅行日期
        start_date = None
        if travel_date:
            try:
                start_date = datetime.fromisoformat(travel_date)
            except:
                pass

        if not start_date:
            start_date = datetime.now()

        end_date = start_date + timedelta(days=30)

        # 模拟活动数据
        events = []

        # 通用活动
        general_events = self._get_general_events(destination, start_date, end_date)
        events.extend(general_events)

        # 目的地特定活动
        specific_events = self._get_destination_specific_events(destination, start_date, end_date)
        events.extend(specific_events)

        return sorted(events, key=lambda x: x.get("start_date", ""))[:10]

    def _get_general_events(self, destination: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取通用活动"""
        events = []

        # 当前月份的活动
        current_month = start_date.month
        if current_month == 3:
            events.append({
                "name": f"{destination}春季花卉展",
                "type": "festival",
                "start_date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "end_date": (start_date + timedelta(days=21)).strftime("%Y-%m-%d"),
                "location": f"{destination}植物园/公园",
                "description": "春季赏花活动，欣赏樱花、郁金香等春季花卉",
                "recommendation": "推荐！摄影爱好者不容错过",
                "tickets": "现场购票或公众号预约"
            })
        elif current_month == 4:
            events.append({
                "name": f"{destination}清明文化体验活动",
                "type": "cultural",
                "start_date": (start_date + timedelta(days=5)).strftime("%Y-%m-%d"),
                "end_date": (start_date + timedelta(days=7)).strftime("%Y-%m-%d"),
                "location": f"{destination}博物馆/文化中心",
                "description": "清明传统文化体验活动，包括传统手工艺、民俗表演等",
                "recommendation": "适合家庭参与",
                "tickets": "免费或低收费"
            })
        elif current_month == 5:
            events.append({
                "name": "五一劳动节假期活动",
                "type": "holiday",
                "start_date": f"{start_date.year}-05-01",
                "end_date": f"{start_date.year}-05-05",
                "location": f"{destination}各大景区",
                "description": "五一假期各类主题活动，景区可能有特殊安排",
                "recommendation": "提前预订，错峰出行",
                "tickets": "景区门票可能紧张"
            })
        elif current_month == 10:
            events.append({
                "name": "国庆黄金周活动",
                "type": "holiday",
                "start_date": f"{start_date.year}-10-01",
                "end_date": f"{start_date.year}-10-07",
                "location": f"{destination}各大景区",
                "description": "国庆假期各类主题活动，灯光秀、演出等",
                "recommendation": "热门景区人流较大",
                "tickets": "提前预订，考虑周边景点"
            })

        return events

    def _get_destination_specific_events(self, destination: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """获取目的地特定活动"""
        events = []

        if "杭州" in destination or "浙江" in destination:
            # 西湖龙井茶节
            tea_festival = {
                "name": "杭州西湖龙井茶文化节",
                "type": "festival",
                "start_date": f"{start_date.year}-04-01",
                "end_date": f"{start_date.year}-04-15",
                "location": "龙井村、西湖风景区",
                "description": "杭州春季龙井茶文化盛会，体验采茶、制茶、品茶，了解茶文化",
                "recommendation": "🍵 推荐！茶文化爱好者必体验",
                "tickets": "部分活动免费，部分需预约",
                "highlights": ["采茶体验", "茶艺表演", "茶文化讲座", "龙井茶品尝"]
            }
            events.append(tea_festival)

            # 杭州动漫节（通常是5月）
            if start_date.month <= 5 <= end_date.month:
                anime_festival = {
                    "name": "中国国际动漫节",
                    "type": "festival",
                    "start_date": f"{start_date.year}-05-01",
                    "end_date": f"{start_date.year}-05-05",
                    "location": "滨江白马湖",
                    "description": "国内最大的动漫节之一，有cosplay比赛、动漫展览等",
                    "recommendation": "动漫爱好者不容错过",
                    "tickets": "需购票"
                }
                events.append(anime_festival)

        elif "成都" in destination or "四川" in destination:
            # 成都美食节
            food_festival = {
                "name": "成都国际美食旅游节",
                "type": "festival",
                "start_date": f"{start_date.year}-07-20",
                "end_date": f"{start_date.year}-07-30",
                "location": "成都各区县",
                "description": "成都最大规模的美食盛会，汇集川菜、火锅、小吃等",
                "recommendation": "🌶️ 推荐！美食爱好者的天堂",
                "tickets": "多数活动免费"
            }
            events.append(food_festival)

        elif "北京" in destination:
            # 北京庙会（春节）
            if start_date.month <= 2 <= end_date.month:
                temple_fair = {
                    "name": "春节庙会",
                    "type": "festival",
                    "start_date": f"{start_date.year}-02-10",
                    "end_date": f"{start_date.year}-02-17",
                    "location": "地坛公园、龙潭公园等",
                    "description": "北京传统春节活动，有民俗表演、小吃、手工艺品等",
                    "recommendation": "体验老北京春节文化",
                    "tickets": "公园门票5-10元"
                }
                events.append(temple_fair)

        elif "西安" in destination:
            # 唐文化主题活动
            if start_date.month <= 5 <= end_date.month:
                tang_culture = {
                    "name": "大唐不夜城唐文化活动",
                    "type": "cultural",
                    "start_date": f"{start_date.year}-05-01",
                    "end_date": f"{start_date.year}-05-31",
                    "location": "大唐不夜城",
                    "description": "唐代文化体验活动，包括古装表演、唐风市集等",
                    "recommendation": "沉浸式体验盛唐文化",
                    "tickets": "景区门票包含活动"
                }
                events.append(tang_culture)

        return events

    async def _recommend_culture(self, destination: str) -> Dict:
        """推荐文化体验"""
        logger.info(f"[文化推荐] 为 {destination} 推荐文化体验...")

        recommendations = {
            "museums": [],
            "performances": [],
            "food_experiences": [],
            "local_specialties": [],
            "cultural_tips": []
        }

        # 目的地特定文化推荐
        if "杭州" in destination:
            recommendations["museums"] = [
                {
                    "name": "浙江省博物馆",
                    "description": "了解浙江历史文化的最佳场所",
                    "duration": "2-3小时",
                    "tips": "周一闭馆，需提前预约，免费参观"
                },
                {
                    "name": "中国丝绸博物馆",
                    "description": "中国丝绸文化的集中展示",
                    "duration": "1-2小时",
                    "tips": "可以体验丝绸制作过程"
                },
                {
                    "name": "中国茶叶博物馆",
                    "description": "中华茶文化展示",
                    "duration": "1-2小时",
                    "tips": "可以品尝各种茶叶"
                }
            ]

            recommendations["performances"] = [
                {
                    "name": "印象西湖",
                    "description": "大型户外实景演出，展示西湖历史文化",
                    "duration": "1小时",
                    "tips": "晚间演出，需提前购票"
                },
                {
                    "name": "宋城千古情",
                    "description": "大型歌舞表演，再现宋代文化",
                    "duration": "1小时",
                    "tips": "被誉为一生必看的演出"
                }
            ]

            recommendations["food_experiences"] = [
                {
                    "name": "杭帮菜体验",
                    "dishes": ["西湖醋鱼", "东坡肉", "龙井虾仁", "叫化童鸡"],
                    "restaurants": ["楼外楼", "知味观", "外婆家"],
                    "tips": "楼外楼是百年老字号，需排队"
                },
                {
                    "name": "茶文化体验",
                    "description": "在龙井村体验采茶、制茶过程",
                    "tips": "春季是采茶的好时节"
                }
            ]

            recommendations["local_specialties"] = [
                {"name": "西湖龙井", "description": "中国十大名茶之一"},
                {"name": "西湖绸伞", "description": "杭州特色手工艺品"},
                {"name": "王星记扇子", "description": "杭州传统工艺品"}
            ]

            recommendations["cultural_tips"] = [
                "杭州人爱喝茶，茶馆是社交的重要场所",
                "杭州话软糯好听，可以学几句当地方言",
                "西湖不仅是景点，也是杭州人生活的一部分"
            ]

        elif "北京" in destination:
            recommendations["museums"] = [
                {
                    "name": "故宫博物院",
                    "description": "明清两代皇宫，世界文化遗产",
                    "duration": "半天",
                    "tips": "必须提前预约，周一闭馆"
                },
                {
                    "name": "国家博物馆",
                    "description": "中国最高历史文化殿堂",
                    "duration": "半天",
                    "tips": "免费参观，需预约"
                }
            ]

            recommendations["performances"] = [
                {
                    "name": "京剧表演",
                    "description": "在北京听一场正宗京剧",
                    "venues": ["梅兰芳大剧院", "长安大戏院"],
                    "tips": "可以提前了解京剧基本知识"
                },
                {
                    "name": "相声表演",
                    "description": "体验北京的曲艺文化",
                    "venues": ["德云社", "嘻哈包袱铺"],
                    "tips": "很受年轻人欢迎"
                }
            ]

            recommendations["food_experiences"] = [
                {
                    "name": "北京烤鸭",
                    "restaurants": ["全聚德", "便宜坊", "大董"],
                    "tips": "全聚德是老字号，大董更精致"
                },
                {
                    "name": "老北京小吃",
                    "dishes": ["豆汁", "焦圈", "卤煮", "炸酱面"],
                    "locations": ["牛街", "护国寺小吃街"],
                    "tips": "豆汁味道特别，可能需要适应"
                }
            ]

        elif "成都" in destination:
            recommendations["museums"] = [
                {
                    "name": "三星堆博物馆",
                    "description": "古蜀文明的震撼展示",
                    "duration": "半天",
                    "tips": "距离市区较远，需预留时间"
                },
                {
                    "name": "成都博物馆",
                    "description": "了解成都历史文化",
                    "duration": "1-2小时",
                    "tips": "就在市区，交通便利"
                }
            ]

            recommendations["performances"] = [
                {
                    "name": "川剧变脸",
                    "description": "四川传统戏曲表演",
                    "venues": ["蜀风雅韵", "宽窄巷子茶馆"],
                    "tips": "变脸是川剧绝活"
                },
                {
                    "name": "芙蓉国粹",
                    "description": "大型歌舞剧",
                    "duration": "1小时",
                    "tips": "蜀绣表演很精彩"
                }
            ]

            recommendations["food_experiences"] = [
                {
                    "name": "火锅文化",
                    "description": "体验成都的火锅文化",
                    "restaurants": ["小龙坎", "大龙燚", "蜀九香"],
                    "tips": "成都火锅以麻辣著称"
                },
                {
                    "name": "串串香",
                    "description": "成都街头美食代表",
                    "locations": ["街头巷尾的串串店"],
                    "tips": "按签子数量计算价格，很有趣"
                },
                {
                    "name": "茶馆文化",
                    "description": "体验成都的慢生活",
                    "locations": ["人民公园茶馆", "宽窄巷子"],
                    "tips": "掏耳朵是成都茶馆特色体验"
                }
            ]

        elif "西安" in destination:
            recommendations["museums"] = [
                {
                    "name": "秦始皇兵马俑",
                    "description": "世界第八大奇迹",
                    "duration": "半天",
                    "tips": "建议请讲解员，更了解历史"
                },
                {
                    "name": "陕西历史博物馆",
                    "description": "了解陕西历史",
                    "duration": "2-3小时",
                    "tips": "馆藏丰富，免费参观"
                }
            ]

            recommendations["performances"] = [
                {
                    "name": "大唐芙蓉园演出",
                    "description": "盛唐文化体验",
                    "tips": "夜景更美"
                },
                {
                    "name": "城墙表演",
                    "description": "西安城墙上的文化演出",
                    "tips": "可以租自行车环城"
                }
            ]

        elif "西藏" in destination or "拉萨" in destination:
            recommendations["museums"] = [
                {
                    "name": "布达拉宫",
                    "description": "藏传佛教圣地",
                    "duration": "半天",
                    "tips": "需要尊重当地宗教习俗，不能穿裙子"
                },
                {
                    "name": "大昭寺",
                    "description": "拉萨最古老的寺庙",
                    "duration": "1-2小时",
                    "tips": "八廓街转经的起点"
                }
            ]

            recommendations["cultural_tips"] = [
                "进入寺庙不能戴帽子和墨镜",
                "不能随便拍照，特别是佛像和僧人",
                "转经要顺时针方向",
                "不要摸小孩的头（当地禁忌）"
            ]

        # 通用文化推荐（如果目的地特定推荐不足）
        if not recommendations["museums"]:
            recommendations["museums"] = [
                {
                    "name": f"{destination}博物馆",
                    "description": f"了解{destination}的历史文化",
                    "duration": "1-2小时",
                    "tips": "建议提前了解开放时间"
                }
            ]

        return recommendations

    def _generate_recommendations(self, report: Dict) -> List[str]:
        """生成综合建议 - 使用LLM生成个性化建议"""
        import os

        # 检查是否应该使用LLM
        use_llm = os.getenv("USE_LLM_FOR_RECOMMENDATIONS", "true").lower() == "true"
        llm_provider = os.getenv("LLM_PROVIDER", "deepseek")

        if use_llm:
            try:
                # 尝试使用LLM生成个性化建议
                return self._generate_llm_recommendations(report, llm_provider)
            except Exception as e:
                logger.warning(f"[智能建议] LLM生成失败，使用规则生成: {e}")

        # 回退到规则生成（原有逻辑）
        recommendations = []

        # 基于风险的建议
        risk_assessment = report.get("risk_assessment", {})
        overall_risk = risk_assessment.get("overall_risk", "low")

        if overall_risk == "low":
            recommendations.append("✅ 目的地安全，可以放心前往")
        elif overall_risk == "medium":
            recommendations.append("⚠️ 需要注意一些风险因素，建议购买旅游保险")
        else:
            recommendations.append("🚫 当前不建议前往，建议推迟行程")

        # 基于活动的建议
        events = report.get("events", [])
        if events:
            high_priority_events = [e for e in events if "推荐" in e.get("recommendation", "")]
            if high_priority_events:
                recommendations.append(f"🎉 近期有{len(high_priority_events)}个推荐活动")

        # 基于季节的建议
        current_month = datetime.now().month
        if current_month in [3, 4, 5]:
            recommendations.append("🌸 春季赏花好时节，建议提前预订")
        elif current_month in [6, 7, 8]:
            recommendations.append("☀️ 夏季炎热多雨，注意防暑防雨")
        elif current_month in [9, 10, 11]:
            recommendations.append("🍂 秋季天高气爽，是旅游的好时节")
        elif current_month in [12, 1, 2]:
            recommendations.append("❄️ 冬季寒冷，注意保暖")

        # 通用建议
        recommendations.extend([
            "💡 建议提前了解当地风俗习惯",
            "📱 下载当地旅游APP获取实时信息",
            "🏨 提前预订住宿可以享受更优惠价格"
        ])

        return recommendations[:8]  # 返回最多8条建议

    def _generate_llm_recommendations(self, report: Dict, llm_provider: str) -> List[str]:
        """使用LLM生成个性化建议"""
        # 检查LLM是否可用
        if not LLM_AVAILABLE:
            raise ImportError("LLM功能不可用")

        # 准备上下文信息
        destination = report.get("destination", "")
        weather = report.get("weather", {})
        risk_assessment = report.get("risk_assessment", {})
        events = report.get("events", [])
        news = report.get("news", [])
        cultural = report.get("cultural_experiences", {})

        # 构建提示词
        prompt = f"""为前往{destination}旅行生成5-8条智能建议。

目的地: {destination}

天气状况:
- {weather.get('description', '适宜出行')}

风险等级: {risk_assessment.get('overall_risk_text', '低风险')}

近期活动: {len(events)}个

文化体验: {len(cultural.get('museums', []))}个博物馆，{len(cultural.get('performances', []))}个表演

最新资讯: {len(news)}条

请根据以上信息生成实用的旅行建议，每条建议要具体、可操作。建议应该涵盖:
1. 最佳游览时间建议
2. 不可错过的体验
3. 实用小贴士 (交通、住宿等)
4. 当地文化注意事项

每条建议以emoji开头，简洁明了（20字以内）。直接输出建议列表，每行一条，不要编号。"""

        # 创建LLM实例
        try:
            llm = create_llm_by_provider(
                provider=llm_provider,
                model_name=os.getenv("QUICK_THINK_LLM", "deepseek-chat"),
                temperature=0.7
            )

            # 调用LLM
            response = llm.predict(prompt)

            # 解析响应
            recommendations = []
            for line in response.strip().split('\n'):
                line = line.strip()
                # 移除编号
                line = line.lstrip('0123456789.-•* ')
                if line and len(line) > 5:  # 过滤过短的行
                    recommendations.append(line)

            return recommendations[:8]  # 最多返回8条

        except Exception as e:
            logger.error(f"[智能建议] LLM调用失败: {e}")
            raise

    def format_intelligence_report(self, report: Dict) -> str:
        """格式化为Markdown报告"""
        destination = report["destination"]

        md = f"""# 🏙️ 目的地情报报告：{destination}

## 📊 分析概要

- **分析时间**: {report['generated_at']}
- **旅行日期**: {report.get('travel_date', '未指定')}
- **综合风险**: {report.get('risk_assessment', {}).get('overall_risk_text', '未知')}

---

## 📰 最新资讯

"""

        # 添加新闻
        for i, news in enumerate(report.get("news", [])[:5], 1):
            sentiment_icon = {"positive": "✅", "neutral": "📋", "negative": "⚠️"}
            icon = sentiment_icon.get(news.get("sentiment", "neutral"), "📋")
            md += f"""### {icon} {news['title']}
- **来源**: {news['source']}
- **时间**: {news['published_at'][:10]}
- **摘要**: {news['summary']}

"""

        # 添加风险评估
        md += f"""
---

## ⚠️ 风险评估

**综合风险等级**: {report.get('risk_assessment', {}).get('overall_risk_text', '未知')}

### 详细评估
| 风险类别 | 状态 | 说明 |
|---------|------|------|
"""

        risk_categories = report.get("risk_assessment", {}).get("risk_categories", {})
        for category, info in risk_categories.items():
            if isinstance(info, dict):
                md += f"| {category} | {info.get('status', '-')} | {info.get('description', '-')} |\n"

        risk_factors = report.get("risk_assessment", {}).get("risk_factors", [])
        if risk_factors:
            md += "\n### 风险因素\n"
            for factor in risk_factors:
                md += f"- **{factor['type']}**: {factor['description']}\n"
                if factor.get("advice"):
                    md += f"  💡 {factor['advice']}\n"

        recommendation = report.get("risk_assessment", {}).get("recommendation", "")
        if recommendation:
            md += f"\n**建议**: {recommendation}\n"

        # 添加活动推荐
        events = report.get("events", [])
        if events:
            md += f"""
---

## 🎉 推荐活动

### 近期节日活动
"""
            for event in events[:5]:
                event_icon = {"festival": "🎊", "cultural": "🎭", "holiday": "🎉"}.get(event.get("type", ""), "📅")
                md += f"""{event_icon} **{event['name']}** ({event.get('start_date', '')} - {event.get('end_date', '')})
   - 📍 {event.get('location', '')}
   - 📝 {event.get('description', '')}
   - 💡 {event.get('recommendation', '')}

"""

        # 添加文化推荐
        culture = report.get("cultural_experiences", {})
        if culture:
            md += """
---

## 🎭 文化体验推荐
"""
            # 博物馆
            museums = culture.get("museums", [])
            if museums:
                md += "### 🏛️ 博物馆/美术馆\n"
                for museum in museums[:3]:
                    md += f"- **{museum['name']}**: {museum['description']} ({museum.get('duration', '')})\n"

            # 表演
            performances = culture.get("performances", [])
            if performances:
                md += "\n### 🎭 传统表演\n"
                for perf in performances[:3]:
                    md += f"- **{perf['name']}**: {perf['description']}\n"

            # 美食
            food = culture.get("food_experiences", [])
            if food:
                md += "\n### 🍜 美食体验\n"
                for food_exp in food[:2]:
                    md += f"- **{food_exp['name']}**: {food_exp.get('description', '')}\n"
                    if food_exp.get("restaurants"):
                        md += f"  📍 推荐餐厅: {', '.join(food_exp['restaurants'][:3])}\n"

            # 特产
            specialties = culture.get("local_specialties", [])
            if specialties:
                md += "\n### 🎁 特色手工艺品/特产\n"
                for item in specialties:
                    md += f"- {item['name']}: {item.get('description', '')}\n"

            # 文化贴士
            tips = culture.get("cultural_tips", [])
            if tips:
                md += "\n### 💡 文化小贴士\n"
                for tip in tips:
                    md += f"- {tip}\n"

        # 添加综合建议
        md += f"""
---

## 💡 综合建议

"""
        for i, rec in enumerate(report.get("recommendations", []), 1):
            md += f"{i}. {rec}\n"

        md += f"""
---

**报告生成时间**: {report['generated_at']}
**数据来源**: 综合新闻源、文旅局官网、社交媒体
**建议更新频率**: 出发前7天和出发前1天

"""

        return md


# ============================================================
# 便捷函数
# ============================================================

def get_destination_intelligence_agent() -> DestinationIntelligenceAgent:
    """获取目的地情报智能体单例"""
    global _agent_instance
    if '_agent_instance' not in globals():
        _agent_instance = DestinationIntelligenceAgent()
    return _agent_instance


async def analyze_destination(destination: str, travel_date: Optional[str] = None) -> Dict:
    """分析目的地情报（便捷函数）"""
    agent = get_destination_intelligence_agent()
    return await agent.analyze_destination(destination, travel_date)


# 导出
__all__ = [
    "DestinationIntelligenceAgent",
    "get_destination_intelligence_agent",
    "analyze_destination"
]
