#!/usr/bin/env python3
"""
测试后端图片API服务
验证Unsplash配置是否正确工作
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

import requests

# 测试Unsplash API Key
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
print(f"Unsplash Access Key: {UNSPLASH_ACCESS_KEY[:20]}..." if UNSPLASH_ACCESS_KEY else "None")

# 测试Unsplash API
if UNSPLASH_ACCESS_KEY and UNSPLASH_ACCESS_KEY != "your_unsplash_key_here":
    print("\n测试Unsplash API...")

    test_queries = [
        ("thailand travel", "泰国"),
        ("south korea travel", "韩国"),
        ("tokyo city", "日本东京"),
        ("singapore city", "新加坡"),
    ]

    for query, desc in test_queries:
        try:
            url = f"https://api.unsplash.com/search/photos"
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }
            headers = {
                "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get("results"):
                    image_url = data["results"][0]["urls"]["regular"]
                    print(f"✅ {desc:12s} -> {image_url[:60]}...")
                else:
                    print(f"⚠️ {desc:12s} -> 无搜索结果")
            else:
                print(f"❌ {desc:12s} -> API错误 {response.status_code}")
        except Exception as e:
            print(f"❌ {desc:12s} -> {e}")
else:
    print("\n❌ Unsplash API Key 未配置或为占位符")
    print("请在.env文件中设置有效的 UNSPLASH_ACCESS_KEY")
