# Windows工具集

一个模块化的Windows工具集，提供各种实用功能，支持命令行调用和MCP服务器模式。

## 项目结构

```
tools/
├── all_tools.py        # 主入口文件
├── tool_base.py        # 工具基类和接口规范
├── screen_lock.py      # 自动锁屏工具
├── system_info.py      # 系统信息工具
├── code_counter.py     # 代码行数统计工具
├── data/              # 数据存储目录
│   └── README.md      # 数据存储规范说明
├── requirements.txt    # 项目依赖
├── .gitignore         # Git忽略文件配置
└── README.md          # 项目说明
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 1. 查看帮助信息

#### 简洁模式 - 查看所有可用工具

```bash
python all_tools.py -h
```

显示工具列表和简单描述。

#### 详细模式 - 查看特定工具的详细信息

```bash
python all_tools.py <工具名> -h
```

显示指定工具的详细参数说明，例如：

```bash
python all_tools.py screen_lock -h
python all_tools.py system_info -h
```

### 2. 使用具体工具

#### 自动锁屏工具

```bash
# 立即锁屏
python all_tools.py screen_lock

# 延时10秒锁屏
python all_tools.py screen_lock -delay 10

# 延时锁屏并显示自定义消息
python all_tools.py screen_lock -delay 5 -message "工作结束，准备锁屏"

# 需要确认的锁屏
python all_tools.py screen_lock -confirm true
```

#### 系统信息工具

```bash
# 获取所有系统信息
python all_tools.py system_info

# 只获取CPU信息
python all_tools.py system_info -info_type cpu

# 获取内存信息并以JSON格式输出
python all_tools.py system_info -info_type memory -format json

# 支持的信息类型: all, cpu, memory, disk, network, system
```

#### 代码行数统计工具

```bash
# 统计当前目录下所有Python文件的行数
python all_tools.py code_counter -folder . -pattern "\.py$"

# 统计指定目录下所有代码文件（不递归）
python all_tools.py code_counter -folder ./src -pattern "\.(py|js|java)$" -recursive false

# 简洁输出，按行数排序
python all_tools.py code_counter -folder . -pattern "\.py$" -show_details false -sort_by size

# 排除空行统计
python all_tools.py code_counter -folder . -pattern "\.py$" -exclude_empty true
```

### 3. 独立运行工具

每个工具都可以独立运行：

```bash
# 独立运行锁屏工具
python screen_lock.py -delay 10

# 独立运行系统信息工具
python system_info.py -info_type cpu

# 独立运行代码统计工具
python code_counter.py -folder . -pattern "\.py$"
```

### 4. MCP服务器模式

启动MCP服务器，用于与其他应用集成：

```bash
python all_tools.py --mcp-server
```

## 开发新工具

### 方法1: 使用基类继承

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我的工具
"""

from typing import Dict, Any
from tool_base import BaseTool

class MyTool(BaseTool):
    def get_description(self) -> Dict[str, Any]:
        return {
            "name": "my_tool",
            "description": "我的工具描述",
            "parameters": {
                "param1": {
                    "type": "string",
                    "description": "参数1描述",
                    "required": True
                },
                "param2": {
                    "type": "int", 
                    "description": "参数2描述",
                    "required": False,
                    "default": 0
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        # 验证参数
        self.validate_args(args)
        
        # 实现工具逻辑
        param1 = args.get('param1')
        param2 = args.get('param2', 0)
        
        return f"处理结果: {param1}, {param2}"

# 标准接口函数
_tool_instance = MyTool()

def get_tool_description() -> Dict[str, Any]:
    return _tool_instance.get_description()

def execute_tool(args: Dict[str, Any]) -> str:
    return _tool_instance.execute(args)

if __name__ == "__main__":
    # 独立运行支持
    pass
```

### 方法2: 直接实现接口函数

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
我的简单工具
"""

from typing import Dict, Any

def get_tool_description() -> Dict[str, Any]:
    """获取工具描述"""
    return {
        "name": "simple_tool",
        "description": "简单工具描述",
        "parameters": {
            "input": {
                "type": "string",
                "description": "输入参数",
                "required": True
            }
        }
    }

def execute_tool(args: Dict[str, Any]) -> str:
    """执行工具"""
    input_value = args.get('input')
    if not input_value:
        raise ValueError("缺少必需参数: input")
    
    return f"处理结果: {input_value}"

if __name__ == "__main__":
    # 独立运行支持
    pass
```

### 工具接口规范

每个工具文件必须实现以下两个函数：

1. **get_tool_description() -> Dict[str, Any]**
   - 返回工具的描述信息
   - 包含name、description和parameters字段

2. **execute_tool(args: Dict[str, Any]) -> Any**
   - 执行工具的主要功能
   - 参数为字典格式
   - 返回执行结果

### 参数类型支持

- `string`: 字符串类型
- `int`: 整数类型  
- `float`: 浮点数类型
- `bool`: 布尔类型

### 参数属性

- `type`: 参数类型
- `description`: 参数描述
- `required`: 是否必需 (True/False)
- `default`: 默认值 (可选)

### 数据存储最佳实践

开发新工具时，如需存储数据请遵循以下规范：

```python
import os

def get_tool_data_dir(tool_name: str) -> str:
    """获取工具专用数据目录"""
    base_dir = os.path.join(os.path.dirname(__file__), 'data', tool_name)
    os.makedirs(base_dir, exist_ok=True)
    return base_dir

def get_tool_config_dir(tool_name: str) -> str:
    """获取工具配置目录"""
    config_dir = os.path.join(get_tool_data_dir(tool_name), 'config')
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

# 使用示例
data_dir = get_tool_data_dir('my_tool')
config_file = os.path.join(get_tool_config_dir('my_tool'), 'settings.json')
```

## 数据存储规范

项目采用统一的数据存储规范，所有工具的数据文件、配置文件和临时文件都存储在 `data/` 目录下：

### 目录结构
- `data/config/` - 全局配置文件
- `data/<工具名>/` - 各工具的专用数据目录
  - `config/` - 工具特定配置
  - `cache/` - 缓存文件  
  - `logs/` - 日志文件
  - `output/` - 输出文件
  - `temp/` - 临时文件
- `data/shared/` - 工具间共享的数据

### 设计原则
- **工具隔离**: 每个工具使用独立的数据目录
- **类型分类**: 按数据类型进行目录分类
- **自动管理**: 工具自动创建所需目录和清理临时文件
- **版本控制**: data目录已在.gitignore中排除（保留README.md）

详细规范请参考 [data/README.md](data/README.md)

## 项目特性

- ✅ **模块化设计**: 每个工具独立，可单独运行
- ✅ **统一接口**: 所有工具遵循统一的接口规范
- ✅ **自动发现**: 主程序自动扫描并加载所有工具
- ✅ **参数验证**: 自动进行参数类型转换和必需性检查
- ✅ **帮助系统**: 自动生成工具列表和参数说明
- ✅ **MCP集成**: 支持MCP服务器模式，便于与其他应用集成
- ✅ **错误处理**: 完善的错误处理和用户友好的错误信息
- ✅ **数据管理**: 统一的数据存储规范和目录结构

## 技术栈

- Python 3.6+
- psutil (用于系统信息获取)
- 标准库模块

## 许可证

本项目采用 MIT 许可证。
