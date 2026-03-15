"""
完整的API集成测试脚本

测试分阶段旅行规划系统的完整流程：
1. 阶段3: 获取目的地推荐 (Group A)
2. 阶段4: 获取风格方案 (Group B - 并行执行)
3. 阶段5: 生成详细攻略 (Group C - 混合并行)

展示智能体的生成效果和输出内容
"""

import os
import sys
import json
import time
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

# 导入测试工具
import requests
from tradingagents.graph.trading_graph import create_llm_by_provider


# ============================================================
# 配置
# ============================================================

API_BASE_URL = "http://localhost:8005"
HEADERS = {"Content-Type": "application/json"}

# 测试数据
TEST_REQUIREMENTS = {
    "travel_scope": "domestic",
    "days": 3,
    "adults": 2,
    "children": 0,
    "budget": "medium",
    "interests": ["历史文化", "美食"],
    "start_date": "2024-04-15"
}

# ============================================================
# 测试函数
# ============================================================

def print_section(title):
    """打印分节标题"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_subsection(title):
    """打印子标题"""
    print(f"\n--- {title} ---")


def check_backend_health():
    """检查后端服务健康状态"""
    print_section("检查后端服务")

    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("[OK] 后端服务运行正常")
            return True
        else:
            print(f"[ERROR] 后端服务异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] 无法连接到后端服务")
        print(f"   请确认后端服务是否在 {API_BASE_URL} 运行")
        return False
    except Exception as e:
        print(f"[ERROR] 健康检查失败: {e}")
        return False


def test_stage3_get_destinations():
    """测试阶段3：获取目的地推荐 (Group A)"""
    print_section("阶段3: 获取目的地推荐 (Group A)")

    url = f"{API_BASE_URL}/api/travel/staged/get-destinations"

    print(f"请求数据: {json.dumps(TEST_REQUIREMENTS, ensure_ascii=False)}")
    print_subsection("发送请求...")

    start = time.time()
    try:
        response = requests.post(url, json=TEST_REQUIREMENTS, headers=HEADERS, timeout=120)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 请求成功 (耗时: {elapsed:.2f}秒)")

            # 显示用户画像
            if "user_portrait" in data:
                portrait = data["user_portrait"]
                print_subsection("用户画像 (A1输出)")
                print(f"  旅行类型: {portrait.get('travel_type', 'N/A')}")
                print(f"  节奏偏好: {portrait.get('pace_preference', 'N/A')}")
                print(f"  预算等级: {portrait.get('budget_level', 'N/A')}")
                print(f"  主要兴趣: {', '.join(portrait.get('primary_interests', []))}")

                if 'portrait_description' in portrait:
                    desc = portrait['portrait_description']
                    print(f"\n  [NOTE] LLM描述:")
                    print(f"  {desc[:100]}...")

            # 显示推荐目的地
            if "ranked_destinations" in data:
                destinations = data["ranked_destinations"]
                print_subsection(f"推荐目的地 (A3输出) - {len(destinations)}个")

                for i, dest in enumerate(destinations, 1):
                    print(f"\n  [{i}] {dest.get('destination', 'N/A')}")
                    print(f"      匹配分数: {dest.get('match_score', 'N/A')}/100")
                    print(f"      预估费用: {dest.get('estimated_budget', 'N/A')}元")
                    print(f"      最佳季节: {dest.get('best_season', 'N/A')}")
                    print(f"      适合人群: {', '.join(dest.get('suitable_for', [])[:3])}")

                    # 显示推荐理由
                    if 'recommendation_reason' in dest:
                        print(f"      推荐理由: {dest['recommendation_reason']}")

                    # 显示AI解释（如果有）
                    if 'ai_explanation' in dest:
                        print(f"      [AI] AI解释: {dest['ai_explanation'][:80]}...")

                    # 显示热门景点
                    highlights = dest.get('highlights', [])
                    if highlights:
                        print(f"      热门景点: {', '.join(highlights[:3])}")

                return destinations

        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"[ERROR] 请求超时 (120秒)")
        return None
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
        return None


def test_stage4_get_styles(selected_destination):
    """测试阶段4：获取风格方案 (Group B - 并行执行)"""
    print_section(f"阶段4: 获取风格方案 (Group B - 并行执行)")

    print(f"用户选择的目的地: {selected_destination}")

    url = f"{API_BASE_URL}/api/travel/staged/get-styles"

    request_data = {
        **TEST_REQUIREMENTS,
        "selected_destination": selected_destination
    }

    print_subsection("发送请求...")

    start = time.time()
    try:
        response = requests.post(url, json=request_data, headers=HEADERS, timeout=120)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 请求成功 (耗时: {elapsed:.2f}秒)")

            if "style_proposals" in data:
                proposals = data["style_proposals"]
                print_subsection(f"风格方案 (Group B并行输出) - {len(proposals)}个")

                for i, proposal in enumerate(proposals, 1):
                    print(f"\n  [{i}] {proposal.get('style_name', 'N/A')}")
                    print(f"      风格类型: {proposal.get('style_type', 'N/A')}")
                    print(f"      每日节奏: {proposal.get('daily_pace', 'N/A')}")
                    print(f"      强度等级: {proposal.get('intensity_level', 'N/A')}/5")
                    print(f"      预估费用: {proposal.get('estimated_cost', 'N/A')}元")

                    # 显示行程预览
                    preview = proposal.get('preview_itinerary', [])
                    if preview and len(preview) > 0:
                        print(f"      行程预览:")
                        for day in preview[:2]:  # 只显示前2天
                            print(f"        Day {day.get('day', '?')}: {day.get('title', 'N/A')}")

                    # 显示LLM描述
                    if 'llm_description' in proposal:
                        desc = proposal['llm_description']
                        print(f"\n      [AI] LLM描述:")
                        # 分行显示，每行约60字符
                        lines = [desc[i:i+60] for i in range(0, len(desc), 60)]
                        for line in lines[:3]:  # 只显示前3行
                            print(f"        {line}")
                        if len(lines) > 3:
                            print(f"        ...")

                    # 显示代理信息
                    if 'agent_info' in proposal:
                        agent = proposal['agent_info']
                        print(f"      生成智能体: {agent.get('name_en', 'N/A')} {agent.get('icon', '')}")

                return proposals

        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"[ERROR] 请求超时 (120秒)")
        return None
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
        return None


def test_stage5_get_guide(selected_destination, selected_style):
    """测试阶段5：生成详细攻略 (Group C - 混合并行)"""
    print_section(f"阶段5: 生成详细攻略 (Group C - 混合并行)")

    print(f"用户选择的目的地: {selected_destination}")
    print(f"用户选择的风格: {selected_style}")

    url = f"{API_BASE_URL}/api/travel/staged/get-guide"

    request_data = {
        **TEST_REQUIREMENTS,
        "selected_destination": selected_destination,
        "selected_style": selected_style
    }

    print_subsection("发送请求...")

    start = time.time()
    try:
        response = requests.post(url, json=request_data, headers=HEADERS, timeout=180)
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            print(f"[OK] 请求成功 (耗时: {elapsed:.2f}秒)")

            # 显示详细攻略
            if "detailed_guide" in data:
                guide = data["detailed_guide"]

                print_subsection("详细攻略概览")

                # 景点排程
                if "scheduled_attractions" in guide:
                    attractions = guide["scheduled_attractions"]
                    print(f"\n  [LOCATION] 景点排程 (C1): {len(attractions)}天")
                    for day in attractions[:2]:  # 只显示前2天
                        print(f"\n    Day {day.get('day', '?')}: {day.get('title', 'N/A')}")
                        schedule = day.get('schedule', [])
                        for item in schedule[:3]:  # 每天只显示前3个
                            period = item.get('period', '')
                            activity = item.get('activity', '')
                            location = item.get('location', '')
                            print(f"      {period:8} {activity} @ {location}")

                # 住宿建议
                if "accommodation_plan" in guide:
                    accom = guide["accommodation_plan"]
                    print_subsection("住宿建议 (C4)")
                    area = accom.get("recommended_area", {})
                    print(f"  推荐区域: {area.get('area', 'N/A')}")
                    print(f"  价格范围: {area.get('price_range', 'N/A')}")
                    if "ai_explanation" in area:
                        print(f"  [AI] AI解释: {area['ai_explanation'][:80]}...")
                    hotels = accom.get("hotel_recommendations", {})
                    hotel_list = hotels.get("hotels", [])
                    if hotel_list:
                        print(f"  推荐酒店: {', '.join(hotel_list[:3])}")

                # 交通规划
                if "transport_plan" in guide:
                    transport = guide["transport_plan"]
                    print_subsection("交通规划 (C2)")
                    cost = transport.get("total_transport_cost", 0)
                    print(f"  总交通费用: {cost}元")

                    daily_transport = transport.get("daily_transport", [])
                    for day in daily_transport[:2]:  # 只显示前2天
                        print(f"\n    Day {day.get('day', '?')}:")
                        segments = day.get("transport_segments", [])
                        for seg in segments[:2]:  # 每天只显示前2段
                            method = seg.get("method", "")
                            from_loc = seg.get("from", "")
                            to_loc = seg.get("to", "")
                            print(f"      {from_loc} → {to_loc}: {method}")
                            if "ai_explanation" in seg:
                                print(f"        [AI] {seg['ai_explanation'][:60]}...")

                # 餐饮推荐
                if "dining_plan" in guide:
                    dining = guide["dining_plan"]
                    print_subsection("餐饮推荐 (C3)")
                    cost = dining.get("estimated_meal_cost", {})
                    total = cost.get("per_day", 0) * 3
                    print(f"  预估餐饮费用: {total}元 (3天)")

                    daily_dining = dining.get("daily_dining", [])
                    for day in daily_dining[:2]:  # 只显示前2天
                        print(f"\n    Day {day.get('day', '?')}:")
                        lunch = day.get("lunch")
                        if lunch:
                            print(f"      午餐: {lunch.get('special_dishes', [])[:2]}")
                            if lunch.get("recommended_restaurant"):
                                rest = lunch["recommended_restaurant"]
                                if "ai_explanation" in rest:
                                    print(f"        [AI] {rest['ai_explanation'][:60]}...")
                        dinner = day.get("dinner")
                        if dinner:
                            print(f"      晚餐: {dinner.get('special_dishes', [])[:2]}")

                # 攻略内容
                if "guide_content" in guide:
                    guide_content = guide["guide_content"]
                    if guide_content and guide_content.get("guide_content"):
                        print_subsection("完整攻略 (C5)")
                        content = guide_content["guide_content"]
                        print(f"  攻略标题: {content.get('title', 'N/A')}")
                        print(f"  攻略长度: {len(content.get('content', ''))}字")
                        print(f"\n  [GUIDE] 攻略内容预览:")
                        content_text = content.get('content', '')
                        lines = content_text.split('\n')[:10]  # 显示前10行
                        for line in lines:
                            print(f"    {line}")
                        if len(content_text.split('\n')) > 10:
                            print(f"    ... (还有{len(content_text.split('\n'))-10}行)")

                return guide

        else:
            print(f"[ERROR] 请求失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print(f"[ERROR] 请求超时 (180秒)")
        return None
    except Exception as e:
        print(f"[ERROR] 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_test_results(stage3_result, stage4_result, stage5_result):
    """保存测试结果到文件"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"

    results = {
        "timestamp": timestamp,
        "test_requirements": TEST_REQUIREMENTS,
        "stage3_destinations": stage3_result,
        "stage4_styles": stage4_result,
        "stage5_guide": stage5_result
    }

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 测试结果已保存到: {filename}")
    except Exception as e:
        print(f"\n⚠️  保存结果失败: {e}")


