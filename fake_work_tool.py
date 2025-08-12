#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
假装工作工具
模拟各种开发工作场景，让命令行看起来很忙碌
"""

import sys
import time
import random
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
from tool_base import BaseTool


class FakeWorkTool(BaseTool):
    """假装工作工具类"""
    
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.total_duration = 0
        self.start_time = None
        
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "fake_work_tool",
            "description": "假装在工作的工具，模拟各种开发任务，让命令行看起来很忙碌",
            "parameters": {
                "duration": {
                    "type": "int",
                    "description": "持续时间（分钟），默认30分钟",
                    "required": False,
                    "default": 30
                },
                "scenario": {
                    "type": "string",
                    "description": "工作场景：cmake(构建工程)、compile(编译代码)、test(运行测试)、deploy(部署)、analysis(代码分析)、mixed(混合模式)",
                    "required": False,
                    "default": "mixed"
                },
                "speed": {
                    "type": "string",
                    "description": "输出速度：fast(快速)、normal(正常)、slow(慢速)",
                    "required": False,
                    "default": "normal"
                },
                "intensity": {
                    "type": "string",
                    "description": "忙碌程度：low(轻松)、normal(正常)、high(高强度)",
                    "required": False,
                    "default": "normal"
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行假装工作"""
        # 验证参数
        self.validate_args(args)
        
        duration = args.get('duration', 30)
        scenario = args.get('scenario', 'mixed').lower()
        speed = args.get('speed', 'normal').lower()
        intensity = args.get('intensity', 'normal').lower()
        
        # 验证参数
        if duration <= 0 or duration > 480:  # 最多8小时
            raise ValueError("持续时间必须在1-480分钟之间")
        
        valid_scenarios = ['cmake', 'compile', 'test', 'deploy', 'analysis', 'mixed']
        if scenario not in valid_scenarios:
            raise ValueError(f"不支持的场景: {scenario}")
        
        valid_speeds = ['fast', 'normal', 'slow']
        if speed not in valid_speeds:
            raise ValueError(f"不支持的速度: {speed}")
        
        valid_intensities = ['low', 'normal', 'high']
        if intensity not in valid_intensities:
            raise ValueError(f"不支持的强度: {intensity}")
        
        try:
            # 设置参数
            self.total_duration = duration * 60  # 转换为秒
            self.start_time = datetime.now()
            
            # 清屏并开始假装工作
            self._clear_screen()
            self._print_header(duration, scenario)
            
            # 设置键盘中断处理
            try:
                self._start_fake_work(scenario, speed, intensity)
            except KeyboardInterrupt:
                self._print_exit_message()
                #return "\n\n🎭 假装工作已停止，记得保存您的\"成果\"！"
            
            self._print_completion_message()
            #return f"\n\n🎉 恭喜！您已经\"工作\"了 {duration} 分钟！\n💼 今天的工作表现非常出色！"
            
        except Exception as e:
            #return f"假装工作失败: {str(e)}"
            pass
    
    def _clear_screen(self):
        """清屏"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def _print_header(self, duration: int, scenario: str):
        """打印标题信息"""
        print("=" * 80)
        print("💡 提示: 按 Ctrl+C 可随时停止")
        print("=" * 80)
        print()
        time.sleep(2)
    
    def _start_fake_work(self, scenario: str, speed: str, intensity: str):
        """开始假装工作"""
        # 设置输出间隔
        speed_intervals = {
            'fast': (0.1, 0.3),
            'normal': (0.3, 0.8),
            'slow': (0.8, 1.5)
        }
        
        min_interval, max_interval = speed_intervals[speed]
        
        # 工作场景循环
        scenarios = [scenario] if scenario != 'mixed' else ['cmake', 'compile', 'test', 'deploy', 'analysis']
        
        while not self._is_time_up():
            current_scenario = random.choice(scenarios)
            self._run_scenario(current_scenario, min_interval, max_interval, intensity)
            
            if not self._is_time_up():
                self._show_break_message()
                time.sleep(random.uniform(2, 5))
    
    def _run_scenario(self, scenario: str, min_interval: float, max_interval: float, intensity: str):
        """运行特定场景"""
        scenario_methods = {
            'cmake': self._cmake_scenario,
            'compile': self._compile_scenario,
            'test': self._test_scenario,
            'deploy': self._deploy_scenario,
            'analysis': self._analysis_scenario
        }
        
        if scenario in scenario_methods:
            scenario_methods[scenario](min_interval, max_interval, intensity)
    
    def _cmake_scenario(self, min_interval: float, max_interval: float, intensity: str):
        """CMake构建场景"""
        print(f"🔨 开始CMake构建...")
        print("-- The C compiler identification is GNU 11.4.0")
        print("-- The CXX compiler identification is GNU 11.4.0")
        print("-- Detecting C compiler ABI info")
        print("-- Detecting C compiler ABI info - done")
        time.sleep(random.uniform(min_interval, max_interval))
        
        projects = ['CoreEngine', 'NetworkModule', 'DatabaseLayer', 'UIFramework', 'MathUtils']
        
        for i in range(random.randint(15, 35)):
            if self._is_time_up():
                break
                
            project = random.choice(projects)
            action = random.choice([
                'Configuring', 'Building', 'Linking', 'Generating', 'Installing'
            ])
            
            file_types = ['.cpp', '.h', '.cmake', '.proto', '.cc']
            filename = f"{random.choice(['main', 'utils', 'config', 'handler', 'service'])}{random.choice(file_types)}"
            
            print(f"-- {action} {project}/{filename}")
            
            # 随机显示一些详细信息
            if random.random() < 0.3:
                details = [
                    f"   Found dependency: {random.choice(['OpenSSL', 'Boost', 'Qt5', 'gRPC', 'Protobuf'])}",
                    f"   Linking target: lib{project.lower()}.so",
                    f"   Generated: {random.randint(50, 500)} object files",
                    f"   Memory usage: {random.randint(128, 2048)}MB"
                ]
                print(random.choice(details))
            
            time.sleep(random.uniform(min_interval, max_interval))
            
            # 随机显示进度条
            if i % random.randint(8, 15) == 0:
                self._show_progress_bar(f"Building {project}", i, 30, random.randint(40, 90))
        
        print("-- Build files have been written to: /build")
        print("✅ CMake配置完成!")
    
    def _compile_scenario(self, min_interval: float, max_interval: float, intensity: str):
        """编译场景"""
        print("🔄 开始编译项目...")
        
        languages = ['C++', 'Python', 'Java', 'Go', 'Rust']
        current_lang = random.choice(languages)
        print(f"📝 编译语言: {current_lang}")
        
        for i in range(random.randint(20, 40)):
            if self._is_time_up():
                break
                
            # 生成随机文件路径
            dirs = ['src', 'lib', 'core', 'utils', 'modules', 'services']
            files = ['main', 'handler', 'parser', 'validator', 'controller', 'model']
            extensions = {
                'C++': ['.cpp', '.cc', '.cxx'],
                'Python': ['.py'],
                'Java': ['.java'],
                'Go': ['.go'],
                'Rust': ['.rs']
            }
            
            dir_name = random.choice(dirs)
            file_name = random.choice(files)
            ext = random.choice(extensions[current_lang])
            full_path = f"{dir_name}/{file_name}{ext}"
            
            # 编译输出
            compiler_commands = {
                'C++': f"g++ -O2 -std=c++17 -c {full_path}",
                'Python': f"python -m py_compile {full_path}",
                'Java': f"javac -cp ./lib/* {full_path}",
                'Go': f"go build {full_path}",
                'Rust': f"rustc --edition 2021 {full_path}"
            }
            
            print(f"[{i+1:3d}/40] {compiler_commands[current_lang]}")
            
            # 随机显示编译警告或信息
            if random.random() < 0.15:
                warnings = [
                    "warning: unused variable 'temp'",
                    "warning: implicit conversion from double to int",
                    "info: optimization level set to O2",
                    "note: including precompiled headers"
                ]
                print(f"         {random.choice(warnings)}")
            
            time.sleep(random.uniform(min_interval, max_interval))
            
            # 显示编译进度
            if i % 10 == 9:
                self._show_progress_bar("Compiling", i+1, 40, random.randint(60, 95))
        
        print("✅ 编译完成! 生成了可执行文件。")
    
    def _test_scenario(self, min_interval: float, max_interval: float, intensity: str):
        """测试场景"""
        print("🧪 运行自动化测试...")
        
        test_suites = ['unit_tests', 'integration_tests', 'e2e_tests', 'performance_tests']
        
        for suite in test_suites:
            if self._is_time_up():
                break
                
            print(f"\n📋 运行测试套件: {suite}")
            total_tests = random.randint(25, 80)
            passed = 0
            failed = 0
            
            for i in range(total_tests):
                if self._is_time_up():
                    break
                    
                test_names = [
                    'test_user_authentication',
                    'test_database_connection',
                    'test_api_response_time',
                    'test_data_validation',
                    'test_error_handling',
                    'test_memory_leak',
                    'test_concurrent_access',
                    'test_security_headers'
                ]
                
                test_name = random.choice(test_names)
                
                # 大多数测试通过
                if random.random() < 0.88:
                    print(f"✅ {test_name} ... PASSED ({random.randint(5, 150)}ms)")
                    passed += 1
                else:
                    print(f"❌ {test_name} ... FAILED")
                    failed += 1
                    if random.random() < 0.5:
                        error_msgs = [
                            "    AssertionError: Expected 200, got 404",
                            "    TimeoutError: Connection timeout after 5s",
                            "    ValueError: Invalid input parameter",
                            "    DatabaseError: Connection refused"
                        ]
                        print(random.choice(error_msgs))
                
                time.sleep(random.uniform(min_interval * 0.5, max_interval * 0.5))
                
                if i % 15 == 14:
                    self._show_progress_bar(f"Testing {suite}", i+1, total_tests, random.randint(70, 95))
            
            print(f"\n📊 {suite} 结果: {passed} 通过, {failed} 失败")
        
        print(f"\n🎯 测试总结: 总体通过率 {random.randint(85, 98)}%")
    
    def _deploy_scenario(self, min_interval: float, max_interval: float, intensity: str):
        """部署场景"""
        print("🚀 开始自动化部署...")
        
        environments = ['staging', 'production', 'testing']
        env = random.choice(environments)
        
        print(f"🌍 目标环境: {env}")
        print(f"🔧 Docker版本: {random.randint(20, 24)}.{random.randint(1, 12)}.{random.randint(0, 9)}")
        print(f"☸️  Kubernetes版本: 1.{random.randint(25, 29)}.{random.randint(0, 15)}")
        
        deployment_steps = [
            ("准备Docker镜像", "docker build -t app:latest ."),
            ("推送镜像到仓库", "docker push registry.company.com/app:latest"),
            ("更新Kubernetes配置", "kubectl apply -f deployment.yaml"),
            ("执行数据库迁移", "python manage.py migrate"),
            ("更新配置文件", "kubectl create configmap app-config"),
            ("滚动更新服务", "kubectl rollout restart deployment/app"),
            ("等待Pod就绪", "kubectl wait --for=condition=ready pod"),
            ("运行健康检查", "curl -f http://app/health"),
            ("更新负载均衡", "kubectl patch service app"),
            ("清理旧版本", "docker system prune -f")
        ]
        
        for i, (step_name, command) in enumerate(deployment_steps):
            if self._is_time_up():
                break
                
            print(f"\n[{i+1:2d}/10] {step_name}...")
            print(f"        $ {command}")
            
            # 模拟命令输出
            if 'docker' in command:
                print(f"        Sending build context to Docker daemon  {random.randint(10, 500)}MB")
                print(f"        Successfully built {self._random_hash()}")
            elif 'kubectl' in command:
                print(f"        deployment.apps/app {'created' if random.random() < 0.5 else 'configured'}")
            elif 'migrate' in command:
                migrations = random.randint(0, 8)
                if migrations > 0:
                    print(f"        Running {migrations} migrations:")
                    for j in range(migrations):
                        print(f"          Applying migration {j+1:04d}... OK")
                else:
                    print("        No migrations to apply.")
            
            time.sleep(random.uniform(min_interval, max_interval * 2))
            
            if i % 3 == 2:
                self._show_progress_bar("Deploying", i+1, 10, random.randint(75, 100))
        
        print(f"\n✅ 部署到 {env} 环境成功!")
        print(f"🌐 应用URL: https://app-{env}.company.com")
    
    def _analysis_scenario(self, min_interval: float, max_interval: float, intensity: str):
        """代码分析场景"""
        print("🔍 开始代码质量分析...")
        
        tools = ['SonarQube', 'ESLint', 'PyLint', 'SpotBugs', 'CodeClimate']
        current_tool = random.choice(tools)
        
        print(f"🛠️  分析工具: {current_tool}")
        
        analysis_types = [
            ("静态代码分析", "正在扫描代码质量问题..."),
            ("安全漏洞检查", "正在检查潜在安全风险..."),
            ("性能分析", "正在分析性能瓶颈..."),
            ("代码重复检测", "正在检测重复代码..."),
            ("依赖关系分析", "正在分析项目依赖...")
        ]
        
        for analysis_name, description in analysis_types:
            if self._is_time_up():
                break
                
            print(f"\n📊 {analysis_name}")
            print(f"     {description}")
            
            files_to_analyze = random.randint(50, 200)
            
            for i in range(files_to_analyze):
                if self._is_time_up():
                    break
                    
                if i % 20 == 0:
                    file_path = f"src/{random.choice(['controllers', 'models', 'utils', 'services'])}/{random.choice(['user', 'auth', 'data', 'config'])}.py"
                    print(f"     正在分析: {file_path}")
                
                time.sleep(random.uniform(min_interval * 0.3, max_interval * 0.3))
                
                if i % 25 == 24:
                    self._show_progress_bar(analysis_name, i+1, files_to_analyze, random.randint(60, 90))
            
            # 分析结果
            issues = random.randint(0, 15)
            if issues > 0:
                print(f"     ⚠️  发现 {issues} 个问题")
                issue_types = ['代码异味', '安全风险', '性能问题', '重复代码', '复杂度过高']
                for _ in range(min(issues, 3)):
                    print(f"       - {random.choice(issue_types)}: 第{random.randint(1, 500)}行")
            else:
                print(f"     ✅ 未发现问题")
        
        print(f"\n📈 代码质量评分: {random.randint(75, 95)}/100")
        print(f"🏆 代码覆盖率: {random.randint(80, 98)}%")
    
    def _show_progress_bar(self, task: str, current: int, total: int, percentage: int):
        """显示进度条"""
        bar_length = 40
        filled_length = int(bar_length * percentage // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]
        
        print(f"\n[{bar}] {percentage:3d}% | {task} ({current}/{total}) | 运行时间: {elapsed_str}")
        time.sleep(random.uniform(1, 3))
    
    def _show_break_message(self):
        """显示休息信息"""
        break_messages = [
            "\n☕ 短暂休息，准备下一个任务...",
            "\n🔄 正在切换工作环境...",
            "\n📝 正在更新项目文档...",
            "\n🔧 正在优化系统配置...",
            "\n💾 正在保存工作进度...",
            "\n🌐 正在同步远程仓库...",
            "\n🧹 正在清理临时文件..."
        ]
        
        print(random.choice(break_messages))
    
    def _random_hash(self) -> str:
        """生成随机哈希"""
        chars = 'abcdef0123456789'
        return ''.join(random.choice(chars) for _ in range(12))
    
    def _is_time_up(self) -> bool:
        """检查时间是否到了"""
        if self.start_time is None:
            return False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed >= self.total_duration
    
    def _print_exit_message(self):
        """打印退出信息"""
        elapsed = datetime.now() - self.start_time
        elapsed_minutes = int(elapsed.total_seconds() // 60)
        
        print("\n" + "="*60)
        print("="*60)
    
    def _print_completion_message(self):
        """打印完成信息"""
        print("\n" + "="*60)
        
        print("="*60)


# 实例化工具
_tool_instance = FakeWorkTool()


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
    parser = argparse.ArgumentParser(description='假装工作工具 - 让你看起来很忙碌')
    parser.add_argument('-duration', type=int, default=30,
                       help='持续时间（分钟），默认30分钟')
    parser.add_argument('-scenario', type=str, default='mixed',
                       choices=['cmake', 'compile', 'test', 'deploy', 'analysis', 'mixed'],
                       help='工作场景')
    parser.add_argument('-speed', type=str, default='normal',
                       choices=['fast', 'normal', 'slow'],
                       help='输出速度')
    parser.add_argument('-intensity', type=str, default='normal',
                       choices=['low', 'normal', 'high'],
                       help='忙碌程度')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'duration': args.duration,
        'scenario': args.scenario,
        'speed': args.speed,
        'intensity': args.intensity
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
