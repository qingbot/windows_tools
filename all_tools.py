#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows工具集主入口
提供工具扫描、调用和MCP服务器功能
"""

import os
import sys
import glob
import importlib.util
import argparse
import json
import inspect
from typing import Dict, Any, List, Tuple, Optional

class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools = {}
        self.scan_tools()
    
    def scan_tools(self):
        """扫描目录下所有工具文件"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tool_files = glob.glob(os.path.join(current_dir, "*.py"))
        
        for file_path in tool_files:
            filename = os.path.basename(file_path)
            
            # 跳过主入口文件和基类文件
            if filename in ["all_tools.py", "tool_base.py"]:
                continue
                
            try:
                self.load_tool(file_path, filename[:-3])  # 去掉.py后缀
            except Exception as e:
                print(f"警告: 加载工具 {filename} 失败: {e}")
    
    def load_tool(self, file_path: str, tool_name: str):
        """加载单个工具"""
        spec = importlib.util.spec_from_file_location(tool_name, file_path)
        if spec is None or spec.loader is None:
            return
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 检查是否有必需的函数
        if hasattr(module, 'get_tool_description') and hasattr(module, 'execute_tool'):
            description = module.get_tool_description()
            self.tools[tool_name] = {
                'module': module,
                'description': description,
                'file_path': file_path
            }
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具信息"""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        """列出所有工具"""
        return self.tools
    
    def execute_tool(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """执行指定工具"""
        if tool_name not in self.tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        
        tool_info = self.tools[tool_name]
        return tool_info['module'].execute_tool(args)


def print_help(tool_manager: ToolManager):
    """打印简洁帮助信息"""
    print("Windows工具集")
    print("=" * 50)
    print()
    
    if not tool_manager.tools:
        print("当前没有可用的工具。")
        return
    
    print("可用工具:")
    for tool_name, tool_info in tool_manager.tools.items():
        desc = tool_info['description']
        print(f"  {tool_name:<15} - {desc.get('description', '无描述')}")
    
    print("\n使用方法:")
    print("  显示帮助: python all_tools.py -h")
    print("  工具详细帮助: python all_tools.py <工具名> -h")
    print("  执行工具: python all_tools.py <工具名> [-参数名 参数值] ...")
    print("  MCP服务器模式: python all_tools.py --mcp-server")


def print_tool_help(tool_manager: ToolManager, tool_name: str):
    """打印指定工具的详细帮助信息"""
    if tool_name not in tool_manager.tools:
        print(f"错误: 工具 '{tool_name}' 不存在")
        print("\n可用工具:")
        for name in tool_manager.tools:
            print(f"  {name}")
        return
    
    tool_info = tool_manager.tools[tool_name]
    desc = tool_info['description']
    
    print(f"工具: {tool_name}")
    print("=" * (6 + len(tool_name)))
    print(f"描述: {desc.get('description', '无描述')}")
    print()
    
    if 'parameters' in desc and desc['parameters']:
        print("参数:")
        for param_name, param_info in desc['parameters'].items():
            required = param_info.get('required', False)
            param_type = param_info.get('type', 'string')
            param_desc = param_info.get('description', '无描述')
            default_value = param_info.get('default')
            
            required_str = " [必需]" if required else " [可选]"
            default_str = f" (默认: {default_value})" if default_value is not None and not required else ""
            
            print(f"  -{param_name} ({param_type}){required_str}{default_str}")
            print(f"    {param_desc}")
            print()
    else:
        print("此工具不需要参数。\n")
    
    print("使用方法:")
    if 'parameters' in desc and desc['parameters']:
        required_params = [name for name, info in desc['parameters'].items() if info.get('required', False)]
        optional_params = [name for name, info in desc['parameters'].items() if not info.get('required', False)]
        
        usage = f"  python all_tools.py {tool_name}"
        if required_params:
            usage += " " + " ".join([f"-{param} <值>" for param in required_params])
        if optional_params:
            usage += " [" + "] [".join([f"-{param} <值>" for param in optional_params]) + "]"
        print(usage)
    else:
        print(f"  python all_tools.py {tool_name}")
    
    print(f"  python {tool_name}.py -h  (独立运行帮助)")


def parse_tool_args(args: List[str], tool_description: Dict[str, Any]) -> Dict[str, Any]:
    """解析工具参数"""
    result = {}
    parameters = tool_description.get('parameters', {})
    
    i = 0
    while i < len(args):
        if args[i].startswith('-'):
            param_name = args[i][1:]  # 去掉前缀的-
            
            if param_name not in parameters:
                raise ValueError(f"未知参数: {param_name}")
            
            if i + 1 >= len(args):
                raise ValueError(f"参数 {param_name} 需要一个值")
            
            param_value = args[i + 1]
            param_type = parameters[param_name].get('type', 'string')
            
            # 类型转换
            if param_type == 'int':
                param_value = int(param_value)
            elif param_type == 'float':
                param_value = float(param_value)
            elif param_type == 'bool':
                param_value = param_value.lower() in ('true', '1', 'yes', 'on')
            
            result[param_name] = param_value
            i += 2
        else:
            raise ValueError(f"意外的参数: {args[i]}")
    
    # 检查必需参数
    for param_name, param_info in parameters.items():
        if param_info.get('required', False) and param_name not in result:
            raise ValueError(f"缺少必需参数: {param_name}")
    
    return result


def run_mcp_server(tool_manager: ToolManager):
    """运行MCP服务器模式"""
    print("启动MCP服务器模式...")
    print("等待MCP调用...")
    
    # 这里可以实现MCP服务器逻辑
    # 暂时提供一个简单的实现
    while True:
        try:
            # 读取JSON-RPC请求
            line = input()
            if not line:
                continue
                
            request = json.loads(line)
            method = request.get('method', '')
            
            if method == 'tools/list':
                # 返回所有工具列表
                tools_list = []
                for tool_name, tool_info in tool_manager.tools.items():
                    desc = tool_info['description']
                    tool_def = {
                        'name': tool_name,
                        'description': desc.get('description', ''),
                        'inputSchema': {
                            'type': 'object',
                            'properties': {},
                            'required': []
                        }
                    }
                    
                    # 添加参数定义
                    if 'parameters' in desc:
                        for param_name, param_info in desc['parameters'].items():
                            tool_def['inputSchema']['properties'][param_name] = {
                                'type': param_info.get('type', 'string'),
                                'description': param_info.get('description', '')
                            }
                            if param_info.get('required', False):
                                tool_def['inputSchema']['required'].append(param_name)
                    
                    tools_list.append(tool_def)
                
                response = {
                    'jsonrpc': '2.0',
                    'id': request.get('id'),
                    'result': {'tools': tools_list}
                }
                print(json.dumps(response))
                
            elif method == 'tools/call':
                # 调用工具
                tool_name = request['params']['name']
                arguments = request['params'].get('arguments', {})
                
                try:
                    result = tool_manager.execute_tool(tool_name, arguments)
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {'content': [{'type': 'text', 'text': str(result)}]}
                    }
                except Exception as e:
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {'code': -1, 'message': str(e)}
                    }
                    
                print(json.dumps(response))
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"MCP服务器错误: {e}", file=sys.stderr)


def main():
    """主函数"""
    # 初始化工具管理器
    tool_manager = ToolManager()
    
    if len(sys.argv) == 1:
        print_help(tool_manager)
        return
    
    # 检查全局帮助参数
    if sys.argv[1] in ['-h', '--help', 'help']:
        print_help(tool_manager)
        return
    
    # 检查MCP服务器模式
    if sys.argv[1] == '--mcp-server':
        run_mcp_server(tool_manager)
        return
    
    # 解析工具名和参数
    if len(sys.argv) < 2:
        print("错误: 请指定工具名")
        print_help(tool_manager)
        return
    
    tool_name = sys.argv[1]
    tool_args = sys.argv[2:]
    
    # 检查工具特定的帮助参数
    if len(tool_args) > 0 and tool_args[0] in ['-h', '--help']:
        print_tool_help(tool_manager, tool_name)
        return
    
    # 检查工具是否存在
    if tool_name not in tool_manager.tools:
        print(f"错误: 工具 '{tool_name}' 不存在")
        print("\n可用工具:")
        for name in tool_manager.tools:
            print(f"  {name}")
        print(f"\n提示: 使用 'python all_tools.py -h' 查看所有工具")
        return
    
    try:
        # 解析参数
        tool_info = tool_manager.tools[tool_name]
        parsed_args = parse_tool_args(tool_args, tool_info['description'])
        
        # 执行工具
        result = tool_manager.execute_tool(tool_name, parsed_args)
        if result is not None:
            print(result)
            
    except Exception as e:
        print(f"错误: {e}")
        print(f"\n提示: 使用 'python all_tools.py {tool_name} -h' 查看工具帮助")


if __name__ == "__main__":
    main()
