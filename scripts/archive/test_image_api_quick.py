"""
快速测试后端图片API是否正常工作
"""
import requests
import time

def test_image_api():
    # 测试端口
    ports = [8005, 8006]

    # 测试景点
    attractions = [
        ("圣淘沙", "新加坡"),
        ("滨海湾", "新加坡"),
        ("乌节路", "新加坡"),
    ]

    print("=" * 60)
    print("测试后端图片API")
    print("=" * 60)

    working_port = None

    # 找到工作的端口
    for port in ports:
        try:
            url = f"http://localhost:{port}/api/travel/images/attraction"
            params = {
                "attraction_name": "圣淘沙",
                "city": "新加坡",
                "width": 200,
                "height": 150
            }

            print(f"\n测试端口 {port}...")
            response = requests.get(url, params=params, timeout=3)

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("url", "")
                print(f"✅ 端口 {port} 连接成功!")
                print(f"   返回URL: {image_url[:80]}...")

                if image_url and "placehold.co" not in image_url:
                    print(f"   ✅ 获取到真实图片!")
                    working_port = port
                    break
                else:
                    print(f"   ⚠️ 返回的是占位图")
            else:
                print(f"❌ 端口 {port} 返回状态码: {response.status_code}")

        except requests.exceptions.ConnectionError:
            print(f"❌ 端口 {port} 无法连接")
        except Exception as e:
            print(f"❌ 端口 {port} 出错: {str(e)[:50]}")

    if not working_port:
        print("\n❌ 没有找到可用的端口!")
        return

    print(f"\n使用端口 {working_port} 进行详细测试...")
    print("-" * 60)

    # 测试多个景点
    for attraction_name, city in attractions:
        try:
            url = f"http://localhost:{working_port}/api/travel/images/attraction"
            params = {
                "attraction_name": attraction_name,
                "city": city,
                "width": 200,
                "height": 150
            }

            start = time.time()
            response = requests.get(url, params=params, timeout=5)
            elapsed = time.time() - start

            if response.status_code == 200:
                data = response.json()
                image_url = data.get("url", "")
                source = data.get("source", "")
                print(f"✅ {attraction_name} ({city})")
                print(f"   来源: {source}")
                print(f"   URL: {image_url[:80]}...")
                print(f"   耗时: {elapsed:.2f}秒")
            else:
                print(f"❌ {attraction_name}: HTTP {response.status_code}")

        except Exception as e:
            print(f"❌ {attraction_name}: {str(e)[:50]}")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test_image_api()
