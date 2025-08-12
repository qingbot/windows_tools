#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动关机、重启工具
支持延时关机、重启和立即执行功能
"""

import os
import time
import subprocess
import sys
from typing import Dict, Any
from tool_base import BaseTool


class ShutdownTool(BaseTool):
    """自动关机、重启工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "shutdown_tool",
            "description": "自动关机、重启工具，支持延时和立即执行",
            "parameters": {
                "action": {
                    "type": "string",
                    "description": "执行的操作类型：shutdown(关机)、restart(重启)、cancel(取消)",
                    "required": True
                },
                "delay": {
                    "type": "int",
                    "description": "延时执行时间(秒)，0表示立即执行",
                    "required": False,
                    "default": 30
                },
                "message": {
                    "type": "string",
                    "description": "执行前显示的提示消息",
                    "required": False,
                    "default": "系统即将执行操作..."
                },
                "confirm": {
                    "type": "bool",
                    "description": "是否需要用户确认才执行",
                    "required": False,
                    "default": True
                },
                "force": {
                    "type": "bool",
                    "description": "是否强制执行（关闭所有程序）",
                    "required": False,
                    "default": False
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行关机或重启操作"""
        # 验证参数
        self.validate_args(args)
        
        # 获取参数
        action = args.get('action', '').lower()
        delay = args.get('delay', 30)
        message = args.get('message', '系统即将执行操作...')
        confirm = args.get('confirm', True)
        force = args.get('force', False)
        
        # 验证操作类型
        valid_actions = ['shutdown', 'restart', 'cancel']
        if action not in valid_actions:
            raise ValueError(f"无效的操作类型: {action}。支持的操作: {', '.join(valid_actions)}")
        
        # 取消关机/重启
        if action == 'cancel':
            try:
                subprocess.run(['shutdown', '/a'], check=True)
                return "已取消计划的关机/重启操作"
            except subprocess.CalledProcessError:
                return "没有找到计划的关机/重启操作，或取消失败"
            except FileNotFoundError:
                return "shutdown命令不可用 (仅支持Windows)"
        
        # 设置操作描述
        action_desc = "关机" if action == 'shutdown' else "重启"
        
        # 如果需要确认
        if confirm:
            if delay > 0:
                prompt = f"{message}\n系统将在 {delay} 秒后{action_desc}，是否继续? (y/N): "
            else:
                prompt = f"{message}\n系统将立即{action_desc}，是否继续? (y/N): "
            
            response = input(prompt)
            if response.lower() not in ['y', 'yes', 'true', '1']:
                return f"{action_desc}操作已取消"
        
        # 构建命令
        cmd_action = '/s' if action == 'shutdown' else '/r'
        cmd = ['shutdown', cmd_action, '/t', str(delay)]
        
        if force:
            cmd.append('/f')  # 强制关闭应用程序
        
        # 添加提示消息
        if message and message != '系统即将执行操作...':
            cmd.extend(['/c', f'"{message} 系统将在 {delay} 秒后{action_desc}"'])
        
        # 延时处理（仅用于显示倒计时）
        if delay > 0 and delay <= 60:  # 只在短时间延时时显示倒计时
            print(f"{message}")
            print(f"系统将在 {delay} 秒后{action_desc}...")
            
            # 如果延时很短，显示倒计时
            if delay <= 10:
                for i in range(delay, 0, -1):
                    print(f"{action_desc}倒计时: {i} 秒...", end='\r')
                    time.sleep(1)
                print()  # 换行
        
        # 执行命令
        try:
            subprocess.run(cmd, check=True)
            
            if delay == 0:
                return f"系统正在立即{action_desc}..."
            else:
                return f"系统已计划在 {delay} 秒后{action_desc}。使用 'shutdown_tool -action cancel' 可取消操作。"
                
        except subprocess.CalledProcessError as e:
            return f"{action_desc}命令执行失败: {e}"
        except FileNotFoundError:
            return "shutdown命令不可用 (仅支持Windows)"


# 实例化工具
_tool_instance = ShutdownTool()


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
    parser = argparse.ArgumentParser(description='自动关机、重启工具')
    parser.add_argument('-action', type=str, required=True,
                       choices=['shutdown', 'restart', 'cancel'],
                       help='执行的操作类型：shutdown(关机)、restart(重启)、cancel(取消)')
    parser.add_argument('-delay', type=int, default=30,
                       help='延时执行时间(秒)，0表示立即执行')
    parser.add_argument('-message', type=str, default='系统即将执行操作...',
                       help='执行前显示的提示消息')
    parser.add_argument('-confirm', action='store_true', default=True,
                       help='需要用户确认才执行（默认开启）')
    parser.add_argument('-no-confirm', dest='confirm', action='store_false',
                       help='不需要用户确认直接执行')
    parser.add_argument('-force', action='store_true',
                       help='强制执行（关闭所有程序）')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'action': args.action,
        'delay': args.delay,
        'message': args.message,
        'confirm': args.confirm,
        'force': args.force
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
