#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动锁屏工具
支持立即锁屏和延时锁屏功能
"""

import os
import time
import subprocess
import sys
from typing import Dict, Any
from tool_base import BaseTool


class ScreenLockTool(BaseTool):
    """自动锁屏工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "screen_lock",
            "description": "自动锁屏工具，支持立即锁屏和延时锁屏",
            "parameters": {
                "delay": {
                    "type": "int",
                    "description": "延时锁屏时间(秒)，0表示立即锁屏",
                    "required": False,
                    "default": 0
                },
                "message": {
                    "type": "string",
                    "description": "锁屏前显示的提示消息",
                    "required": False,
                    "default": "即将锁屏..."
                },
                "confirm": {
                    "type": "bool",
                    "description": "是否需要用户确认才锁屏",
                    "required": False,
                    "default": False
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行锁屏操作"""
        # 验证参数
        self.validate_args(args)
        
        # 获取参数
        delay = args.get('delay', 0)
        message = args.get('message', '即将锁屏...')
        confirm = args.get('confirm', False)
        
        # 如果需要确认
        if confirm:
            response = input(f"{message} 是否继续? (y/N): ")
            if response.lower() not in ['y', 'yes', 'true', '1']:
                return "锁屏操作已取消"
        
        # 延时处理
        if delay > 0:
            print(f"{message}")
            for i in range(delay, 0, -1):
                print(f"锁屏倒计时: {i} 秒...", end='\r')
                time.sleep(1)
            print()  # 换行
        
        # 执行锁屏
        try:
            # Windows锁屏命令
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            return "屏幕已锁定"
        except subprocess.CalledProcessError as e:
            return f"锁屏失败: {e}"
        except FileNotFoundError:
            return "锁屏命令不可用 (仅支持Windows)"


# 实例化工具
_tool_instance = ScreenLockTool()


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
    parser = argparse.ArgumentParser(description='自动锁屏工具')
    parser.add_argument('-delay', type=int, default=0, 
                       help='延时锁屏时间(秒)，0表示立即锁屏')
    parser.add_argument('-message', type=str, default='即将锁屏...', 
                       help='锁屏前显示的提示消息')
    parser.add_argument('-confirm', action='store_true', 
                       help='是否需要用户确认才锁屏')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'delay': args.delay,
        'message': args.message,
        'confirm': args.confirm
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
