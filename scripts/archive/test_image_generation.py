#!/usr/bin/env python3
"""
测试图片生成服务
验证不同国家和城市的图片URL生成是否正确
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.services.attraction_image_service import get_attraction_image

# 测试用例：不同国家和城市
test_cases = [
    # 国家名
    ("泰国", "泰国", 800, 600),
    ("韩国", "韩国", 800, 600),
    ("日本", "日本", 800, 600),
    ("新加坡", "新加坡", 800, 600),

    # 城市名
    ("曼谷", "泰国", 800, 600),
    ("首尔", "韩国", 800, 600),
    ("东京", "日本", 800, 600),
    ("北京", "中国", 800, 600),
    ("上海", "中国", 800, 600),
    ("成都", "中国", 800, 600),
]

print("=" * 80)
print("图片生成测试")
print("=" * 80)
print()

for attraction, city, width, height in test_cases:
    try:
        url = get_attraction_image(attraction, city, width, height)

        # 判断图片来源
        if "unsplash.com" in url:
            source = "Unsplash ✅"
        elif "pexels.com" in url:
            source = "Pexels ✅"
        elif "loremflickr.com" in url:
            source = "LoremFlickr ⚠️"
        elif "placehold.co" in url:
            source = "占位图 ⚠️"
        else:
            source = "未知 ❓"

        print(f"景点: {attraction:10s} | 城市: {city:10s} | {source}")
        print(f"URL: {url}")
        print()

    except Exception as e:
        print(f"景点: {attraction:10s} | 城市: {city:10s} | 错误: {e}")
        print()

print("=" * 80)
print("测试完成")
print("=" * 80)