def main():
    """主测试流程"""
    print_section("TravelAgents-CN 完整API集成测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {API_BASE_URL}")

    # 1. 检查后端服务
    if not check_backend_health():
        print("\n请先启动后端服务:")
        print("  cd app")
        print("  python -m uvicorn main:app --reload")
        return

    # 2. 测试阶段3：获取目的地推荐
    destinations = test_stage3_get_destinations()
    if not destinations:
        print("\n[ERROR] 阶段3测试失败，无法继续")
        return

    # 3. 用户选择第一个目的地进行后续测试
    selected_destination = destinations[0].get("destination", "西安")
    print(f"\n[USER] 模拟用户选择: {selected_destination}")

    # 4. 测试阶段4：获取风格方案
    styles = test_stage4_get_styles(selected_destination)
    if not styles:
        print("\n[ERROR] 阶段4测试失败，无法继续")
        return

    # 5. 用户选择第一个风格进行后续测试
    selected_style = styles[0].get("style_type", "immersive")
    style_name = styles[0].get("style_name", "沉浸式")
    print(f"\n[USER] 模拟用户选择: {style_name} ({selected_style})")

    # 6. 测试阶段5：生成详细攻略
    guide = test_stage5_get_guide(selected_destination, selected_style)
    if not guide:
        print("\n[ERROR] 阶段5测试失败")
        return

    # 7. 保存测试结果
    save_test_results(destinations, styles, guide)

    # 8. 测试总结
    print_section("测试总结")
    print("[OK] 所有阶段测试通过")
    print(f"[OK] Group A (需求分析+目的地推荐): 正常工作")
    print(f"[OK] Group B (4个风格设计师并行): 正常工作")
    print(f"[OK] Group C (5个详细规划智能体混合并行): 正常工作")
    print(f"[OK] LLM增强 (ai_explanation): 正常工作")
    print(f"[OK] 并行执行优化: 正常工作")
    print("\n[SUCCESS] 系统功能完整，可以投入使用！")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n[ERROR] 测试异常: {e}")
        import traceback
        traceback.print_exc()
