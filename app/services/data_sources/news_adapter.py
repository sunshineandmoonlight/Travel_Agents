"""
新闻数据适配器

支持多个新闻数据源的统一接口：
- 天行数据 (推荐) - 支持综合新闻、文旅新闻、地区新闻
- 聚合数据
- SerpApi (百度新闻)
- 模拟数据 (默认)
"""
import os
import asyncio
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class NewsAdapter:
    """新闻数据适配器"""

    # 天行数据API端点配置
    TIANAPI_ENDPOINTS = {
        "travel": "https://apis.tianapi.com/travel/index",        # 文旅新闻（主要接口）
        "general": "http://api.tianapi.com/generalnews/index",    # 综合新闻（备用）
        "regional": "http://api.tianapi.com/areanews/index",       # 地区新闻（备用）
    }

    def __init__(self, source: Optional[str] = None):
        """
        初始化新闻适配器

        Args:
            source: 数据源类型 (tianapi/serpapi/juhe/mock)
                   默认从环境变量 NEWS_SOURCE 读取，如果未设置则使用 mock
        """
        self.source = source or os.getenv("NEWS_SOURCE", "mock")
        self.api_key = self._get_api_key()

        logger.info(f"[新闻适配器] 使用数据源: {self.source}")

    def _get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        if self.source == "tianapi":
            return os.getenv("TIANAPI_KEY")
        elif self.source == "serpapi":
            return os.getenv("SERPAPI_KEY")
        elif self.source == "juhe":
            return os.getenv("JUHE_API_KEY")
        return None

    async def search_news(
        self,
        keyword: str,
        days: int = 7,
        num: int = 10
    ) -> List[Dict]:
        """
        搜索新闻

        Args:
            keyword: 搜索关键词
            days: 搜索最近几天的新闻
            num: 返回数量

        Returns:
            新闻列表
        """
        try:
            if self.source == "tianapi":
                return await self._search_tianapi(keyword, days, num)
            elif self.source == "serpapi":
                return await self._search_serpapi(keyword, days, num)
            elif self.source == "juhe":
                return await self._search_juhe(keyword, days, num)
            else:
                return await self._mock_news(keyword, days)

        except Exception as e:
            logger.error(f"[新闻适配器] 搜索失败 ({self.source}): {e}")
            # 失败时降级到模拟数据
            return await self._mock_news(keyword, days)

    async def _search_tianapi(
        self,
        keyword: str,
        days: int,
        num: int
    ) -> List[Dict]:
        """
        使用天行数据搜索新闻

        智能选择最合适的接口：
        1. 优先使用文旅新闻（最适合旅行相关）
        2. 其次使用地区新闻（针对特定地区）
        3. 最后使用综合新闻（兜底）
        """
        if not self.api_key:
            logger.warning("[天行数据] API Key未配置，使用模拟数据")
            return await self._mock_news(keyword, days)

        # 提取目的地关键词
        destination = keyword.replace("旅游", "").strip()

        # 按优先级尝试不同的接口
        endpoints_to_try = [
            ("travel", self.TIANAPI_ENDPOINTS["travel"], "文旅新闻"),
            ("regional", self.TIANAPI_ENDPOINTS["regional"], "地区新闻"),
            ("general", self.TIANAPI_ENDPOINTS["general"], "综合新闻")
        ]

        all_news = []
        attempted = []

        for endpoint_type, url, endpoint_name in endpoints_to_try:
            try:
                logger.info(f"[天行数据] 尝试使用 {endpoint_name} 接口...")
                attempted.append(endpoint_name)

                # 构建请求参数
                params = {
                    "key": self.api_key,
                    "num": min(num, 20)  # 每个接口最多获取20条
                }

                # 根据接口类型设置不同的关键词
                if endpoint_type == "travel":
                    # 文旅新闻使用完整关键词
                    params["word"] = keyword
                elif endpoint_type == "regional":
                    # 地区新闻使用 areaname 参数（不是word）
                    params["areaname"] = destination
                    # 地区新闻也可以用word作为检索关键词
                    params["word"] = keyword
                else:
                    # 综合新闻使用完整关键词
                    params["word"] = keyword

                # 使用线程池执行同步请求
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: requests.get(url, params=params, timeout=10)
                )

                data = response.json()

                if data.get("code") == 200:
                    # 天行数据有两种返回格式，需要兼容处理
                    # 1. 文旅新闻接口: result.list
                    # 2. 其他接口: newsList
                    if "result" in data and isinstance(data["result"], dict):
                        news_list = data["result"].get("list", [])
                    else:
                        news_list = data.get("newsList", [])

                    if news_list:
                        logger.info(f"[天行数据] {endpoint_name} 获取到 {len(news_list)} 条新闻")

                        # 处理新闻数据
                        for item in news_list:
                            # 避免重复（根据URL去重）
                            news_url = item.get("url", "")
                            if not any(n.get("url") == news_url for n in all_news):
                                sentiment = self._analyze_sentiment(item.get("title", ""))

                                all_news.append({
                                    "title": item.get("title", ""),
                                    "source": item.get("source", endpoint_name),
                                    "published_at": item.get("ctime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                                    "url": news_url,
                                    "summary": item.get("description", item.get("title", ""))[:150],
                                    "sentiment": sentiment,
                                    "category": self._categorize_news(item.get("title", "")),
                                    "api_source": endpoint_name  # 记录数据来源
                                })

                        # 如果已经获取足够的新闻，停止尝试其他接口
                        if len(all_news) >= num:
                            logger.info(f"[天行数据] 已获取足够新闻，停止尝试其他接口")
                            break
                    else:
                        logger.info(f"[天行数据] {endpoint_name} 无相关数据")
                else:
                    error_msg = data.get('msg', '未知错误')
                    error_code = data.get('code', 'N/A')

                    # 接口未申请的错误代码
                    if error_code == 160:
                        logger.warning(f"[天行数据] {endpoint_name} 未申请，跳过")
                    else:
                        logger.warning(f"[天行数据] {endpoint_name} API错误: {error_msg} (code: {error_code})")

            except Exception as e:
                logger.error(f"[天行数据] {endpoint_name} 请求失败: {e}")
                continue

        # 如果所有接口都失败或没有数据，使用模拟数据
        if not all_news:
            logger.warning(f"[天行数据] 所有接口都未获取到数据 (已尝试: {', '.join(attempted)})，使用模拟数据")
            return await self._mock_news(keyword, days)

        logger.info(f"[天行数据] 总共获取到 {len(all_news)} 条新闻 (来源: {', '.join(set(n.get('api_source', '未知') for n in all_news))})")

        # 按发布时间排序，返回最新的num条
        all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        return all_news[:num]

    async def _search_serpapi(
        self,
        keyword: str,
        days: int,
        num: int
    ) -> List[Dict]:
        """使用SerpApi搜索百度新闻"""
        if not self.api_key:
            logger.warning("[SerpApi] API Key未配置，使用模拟数据")
            return await self._mock_news(keyword, days)

        try:
            # 需要先安装: pip install google-search-results
            from serpapi import GoogleSearch

            params = {
                "engine": "baidu_news",
                "q": keyword,
                "num": num,
                "api_key": self.api_key
            }

            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: GoogleSearch(params).get_dict()
            )

            news_list = []
            for item in results.get("news_results", [])[:num]:
                sentiment = self._analyze_sentiment(item.get("title", ""))

                news_list.append({
                    "title": item.get("title", ""),
                    "source": item.get("source", "百度新闻"),
                    "published_at": item.get("date", datetime.now().strftime("%Y-%m-%d")),
                    "url": item.get("link", ""),
                    "summary": item.get("snippet", item.get("title", ""))[:100],
                    "sentiment": sentiment,
                    "category": self._categorize_news(item.get("title", ""))
                })

            logger.info(f"[SerpApi] 获取到 {len(news_list)} 条新闻")
            return news_list

        except ImportError:
            logger.warning("[SerpApi] 未安装 google-search-results 库")
            return await self._mock_news(keyword, days)
        except Exception as e:
            logger.error(f"[SerpApi] 请求失败: {e}")
            return await self._mock_news(keyword, days)

    async def _search_juhe(
        self,
        keyword: str,
        days: int,
        num: int
    ) -> List[Dict]:
        """使用聚合数据搜索新闻"""
        if not self.api_key:
            logger.warning("[聚合数据] API Key未配置，使用模拟数据")
            return await self._mock_news(keyword, days)

        try:
            url = "http://v.juhe.cn/news/index"
            params = {
                "key": self.api_key,
                "keyword": keyword,
                "page_size": num
            }

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("error_code") == 0:
                news_list = []
                for item in data.get("result", {}).get("data", [])[:num]:
                    sentiment = self._analyze_sentiment(item.get("title", ""))

                    news_list.append({
                        "title": item.get("title", ""),
                        "source": item.get("author_name", "聚合数据"),
                        "published_at": item.get("date", datetime.now().strftime("%Y-%m-%d")),
                        "url": item.get("url", ""),
                        "summary": item.get("title", "")[:100],
                        "sentiment": sentiment,
                        "category": self._categorize_news(item.get("title", ""))
                    })

                logger.info(f"[聚合数据] 获取到 {len(news_list)} 条新闻")
                return news_list
            else:
                logger.warning(f"[聚合数据] API返回错误: {data.get('reason')}")
                return await self._mock_news(keyword, days)

        except Exception as e:
            logger.error(f"[聚合数据] 请求失败: {e}")
            return await self._mock_news(keyword, days)

    async def _mock_news(self, destination: str, days: int) -> List[Dict]:
        """生成模拟新闻数据"""
        logger.info(f"[模拟数据] 生成 {destination} 的模拟新闻")

        now = datetime.now()
        news_list = []

        # 正面新闻
        positive_news = [
            {
                "title": f"{destination}推出新一轮旅游优惠政策",
                "summary": f"{destination}文旅局宣布推出新一轮旅游优惠政策，部分景点门票减免，吸引更多游客",
                "category": "policy"
            },
            {
                "title": f"{destination}新增直达高铁，交通更便利",
                "summary": f"随着新高铁线路的开通，前往{destination}的交通更加便利，从上海出发仅需2小时",
                "category": "transport"
            },
            {
                "title": f"{destination}春季旅游旺季，游客数量稳步增长",
                "summary": f"春季旅游旺季到来，{destination}各景区游客数量稳步增长，旅游市场复苏良好",
                "category": "tourism"
            }
        ]

        # 中性新闻
        neutral_news = [
            {
                "title": f"{destination}天气预报：未来一周晴雨相间",
                "summary": f"气象部门发布{destination}未来一周天气预报，预计晴雨相间，气温适宜",
                "category": "weather"
            },
            {
                "title": f"{destination}举办旅游推介会，展示旅游资源",
                "summary": f"{destination}文旅局在多地举办旅游推介会，向游客展示丰富的旅游资源和特色产品",
                "category": "event"
            }
        ]

        # 生成新闻列表
        for i, news in enumerate(positive_news):
            pub_date = now - timedelta(days=i * 2)
            news_list.append({
                "title": news["title"],
                "source": f"{destination}日报",
                "published_at": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"https://example.com/news/{i}",
                "summary": news["summary"],
                "sentiment": "positive",
                "category": news["category"]
            })

        for i, news in enumerate(neutral_news):
            pub_date = now - timedelta(days=i * 2 + 1)
            news_list.append({
                "title": news["title"],
                "source": f"{destination}新闻网",
                "published_at": pub_date.strftime("%Y-%m-%d %H:%M:%S"),
                "url": f"https://example.com/news/{i + 3}",
                "summary": news["summary"],
                "sentiment": "neutral",
                "category": news["category"]
            })

        # 按日期排序
        news_list.sort(key=lambda x: x["published_at"], reverse=True)
        return news_list[:days]

    def _analyze_sentiment(self, text: str) -> str:
        """分析新闻情感"""
        positive_keywords = ["优惠", "新增", "增长", "推荐", "开放", "成功", "提升", "改善"]
        negative_keywords = ["取消", "暂停", "关闭", "预警", "风险", "事故", "禁止", "限制"]

        text_lower = text.lower()

        for keyword in negative_keywords:
            if keyword in text_lower:
                return "negative"

        for keyword in positive_keywords:
            if keyword in text_lower:
                return "positive"

        return "neutral"

    def _categorize_news(self, title: str) -> str:
        """对新闻进行分类"""
        category_keywords = {
            "safety": ["安全", "事故", "风险", "封闭", "禁止"],  # 放在前面优先匹配
            "policy": ["政策", "优惠", "措施", "发布"],
            "transport": ["交通", "高铁", "航班", "地铁", "公交"],
            "weather": ["天气", "气温", "降雨", "台风", "预警"],
            "tourism": ["旅游", "游客", "景区", "景点", "酒店"],
            "event": ["活动", "节庆", "展览", "演出", "节日"]
        }

        title_lower = title.lower()
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category

        return "general"


# ============================================================
# 便捷函数
# ============================================================

_default_adapter: Optional[NewsAdapter] = None


def get_news_adapter() -> NewsAdapter:
    """获取新闻适配器单例"""
    global _default_adapter
    if _default_adapter is None:
        _default_adapter = NewsAdapter()
    return _default_adapter


async def search_destination_news(
    destination: str,
    days: int = 7,
    num: int = 10
) -> List[Dict]:
    """
    搜索目的地新闻

    Args:
        destination: 目的地名称
        days: 搜索最近几天
        num: 返回数量

    Returns:
        新闻列表
    """
    adapter = get_news_adapter()
    return await adapter.search_news(f"{destination} 旅游", days, num)
