#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
法定节假日倒计时工具
计算距离下次法定节假日还有多久
"""

import requests
import json
import sys
import os
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from tool_base import BaseTool


class HolidayCountdownTool(BaseTool):
    """法定节假日倒计时工具类"""
    
    def get_description(self) -> Dict[str, Any]:
        """获取工具描述"""
        return {
            "name": "holiday_countdown_tool", 
            "description": "计算距离下次中国法定节假日还有多长时间",
            "parameters": {
                "year": {
                    "type": "int",
                    "description": "查询年份，默认为当前年份",
                    "required": False
                },
                "show_all": {
                    "type": "bool",
                    "description": "是否显示全年所有节假日信息",
                    "required": False,
                    "default": False
                },
                "source": {
                    "type": "string",
                    "description": "数据源：api(在线API)、local(本地数据)",
                    "required": False,
                    "default": "api"
                },
                "format": {
                    "type": "string",
                    "description": "输出格式：simple(简洁)、detailed(详细)",
                    "required": False,
                    "default": "simple"
                }
            }
        }
    
    def execute(self, args: Dict[str, Any]) -> str:
        """执行节假日倒计时计算"""
        # 验证参数
        self.validate_args(args)
        
        current_year = datetime.now().year
        year = args.get('year', current_year)
        show_all = args.get('show_all', False)
        source = args.get('source', 'api').lower()
        format_type = args.get('format', 'simple').lower()
        
        # 验证参数
        if year < 2020 or year > 2030:
            raise ValueError("年份必须在2020-2030之间")
        
        if source not in ['api', 'local']:
            raise ValueError("数据源必须是 api 或 local")
        
        if format_type not in ['simple', 'detailed']:
            raise ValueError("输出格式必须是 simple 或 detailed")
        
        try:
            # 获取节假日数据
            holidays = self._get_holidays(year, source)
            
            # 计算倒计时
            result = self._calculate_countdown(holidays, show_all, format_type)
            
            return result
            
        except Exception as e:
            return f"获取节假日信息失败: {str(e)}"
    
    def _get_holidays(self, year: int, source: str) -> List[Dict]:
        """获取节假日数据"""
        if source == 'api':
            return self._get_holidays_from_api(year)
        else:
            return self._get_local_holidays(year)
    
    def _get_holidays_from_api(self, year: int) -> List[Dict]:
        """从API获取节假日数据"""
        try:
            # 使用免费的节假日API
            url = f"https://timor.tech/api/holiday/year/{year}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('code') != 0:
                raise Exception(f"API返回错误: {data.get('message', '未知错误')}")
            
            holidays = []
            holiday_data = data.get('holiday', {})
            
            for date_str, info in holiday_data.items():
                holidays.append({
                    'date': date_str,
                    'name': info.get('name', ''),
                    'holiday': info.get('holiday', False),
                    'type': 'holiday' if info.get('holiday', False) else 'workday'
                })
            
            return sorted(holidays, key=lambda x: x['date'])
            
        except requests.RequestException:
            # 网络错误时回退到本地数据
            return self._get_local_holidays(year)
    
    def _get_local_holidays(self, year: int) -> List[Dict]:
        """获取本地预定义的节假日数据"""
        # 中国法定节假日（需要根据实际情况更新）
        holidays_template = {
            # 元旦
            'new_year': {'name': '元旦', 'month': 1, 'day': 1, 'duration': 3},
            # 春节（农历，需要计算）
            'spring_festival': {'name': '春节', 'lunar': True},
            # 清明节（通常4月4-6日）
            'qingming': {'name': '清明节', 'month': 4, 'day': 4, 'duration': 3},
            # 劳动节
            'labor_day': {'name': '劳动节', 'month': 5, 'day': 1, 'duration': 5},
            # 端午节（农历五月初五，需要计算）
            'dragon_boat': {'name': '端午节', 'lunar': True},
            # 中秋节（农历八月十五，需要计算）
            'mid_autumn': {'name': '中秋节', 'lunar': True},
            # 国庆节
            'national_day': {'name': '国庆节', 'month': 10, 'day': 1, 'duration': 7}
        }
        
        holidays = []
        
        # 固定日期的节假日
        fixed_holidays = [
            {'date': f'{year}-01-01', 'name': '元旦', 'holiday': True},
            {'date': f'{year}-04-04', 'name': '清明节', 'holiday': True},
            {'date': f'{year}-04-05', 'name': '清明节', 'holiday': True},
            {'date': f'{year}-04-06', 'name': '清明节', 'holiday': True},
            {'date': f'{year}-05-01', 'name': '劳动节', 'holiday': True},
            {'date': f'{year}-05-02', 'name': '劳动节', 'holiday': True},
            {'date': f'{year}-05-03', 'name': '劳动节', 'holiday': True},
            {'date': f'{year}-10-01', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-02', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-03', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-04', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-05', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-06', 'name': '国庆节', 'holiday': True},
            {'date': f'{year}-10-07', 'name': '国庆节', 'holiday': True},
        ]
        
        # 添加农历节日（简化版本，实际需要农历转换）
        lunar_holidays = self._get_lunar_holidays(year)
        fixed_holidays.extend(lunar_holidays)
        
        return sorted(fixed_holidays, key=lambda x: x['date'])
    
    def _get_lunar_holidays(self, year: int) -> List[Dict]:
        """获取农历节日（简化版本）"""
        # 这里提供一个简化的农历节日日期
        # 实际使用中应该使用准确的农历转换算法
        lunar_dates = {
            2024: {
                'spring_festival': ['02-10', '02-11', '02-12', '02-13', '02-14', '02-15', '02-16'],
                'dragon_boat': ['06-10'],
                'mid_autumn': ['09-17']
            },
            2025: {
                'spring_festival': ['01-29', '01-30', '01-31', '02-01', '02-02', '02-03', '02-04'],
                'dragon_boat': ['05-31'],
                'mid_autumn': ['10-06']
            }
        }
        
        holidays = []
        if year in lunar_dates:
            # 春节
            for date_str in lunar_dates[year]['spring_festival']:
                holidays.append({
                    'date': f'{year}-{date_str}',
                    'name': '春节',
                    'holiday': True
                })
            
            # 端午节
            for date_str in lunar_dates[year]['dragon_boat']:
                holidays.append({
                    'date': f'{year}-{date_str}',
                    'name': '端午节',
                    'holiday': True
                })
            
            # 中秋节
            for date_str in lunar_dates[year]['mid_autumn']:
                holidays.append({
                    'date': f'{year}-{date_str}',
                    'name': '中秋节',
                    'holiday': True
                })
        
        return holidays
    
    def _calculate_countdown(self, holidays: List[Dict], show_all: bool, format_type: str) -> str:
        """计算倒计时"""
        today = date.today()
        today_str = today.strftime('%Y-%m-%d')
        
        # 过滤出真正的节假日
        holiday_list = [h for h in holidays if h.get('holiday', False)]
        
        # 找到下一个节假日
        next_holiday = None
        upcoming_holidays = []
        
        for holiday in holiday_list:
            holiday_date = datetime.strptime(holiday['date'], '%Y-%m-%d').date()
            
            if holiday_date >= today:
                upcoming_holidays.append({
                    'name': holiday['name'],
                    'date': holiday_date,
                    'days_left': (holiday_date - today).days
                })
                
                if next_holiday is None:
                    next_holiday = {
                        'name': holiday['name'],
                        'date': holiday_date,
                        'days_left': (holiday_date - today).days
                    }
        
        # 格式化输出
        if show_all:
            return self._format_all_holidays(upcoming_holidays, format_type)
        else:
            return self._format_next_holiday(next_holiday, format_type)
    
    def _format_next_holiday(self, next_holiday: Optional[Dict], format_type: str) -> str:
        """格式化下一个节假日信息"""
        if not next_holiday:
            return "🎉 今年已经没有更多法定节假日了！\n💡 可以用 -show_all true 查看全年节假日安排"
        
        name = next_holiday['name']
        date_obj = next_holiday['date']
        days_left = next_holiday['days_left']
        
        # 格式化日期
        date_str = date_obj.strftime('%Y年%m月%d日')
        weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date_obj.weekday()]
        
        if format_type == 'simple':
            if days_left == 0:
                return f"🎉 今天就是{name}！祝您节日快乐！"
            elif days_left == 1:
                return f"⏰ 明天就是{name}了！({date_str} {weekday})"
            else:
                return f"⏰ 距离下次法定节假日【{name}】还有 {days_left} 天\n📅 {date_str} {weekday}"
        
        else:  # detailed
            result = f"🎯 下次法定节假日倒计时\n" + "=" * 30 + "\n"
            result += f"🏮 节假日: {name}\n"
            result += f"📅 日期: {date_str} {weekday}\n"
            
            if days_left == 0:
                result += f"🎉 状态: 今天就是节假日！\n"
            elif days_left == 1:
                result += f"⏰ 倒计时: 明天就到了！\n"
            else:
                weeks = days_left // 7
                days = days_left % 7
                result += f"⏰ 倒计时: {days_left} 天"
                
                if weeks > 0:
                    result += f" ({weeks}周{days}天)"
                result += "\n"
            
            # 添加工作日计算
            workdays = self._count_workdays(date.today(), date_obj)
            result += f"💼 工作日: 约{workdays}个工作日\n"
            
            # 添加励志信息
            if days_left <= 7:
                result += f"🚀 马上就要放假了，加油！"
            elif days_left <= 30:
                result += f"⌛ 还有不到一个月，坚持住！"
            else:
                result += f"🌟 还需要等待一段时间，保持耐心！"
            
            return result
    
    def _format_all_holidays(self, upcoming_holidays: List[Dict], format_type: str) -> str:
        """格式化所有即将到来的节假日"""
        if not upcoming_holidays:
            return "🎉 今年已经没有更多法定节假日了！"
        
        result = f"📅 {datetime.now().year}年剩余法定节假日安排\n" + "=" * 40 + "\n"
        
        # 按节假日名称分组
        holiday_groups = {}
        for holiday in upcoming_holidays:
            name = holiday['name']
            if name not in holiday_groups:
                holiday_groups[name] = []
            holiday_groups[name].append(holiday)
        
        for i, (name, group) in enumerate(holiday_groups.items(), 1):
            # 获取第一天和最后一天
            first_day = min(group, key=lambda x: x['date'])
            last_day = max(group, key=lambda x: x['date'])
            duration = len(group)
            
            if format_type == 'simple':
                if duration == 1:
                    date_str = first_day['date'].strftime('%m月%d日')
                    result += f"{i}. {name} - {date_str} (还有{first_day['days_left']}天)\n"
                else:
                    start_date = first_day['date'].strftime('%m月%d日')
                    end_date = last_day['date'].strftime('%m月%d日')
                    result += f"{i}. {name} - {start_date}~{end_date} 共{duration}天 (还有{first_day['days_left']}天)\n"
            
            else:  # detailed
                start_date = first_day['date'].strftime('%Y年%m月%d日')
                end_date = last_day['date'].strftime('%Y年%m月%d日')
                start_weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][first_day['date'].weekday()]
                
                result += f"\n🏮 {name}\n"
                if duration == 1:
                    result += f"   📅 {start_date} {start_weekday}\n"
                else:
                    result += f"   📅 {start_date} ~ {end_date}\n"
                    result += f"   ⏱️  共 {duration} 天假期\n"
                
                result += f"   ⏰ 倒计时: {first_day['days_left']} 天\n"
                
                if first_day['days_left'] <= 7:
                    result += f"   🚀 即将到来！\n"
                elif first_day['days_left'] <= 30:
                    result += f"   ⌛ 不到一个月\n"
        
        return result
    
    def _count_workdays(self, start_date: date, end_date: date) -> int:
        """计算工作日数量（简化版本，不考虑节假日调休）"""
        workdays = 0
        current_date = start_date
        
        while current_date < end_date:
            if current_date.weekday() < 5:  # 周一到周五
                workdays += 1
            current_date += timedelta(days=1)
        
        return workdays


# 实例化工具
_tool_instance = HolidayCountdownTool()


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
    parser = argparse.ArgumentParser(description='法定节假日倒计时工具')
    parser.add_argument('-year', type=int, default=datetime.now().year,
                       help='查询年份')
    parser.add_argument('-show_all', action='store_true',
                       help='显示全年所有节假日信息')
    parser.add_argument('-source', type=str, default='api',
                       choices=['api', 'local'],
                       help='数据源：api(在线API)、local(本地数据)')
    parser.add_argument('-format', type=str, default='simple',
                       choices=['simple', 'detailed'],
                       help='输出格式')
    
    args = parser.parse_args()
    
    # 转换为字典格式
    tool_args = {
        'year': args.year,
        'show_all': args.show_all,
        'source': args.source,
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
