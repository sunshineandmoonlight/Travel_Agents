"""
目的地情报服务

整合多个真实API获取目的地信息：
- 天行数据: 文旅新闻
- ExchangeRate-API: 实时汇率
- OpenWeatherMap: 天气预报
- SerpAPI: Google搜索结果
- 高德地图: 国内景点信息
"""

import os
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

# LLM导入（用于智能建议生成）
try:
    from tradingagents.graph.trading_graph import create_llm_by_provider
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    logger.warning("[目的地情报] LLM功能不可用，将使用规则生成建议")


class DestinationIntelligenceService:
    """目的地情报服务 - 整合真实API"""

    def __init__(self):
        """初始化服务"""
        # API配置
        self.tianapi_key = os.getenv("TIANAPI_KEY", "")
        self.exchangerate_key = os.getenv("EXCHANGERATE_API_KEY", "86894aac3ce5084f3afc7068")
        self.amap_key = os.getenv("AMAP_API_KEY", "0f52326f698fc89f3bc0941c3bb113ec")
        self.serpapi_key = os.getenv("SERPAPI_KEY", "dd5682943bc32a9ac9a83ef9772ec819b8aa1f3f74e418f960a4715ae18b2d6e")

        # 货币代码映射
        self.destination_currency_map = {
            "日本": "JPY",
            "韩国": "KRW",
            "泰国": "THB",
            "新加坡": "SGD",
            "马来西亚": "MYR",
            "越南": "VND",
            "柬埔寨": "KHR",
            "印尼": "IDR",
            "菲律宾": "PHP",
            "美国": "USD",
            "英国": "GBP",
            "法国": "EUR",
            "意大利": "EUR",
            "澳大利亚": "AUD",
            "新西兰": "NZD",
        }

        # 城市坐标映射（用于天气API）
        self.city_coordinates = {
            "北京": {"lat": 39.9042, "lon": 116.4074},
            "上海": {"lat": 31.2304, "lon": 121.4737},
            "广州": {"lat": 23.1291, "lon": 113.2644},
            "深圳": {"lat": 22.5431, "lon": 114.0579},
            "杭州": {"lat": 30.2741, "lon": 120.1551},
            "成都": {"lat": 30.5728, "lon": 104.0668},
            "西安": {"lat": 34.3416, "lon": 108.9398},
            "厦门": {"lat": 24.4798, "lon": 118.0894},
            "三亚": {"lat": 18.2524, "lon": 109.5119},
            "重庆": {"lat": 29.4316, "lon": 106.9123},
            "南京": {"lat": 32.0603, "lon": 118.7969},
            "苏州": {"lat": 31.2989, "lon": 120.5853},
            "武汉": {"lat": 30.5928, "lon": 114.3055},
            "长沙": {"lat": 28.2282, "lon": 112.9388},
            "青岛": {"lat": 36.0671, "lon": 120.3826},
            "大连": {"lat": 38.9140, "lon": 121.6147},
            "桂林": {"lat": 25.2742, "lon": 110.2901},
            "丽江": {"lat": 26.8556, "lon": 100.2271},
            "拉萨": {"lat": 29.6500, "lon": 91.1000},
        }

    async def get_intelligence(
        self,
        destination: str,
        travel_date: Optional[str] = None
    ) -> Dict:
        """
        获取目的地完整情报

        Args:
            destination: 目的地名称
            travel_date: 旅行日期（YYYY-MM-DD）

        Returns:
            完整情报数据
        """
        logger.info(f"[目的地情报] 开始获取 {destination} 的情报...")

        # 并发获取所有信息
        tasks = [
            self._get_news(destination),
            self._get_weather(destination),
            self._get_exchange_rate(destination),
            self._get_attractions(destination),
            self._get_risk_assessment(destination),
        ]

        try:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            intelligence = {
                "destination": destination,
                "generated_at": datetime.now().isoformat(),
                "travel_date": travel_date,
                "news": results[0] if not isinstance(results[0], Exception) else [],
                "weather": results[1] if not isinstance(results[1], Exception) else {},
                "exchange_rate": results[2] if not isinstance(results[2], Exception) else {},
                "attractions": results[3] if not isinstance(results[3], Exception) else [],
                "risk_assessment": results[4] if not isinstance(results[4], Exception) else {},
            }

            # 生成智能建议
            intelligence["recommendations"] = self._generate_recommendations(intelligence)

            logger.info(f"[目的地情报] {destination} 情报获取完成")
            return intelligence

        except Exception as e:
            logger.error(f"[目的地情报] 获取失败: {e}")
            raise

    async def _get_news(self, destination: str) -> List[Dict]:
        """获取新闻信息"""
        try:
            # 使用天行数据API
            if self.tianapi_key:
                return await self._fetch_tianapi_news(destination)
            else:
                # 降级到模拟数据
                return self._mock_news(destination)
        except Exception as e:
            logger.error(f"[新闻获取] 失败: {e}")
            return self._mock_news(destination)

    async def _fetch_tianapi_news(self, destination: str) -> List[Dict]:
        """使用天行数据获取新闻 - 旅游新闻专用接口"""
        # 使用旅游新闻专用接口 https://apis.tianapi.com/travel/index
        url = "https://apis.tianapi.com/travel/index"
        params = {
            "key": self.tianapi_key,
            "num": 10,  # 必需参数
            "form": 1,  # 兼容历史问题，建议传1
            "word": destination  # 搜索关键词
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("code") == 200:
                # 旅游新闻接口返回字段是 newslist
                news_list = data.get("result", {}).get("newslist", [])

                if news_list:
                    return [
                        {
                            "title": item.get("title", ""),
                            "source": item.get("source", "旅游资讯"),
                            "published_at": item.get("ctime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            "url": item.get("url", ""),
                            "summary": item.get("description", "")[:150],
                            "picUrl": item.get("picUrl", ""),
                            "sentiment": self._analyze_sentiment(item.get("title", "")),
                            "category": self._categorize_news(item.get("title", ""))
                        }
                        for item in news_list
                    ]
                else:
                    logger.warning(f"[天行数据] 无相关新闻: {destination}")
                    return self._mock_news(destination)
            else:
                logger.warning(f"[天行数据] API错误 (code={data.get('code')}): {data.get('msg')}")
                return self._mock_news(destination)

        except Exception as e:
            logger.error(f"[天行数据] 请求失败: {e}")
            return self._mock_news(destination)

    async def _fetch_travel_news(self, destination: str, num: int = 10) -> List[Dict]:
        """获取旅游新闻 - 旅游专用接口"""
        # 如果没有API key，直接返回模拟数据
        if not self.tianapi_key:
            logger.info(f"[旅游新闻] 未配置TIANAPI_KEY，使用模拟数据")
            return self._mock_news_for_type(destination, "travel", num)

        url = "https://apis.tianapi.com/travel/index"
        params = {
            "key": self.tianapi_key,
            "num": num,
            "word": destination
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("code") == 200:
                # 旅游新闻接口返回字段是 newslist
                news_list = data.get("result", {}).get("newslist", [])
                logger.info(f"[旅游新闻] 获取到 {len(news_list)} 条新闻")
                return [
                    {
                        "title": item.get("title", ""),
                        "source": item.get("source", "旅游资讯"),
                        "published_at": item.get("ctime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "url": item.get("url", ""),
                        "summary": item.get("description", "")[:150],
                        "picUrl": item.get("picUrl", ""),
                        "sentiment": self._analyze_sentiment(item.get("title", "")),
                        "category": "tourism"
                    }
                    for item in news_list
                ]
            else:
                logger.warning(f"[旅游新闻] API错误 (code={data.get('code')}): {data.get('msg')}")
                return self._mock_news_for_type(destination, "travel", num)

        except Exception as e:
            logger.error(f"[旅游新闻] 请求失败: {e}")
            return self._mock_news_for_type(destination, "travel", num)

    async def _fetch_area_news(self, destination: str, num: int = 10) -> List[Dict]:
        """获取地区新闻 - 地区新闻接口"""
        # 如果没有API key，直接返回模拟数据
        if not self.tianapi_key:
            logger.info(f"[地区新闻] 未配置TIANAPI_KEY，使用模拟数据")
            return self._mock_news_for_type(destination, "area", num)

        # 映射城市到省份/地区
        area_mapping = {
            "北京": "北京", "上海": "上海", "天津": "天津", "重庆": "重庆",
            "杭州": "浙江", "宁波": "浙江", "温州": "浙江",
            "南京": "江苏", "苏州": "江苏", "无锡": "江苏",
            "广州": "广东", "深圳": "广东", "佛山": "广东", "东莞": "广东",
            "成都": "四川", "绵阳": "四川",
            "武汉": "湖北", "宜昌": "湖北",
            "西安": "陕西", "咸阳": "陕西",
            "长沙": "湖南", "株洲": "湖南",
            "郑州": "河南", "洛阳": "河南",
            "济南": "山东", "青岛": "山东",
            "沈阳": "辽宁", "大连": "辽宁",
            "哈尔滨": "黑龙江", "大庆": "黑龙江",
            "长春": "吉林", "吉林": "吉林",
            "石家庄": "河北", "唐山": "河北",
            "合肥": "安徽", "芜湖": "安徽",
            "福州": "福建", "厦门": "福建", "泉州": "福建",
            "南昌": "江西", "九江": "江西",
            "昆明": "云南", "丽江": "云南", "大理": "云南",
            "贵阳": "贵州", "遵义": "贵州",
            "兰州": "甘肃",
            "西宁": "青海",
            "南宁": "广西", "桂林": "广西",
            "海口": "海南", "三亚": "海南",
            "呼和浩特": "内蒙古",
            "银川": "宁夏",
            "乌鲁木齐": "新疆",
            "拉萨": "西藏"
        }

        # 获取地区名
        area_name = area_mapping.get(destination, destination)

        url = "https://apis.tianapi.com/areanews/index"
        params = {
            "key": self.tianapi_key,
            "areaname": area_name,
            "page": 1
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("code") == 200:
                news_list = data.get("result", {}).get("list", [])
                logger.info(f"[地区新闻] 获取到 {len(news_list)} 条新闻")
                return [
                    {
                        "title": item.get("title", ""),
                        "source": item.get("source", "地区新闻"),
                        "published_at": item.get("ctime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "url": item.get("url", ""),
                        "summary": item.get("description", "")[:150] or item.get("title", ""),
                        "picUrl": item.get("picUrl", ""),
                        "sentiment": self._analyze_sentiment(item.get("title", "")),
                        "category": "local"
                    }
                    for item in news_list
                ]
            else:
                logger.warning(f"[地区新闻] API错误 (code={data.get('code')}): {data.get('msg')}")
                return self._mock_news_for_type(destination, "area", num)

        except Exception as e:
            logger.error(f"[地区新闻] 请求失败: {e}")
            return self._mock_news_for_type(destination, "area", num)

    async def _fetch_general_news(self, destination: str, num: int = 10) -> List[Dict]:
        """获取综合新闻 - 综合新闻接口"""
        # 如果没有API key，直接返回模拟数据
        if not self.tianapi_key:
            logger.info(f"[综合新闻] 未配置TIANAPI_KEY，使用模拟数据")
            return self._mock_news_for_type(destination, "general", num)

        url = "https://apis.tianapi.com/generalnews/index"
        params = {
            "key": self.tianapi_key,
            "word": destination,
            "page": 1
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("code") == 200:
                # 综合新闻接口返回字段是 newslist
                news_list = data.get("result", {}).get("newslist", [])
                logger.info(f"[综合新闻] 获取到 {len(news_list)} 条新闻")
                return [
                    {
                        "title": item.get("title", ""),
                        "source": item.get("source", "综合新闻"),
                        "published_at": item.get("ctime", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "url": item.get("url", ""),
                        "summary": item.get("description", "")[:150],
                        "picUrl": item.get("picUrl", ""),
                        "sentiment": self._analyze_sentiment(item.get("title", "")),
                        "category": self._categorize_news(item.get("title", ""))
                    }
                    for item in news_list
                ]
            else:
                logger.warning(f"[综合新闻] API错误 (code={data.get('code')}): {data.get('msg')}")
                return self._mock_news_for_type(destination, "general", num)

        except Exception as e:
            logger.error(f"[综合新闻] 请求失败: {e}")
            return self._mock_news_for_type(destination, "general", num)

    async def _get_weather(self, destination: str) -> Dict:
        """获取天气信息"""
        # 使用高德天气API
        if destination in self.city_coordinates and self.amap_key:
            return await self._fetch_amap_weather(destination)
        else:
            # 模拟天气数据
            return self._mock_weather(destination)

    async def _fetch_amap_weather(self, city: str) -> Dict:
        """使用高德地图获取天气"""
        coords = self.city_coordinates[city]
        url = "https://restapi.amap.com/v3/weather/weatherInfo"

        params = {
            "key": self.amap_key,
            "city": city,
            "extensions": "all"  # 获取预报天气
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("status") == "1" and data.get("forecasts"):
                forecast = data["forecasts"][0]
                casts = forecast.get("casts", [])

                # 今天和明天的天气
                today = casts[0] if len(casts) > 0 else {}
                tomorrow = casts[1] if len(casts) > 1 else {}

                return {
                    "city": city,
                    "current": {
                        "temperature": f"{today.get('daytemp', '25')}°C",
                        "weather": today.get('dayweather', '晴'),
                        "wind": today.get('daywind', '微风'),
                        "humidity": "65%"
                    },
                    "forecast": [
                        {
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "day_temp": f"{today.get('daytemp', '25')}°C",
                            "night_temp": f"{today.get('nighttemp', '18')}°C",
                            "weather": today.get('dayweather', '晴'),
                            "week": self._get_weekday(datetime.now().weekday())
                        },
                        {
                            "date": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                            "day_temp": f"{tomorrow.get('daytemp', '26')}°C",
                            "night_temp": f"{tomorrow.get('nighttemp', '19')}°C",
                            "weather": tomorrow.get('dayweather', '多云'),
                            "week": self._get_weekday((datetime.now().weekday() + 1) % 7)
                        }
                    ],
                    "tips": self._generate_weather_tips(today.get('dayweather', '晴'))
                }

            else:
                return self._mock_weather(city)

        except Exception as e:
            logger.error(f"[高德天气] 请求失败: {e}")
            return self._mock_weather(city)

    async def _get_exchange_rate(self, destination: str) -> Dict:
        """获取汇率信息"""
        # 查找对应的货币
        currency = None
        for country, curr in self.destination_currency_map.items():
            if country in destination:
                currency = curr
                break

        if not currency:
            # 尝试直接匹配
            for country, curr in self.destination_currency_map.items():
                if destination in country:
                    currency = curr
                    break

        if not currency:
            return {"available": False, "reason": "未找到对应货币"}

        # 调用ExchangeRate-API
        try:
            url = f"https://v6.exchangerate-api.com/v6/{self.exchangerate_key}/latest/CNY"
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, timeout=10)
            )

            data = response.json()

            if data.get("result") == "success":
                rate = data.get("conversion_rates", {}).get(currency, 0)

                if rate > 0:
                    return {
                        "available": True,
                        "from": "CNY",
                        "to": currency,
                        "rate": rate,
                        "inverse": round(1 / rate, 4),
                        "example": f"1 CNY = {rate:.2f} {currency}",
                        "updated": data.get("time_last_update_unix", 0)
                    }
                else:
                    return {"available": False, "reason": "货币不支持"}
            else:
                return {"available": False, "reason": "API错误"}

        except Exception as e:
            logger.error(f"[汇率获取] 失败: {e}")
            return {"available": False, "reason": str(e)}

    async def _get_attractions(self, destination: str) -> List[Dict]:
        """获取景点信息"""
        try:
            # 使用SerpAPI搜索景点
            if self.serpapi_key:
                return await self._fetch_serpapi_attractions(destination)
            else:
                return self._mock_attractions(destination)
        except Exception as e:
            logger.error(f"[景点获取] 失败: {e}")
            return self._mock_attractions(destination)

    async def _fetch_serpapi_attractions(self, destination: str) -> List[Dict]:
        """使用SerpAPI获取景点"""
        url = "https://serpapi.com/search"
        params = {
            "engine": "google_local",
            "q": f"{destination} 景点",  # 使用中文搜索词
            "api_key": self.serpapi_key,
            "num": 10,
            "hl": "zh-CN"  # 设置语言为中文
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=15)
            )

            data = response.json()

            if "local_results" in data:
                attractions = []
                for place in data["local_results"][:10]:
                    name = place.get("title", "")
                    # 中文名称映射
                    name = self._translate_attraction_name(name)

                    attractions.append({
                        "name": name,
                        "rating": place.get("rating", 0),
                        "reviews": place.get("reviews", 0),
                        "address": place.get("address", ""),
                        "phone": place.get("phone", ""),
                        "description": place.get("description", ""),
                        "thumbnail": place.get("thumbnail", "")
                    })

                return attractions
            else:
                # 如果SerpAPI没有结果，尝试使用高德地图POI搜索
                return await self._fetch_amap_attractions(destination)

        except Exception as e:
            logger.error(f"[SerpAPI景点] 请求失败: {e}")
            # 降级到高德地图搜索
            return await self._fetch_amap_attractions(destination)

    async def _fetch_amap_attractions(self, destination: str) -> List[Dict]:
        """使用高德地图POI搜索获取中文景点"""
        url = "https://restapi.amap.com/v5/place/text"
        params = {
            "key": self.amap_key,
            "keywords": "旅游景点",
            "city": destination,
            "citylimit": True,
            "show_fields": "business,name,photos,rating,review_num,address,tel",
            "page_size": 10
        }

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: requests.get(url, params=params, timeout=10)
            )

            data = response.json()

            if data.get("status") == "1" and data.get("pois"):
                attractions = []
                for poi in data["pois"][:10]:
                    name = poi.get("name", "")

                    attractions.append({
                        "name": name,
                        "rating": float(poi.get("biz_ext", {}).get("rating", "0") or 0),
                        "reviews": int(poi.get("biz_ext", {}).get("review_num", "0") or 0),
                        "address": poi.get("address", "") or poi.get("pname", ""),
                        "phone": poi.get("tel", ""),
                        "description": "",
                        "thumbnail": ""
                    })

                return attractions
            else:
                return self._mock_attractions(destination)

        except Exception as e:
            logger.error(f"[高德景点] 请求失败: {e}")
            return self._mock_attractions(destination)

    def _translate_attraction_name(self, name: str) -> str:
        """翻译景点名称为中文"""
        # 常见景点中英文映射
        attraction_translations = {
            # 杭州
            "Lingyin Temple": "灵隐寺",
            "Lingyin Temple (Lingyin Temple)": "灵隐寺",
            "Hangzhou Botanical Garden": "杭州植物园",
            "Xixi National Wetland Park": "西溪国家湿地公园",
            "Leifeng Pagoda": "雷峰塔",
            "West Lake (Xi Hu)": "西湖",
            "Hefang Street": "河坊街",
            "Qinghefang Ancient Street": "清河坊古街",
            "Yue Fei Temple": "岳王庙",
            "Six Harmonies Pagoda": "六和塔",
            "Broken Bridge": "断桥",
            "Su Causeway": "苏堤",
            "Bai Causeway": "白堤",
            # 北京
            "Forbidden City": "故宫博物院",
            "Temple of Heaven": "天坛",
            "Summer Palace": "颐和园",
            "Great Wall": "长城",
            "Tiananmen Square": "天安门广场",
            "Yuanmingyuan": "圆明园",
            "Beihai Park": "北海公园",
            "Jingshan Park": "景山公园",
            "Hutong": "胡同",
            # 成都
            "Chengdu Research Base of Giant Panda Breeding": "成都大熊猫繁育研究基地",
            "Jinli Ancient Street": "锦里古街",
            "Wuhou Memorial Temple": "武侯祠",
            "Dujiangyan": "都江堰",
            "Kuanzhai Alley": "宽窄巷子",
            "Qingyang Taoist Temple": "青羊宫",
            # 西安
            "Terracotta Army": "兵马俑",
            "Ancient City Wall": "古城墙",
            "Big Wild Goose Pagoda": "大雁塔",
            "Small Wild Goose Pagoda": "小雁塔",
            "Bell Tower": "钟楼",
            "Drum Tower": "鼓楼",
            "Muslim Quarter": "回民街",
            # 上海
            "Yu Garden": "豫园",
            "The Bund": "外滩",
            "Oriental Pearl Tower": "东方明珠塔",
            "Shanghai Disney Resort": "上海迪士尼度假区",
            # 三亚
            "Yalong Bay": "亚龙湾",
            "Sanya Bay": "三亚湾",
            "Wuzhizhou Island": "蜈支洲岛",
            "Nanwan Monkey Island": "南湾猴岛",
            "Tianyahajiao": "天涯海角",
            # 厦门
            "Gulangyu Island": "鼓浪屿",
            "Nanputuo Temple": "南普陀寺",
            "Xiamen University": "厦门大学",
            "Zhongshan Road": "中山路",
            # 日本
            "Senso-ji Temple": "浅草寺",
            "Meiji Shrine": "明治神宫",
            "Tokyo Tower": "东京塔",
            "Shibuya Crossing": "涩谷十字路口",
            "Sensoji": "浅草寺",
            "Fushimi Inari Shrine": "伏见稻荷大社",
            "Kinkaku-ji": "金阁寺",
            "Kiyomizu-dera": "清水寺",
            # 泰国
            "Grand Palace": "大皇宫",
            "Wat Phra Kaew": "翡翠佛寺",
            "Wat Pho": "卧佛寺",
            "Wat Arun": "黎明寺",
            "Chao Phraya River": "湄南河",
            "Khao San Road": "考山路",
            # 新加坡
            "Marina Bay Sands": "滨海湾金沙",
            "Gardens by the Bay": "滨海湾花园",
            "Merlion Park": "鱼尾狮公园",
            "Sentosa Island": "圣淘沙岛",
            "Universal Studios Singapore": "新加坡环球影城",
        }

        # 如果有映射，返回中文名；否则返回原名称
        return attraction_translations.get(name, name)

    async def _get_risk_assessment(self, destination: str) -> Dict:
        """获取风险评估"""
        # 基于目的地进行风险评估
        # 这里可以集成真实的风险API，如 Travel Advisory API

        # 国内目的地通常安全
        domestic_destinations = ["北京", "上海", "广州", "深圳", "杭州", "成都", "西安", "厦门", "三亚"]

        if destination in domestic_destinations:
            return {
                "overall_risk_text": "低风险 - 可以放心前往",
                "risk_level": 1,
                "recommendation": f"{destination}治安状况良好，适宜旅行。建议关注天气变化，做好出行准备。",
                "risk_categories": {
                    "political": {"status": "safe", "description": "政治环境稳定"},
                    "safety": {"status": "safe", "description": "治安状况良好"},
                    "health": {"status": "safe", "description": "无特殊健康风险"},
                    "natural": {"status": "safe", "description": "无极端天气预警"},
                    "social": {"status": "safe", "description": "社会秩序良好"}
                }
            }
        else:
            # 国际目的地默认中等风险
            return {
                "overall_risk_text": "中等风险 - 建议关注旅行提醒",
                "risk_level": 2,
                "recommendation": f"{destination}总体安全，建议关注当地新闻和天气变化。出行前购买旅游保险。",
                "risk_categories": {
                    "political": {"status": "attention", "description": "关注当地政治动态"},
                    "safety": {"status": "safe", "description": "常规安全注意事项"},
                    "health": {"status": "attention", "description": "注意饮食卫生"},
                    "natural": {"status": "safe", "description": "关注天气预报"},
                    "social": {"status": "safe", "description": "社会秩序正常"}
                }
            }

    def _generate_recommendations(self, intelligence: Dict) -> List[str]:
        """生成智能建议 - 使用LLM生成动态建议"""
        import os

        # 检查是否应该使用LLM
        use_llm = os.getenv("USE_LLM_FOR_RECOMMENDATIONS", "true").lower() == "true"
        llm_provider = os.getenv("LLM_PROVIDER", "deepseek")

        if use_llm:
            try:
                # 尝试使用LLM生成个性化建议
                return self._generate_llm_recommendations(intelligence, llm_provider)
            except Exception as e:
                logger.warning(f"[智能建议] LLM生成失败，使用规则生成: {e}")

        # 回退到规则生成
        recommendations = []

        # 基于天气的建议
        weather = intelligence.get("weather", {})
        destination = intelligence.get("destination", "")
        if weather.get("current"):
            weather_desc = weather["current"].get("weather", "")
            if "雨" in weather_desc:
                recommendations.append("☔ 携带雨具，建议安排室内活动")
            elif "晴" in weather_desc:
                recommendations.append("☀️ 天气晴好，适合户外活动和拍照")

        # 基于汇率的建议
        exchange = intelligence.get("exchange_rate", {})
        if exchange.get("available"):
            currency = exchange.get("to", "")
            recommendations.append(f"💱 关注汇率变化，建议提前兑换少量{currency}现金")

        # 基于风险的建议
        risk = intelligence.get("risk_assessment", {})
        risk_level = risk.get("risk_level", 1)
        if risk_level > 2:
            recommendations.append("🛡️ 建议购买包含医疗援助的旅游保险")
        else:
            recommendations.append("🏥 建议购买基础旅游保险")

        # 基于景点的建议
        attractions = intelligence.get("attractions", [])
        if attractions:
            top_attractions = [a["name"] for a in attractions[:3]]
            recommendations.append(f"🎯 热门景点: {', '.join(top_attractions)}")

        # 基于新闻的建议
        news = intelligence.get("news", [])
        positive_news = [n for n in news if n.get("sentiment") == "positive"]
        if positive_news:
            recommendations.append(f"📰 近期有{len(positive_news)}条利好消息")

        # 通用建议
        recommendations.append("📱 提前下载离线地图，准备翻译APP")
        recommendations.append("💊 携带常用药品和充电宝")

        return recommendations

    def _generate_llm_recommendations(self, intelligence: Dict, llm_provider: str) -> List[str]:
        """使用LLM生成个性化建议"""
        # 检查LLM是否可用
        if not LLM_AVAILABLE:
            raise ImportError("LLM功能不可用")

        # 准备上下文信息
        destination = intelligence.get("destination", "")
        weather = intelligence.get("weather", {})
        exchange = intelligence.get("exchange_rate", {})
        risk = intelligence.get("risk_assessment", {})
        attractions = intelligence.get("attractions", [])
        news = intelligence.get("news", [])

        # 构建提示词
        prompt = f"""为前往{destination}旅行生成5-8条智能建议。

目的地: {destination}

天气情况:
- 当前天气: {weather.get('current', {}).get('weather', '未知')}
- 温度: {weather.get('current', {}).get('temperature', '未知')}

风险等级: {risk.get('risk_level', 1)} ({risk.get('overall_risk_text', '')})

热门景点: {', '.join([a['name'] for a in attractions[:5]])}

最新动态: {len(news)}条相关资讯

请根据以上信息生成实用的旅行建议，每条建议要具体、可操作。建议应该涵盖:
1. 天气相关建议 (穿衣、活动安排)
2. 景点游览建议
3. 安全注意事项
4. 实用小贴士 (交通、支付等)

每条建议以emoji开头，简洁明了（15字以内）。直接输出建议列表，每行一条，不要编号。"""

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

    # ============ 辅助方法 ============

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
            "safety": ["安全", "事故", "风险"],
            "policy": ["政策", "优惠", "措施", "发布"],
            "transport": ["交通", "高铁", "航班"],
            "weather": ["天气", "气温", "降雨"],
            "tourism": ["旅游", "游客", "景区"],
            "event": ["活动", "节庆", "展览"]
        }

        title_lower = title.lower()
        for category, keywords in category_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    return category

        return "general"

    def _get_weekday(self, day: int) -> str:
        """获取星期几"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[day]

    def _generate_weather_tips(self, weather: str) -> str:
        """生成天气贴士"""
        tips_map = {
            "晴": "天气晴好，注意防晒，建议携带遮阳帽和太阳镜",
            "多云": "天气舒适，适合户外活动",
            "阴": "天气凉爽，建议携带薄外套",
            "雨": "有雨，记得携带雨具，安排室内景点",
            "雪": "有雪，注意保暖，穿着防滑鞋"
        }

        for key, tip in tips_map.items():
            if key in weather:
                return tip

        return "天气适宜出行，建议关注实时天气变化"

    # ============ 模拟数据（降级方案） ============

    def _mock_news(self, destination: str) -> List[Dict]:
        """模拟新闻数据 - 每个城市有不同内容"""
        now = datetime.now()

        # 英文城市名到中文的映射
        city_name_mapping = {
            "hangzhou": "杭州", "beijing": "北京", "shanghai": "上海",
            "chengdu": "成都", "xian": "西安", "xi'an": "西安",
            "guilin": "桂林", "lijiang": "丽江", "sanya": "三亚",
            "xiamen": "厦门", "kunming": "昆明", "dali": "大理",
            "lhasa": "拉萨", "tokyo": "东京", "kyoto": "京都",
            "osaka": "大阪", "bangkok": "曼谷", "phuket": "普吉岛",
            "singapore": "新加坡", "hanoi": "河内", "ho chi minh": "胡志明市",
            "seoul": "首尔", "busan": "釜山", "jeju": "济州岛"
        }

        # 将英文城市名转换为中文用于匹配
        lookup_destination = city_name_mapping.get(destination.lower(), destination)

        # 城市特色新闻库
        city_news = {
            "杭州": [
                {"title": "西湖景区推出夜游西湖新项目", "category": "tourism", "sentiment": "positive"},
                {"title": "杭州亚运会场馆向公众开放预约", "category": "event", "sentiment": "positive"},
                {"title": "龙井春茶开采，茶文化体验活动开启", "category": "tourism", "sentiment": "positive"},
            ],
            "北京": [
                {"title": "故宫博物院延长开放时间至晚间8点", "category": "policy", "sentiment": "positive"},
                {"title": "环球影城推出春日主题活动", "category": "event", "sentiment": "positive"},
                {"title": "长城景区实施实名预约制", "category": "policy", "sentiment": "neutral"},
            ],
            "成都": [
                {"title": "大熊猫繁育研究基地迎来新生熊猫", "category": "tourism", "sentiment": "positive"},
                {"title": "成都火锅文化节即将开幕", "category": "event", "sentiment": "positive"},
                {"title": "宽窄巷子启动夜间经济示范区", "category": "policy", "sentiment": "positive"},
            ],
            "西安": [
                {"title": "兵马俑景区推出AR导览服务", "category": "tourism", "sentiment": "positive"},
                {"title": "大唐不夜城新增沉浸式演出", "category": "event", "sentiment": "positive"},
                {"title": "古城墙夜游路线优化升级", "category": "policy", "sentiment": "positive"},
            ],
            "上海": [
                {"title": "迪士尼乐园推出春季限定烟花秀", "category": "event", "sentiment": "positive"},
                {"title": "外滩观光隧道升级改造完成", "category": "tourism", "sentiment": "positive"},
                {"title": "上海旅游节活动安排公布", "category": "event", "sentiment": "positive"},
            ],
            "厦门": [
                {"title": "鼓浪屿实施客流管控新措施", "category": "policy", "sentiment": "neutral"},
                {"title": "环岛路骑行道全线贯通", "category": "tourism", "sentiment": "positive"},
                {"title": "曾厝垵文创市集周末开市", "category": "event", "sentiment": "positive"},
            ],
            "三亚": [
                {"title": "海棠湾免税店扩容升级", "category": "tourism", "sentiment": "positive"},
                {"title": "亚龙湾推出水上运动季", "category": "event", "sentiment": "positive"},
                {"title": "蜈支洲岛实施环保新规", "category": "policy", "sentiment": "neutral"},
            ],
            "日本": [
                {"title": "日本放宽部分签证申请条件", "category": "policy", "sentiment": "positive"},
                {"title": "樱花季预测：东京花期提前一周", "category": "tourism", "sentiment": "positive"},
                {"title": "富士山周边新开多条徒步路线", "category": "tourism", "sentiment": "positive"},
            ],
            "泰国": [
                {"title": "泰国延长对中国游客免签政策", "category": "policy", "sentiment": "positive"},
                {"title": "普吉岛新设多个中文服务中心", "category": "tourism", "sentiment": "positive"},
                {"title": "清迈举办泼水节活动预演", "category": "event", "sentiment": "positive"},
            ],
            "新加坡": [
                {"title": "圣淘沙新增游乐设施", "category": "tourism", "sentiment": "positive"},
                {"title": "滨海湾花园推出夜间灯光秀", "category": "event", "sentiment": "positive"},
                {"title": "新加坡调整消费税政策", "category": "policy", "sentiment": "neutral"},
            ],
        }

        # 通用新闻模板（用于没有预设新闻的城市）
        generic_templates = [
            {"title": f"{destination}推出新一轮文旅消费促进活动", "category": "policy", "sentiment": "positive"},
            {"title": f"{destination}新增3A级景区2家", "category": "tourism", "sentiment": "positive"},
            {"title": f"{destination}交通枢纽新增旅游专线", "category": "transport", "sentiment": "positive"},
            {"title": f"{destination}发布年度旅游统计数据", "category": "tourism", "sentiment": "neutral"},
            {"title": f"{destination}举办文化旅游博览会", "category": "event", "sentiment": "positive"},
        ]

        # 获取该城市的新闻
        specific_news = city_news.get(lookup_destination, [])

        # 通用新闻模板（用于没有预设新闻的城市）
        generic_templates = [
            {"title": f"{lookup_destination}推出新一轮文旅消费促进活动", "category": "policy", "sentiment": "positive"},
            {"title": f"{lookup_destination}新增3A级景区2家", "category": "tourism", "sentiment": "positive"},
            {"title": f"{lookup_destination}交通枢纽新增旅游专线", "category": "transport", "sentiment": "positive"},
            {"title": f"{lookup_destination}发布年度旅游统计数据", "category": "tourism", "sentiment": "neutral"},
            {"title": f"{lookup_destination}举办文化旅游博览会", "category": "event", "sentiment": "positive"},
        ]

        all_templates = specific_news + generic_templates

        # 随机选择3-5条新闻
        import random
        selected = random.sample(all_templates, min(len(all_templates), random.randint(3, 5)))

        news_list = []
        for i, item in enumerate(selected):
            hours_ago = random.randint(1, 72)
            news_list.append({
                "title": item["title"],
                "source": random.choice([f"{lookup_destination}文旅局", f"{lookup_destination}新闻网", "文旅中国", "旅游快报"]),
                "published_at": (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S"),
                "url": "#",
                "summary": f"最新消息：{item['title']}"[:80] + "...",
                "sentiment": item["sentiment"],
                "category": item["category"]
            })

        return news_list

    def _mock_news_for_type(self, destination: str, news_type: str, num: int = 10) -> List[Dict]:
        """根据新闻类型生成模拟新闻"""
        import random

        # 英文城市名到中文的映射（与_mock_news保持一致）
        city_name_mapping = {
            "hangzhou": "杭州", "beijing": "北京", "shanghai": "上海",
            "chengdu": "成都", "xian": "西安", "xi'an": "西安",
            "guilin": "桂林", "lijiang": "丽江", "sanya": "三亚",
            "xiamen": "厦门", "kunming": "昆明", "dali": "大理",
            "lhasa": "拉萨", "tokyo": "东京", "kyoto": "京都",
            "osaka": "大阪", "bangkok": "曼谷", "phuket": "普吉岛",
            "singapore": "新加坡", "hanoi": "河内", "ho chi minh": "胡志明市",
            "seoul": "首尔", "busan": "釜山", "jeju": "济州岛"
        }

        # 使用映射后的城市名或原始名称
        display_destination = city_name_mapping.get(destination.lower(), destination)

        # 获取基础模拟新闻
        base_news = self._mock_news(destination)

        # 根据类型调整新闻内容
        if news_type == "travel":
            # 旅游新闻 - 侧重景点、活动
            for item in base_news:
                item["category"] = "tourism"
                item["sentiment"] = "positive"
        elif news_type == "area":
            # 地区新闻 - 侧重本地政策、事件
            for item in base_news:
                item["category"] = random.choice(["policy", "local", "transport"])
                item["sentiment"] = random.choice(["positive", "neutral", "positive"])
        elif news_type == "general":
            # 综合新闻 - 保持原有分类
            pass

        # 确保返回指定数量
        if len(base_news) < num:
            # 补充通用新闻
            generic_news = self._generate_generic_news(display_destination, num - len(base_news), news_type)
            base_news.extend(generic_news)

        return base_news[:num]

    def _generate_generic_news(self, destination: str, count: int, news_type: str) -> List[Dict]:
        """生成通用新闻补充"""
        import random
        now = datetime.now()

        templates = {
            "travel": [
                {"title": f"{destination}春季旅游攻略发布", "category": "tourism", "sentiment": "positive"},
                {"title": f"{destination}文旅部门推出惠民旅游政策", "category": "policy", "sentiment": "positive"},
                {"title": f"{destination}特色民宿预订量上升", "category": "tourism", "sentiment": "positive"},
            ],
            "area": [
                {"title": f"{destination}召开文旅发展大会", "category": "policy", "sentiment": "neutral"},
                {"title": f"{destination}新增公交线路", "category": "transport", "sentiment": "positive"},
                {"title": f"{destination}举办城市文化节", "category": "event", "sentiment": "positive"},
            ],
            "general": [
                {"title": f"{destination}经济持续健康发展", "category": "general", "sentiment": "positive"},
                {"title": f"{destination}城市建设项目进展顺利", "category": "general", "sentiment": "neutral"},
            ]
        }

        news_list = []
        selected_templates = random.sample(templates.get(news_type, templates["general"]), min(count, len(templates.get(news_type, []))))

        for item in selected_templates:
            hours_ago = random.randint(1, 72)
            news_list.append({
                "title": item["title"],
                "source": random.choice([f"{destination}日报", "本地资讯", "新闻中心"]),
                "published_at": (now - timedelta(hours=hours_ago)).strftime("%Y-%m-%d %H:%M:%S"),
                "url": "#",
                "summary": f"{item['title']}"[:80] + "...",
                "sentiment": item["sentiment"],
                "category": item["category"]
            })

        return news_list

    def _mock_weather(self, city: str) -> Dict:
        """模拟天气数据 - 根据城市生成不同天气"""
        import random

        # 城市天气特征
        city_weather = {
            "北京": {"weather": "晴", "temp_range": (12, 22), "humidity": "45%"},
            "上海": {"weather": "多云", "temp_range": (16, 24), "humidity": "70%"},
            "广州": {"weather": "阴", "temp_range": (22, 30), "humidity": "80%"},
            "深圳": {"weather": "多云", "temp_range": (23, 29), "humidity": "75%"},
            "杭州": {"weather": "晴", "temp_range": (15, 24), "humidity": "65%"},
            "成都": {"weather": "阴", "temp_range": (14, 22), "humidity": "70%"},
            "西安": {"weather": "晴", "temp_range": (13, 23), "humidity": "55%"},
            "厦门": {"weather": "多云", "temp_range": (18, 26), "humidity": "72%"},
            "三亚": {"weather": "晴", "temp_range": (24, 32), "humidity": "78%"},
            "重庆": {"weather": "阴", "temp_range": (16, 24), "humidity": "75%"},
            "南京": {"weather": "多云", "temp_range": (15, 23), "humidity": "68%"},
            "苏州": {"weather": "晴", "temp_range": (15, 23), "humidity": "65%"},
        }

        # 国际城市
        international_weather = {
            "日本": {"weather": "多云", "temp_range": (10, 18), "humidity": "60%"},
            "韩国": {"weather": "晴", "temp_range": (8, 16), "humidity": "55%"},
            "泰国": {"weather": "晴", "temp_range": (26, 35), "humidity": "70%"},
            "新加坡": {"weather": "多云", "temp_range": (26, 32), "humidity": "80%"},
            "越南": {"weather": "阴", "temp_range": (24, 32), "humidity": "75%"},
        }

        # 获取天气配置
        weather_config = city_weather.get(city, international_weather.get("日本", {"weather": "晴", "temp_range": (20, 28), "humidity": "65%"}))

        # 生成预报
        weather_types = ["晴", "多云", "阴", "小雨"]
        forecast = []
        for i in range(4):
            date = datetime.now() + timedelta(days=i)
            # 天气有变化
            if i == 0:
                w = weather_config["weather"]
            else:
                w = random.choice(weather_types)

            # 温度波动
            base_temp = random.randint(*weather_config["temp_range"])
            day_temp = f"{base_temp + random.randint(-2, 3)}°C"
            night_temp = f"{base_temp - random.randint(5, 8)}°C"

            forecast.append({
                "date": date.strftime("%Y-%m-%d"),
                "day_temp": day_temp,
                "night_temp": night_temp,
                "weather": w,
                "week": self._get_weekday(date.weekday())
            })

        return {
            "city": city,
            "current": {
                "temperature": f"{random.randint(*weather_config['temp_range'])}°C",
                "weather": weather_config["weather"],
                "wind": random.choice(["东风", "南风", "西风", "北风", "微风"]) + f" {random.randint(1, 4)}级",
                "humidity": weather_config["humidity"]
            },
            "forecast": forecast,
            "tips": self._generate_weather_tips(weather_config["weather"])
        }

    def _mock_attractions(self, destination: str) -> List[Dict]:
        """模拟景点数据 - 中文景点名称"""
        import random

        # 城市景点映射（中文）
        city_attractions = {
            "杭州": [
                {"name": "西湖", "rating": 4.9, "reviews": 15200},
                {"name": "灵隐寺", "rating": 4.7, "reviews": 8900},
                {"name": "雷峰塔", "rating": 4.6, "reviews": 6500},
                {"name": "西溪湿地", "rating": 4.8, "reviews": 4200},
                {"name": "宋城", "rating": 4.5, "reviews": 3100},
                {"name": "河坊街", "rating": 4.4, "reviews": 2800},
                {"name": "六和塔", "rating": 4.6, "reviews": 1900},
                {"name": "岳王庙", "rating": 4.7, "reviews": 2100},
            ],
            "北京": [
                {"name": "故宫博物院", "rating": 4.9, "reviews": 52000},
                {"name": "长城", "rating": 4.8, "reviews": 45000},
                {"name": "天坛", "rating": 4.7, "reviews": 18000},
                {"name": "颐和园", "rating": 4.8, "reviews": 16000},
                {"name": "圆明园", "rating": 4.6, "reviews": 12000},
                {"name": "天安门广场", "rating": 4.7, "reviews": 21000},
                {"name": "北海公园", "rating": 4.5, "reviews": 8900},
            ],
            "上海": [
                {"name": "外滩", "rating": 4.7, "reviews": 28000},
                {"name": "东方明珠", "rating": 4.5, "reviews": 19000},
                {"name": "豫园", "rating": 4.6, "reviews": 12000},
                {"name": "上海迪士尼", "rating": 4.8, "reviews": 35000},
                {"name": "南京路", "rating": 4.4, "reviews": 15000},
            ],
            "成都": [
                {"name": "大熊猫基地", "rating": 4.8, "reviews": 18000},
                {"name": "宽窄巷子", "rating": 4.5, "reviews": 14000},
                {"name": "锦里", "rating": 4.4, "reviews": 11000},
                {"name": "武侯祠", "rating": 4.6, "reviews": 8500},
                {"name": "都江堰", "rating": 4.7, "reviews": 6800},
            ],
            "西安": [
                {"name": "兵马俑", "rating": 4.9, "reviews": 35000},
                {"name": "大雁塔", "rating": 4.7, "reviews": 15000},
                {"name": "古城墙", "rating": 4.6, "reviews": 12000},
                {"name": "回民街", "rating": 4.5, "reviews": 18000},
                {"name": "华清宫", "rating": 4.6, "reviews": 7800},
            ],
            "厦门": [
                {"name": "鼓浪屿", "rating": 4.7, "reviews": 22000},
                {"name": "南普陀寺", "rating": 4.6, "reviews": 9800},
                {"name": "厦门大学", "rating": 4.5, "reviews": 16000},
                {"name": "曾厝垵", "rating": 4.4, "reviews": 13000},
                {"name": "中山路", "rating": 4.3, "reviews": 8900},
            ],
            "三亚": [
                {"name": "亚龙湾", "rating": 4.7, "reviews": 16000},
                {"name": "蜈支洲岛", "rating": 4.8, "reviews": 14000},
                {"name": "天涯海角", "rating": 4.3, "reviews": 19000},
                {"name": "南山寺", "rating": 4.5, "reviews": 7800},
                {"name": "海棠湾", "rating": 4.6, "reviews": 8500},
            ],
            "日本": [
                {"name": "浅草寺", "rating": 4.5, "reviews": 18000},
                {"name": "东京塔", "rating": 4.4, "reviews": 15000},
                {"name": "富士山", "rating": 4.8, "reviews": 22000},
                {"name": "金阁寺", "rating": 4.6, "reviews": 12000},
                {"name": "清水寺", "rating": 4.7, "reviews": 14000},
            ],
            "泰国": [
                {"name": "大皇宫", "rating": 4.6, "reviews": 25000},
                {"name": "卧佛寺", "rating": 4.5, "reviews": 18000},
                {"name": "郑王庙", "rating": 4.4, "reviews": 12000},
                {"name": "考山路", "rating": 4.3, "reviews": 15000},
                {"name": "芭提雅海滩", "rating": 4.5, "reviews": 17000},
            ],
            "新加坡": [
                {"name": "滨海湾金沙", "rating": 4.6, "reviews": 16000},
                {"name": "鱼尾狮", "rating": 4.5, "reviews": 19000},
                {"name": "圣淘沙", "rating": 4.7, "reviews": 14000},
                {"name": "环球影城", "rating": 4.8, "reviews": 12000},
                {"name": "滨海湾花园", "rating": 4.9, "reviews": 11000},
            ],
        }

        attractions = city_attractions.get(destination, [
            {"name": f"{destination}中心广场", "rating": 4.5, "reviews": 5000},
            {"name": f"{destination}历史博物馆", "rating": 4.6, "reviews": 3200},
            {"name": f"{destination}文化公园", "rating": 4.4, "reviews": 2800},
            {"name": f"{destination}古街", "rating": 4.5, "reviews": 4100},
            {"name": f"{destination}风景区", "rating": 4.7, "reviews": 6800},
        ])

        return [
            {
                "name": a["name"],
                "rating": a["rating"],
                "reviews": a["reviews"],
                "address": f"{destination}市区",
                "phone": "",
                "description": f"{a['name']}是{destination}的热门景点",
                "thumbnail": ""
            }
            for a in attractions[:8]
        ]


# ============ 便捷函数 ============

_default_service: Optional[DestinationIntelligenceService] = None


def get_intelligence_service() -> DestinationIntelligenceService:
    """获取情报服务单例"""
    global _default_service
    if _default_service is None:
        _default_service = DestinationIntelligenceService()
    return _default_service


async def get_destination_intelligence(
    destination: str,
    travel_date: Optional[str] = None
) -> Dict:
    """
    获取目的地情报

    Args:
        destination: 目的地名称
        travel_date: 旅行日期

    Returns:
        完整情报数据
    """
    service = get_intelligence_service()
    return await service.get_intelligence(destination, travel_date)
