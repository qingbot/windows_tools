#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
有趣API工具
提供各种有趣的在线API功能，如笑话、名言、冷知识等
"""

import requests
import json
import sys
import webbrowser
import subprocess
import os
from typing import Dict, Any, Optional
from tool_base import BaseTool


class FunApiTool(BaseTool):
    """有趣API工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "fun_api_tool",
            "description": "调用各种有趣的免费API，获取笑话、名言、冷知识、可爱动物图片等",
            "parameters": {
                "service": {
                    "type": "string",
                    "description": "要调用的服务类型：joke(笑话)、quote(名言)、catfact(猫咪知识)、dogimage(狗狗图片)、catimage(猫咪图片)、nasa(NASA每日图片)、uselessfact(无用知识)、advice(人生建议)、chucknorris(查克·诺里斯笑话)",
                    "required": True
                },
                "language": {
                    "type": "string", 
                    "description": "语言偏好：en(英文)、cn(中文，仅部分API支持)",
                    "required": False,
                    "default": "en"
                },
                "category": {
                    "type": "string",
                    "description": "分类过滤（仅部分API支持），如：programming、misc、dark等",
                    "required": False
                },
                "show": {
                    "type": "bool",
                    "description": "对于图片类服务，是否在浏览器中直接显示图片",
                    "required": False,
                    "default": False
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行API调用"""
        # 验证参数
        self.validate_args(args)
        
        service = args.get('service', '').lower()
        language = args.get('language', 'en').lower()
        category = args.get('category', '')
        show = args.get('show', False)
        
        # 服务映射
        api_functions = {
            'joke': self._get_joke,
            'quote': self._get_quote,
            'catfact': self._get_cat_fact,
            'dogimage': self._get_dog_image,
            'catimage': self._get_cat_image,
            'nasa': self._get_nasa_apod,
            'uselessfact': self._get_useless_fact,
            'advice': self._get_advice,
            'chucknorris': self._get_chuck_norris_joke
        }
        
        if service not in api_functions:
            available_services = ', '.join(api_functions.keys())
            raise ValueError(f"不支持的服务类型: {service}。可用服务: {available_services}")
        
        try:
            return api_functions[service](language, category, show)
        except Exception as e:
            return f"API调用失败: {str(e)}"
    
    def _make_request(self, url: str, headers: Optional[Dict] = None, timeout: int = 10) -> Dict:
        """发起HTTP请求"""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {e}")
        except json.JSONDecodeError as e:
            raise Exception(f"JSON解析失败: {e}")
    
    def _open_in_browser(self, url: str) -> str:
        """在浏览器中打开URL"""
        try:
            # 方法1：使用webbrowser模块
            webbrowser.open(url)
            return "已在浏览器中打开"
        except Exception:
            try:
                # 方法2：使用Windows的start命令
                if os.name == 'nt':  # Windows
                    subprocess.run(['start', url], shell=True, check=True)
                    return "已在默认程序中打开"
                else:
                    return "当前系统不支持自动打开"
            except Exception as e:
                return f"打开失败: {e}"
    
    def _get_joke(self, language: str, category: str, show: bool = False) -> str:
        """获取笑话"""
        if language == 'cn':
            # 中文笑话API (可能需要替换为实际可用的API)
            try:
                url = "https://v1.hitokoto.cn/?c=j"  # 一言API的笑话分类
                data = self._make_request(url)
                return f"😄 {data.get('hitokoto', '获取笑话失败')}\n   —— {data.get('from', '未知')}"
            except:
                pass
        
        # 英文笑话API
        url = "https://v2.jokeapi.dev/joke/Any"
        if category:
            url = f"https://v2.jokeapi.dev/joke/{category}"
        url += "?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single"
        
        data = self._make_request(url)
        if data.get('type') == 'single':
            return f"😄 {data.get('joke', '获取笑话失败')}"
        else:
            setup = data.get('setup', '')
            delivery = data.get('delivery', '')
            return f"😄 {setup}\n   {delivery}"
    
    def _get_quote(self, language: str, category: str, show: bool = False) -> str:
        """获取名人名言"""
        if language == 'cn':
            # 中文名言API
            try:
                url = "https://v1.hitokoto.cn/?c=d"  # 一言API的诗词分类
                data = self._make_request(url)
                return f"📝 {data.get('hitokoto', '获取名言失败')}\n   —— {data.get('from', '未知')}"
            except:
                pass
        
        # 英文名言API
        url = "https://api.quotable.io/random"
        if category:
            url += f"?tags={category}"
        
        data = self._make_request(url)
        content = data.get('content', '获取名言失败')
        author = data.get('author', '未知')
        return f"📝 \"{content}\"\n   —— {author}"
    
    def _get_cat_fact(self, language: str, category: str, show: bool = False) -> str:
        """获取猫咪冷知识"""
        url = "https://catfact.ninja/fact"
        data = self._make_request(url)
        fact = data.get('fact', '获取猫咪知识失败')
        return f"🐱 猫咪小知识: {fact}"
    
    def _get_dog_image(self, language: str, category: str, show: bool = False) -> str:
        """获取随机狗狗图片"""
        url = "https://dog.ceo/api/breeds/image/random"
        data = self._make_request(url)
        if data.get('status') == 'success':
            image_url = data.get('message', '')
            result = f"🐕 随机狗狗图片: {image_url}"
            
            if show:
                open_result = self._open_in_browser(image_url)
                result += f"\n📺 {open_result}"
            
            return result
        return "获取狗狗图片失败"
    
    def _get_cat_image(self, language: str, category: str, show: bool = False) -> str:
        """获取随机猫咪图片"""
        url = "https://api.thecatapi.com/v1/images/search"
        data = self._make_request(url)
        if data and len(data) > 0:
            image_url = data[0].get('url', '')
            result = f"🐱 随机猫咪图片: {image_url}"
            
            if show:
                open_result = self._open_in_browser(image_url)
                result += f"\n📺 {open_result}"
            
            return result
        return "获取猫咪图片失败"
    
    def _get_nasa_apod(self, language: str, category: str, show: bool = False) -> str:
        """获取NASA每日天文图片"""
        # 注意：NASA API通常需要API密钥，这里使用演示版本
        url = "https://api.nasa.gov/planetary/apod?api_key=DEMO_KEY"
        try:
            data = self._make_request(url)
            title = data.get('title', '无标题')
            explanation = data.get('explanation', '无描述')[:200] + '...'
            image_url = data.get('url', '')
            date = data.get('date', '')
            
            result = f"🚀 NASA每日天文图片 ({date})\n标题: {title}\n描述: {explanation}\n图片: {image_url}"
            
            if show and image_url:
                open_result = self._open_in_browser(image_url)
                result += f"\n📺 {open_result}"
            
            return result
        except:
            return "🚀 NASA API访问受限，请申请API密钥获取完整功能"
    
    def _get_useless_fact(self, language: str, category: str, show: bool = False) -> str:
        """获取无用知识"""
        url = "https://uselessfacts.jsph.pl/random.json?language=en"
        data = self._make_request(url)
        fact = data.get('text', '获取无用知识失败')
        return f"🤔 无用但有趣的知识: {fact}"
    
    def _get_advice(self, language: str, category: str, show: bool = False) -> str:
        """获取人生建议"""
        url = "https://api.adviceslip.com/advice"
        data = self._make_request(url)
        advice = data.get('slip', {}).get('advice', '获取建议失败')
        return f"💡 人生建议: {advice}"
    
    def _get_chuck_norris_joke(self, language: str, category: str, show: bool = False) -> str:
        """获取查克·诺里斯笑话"""
        url = "https://api.chucknorris.io/jokes/random"
        if category:
            # 获取可用分类
            categories = ['animal', 'career', 'celebrity', 'dev', 'explicit', 'fashion', 'food', 'history', 'money', 'movie', 'music', 'political', 'religion', 'science', 'sport', 'travel']
            if category in categories:
                url = f"https://api.chucknorris.io/jokes/random?category={category}"
        
        data = self._make_request(url)
        joke = data.get('value', '获取查克·诺里斯笑话失败')
        return f"💪 查克·诺里斯: {joke}"


# 实例化工具
_tool_instance = FunApiTool()


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
    parser = argparse.ArgumentParser(description='有趣API工具')
    parser.add_argument('-service', type=str, required=True,
                       choices=['joke', 'quote', 'catfact', 'dogimage', 'catimage', 'nasa', 'uselessfact', 'advice', 'chucknorris'],
                       help='要调用的服务类型')
    parser.add_argument('-language', type=str, default='en',
                       choices=['en', 'cn'],
                       help='语言偏好：en(英文)、cn(中文)')
    parser.add_argument('-category', type=str, default='',
                       help='分类过滤（仅部分API支持）')
    parser.add_argument('-show', action='store_true',
                       help='对于图片类服务，在浏览器中直接显示图片')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'service': args.service,
        'language': args.language,
        'category': args.category,
        'show': args.show
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
