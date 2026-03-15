"""
测试天行数据文旅新闻接口（正确的接口）

根据官方文档测试 https://apis.tianapi.com/travel/index
"""
import os
import sys
import io
import requests

# 设置UTF-8编码输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 天行数据配置
API_KEY = "8879cb7f41e435e278a404fe2be791ae"

# 正确的文旅新闻接口
TRAVEL_NEWS_URL = "https://apis.tianapi.com/travel/index"


def test_travel_news_api(keyword, num=10):
    """测试文旅新闻API"""
    print(f"\n{'='*70}")
    print(f"  天行数据 - 文旅新闻接口测试")
    print(f"{'='*70}")
    print(f"  接口地址: {TRAVEL_NEWS_URL}")
    print(f"  API Key: {API_KEY[:20]}...")
    print(f"  搜索关键词: {keyword}")
    print(f"  返回数量: {num}")
    print(f"{'='*70}\n")

    params = {
        "key": API_KEY,
        "word": keyword,
        "num": num,
        "form": 1  # 建议传1
    }

    try:
        response = requests.get(TRAVEL_NEWS_URL, params=params, timeout=10)

        print(f"HTTP状态码: {response.status_code}")

        data = response.json()

        print(f"响应代码: {data.get('code', 'N/A')}")
        print(f"响应消息: {data.get('msg', 'N/A')}")

        if data.get("code") == 200:
            result = data.get("result", {})
            news_list = result.get("list", [])
            all_num = result.get("allnum", 0)

            print(f"\n✓ 成功获取新闻!")
            print(f"  - 返回数量: {len(news_list)}")
            print(f"  - 总数量: {all_num}")
            print(f"  - 当前页: {result.get('curpage', 1)}")

            if news_list:
                print(f"\n📰 新闻列表:")
                for i, news in enumerate(news_list, 1):
                    print(f"\n  [{i}] {news.get('title', 'N/A')}")
                    print(f"      来源: {news.get('source', 'N/A')}")
                    print(f"      时间: {news.get('ctime', 'N/A')}")
                    print(f"      链接: {news.get('url', 'N/A')}")

                    desc = news.get('description', 'N/A')
                    if desc != 'N/A' and desc:
                        print(f"      摘要: {desc[:80]}...")

                    pic_url = news.get('picUrl', '')
                    if pic_url:
                        print(f"      图片: {pic_url}")

            return True, len(news_list)
        else:
            error_code = data.get('code')
            error_msg = data.get('msg', '未知错误')

            print(f"\n✗ API返回错误")
            print(f"  错误代码: {error_code}")
            print(f"  错误消息: {error_msg}")

            # 常见错误代码说明
            error_meanings = {
                150: "API可用次数不足",
                160: "接口未申请或未通过审核",
                170: "API Key错误",
                250: "数据返回为空",
                260: "参数错误"
            }

            if error_code in error_meanings:
                print(f"  说明: {error_meanings[error_code]}")

            return False, 0

    except requests.exceptions.Timeout:
        print(f"\n✗ 请求超时")
        return False, 0
    except Exception as e:
        print(f"\n✗ 请求失败: {e}")
        import traceback
        traceback.print_exc()
        return False, 0


def test_multiple_keywords():
    """测试多个关键词"""
    keywords = [
        "杭州",
        "北京",
        "成都",
        "旅游",
        "景区"
    ]

    results = []

    for keyword in keywords:
        success, count = test_travel_news_api(keyword, num=5)
        results.append((keyword, success, count))

    # 汇总结果
    print(f"\n\n{'='*70}")
    print(f"  测试结果汇总")
    print(f"{'='*70}")

    total_success = 0
    total_count = 0

    for keyword, success, count in results:
        status = "✓" if success else "✗"
        print(f"  {status} {keyword:10} - {count} 条")
        if success:
            total_success += 1
        total_count += count

    print(f"\n总计: {total_count} 条新闻 (成功 {total_success}/{len(keywords)} 个关键词)")

    return total_success == len(keywords)


def main():
    """主函数"""
    print("\n" + "="*70)
    print("  天行数据文旅新闻接口测试")
    print("  接口文档: https://www.tianapi.com/apiview/156")
    print("="*70)

    # 测试单个关键词
    success, count = test_travel_news_api("杭州", num=5)

    if success:
        print("\n" + "="*70)
        print("🎉 文旅新闻接口测试成功!")
        print("="*70)
        print("\n接口配置正确，可以开始使用真实新闻数据了。")
        print("\n下一步:")
        print("  - 系统会自动在旅行规划时调用此接口")
        print("  - 获取的目的地新闻会显示在规划结果中")
        print("  - 无需额外配置，已自动启用")
    else:
        print("\n" + "="*70)
        print("⚠ 接口测试失败")
        print("="*70)
        print("\n可能的原因:")
        print("  1. API Key未配置或错误")
        print("  2. 文旅新闻接口未申请")
        print("  3. 网络连接问题")
        print("\n建议:")
        print("  - 登录天行数据检查: https://www.tianapi.com/")
        print("  - 确认文旅新闻接口已申请")
        print("  - 检查API Key是否正确")


if __name__ == "__main__":
    main()
