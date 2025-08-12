#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气预报工具
获取指定城市的天气信息，默认获取杭州天气
"""

import requests
import json
import sys
import re
from typing import Dict, Any, Optional
from tool_base import BaseTool


class WeatherTool(BaseTool):
    """天气预报工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "weather_tool",
            "description": "获取指定城市的天气预报信息",
            "parameters": {
                "city": {
                    "type": "string",
                    "description": "城市名称，支持中英文，如：杭州、北京、shanghai等",
                    "required": False,
                    "default": "杭州"
                },
                "days": {
                    "type": "int",
                    "description": "预报天数（1-7天），1表示今天，3表示未来3天",
                    "required": False,
                    "default": 3
                },
                "format": {
                    "type": "string", 
                    "description": "输出格式：simple(简洁)、detailed(详细)",
                    "required": False,
                    "default": "simple"
                },
                "source": {
                    "type": "string",
                    "description": "天气数据源：wttr(wttr.in)、openweather(OpenWeatherMap，需配置API key)",
                    "required": False,
                    "default": "wttr"
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行天气查询"""
        # 验证参数
        self.validate_args(args)
        
        city = args.get('city', '杭州')
        days = args.get('days', 3)
        format_type = args.get('format', 'simple')
        source = args.get('source', 'wttr')
        
        # 验证参数范围
        if days < 1 or days > 7:
            raise ValueError("预报天数必须在1-7之间")
        
        if format_type not in ['simple', 'detailed']:
            raise ValueError("输出格式必须是 simple 或 detailed")
        
        if source not in ['wttr', 'openweather']:
            raise ValueError("数据源必须是 wttr 或 openweather")
        
        try:
            if source == 'wttr':
                return self._get_weather_wttr(city, days, format_type)
            elif source == 'openweather':
                return self._get_weather_openweather(city, days, format_type)
        except Exception as e:
            return f"获取天气信息失败: {str(e)}"
    
    def _make_request(self, url: str, headers: Optional[Dict] = None, timeout: int = 10) -> requests.Response:
        """发起HTTP请求"""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
    
    def _get_weather_wttr(self, city: str, days: int, format_type: str) -> str:
        """使用wttr.in获取天气信息"""
        # wttr.in 支持中文城市名
        url = f"https://wttr.in/{city}?format=j1&lang=zh"
        
        try:
            response = self._make_request(url)
            data = response.json()
            
            return self._format_weather_wttr(data, city, days, format_type)
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试获取纯文本格式
            url_text = f"https://wttr.in/{city}?lang=zh&format=3"
            try:
                response = self._make_request(url_text)
                return f"🌤️ {city}天气:\n{response.text.strip()}"
            except:
                raise Exception("无法获取天气数据，请检查城市名称是否正确")
    
    def _format_weather_wttr(self, data: Dict, city: str, days: int, format_type: str) -> str:
        """格式化wttr.in的天气数据"""
        result = f"🌤️ {city} 天气预报\n" + "=" * 30 + "\n"
        
        # 当前天气
        if 'current_condition' in data and data['current_condition']:
            current = data['current_condition'][0]
            temp = current.get('temp_C', 'N/A')
            feels_like = current.get('FeelsLikeC', 'N/A')
            humidity = current.get('humidity', 'N/A')
            desc = current.get('lang_zh', [{}])[0].get('value', current.get('weatherDesc', [{}])[0].get('value', 'N/A'))
            
            result += f"📍 当前天气:\n"
            result += f"   🌡️  温度: {temp}°C (体感 {feels_like}°C)\n"
            result += f"   ☁️  天气: {desc}\n"
            result += f"   💧 湿度: {humidity}%\n\n"
        
        # 预报天气
        if 'weather' in data:
            result += f"📅 未来{min(days, len(data['weather']))}天预报:\n"
            
            for i, day_data in enumerate(data['weather'][:days]):
                date = day_data.get('date', f'第{i+1}天')
                max_temp = day_data.get('maxtempC', 'N/A')
                min_temp = day_data.get('mintempC', 'N/A')
                
                # 获取天气描述
                desc = 'N/A'
                if 'hourly' in day_data and day_data['hourly']:
                    hourly = day_data['hourly'][0]
                    if 'lang_zh' in hourly and hourly['lang_zh']:
                        desc = hourly['lang_zh'][0].get('value', desc)
                    elif 'weatherDesc' in hourly and hourly['weatherDesc']:
                        desc = hourly['weatherDesc'][0].get('value', desc)
                
                if format_type == 'simple':
                    result += f"   {date}: {min_temp}°C - {max_temp}°C, {desc}\n"
                else:
                    # 详细格式
                    result += f"\n📅 {date}:\n"
                    result += f"   🌡️  温度: {min_temp}°C - {max_temp}°C\n"
                    result += f"   ☁️  天气: {desc}\n"
                    
                    if 'hourly' in day_data and day_data['hourly']:
                        hourly = day_data['hourly'][0]
                        humidity = hourly.get('humidity', 'N/A')
                        wind_speed = hourly.get('windspeedKmph', 'N/A')
                        result += f"   💧 湿度: {humidity}%\n"
                        result += f"   💨 风速: {wind_speed} km/h\n"
        
        return result
    
    def _get_weather_openweather(self, city: str, days: int, format_type: str) -> str:
        """使用OpenWeatherMap获取天气信息（需要API key）"""
        # 这里需要API key，可以从配置文件读取
        api_key = self._get_openweather_api_key()
        
        if not api_key:
            return "❌ OpenWeatherMap需要API密钥。请在data/config/weather.json中配置api_key，或使用wttr数据源。"
        
        # 获取城市坐标
        geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
        
        try:
            geo_response = self._make_request(geo_url)
            geo_data = geo_response.json()
            
            if not geo_data:
                return f"❌ 未找到城市: {city}"
            
            lat = geo_data[0]['lat']
            lon = geo_data[0]['lon']
            
            # 获取天气数据
            weather_url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=zh_cn"
            weather_response = self._make_request(weather_url)
            weather_data = weather_response.json()
            
            return self._format_weather_openweather(weather_data, city, days, format_type)
            
        except Exception as e:
            return f"❌ OpenWeatherMap API调用失败: {e}"
    
    def _get_openweather_api_key(self) -> Optional[str]:
        """从配置文件获取OpenWeatherMap API密钥"""
        try:
            import os
            config_path = os.path.join(os.path.dirname(__file__), 'data', 'config', 'weather.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return config.get('openweather_api_key')
        except:
            pass
        return None
    
    def _format_weather_openweather(self, data: Dict, city: str, days: int, format_type: str) -> str:
        """格式化OpenWeatherMap的天气数据"""
        if 'list' not in data:
            return "❌ 天气数据格式错误"
        
        result = f"🌤️ {city} 天气预报 (OpenWeatherMap)\n" + "=" * 40 + "\n"
        
        forecasts = data['list'][:days * 8]  # 每天8个时间点（3小时间隔）
        
        current_date = None
        day_count = 0
        
        for forecast in forecasts:
            if day_count >= days:
                break
                
            date_str = forecast['dt_txt'].split(' ')[0]
            time_str = forecast['dt_txt'].split(' ')[1]
            
            if date_str != current_date:
                current_date = date_str
                day_count += 1
                
                temp = forecast['main']['temp']
                desc = forecast['weather'][0]['description']
                humidity = forecast['main']['humidity']
                
                if format_type == 'simple':
                    result += f"📅 {date_str}: {temp:.1f}°C, {desc}\n"
                else:
                    result += f"\n📅 {date_str}:\n"
                    result += f"   🌡️  温度: {temp:.1f}°C\n"
                    result += f"   ☁️  天气: {desc}\n"
                    result += f"   💧 湿度: {humidity}%\n"
        
        return result


# 实例化工具
_tool_instance = WeatherTool()


def get_tool_description() -> Dict[str, Any]:
    """获取工具描述 - 标准接口函数"""
    return _tool_instance.get_description()


def execute_tool(args: Dict[str, Any]) -> str:
    """执行工具 - 标准接口函数"""
    return _tool_instance.execute(args)


def main():
    """独立运行模式"""
    import argparse
    
    # 创建参数解析器
    parser = argparse.ArgumentParser(description='天气预报工具')
    parser.add_argument('-city', type=str, default='杭州',
                       help='城市名称，支持中英文')
    parser.add_argument('-days', type=int, default=3,
                       help='预报天数（1-7天）')
    parser.add_argument('-format', type=str, default='simple',
                       choices=['simple', 'detailed'],
                       help='输出格式：simple(简洁)、detailed(详细)')
    parser.add_argument('-source', type=str, default='wttr',
                       choices=['wttr', 'openweather'],
                       help='天气数据源')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'city': args.city,
        'days': args.days,
        'format': args.format,
        'source': args.source
    }
    
    # 执行工具
    try:
        result = execute_tool(tool_args)
        print(result)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
