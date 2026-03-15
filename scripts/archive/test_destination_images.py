#!/usr/bin/env python3
"""
测试目的地图片API
验证修复后的Unsplash服务是否正常工作
"""

import sys
import os

# Fix Windows encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json

BASE_URL = "http://127.0.0.1:8005"

def test_destination_image(city: str):
    """测试目的地图片API"""
    url = f"{BASE_URL}/api/travel/images/destination/{city}"
    params = {"width": 800, "height": 600}

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            image_url = data.get("url", "")
            source = data.get("source", "unknown")

            # 判断图片来源
            if "unsplash.com" in image_url:
                status = "✅ Unsplash"
            elif "pexels.com" in image_url:
                status = "✅ Pexels"
            elif "loremflickr.com" in image_url:
                status = "⚠️ LoremFlickr"
            elif "placehold.co" in image_url:
                status = "❌ Placeholder"
            else:
                status = "❓ Unknown"

            print(f"{status} | {city:12s} | {source:12s} | {image_url[:60]}...")
            return source == "unsplash"
        else:
            print(f"❌ | {city:12s} | HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ | {city:12s} | Error: {e}")
        return False

def main():
    print("测试目的地图片API")
    print("=" * 100)
    print(f"{'状态':<15} | {'目的地':<12s} | {'来源':<12s} | {'URL'}")
    print("-" * 100)

    # 测试国家/地区
    destinations = ["韩国", "泰国", "日本", "新加坡", "马来西亚", "越南", "印尼"]

    unsplash_count = 0
    for dest in destinations:
        if test_destination_image(dest):
            unsplash_count += 1

    print("-" * 100)
    print(f"结果: {unsplash_count}/{len(destinations)} 使用了 Unsplash")

    if unsplash_count == len(destinations):
        print("✅ 所有目的地都使用了 Unsplash API")
    else:
        print("⚠️ 部分目的地未使用 Unsplash API，可能需要重启后端服务")

if __name__ == "__main__":
    main()
