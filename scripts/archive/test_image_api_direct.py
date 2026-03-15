"""
测试图片API是否正常工作
"""
import requests

# 测试不同端口
ports = [8005, 8006, 8000, 8080]

print("=" * 60)
print("测试图片API连接...")
print("=" * 60)

for port in ports:
    try:
        url = f"http://localhost:{port}/api/travel/images/attraction"
        params = {
            "attraction_name": "圣淘沙",
            "city": "新加坡",
            "width": 200,
            "height": 150
        }

        print(f"\n尝试端口 {port}...")
        response = requests.get(url, params=params, timeout=5)

        if response.status_code == 200:
            data = response.json()
            image_url = data.get("url", "")
            print(f"✅ 端口 {port} 连接成功!")
            print(f"   返回URL: {image_url[:80]}...")
        else:
            print(f"❌ 端口 {port} 返回状态码: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"❌ 端口 {port} 无法连接（连接被拒绝）")
    except Exception as e:
        print(f"❌ 端口 {port} 出错: {str(e)[:50]}")

print("\n" + "=" * 60)
