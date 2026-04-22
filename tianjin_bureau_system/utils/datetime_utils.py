# -*- coding: utf-8 -*-
"""
日期工具
"""
from datetime import datetime


def get_current_datetime():
    """获取当前日期时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_date():
    """获取当前日期"""
    return datetime.now().strftime("%Y-%m-%d")


def format_datetime(dt):
    """格式化日期时间"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt


def format_date(d):
    """格式化日期"""
    if isinstance(d, datetime):
        return d.strftime("%Y-%m-%d")
    return d