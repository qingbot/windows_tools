#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统信息工具
获取和显示系统相关信息
"""

import os
import platform
import psutil
import sys
import socket
from datetime import datetime
from typing import Dict, Any
from tool_base import BaseTool


class SystemInfoTool(BaseTool):
    """系统信息工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "system_info",
            "description": "获取系统信息，包括CPU、内存、磁盘、网络等",
            "parameters": {
                "info_type": {
                    "type": "string",
                    "description": "信息类型：all(所有), cpu(CPU信息), memory(内存), disk(磁盘), network(网络), system(系统基本信息)",
                    "required": False,
                    "default": "all"
                },
                "format": {
                    "type": "string",
                    "description": "输出格式：text(文本), json(JSON格式)",
                    "required": False,
                    "default": "text"
                }
            }
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """获取系统基本信息"""
        return {
            "操作系统": platform.system(),
            "系统版本": platform.release(),
            "系统详细版本": platform.version(),
            "机器类型": platform.machine(),
            "处理器": platform.processor(),
            "计算机名": platform.node(),
            "用户名": os.getlogin() if hasattr(os, 'getlogin') else "未知",
            "当前时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_cpu_info(self) -> Dict[str, Any]:
        """获取CPU信息"""
        return {
            "CPU核心数": psutil.cpu_count(logical=False),
            "CPU逻辑核心数": psutil.cpu_count(logical=True),
            "CPU使用率(%)": psutil.cpu_percent(interval=1),
            "CPU频率(MHz)": f"{psutil.cpu_freq().current:.2f}" if psutil.cpu_freq() else "未知"
        }
    
    def get_memory_info(self) -> Dict[str, Any]:
        """获取内存信息"""
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        return {
            "总内存(GB)": f"{mem.total / (1024**3):.2f}",
            "可用内存(GB)": f"{mem.available / (1024**3):.2f}",
            "已使用内存(GB)": f"{mem.used / (1024**3):.2f}",
            "内存使用率(%)": f"{mem.percent:.1f}",
            "交换分区大小(GB)": f"{swap.total / (1024**3):.2f}",
            "交换分区使用率(%)": f"{swap.percent:.1f}"
        }
    
    def get_disk_info(self) -> Dict[str, Any]:
        """获取磁盘信息"""
        disk_info = {}
        for partition in psutil.disk_partitions():
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info[f"磁盘 {partition.device}"] = {
                    "文件系统": partition.fstype,
                    "挂载点": partition.mountpoint,
                    "总大小(GB)": f"{partition_usage.total / (1024**3):.2f}",
                    "已使用(GB)": f"{partition_usage.used / (1024**3):.2f}",
                    "剩余空间(GB)": f"{partition_usage.free / (1024**3):.2f}",
                    "使用率(%)": f"{(partition_usage.used / partition_usage.total) * 100:.1f}"
                }
            except PermissionError:
                disk_info[f"磁盘 {partition.device}"] = "无访问权限"
        return disk_info
    
    def get_network_info(self) -> Dict[str, Any]:
        """获取网络信息"""
        network_info = {}
        
        # 网络接口信息
        net_io = psutil.net_io_counters(pernic=True)
        for interface, stats in net_io.items():
            network_info[f"网卡 {interface}"] = {
                "发送字节数": f"{stats.bytes_sent / (1024**2):.2f} MB",
                "接收字节数": f"{stats.bytes_recv / (1024**2):.2f} MB",
                "发送包数": stats.packets_sent,
                "接收包数": stats.packets_recv
            }
        
        # IP地址信息
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            network_info["网络配置"] = {
                "主机名": hostname,
                "本地IP": local_ip
            }
        except Exception:
            network_info["网络配置"] = "无法获取网络配置"
        
        return network_info
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行系统信息获取"""
        # 验证参数
        self.validate_args(args)
        
        # 获取参数
        info_type = args.get('info_type', 'all').lower()
        output_format = args.get('format', 'text').lower()
        
        # 收集信息
        all_info = {}
        
        if info_type in ['all', 'system']:
            all_info['系统信息'] = self.get_system_info()
        
        if info_type in ['all', 'cpu']:
            all_info['CPU信息'] = self.get_cpu_info()
        
        if info_type in ['all', 'memory']:
            all_info['内存信息'] = self.get_memory_info()
        
        if info_type in ['all', 'disk']:
            all_info['磁盘信息'] = self.get_disk_info()
        
        if info_type in ['all', 'network']:
            all_info['网络信息'] = self.get_network_info()
        
        # 格式化输出
        if output_format == 'json':
            import json
            return json.dumps(all_info, ensure_ascii=False, indent=2)
        else:
            return self.format_text_output(all_info)
    
    def format_text_output(self, info: Dict[str, Any]) -> str:
        """格式化文本输出"""
        lines = []
        lines.append("=" * 50)
        lines.append("系统信息报告")
        lines.append("=" * 50)
        
        for category, data in info.items():
            lines.append(f"\n【{category}】")
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict):
                        lines.append(f"  {key}:")
                        for sub_key, sub_value in value.items():
                            lines.append(f"    {sub_key}: {sub_value}")
                    else:
                        lines.append(f"  {key}: {value}")
            else:
                lines.append(f"  {data}")
        
        return "\n".join(lines)


# 实例化工具
_tool_instance = SystemInfoTool()


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
    parser = argparse.ArgumentParser(description='系统信息工具')
    parser.add_argument('-info_type', type=str, default='all',
                       choices=['all', 'cpu', 'memory', 'disk', 'network', 'system'],
                       help='信息类型')
    parser.add_argument('-format', type=str, default='text',
                       choices=['text', 'json'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'info_type': args.info_type,
        'format': args.format
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
