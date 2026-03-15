#!/usr/bin/env python3
"""
TradingAgents-CN 核心模块

已从股票分析系统改造为旅行规划系统。
"""

__version__ = "2.0.0-travel"
__author__ = "TradingAgents-CN Team"
__description__ = "Multi-agent travel planning system"

__all__ = [
    "__version__",
    "__author__",
    "__description__"
]

# 注意：不再自动导入 config_manager，因为它需要数据库连接
# 需要使用配置系统时，手动导入：
# from tradingagents.config import config_manager
