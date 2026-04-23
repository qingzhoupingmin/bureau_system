# -*- coding: utf-8 -*-
"""
外部API调用工具
"""
import requests
from datetime import datetime
import time


# 备用时间API（HTTP接口可能被阻止）
TIME_API_URL = "http://time.tianyouhui.net/api/time"  # 备用

# 和风天气API配置
QWEATHER_KEY = "0df420feef834729b375cd3fb68cf458"
QWEATHER_HOST = "https://nc4nmu8dfk.re.qweatherapi.com"

# 备用免费天气API（无需配置）
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"
# 天津的Location ID
TIANJIN_LOCATION = "101030100"


class ExternalAPI:
    """外部API调用类"""

    # 缓存时间（秒）
    _cache_time = None
    _cached_time = None
    _weather_cache_time = None
    _cached_weather = None

    # 天气图标映射
    WEATHER_ICONS = {
        "100": "☀️",   # 晴
        "101": "☁️",   # 多云
        "102": "☁️",   # 少云
        "103": "☁️",   # 多云
        "104": "☁️",   # 阴
        "300": "🌧️",   # 小雨
        "301": "🌧️",   # 中雨
        "302": "🌧️",   # 大雨
        "303": "🌧️",   # 暴雨
        "304": "⛈️",   # 雷暴
        "400": "❄️",   # 小雪
        "401": "❄️",   # 中雪
        "402": "❄️",   # 大雪
        "500": "🌫️",   # 雾
        "501": "🌫️",   # 雾
    }

    # 天气文字映射
    WEATHER_TEXT = {
        "100": "晴",
        "101": "多云",
        "102": "少云",
        "103": "多云",
        "104": "阴",
        "300": "小雨",
        "301": "中雨",
        "302": "大雨",
        "303": "暴雨",
        "304": "雷暴",
        "400": "小雪",
        "401": "中雪",
        "402": "大雪",
        "500": "雾",
        "501": "雾",
    }
    
    @classmethod
    def get_world_time(cls):
        """
        获取时间（当前环境网络受限，统一使用本地时间）

        Returns:
            str: 时间字符串，格式 YYYY-MM-DD HH:MM:SS
        """
        return cls.get_local_time()
    
    @staticmethod
    def get_local_time():
        """
        获取本地时间
        
        Returns:
            str: 时间字符串，格式 YYYY-MM-DD HH:MM:SS
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def get_time_with_source(use_external=True):
        """
        获取时间，可选来源

        Args:
            use_external: 是否优先使用外部API（保留参数，实际使用本地时间）

        Returns:
            tuple: (时间字符串, 来源标识)
        """
        # 直接使用本地时间
        return ExternalAPI.get_local_time(), "本地时间"
    
    @staticmethod
    def test_connection():
        """
        测试外部API连接
        
        Returns:
            dict: 测试结果
        """
        result = {
            "success": False,
            "external_time": None,
            "local_time": None,
            "message": ""
        }

        # 测试本地时间
        result["local_time"] = ExternalAPI.get_local_time()

        # 测试外部API
        try:
            resp = requests.get(
                "http://worldtimeapi.org/api/timezone/Asia/Shanghai",
                timeout=3
            )
            if resp.status_code == 200:
                data = resp.json()
                result["external_time"] = data.get('datetime', '')[:19].replace('T', ' ')
                result["success"] = True
                result["message"] = "外部API连接成功"
            else:
                result["message"] = f"外部API返回状态码: {resp.status_code}"
        except requests.exceptions.Timeout:
            result["message"] = "外部API连接超时"
        except requests.exceptions.ConnectionError:
            result["message"] = "无法连接外部API"
        except Exception as e:
            result["message"] = f"外部API错误: {str(e)}"

        return result

    @classmethod
    def get_tianjin_weather(cls):
        """
        获取天津天气（优先和风天气，失败则用Open-Meteo备选）

        Returns:
            dict: 天气信息，包含温度、天气状况、风力等
        """
        # 10分钟内不重复请求（缓存）
        if cls._weather_cache_time and cls._cached_weather:
            if time.time() - cls._weather_cache_time < 600:
                return cls._cached_weather

        # 首先尝试和风天气
        weather = cls._get_qweather()
        if weather:
            cls._cached_weather = weather
            cls._weather_cache_time = time.time()
            return weather

        # 和风失败，尝试 Open-Meteo 备用
        weather = cls._get_open_meteo_weather()
        if weather:
            cls._cached_weather = weather
            cls._weather_cache_time = time.time()
            return weather

        # 全部失败返回默认值
        return {
            "city": "天津",
            "weather": "未知",
            "icon": "🌤️",
            "temp": "--",
            "feels_like": "--",
            "wind_dir": "--",
            "wind_scale": "--",
            "humidity": "--",
            "source": "本地"
        }

    @classmethod
    def _get_qweather(cls):
        """获取和风天气数据"""
        try:
            url = f"{QWEATHER_HOST}/v7/weather/now"
            params = {
                "location": TIANJIN_LOCATION,
                "key": QWEATHER_KEY
            }
            resp = requests.get(url, params=params, timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                if data.get("code") == "200":
                    weather_data = data.get("now", {})
                    weather_code = weather_data.get("icon", "104")
                    weather_text = weather_data.get("text", "未知")
                    temp = weather_data.get("temp", "--")
                    feels_like = weather_data.get("feelsLike", "--")
                    wind_dir = weather_data.get("windDir", "--")
                    wind_scale = weather_data.get("windScale", "--")
                    humidity = weather_data.get("humidity", "--")

                    if weather_text == "未知" or weather_text not in ["晴", "多云", "阴", "雨", "雪", "雾"]:
                        weather_text = cls.WEATHER_TEXT.get(weather_code, weather_text)

                    return {
                        "city": "天津",
                        "weather": weather_text,
                        "icon": cls.WEATHER_ICONS.get(weather_code, "🌤️"),
                        "temp": temp,
                        "feels_like": feels_like,
                        "wind_dir": wind_dir,
                        "wind_scale": wind_scale,
                        "humidity": humidity,
                        "source": "和风天气"
                    }
        except Exception as e:
            print(f"和风天气API失败: {e}")
        return None

    @classmethod
    def _get_open_meteo_weather(cls):
        """获取Open-Meteo备用天气数据（免费无需Key）"""
        try:
            # 天津坐标: 39.1256, 117.1909
            params = {
                "latitude": 39.1256,
                "longitude": 117.1909,
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m",
                "timezone": "Asia/Shanghai"
            }
            resp = requests.get(OPENMETEO_URL, params=params, timeout=5)

            if resp.status_code == 200:
                data = resp.json()
                current = data.get("current", {})

                # WMO天气代码映射
                wmo_code = str(current.get("weather_code", 0))
                weather_text = cls._wmo_to_weather_text(wmo_code)

                return {
                    "city": "天津",
                    "weather": weather_text,
                    "icon": cls.WEATHER_ICONS.get(wmo_code, "🌤️"),
                    "temp": str(int(current.get("temperature_2m", 0))),
                    "feels_like": str(int(current.get("temperature_2m", 0))),
                    "wind_dir": cls._degrees_to_dir(current.get("wind_direction_10m", 0)),
                    "wind_scale": cls._wind_speed_to_scale(current.get("wind_speed_10m", 0)),
                    "humidity": str(int(current.get("relative_humidity_2m", 0))),
                    "source": "Open-Meteo"
                }
        except Exception as e:
            print(f"Open-Meteo API失败: {e}")
        return None

    @staticmethod
    def _wmo_to_weather_text(code):
        """WMO天气代码转中文"""
        wmo_map = {
            "0": "晴",
            "1": "多云", "2": "多云", "3": "多云",
            "45": "雾", "48": "雾",
            "51": "小雨", "53": "中雨", "55": "大雨",
            "61": "小雨", "63": "中雨", "65": "大雨",
            "71": "小雪", "73": "中雪", "75": "大雪",
            "80": "小雨", "81": "中雨", "82": "大雨",
            "95": "雷暴", "96": "雷暴", "99": "雷暴"
        }
        return wmo_map.get(str(code), "多云")

    @staticmethod
    def _degrees_to_dir(degrees):
        """风向角度转文字"""
        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = int((degrees + 22.5) / 45) % 8
        return directions[index]

    @staticmethod
    def _wind_speed_to_scale(speed):
        """风速(m/s)转风力等级"""
        speed = float(speed)
        if speed < 1:
            return "0"
        elif speed < 6:
            return "1-2"
        elif speed < 12:
            return "3-4"
        elif speed < 20:
            return "5-6"
        elif speed < 29:
            return "7-8"
        else:
            return "9+"
        return {
            "city": "天津",
            "weather": "未知",
            "icon": "🌤️",
            "temp": "--",
            "feels_like": "--",
            "wind_dir": "--",
            "wind_scale": "--",
            "humidity": "--",
            "source": "本地"
        }

    @classmethod
    def get_weather_display_text(cls):
        """
        获取天气显示文本

        Returns:
            str: 格式化的天气显示文本
        """
        weather = cls.get_tianjin_weather()
        return f"{weather['icon']} 天津 {weather['weather']} {weather['temp']}°C 湿度 {weather['humidity']}%"