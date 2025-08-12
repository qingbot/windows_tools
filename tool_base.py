#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具基类和接口规范
定义所有工具必须实现的统一接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseTool(ABC):
    """工具基类，定义统一接口"""
    
    @abstractmethod
    def get_description(self) -> Dict[str, Any]:
        """
        获取工具描述
        
        Returns:
            Dict包含以下字段:
            - name: 工具名称
            - description: 工具描述
            - parameters: 参数字典，格式为:
              {
                  "参数名": {
                      "type": "参数类型(string/int/float/bool)",
                      "description": "参数描述",
                      "required": True/False,
                      "default": "默认值(可选)"
                  }
              }
        """
        pass
    
    @abstractmethod
    def execute(self, args: Dict[str, Any]) -> Any:
        """
        执行工具功能
        
        Args:
            args: 参数字典
            
        Returns:
            工具执行结果
        """
        pass
    
    def validate_args(self, args: Dict[str, Any]) -> bool:
        """
        验证参数
        
        Args:
            args: 参数字典
            
        Returns:
            验证是否通过
        """
        description = self.get_description()
        parameters = description.get('parameters', {})
        
        # 检查必需参数
        for param_name, param_info in parameters.items():
            if param_info.get('required', False) and param_name not in args:
                raise ValueError(f"缺少必需参数: {param_name}")
        
        # 检查未知参数
        for param_name in args:
            if param_name not in parameters:
                raise ValueError(f"未知参数: {param_name}")
        
        return True


def get_tool_description() -> Dict[str, Any]:
    """
    标准工具描述函数 - 每个工具文件都必须实现此函数
    这是为了兼容不使用类继承的工具实现
    
    Returns:
        工具描述字典
    """
    raise NotImplementedError("每个工具文件都必须实现 get_tool_description() 函数")


def execute_tool(args: Dict[str, Any]) -> Any:
    """
    标准工具执行函数 - 每个工具文件都必须实现此函数
    这是为了兼容不使用类继承的工具实现
    
    Args:
        args: 参数字典
        
    Returns:
        执行结果
    """
    raise NotImplementedError("每个工具文件都必须实现 execute_tool() 函数")


# 工具装饰器，用于简化工具创建
def tool(name: str, description: str, parameters: Optional[Dict[str, Dict[str, Any]]] = None):
    """
    工具装饰器，用于快速创建工具
    
    Args:
        name: 工具名称
        description: 工具描述
        parameters: 参数定义
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        wrapper.tool_name = name
        wrapper.tool_description = description
        wrapper.tool_parameters = parameters or {}
        
        return wrapper
    
    return decorator
