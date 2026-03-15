"""
Open-Meteo API 客户端

免费的天气数据API（无需API Key）
- 天气预报
- 历史天气
- 气候数据
"""

import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class OpenMeteoClient:
    """Open-Meteo天气API客户端（免费，无需API Key）"""

    BASE_URL = "https://api.open-meteo.com/v1"

    def __init__(self):
        """初始化客户端（Open-Meteo无需API Key）"""
        pass

    def _geocode_city(self, city: str) -> Optional[Dict]:
        """
        将城市名转换为经纬度坐标

        Args:
            city: 城市名称

        Returns:
            {"latitude": float, "longitude": float, "name": str, "country": str}
        """
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {
            "name": city,
            "count": 1,
            "language": "zh",
            "format": "json"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "results" in data and data["results"]:
                result = data["results"][0]
                return {
                    "latitude": result.get("latitude"),
                    "longitude": result.get("longitude"),
                    "name": result.get("name"),
                    "country": result.get("country", ""),
                    "admin1": result.get("admin1", "")  # 省/州
                }
            return None

        except Exception as e:
            print(f"Geocoding error: {e}")
            return None

    def get_weather_forecast(
        self,
        city: str,
        days: int = 7,
        hourly: bool = False
    ) -> Dict:
        """
        获取天气预报

        Args:
            city: 城市名称
            days: 预报天数（1-16天）
            hourly: 是否返回小时级数据

        Returns:
            天气预报数据
        """
        # 首先获取城市坐标
        location = self._geocode_city(city)
        if not location:
            return {
                "success": False,
                "error": f"City not found: {city}",
                "city": city
            }

        url = f"{self.BASE_URL}/forecast"
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "daily": "temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum,windspeed_10m_max",
            "timezone": "auto",
            "forecast_days": min(days, 16)
        }

        if hourly:
            params["hourly"] = "temperature_2m,weathercode"
            params["forecast_days"] = 1  # 小时数据只支持1天

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # 解析每日数据
            daily = data.get("daily", {})
            weather_info = []

            # 天气代码映射
            weather_codes = {
                0: "晴",
                1: "多云",
                2: "多云",
                3: "阴",
                45: "雾",
                48: "雾",
                51: "毛毛雨",
                53: "毛毛雨",
                55: "毛毛雨",
                61: "小雨",
                63: "中雨",
                65: "大雨",
                66: "雨夹雪",
                67: "雨夹雪",
                71: "小雪",
                73: "中雪",
                75: "大雪",
                77: "雪粒",
                80: "阵雨",
                81: "阵雨",
                82: "暴雨",
                85: "阵雪",
                86: "阵雪",
                95: "雷阵雨",
                96: "雷阵雨",
                99: "雷阵雨",
            }

            for i in range(len(daily.get("time", []))):
                weather_code = daily.get("weathercode", [0])[i]
                weather_desc = weather_codes.get(weather_code, "未知")

                weather_info.append({
                    "date": daily.get("time", [])[i],
                    "weather": weather_desc,
                    "weather_code": weather_code,
                    "temperature_max": daily.get("temperature_2m_max", [])[i],
                    "temperature_min": daily.get("temperature_2m_min", [])[i],
                    "temperature": f"{daily.get('temperature_2m_min', [])[i]}°C-{daily.get('temperature_2m_max', [])[i]}°C",
                    "precipitation": daily.get("precipitation_sum", [])[i],
                    "wind_speed": daily.get("windspeed_10m_max", [])[i]
                })

            return {
                "success": True,
                "city": city,
                "city_name": location.get("name", city),
                "country": location.get("country", ""),
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "weather": weather_info,
                "count": len(weather_info),
                "timezone": data.get("timezone", "")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "city": city
            }

    def get_current_weather(self, city: str) -> Dict:
        """
        获取当前天气

        Args:
            city: 城市名称

        Returns:
            当前天气数据
        """
        location = self._geocode_city(city)
        if not location:
            return {
                "success": False,
                "error": f"City not found: {city}",
                "city": city
            }

        url = f"{self.BASE_URL}/forecast"
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "current": "temperature_2m,relative_humidity_2m,weathercode,wind_speed_10m",
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            current = data.get("current", {})
            weather_codes = {
                0: "晴", 1: "多云", 2: "多云", 3: "阴",
                45: "雾", 48: "雾", 51: "毛毛雨", 53: "毛毛雨", 55: "毛毛雨",
                61: "小雨", 63: "中雨", 65: "大雨",
                71: "小雪", 73: "中雪", 75: "大雪",
                95: "雷阵雨", 96: "雷阵雨", 99: "雷阵雨",
            }

            return {
                "success": True,
                "city": city,
                "city_name": location.get("name", city),
                "temperature": current.get("temperature_2m"),
                "humidity": current.get("relative_humidity_2m"),
                "weather": weather_codes.get(current.get("weathercode", 0), "未知"),
                "weather_code": current.get("weathercode", 0),
                "wind_speed": current.get("wind_speed_10m"),
                "time": current.get("time", "")
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "city": city
            }

    def get_historical_weather(
        self,
        city: str,
        start_date: str,
        end_date: str
    ) -> Dict:
        """
        获取历史天气数据

        Args:
            city: 城市名称
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)

        Returns:
            历史天气数据
        """
        location = self._geocode_city(city)
        if not location:
            return {
                "success": False,
                "error": f"City not found: {city}",
                "city": city
            }

        url = f"{self.BASE_URL}/archive"
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "start_date": start_date,
            "end_date": end_date,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            daily = data.get("daily", {})
            weather_info = []

            for i in range(len(daily.get("time", []))):
                weather_info.append({
                    "date": daily.get("time", [])[i],
                    "temperature_max": daily.get("temperature_2m_max", [])[i],
                    "temperature_min": daily.get("temperature_2m_min", [])[i],
                    "precipitation": daily.get("precipitation_sum", [])[i]
                })

            return {
                "success": True,
                "city": city,
                "weather": weather_info,
                "count": len(weather_info)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "city": city
            }

    def get_climate_data(
        self,
        city: str,
        month: Optional[int] = None
    ) -> Dict:
        """
        获取气候数据（用于旅行规划建议）

        Args:
            city: 城市名称
            month: 月份（1-12），不传则返回全年

        Returns:
            气候数据
        """
        # 使用 Climate API
        location = self._geocode_city(city)
        if not location:
            return {
                "success": False,
                "error": f"City not found: {city}",
                "city": city
            }

        url = f"{self.BASE_URL}/climate"
        params = {
            "latitude": location["latitude"],
            "longitude": location["longitude"],
            "timezone": "auto"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            climate_data = data.get("climate", {})
            if not climate_data:
                # 如果没有气候数据，返回空
                return {
                    "success": True,
                    "city": city,
                    "climate": [],
                    "note": "Climate data not available for this location"
                }

            # 解析气候数据
            climate_info = []

            for i in range(len(climate_data.get("time", []))):
                climate_month = climate_data.get("time", [])[i]
                climate_month_num = int(climate_month.split("-")[0])

                if month and climate_month_num != month:
                    continue

                climate_info.append({
                    "month": climate_month_num,
                    "temperature_max": climate_data.get("temperature_2m_max", [])[i],
                    "temperature_min": climate_data.get("temperature_2m_min", [])[i],
                    "precipitation_sum": climate_data.get("precipitation_sum", [])[i],
                    "rain_days": climate_data.get("rain_sum", [])[i] if "rain_sum" in climate_data else 0
                })

            return {
                "success": True,
                "city": city,
                "climate": climate_info,
                "count": len(climate_info)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "city": city
            }


# 使用示例
if __name__ == "__main__":
    client = OpenMeteoClient()

    # 测试天气预报
    print("=== 东京天气预报 ===")
    weather = client.get_weather_forecast("Tokyo", 5)
    if weather["success"]:
        for day in weather["weather"][:5]:
            print(f"  {day['date']}: {day['weather']} {day['temperature']}")
    else:
        print(f"  Error: {weather['error']}")

    # 测试当前天气
    print("\n=== 东京当前天气 ===")
    current = client.get_current_weather("Tokyo")
    if current["success"]:
        print(f"  温度: {current['temperature']}°C")
        print(f"  天气: {current['weather']}")
        print(f"  湿度: {current['humidity']}%")
    else:
        print(f"  Error: {current['error']}")

    # 测试国内城市
    print("\n=== 北京天气预报 ===")
    weather = client.get_weather_forecast("Beijing", 3)
    if weather["success"]:
        for day in weather["weather"][:3]:
            print(f"  {day['date']}: {day['weather']} {day['temperature']}")
    else:
        print(f"  Error: {weather['error']}")
