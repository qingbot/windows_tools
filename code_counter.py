#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
代码行数统计工具
支持指定文件夹、正则表达式匹配文件名、递归检测等功能
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from tool_base import BaseTool


class CodeCounterTool(BaseTool):
    """代码行数统计工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "code_counter",
            "description": "统计指定文件夹内代码文件的行数，支持正则表达式匹配和递归检测",
            "parameters": {
                "folder": {
                    "type": "string",
                    "description": "要统计的目标文件夹路径",
                    "required": True
                },
                "pattern": {
                    "type": "string",
                    "description": "匹配文件名的正则表达式（如：\\\\.py$|\\\\.js$）",
                    "required": False,
                    "default": ".*"
                },
                "recursive": {
                    "type": "bool",
                    "description": "是否递归检测子目录",
                    "required": False,
                    "default": True
                },
                "exclude_empty": {
                    "type": "bool", 
                    "description": "是否排除空行",
                    "required": False,
                    "default": False
                },
                "show_details": {
                    "type": "bool",
                    "description": "是否显示每个文件的详细信息",
                    "required": False,
                    "default": True
                },
                "sort_by": {
                    "type": "string",
                    "description": "排序方式：name(文件名), size(行数), none(不排序)",
                    "required": False,
                    "default": "name"
                }
            }
        }
    
    def count_file_lines(self, file_path: str, exclude_empty: bool = False) -> Tuple[int, int, int]:
        """
        统计单个文件的行数
        
        Returns:
            (总行数, 非空行数, 代码行数)
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            non_empty_lines = 0
            code_lines = 0
            
            for line in lines:
                stripped = line.strip()
                if stripped:  # 非空行
                    non_empty_lines += 1
                    # 简单的注释检测（可以根据需要扩展）
                    if not (stripped.startswith('//') or 
                           stripped.startswith('#') or
                           stripped.startswith('/*') or
                           stripped.startswith('*') or
                           stripped.startswith('<!--') or
                           stripped == '*/'):
                        code_lines += 1
            
            return total_lines, non_empty_lines, code_lines
            
        except Exception as e:
            print(f"警告: 无法读取文件 {file_path}: {e}")
            return 0, 0, 0
    
    def scan_directory(self, folder_path: str, pattern: str, recursive: bool) -> List[str]:
        """扫描目录，返回匹配的文件列表"""
        matched_files = []
        
        try:
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValueError(f"正则表达式错误: {e}")
        
        if not os.path.exists(folder_path):
            raise ValueError(f"文件夹不存在: {folder_path}")
        
        if not os.path.isdir(folder_path):
            raise ValueError(f"路径不是文件夹: {folder_path}")
        
        # 使用os.walk进行递归或非递归扫描
        if recursive:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if compiled_pattern.search(file):
                        matched_files.append(os.path.join(root, file))
        else:
            try:
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path) and compiled_pattern.search(item):
                        matched_files.append(item_path)
            except PermissionError as e:
                raise ValueError(f"无权限访问文件夹: {e}")
        
        return matched_files
    
    def format_file_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f}TB"
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行代码行数统计"""
        # 验证参数
        self.validate_args(args)
        
        # 获取参数
        folder = args.get('folder')
        pattern = args.get('pattern', '.*')
        recursive = args.get('recursive', True)
        exclude_empty = args.get('exclude_empty', False)
        show_details = args.get('show_details', True)
        sort_by = args.get('sort_by', 'name').lower()
        
        # 扫描文件
        try:
            matched_files = self.scan_directory(folder, pattern, recursive)
        except Exception as e:
            return f"扫描失败: {e}"
        
        if not matched_files:
            return f"在文件夹 '{folder}' 中未找到匹配模式 '{pattern}' 的文件"
        
        # 统计每个文件
        file_stats = []
        total_files = len(matched_files)
        total_lines = 0
        total_non_empty = 0
        total_code_lines = 0
        total_size = 0
        
        for file_path in matched_files:
            lines, non_empty, code = self.count_file_lines(file_path, exclude_empty)
            try:
                file_size = os.path.getsize(file_path)
            except OSError:
                file_size = 0
            
            file_stats.append({
                'path': file_path,
                'relative_path': os.path.relpath(file_path, folder),
                'lines': lines,
                'non_empty': non_empty, 
                'code': code,
                'size': file_size
            })
            
            total_lines += lines
            total_non_empty += non_empty
            total_code_lines += code
            total_size += file_size
        
        # 排序
        if sort_by == 'size':
            file_stats.sort(key=lambda x: x['lines'], reverse=True)
        elif sort_by == 'name':
            file_stats.sort(key=lambda x: x['relative_path'])
        # sort_by == 'none' 时不排序
        
        # 格式化输出
        result_lines = []
        result_lines.append("代码行数统计报告")
        result_lines.append("=" * 50)
        result_lines.append(f"扫描路径: {os.path.abspath(folder)}")
        result_lines.append(f"文件模式: {pattern}")
        result_lines.append(f"递归扫描: {'是' if recursive else '否'}")
        result_lines.append(f"排除空行: {'是' if exclude_empty else '否'}")
        result_lines.append("")
        
        if show_details:
            result_lines.append("文件详情:")
            result_lines.append("-" * 80)
            
            # 表头
            result_lines.append(f"{'文件路径':<50} {'总行数':<8} {'非空行':<8} {'代码行':<8} {'文件大小':<10}")
            result_lines.append("-" * 80)
            
            # 文件详情
            for stat in file_stats:
                relative_path = stat['relative_path']
                if len(relative_path) > 47:
                    relative_path = "..." + relative_path[-44:]
                
                result_lines.append(
                    f"{relative_path:<50} "
                    f"{stat['lines']:<8} "
                    f"{stat['non_empty']:<8} "
                    f"{stat['code']:<8} "
                    f"{self.format_file_size(stat['size']):<10}"
                )
            
            result_lines.append("-" * 80)
        
        # 统计汇总
        result_lines.append("")
        result_lines.append("统计汇总:")
        result_lines.append(f"  匹配文件数: {total_files}")
        result_lines.append(f"  总行数: {total_lines:,}")
        result_lines.append(f"  非空行数: {total_non_empty:,}")
        result_lines.append(f"  代码行数: {total_code_lines:,}")
        result_lines.append(f"  总文件大小: {self.format_file_size(total_size)}")
        
        if total_files > 0:
            result_lines.append(f"  平均行数/文件: {total_lines / total_files:.1f}")
        
        # 文件类型统计
        extension_stats = {}
        for stat in file_stats:
            ext = os.path.splitext(stat['path'])[1].lower()
            if not ext:
                ext = '(无扩展名)'
            
            if ext not in extension_stats:
                extension_stats[ext] = {'count': 0, 'lines': 0}
            extension_stats[ext]['count'] += 1
            extension_stats[ext]['lines'] += stat['lines']
        
        if len(extension_stats) > 1:
            result_lines.append("")
            result_lines.append("按文件类型统计:")
            for ext, stats in sorted(extension_stats.items()):
                result_lines.append(f"  {ext}: {stats['count']} 文件, {stats['lines']:,} 行")
        
        return "\n".join(result_lines)


# 实例化工具
_tool_instance = CodeCounterTool()


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
    parser = argparse.ArgumentParser(description='代码行数统计工具')
    parser.add_argument('-folder', type=str, required=True,
                       help='要统计的目标文件夹路径')
    parser.add_argument('-pattern', type=str, default='.*',
                       help='匹配文件名的正则表达式')
    parser.add_argument('-recursive', type=str, default='true',
                       help='递归检测子目录 (true/false)')
    parser.add_argument('-exclude_empty', type=str, default='false',
                       help='排除空行 (true/false)')
    parser.add_argument('-show_details', type=str, default='true',
                       help='显示每个文件的详细信息 (true/false)')
    parser.add_argument('-sort_by', type=str, default='name',
                       choices=['name', 'size', 'none'],
                       help='排序方式')
    
    args = parser.parse_args()
    
    # 转换为字典格式（处理布尔值）
    def str_to_bool(s):
        return s.lower() in ('true', '1', 'yes', 'on')
    
    tool_args = {
        'folder': args.folder,
        'pattern': args.pattern,
        'recursive': str_to_bool(args.recursive),
        'exclude_empty': str_to_bool(args.exclude_empty),
        'show_details': str_to_bool(args.show_details),
        'sort_by': args.sort_by
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
