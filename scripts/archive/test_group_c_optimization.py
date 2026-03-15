"""
测试C组优化后的性能
验证批量LLM调用是否正常工作
"""

import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_transport_optimization():
    """测试交通规划师批量优化"""
    print("\n" + "="*70)
    print("测试交通规划师批量优化")
    print("="*70)

    from tradingagents.agents.group_c import plan_transport
    from langchain_openai import ChatOpenAI

    # 创建LLM
    llm = ChatOpenAI(
        model='Qwen/Qwen2.5-7B-Instruct',
        api_key=os.getenv('SILICONFLOW_API_KEY', ''),
        base_url='https://api.siliconflow.cn/v1',
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    # 模拟3天的景点安排
    scheduled_attractions = [
        {
            "day": 1,
            "schedule": [
                {"period": "morning", "activity": "故宫", "location": "故宫"},
                {"period": "lunch", "activity": "午餐", "location": "王府井"},
                {"period": "afternoon", "activity": "天坛", "location": "天坛"},
                {"period": "dinner", "activity": "晚餐", "location": "前门"}
            ]
        },
        {
            "day": 2,
            "schedule": [
                {"period": "morning", "activity": "颐和园", "location": "颐和园"},
                {"period": "lunch", "activity": "午餐", "location": "颐和园"},
                {"period": "afternoon", "activity": "圆明园", "location": "圆明园"},
                {"period": "dinner", "activity": "晚餐", "location": "中关村"}
            ]
        },
        {
            "day": 3,
            "schedule": [
                {"period": "morning", "activity": "长城", "location": "八达岭长城"},
                {"period": "lunch", "activity": "午餐", "location": "长城"},
                {"period": "afternoon", "activity": "十三陵", "location": "十三陵"},
                {"period": "dinner", "activity": "晚餐", "location": "市区"}
            ]
        }
    ]

    # 测试批量优化
    print("\n[测试] 交通规划批量优化...")
    start = time.time()

    transport_plan = plan_transport(
        destination="北京",
        scheduled_attractions=scheduled_attractions,
        budget_level="medium",
        llm=llm
    )

    duration = time.time() - start

    # 统计路段数量
    total_segments = sum(len(day.get("transport_segments", [])) for day in transport_plan.get("daily_transport", []))

    print(f"完成: {duration:.2f}秒")
    print(f"总路段数: {total_segments}")
    print(f"总费用: {transport_plan.get('total_transport_cost', 0)}元")

    # 检查是否有AI解释
    segments_with_explanation = 0
    for day in transport_plan.get("daily_transport", []):
        for segment in day.get("transport_segments", []):
            if segment.get("ai_explanation"):
                segments_with_explanation += 1

    print(f"有AI解释的路段: {segments_with_explanation}/{total_segments}")

    # 显示第一个路段的解释示例
    if segments_with_explanation > 0:
        for day in transport_plan.get("daily_transport", []):
            for segment in day.get("transport_segments", []):
                if segment.get("ai_explanation"):
                    print(f"\n示例路段解释:")
                    print(f"  {segment.get('route')}")
                    print(f"  解释: {segment.get('ai_explanation')[:100]}...")
                    break
            else:
                continue
            break

    return duration, total_segments


def test_dining_optimization():
    """测试餐饮推荐师批量优化"""
    print("\n" + "="*70)
    print("测试餐饮推荐师批量优化")
    print("="*70)

    from tradingagents.agents.group_c import recommend_dining
    from langchain_openai import ChatOpenAI

    # 创建LLM
    llm = ChatOpenAI(
        model='Qwen/Qwen2.5-7B-Instruct',
        api_key=os.getenv('SILICONFLOW_API_KEY', ''),
        base_url='https://api.siliconflow.cn/v1',
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    # 使用与交通相同的测试数据
    scheduled_attractions = [
        {
            "day": 1,
            "schedule": [
                {"period": "morning", "activity": "故宫", "location": "故宫"},
                {"period": "lunch", "activity": "午餐", "location": "故宫"},
                {"period": "afternoon", "activity": "天坛", "location": "天坛"},
                {"period": "dinner", "activity": "晚餐", "location": "天坛"}
            ]
        },
        {
            "day": 2,
            "schedule": [
                {"period": "morning", "activity": "颐和园", "location": "颐和园"},
                {"period": "lunch", "activity": "午餐", "location": "颐和园"},
                {"period": "afternoon", "activity": "圆明园", "location": "圆明园"},
                {"period": "dinner", "activity": "晚餐", "location": "圆明园"}
            ]
        },
        {
            "day": 3,
            "schedule": [
                {"period": "morning", "activity": "长城", "location": "八达岭长城"},
                {"period": "lunch", "activity": "午餐", "location": "长城"},
                {"period": "afternoon", "activity": "十三陵", "location": "十三陵"},
                {"period": "dinner", "activity": "晚餐", "location": "十三陵"}
            ]
        }
    ]

    # 测试批量优化
    print("\n[测试] 餐饮推荐批量优化...")
    start = time.time()

    dining_plan = recommend_dining(
        destination="北京",
        scheduled_attractions=scheduled_attractions,
        budget_level="medium",
        llm=llm
    )

    duration = time.time() - start

    # 统计用餐推荐数量
    total_meals = 0
    meals_with_explanation = 0

    for day_dining in dining_plan.get("daily_dining", []):
        if day_dining.get("lunch"):
            total_meals += 1
            if day_dining["lunch"].get("ai_explanation"):
                meals_with_explanation += 1
        if day_dining.get("dinner"):
            total_meals += 1
            if day_dining["dinner"].get("ai_explanation"):
                meals_with_explanation += 1

    print(f"完成: {duration:.2f}秒")
    print(f"总用餐推荐: {total_meals}")
    print(f"有AI解释的用餐: {meals_with_explanation}/{total_meals}")

    # 显示第一个用餐推荐的解释示例
    if meals_with_explanation > 0:
        for day_dining in dining_plan.get("daily_dining", []):
            if day_dining.get("lunch") and day_dining["lunch"].get("ai_explanation"):
                print(f"\n示例午餐推荐解释:")
                print(f"  区域: {day_dining['lunch'].get('recommended_area')}")
                print(f"  餐厅: {day_dining['lunch'].get('restaurant_name')}")
                print(f"  解释: {day_dining['lunch'].get('ai_explanation')[:100]}...")
                break

    return duration, total_meals


def test_accommodation_optimization():
    """测试住宿顾问批量优化"""
    print("\n" + "="*70)
    print("测试住宿顾问批量优化")
    print("="*70)

    from tradingagents.agents.group_c import recommend_accommodation
    from langchain_openai import ChatOpenAI

    # 创建LLM
    llm = ChatOpenAI(
        model='Qwen/Qwen2.5-7B-Instruct',
        api_key=os.getenv('SILICONFLOW_API_KEY', ''),
        base_url='https://api.siliconflow.cn/v1',
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )

    # 测试批量优化
    print("\n[测试] 住宿推荐批量优化...")
    start = time.time()

    accommodation_plan = recommend_accommodation(
        destination="北京",
        days=3,
        budget_level="medium",
        travelers=2,
        llm=llm
    )

    duration = time.time() - start

    print(f"完成: {duration:.2f}秒")
    print(f"推荐区域: {accommodation_plan.get('recommended_area', {}).get('area')}")
    print(f"总费用: {accommodation_plan.get('accommodation_cost', {}).get('total_cost', 0)}元")

    # 检查是否有AI解释
    has_area_explanation = bool(accommodation_plan.get('recommended_area', {}).get('ai_explanation'))
    has_llm_description = bool(accommodation_plan.get('llm_description'))

    print(f"有区域解释: {has_area_explanation}")
    print(f"有整体描述: {has_llm_description}")

    if has_area_explanation:
        print(f"\n区域解释示例:")
        print(f"  {accommodation_plan['recommended_area']['ai_explanation'][:100]}...")

    return duration


def main():
    print("="*70)
    print("C组批量优化性能测试")
    print("="*70)

    try:
        # 测试交通规划
        transport_time, transport_segments = test_transport_optimization()

        # 测试餐饮推荐
        dining_time, dining_meals = test_dining_optimization()

        # 测试住宿推荐
        accommodation_time = test_accommodation_optimization()

        # 汇总结果
        print("\n" + "="*70)
        print("性能测试汇总")
        print("="*70)
        print(f"\n{'智能体':<20} {'耗时':<15} {'处理数量':<15}")
        print("-"*70)
        print(f"{'交通规划师':<20} {transport_time:<15.2f} {transport_segments:<15}")
        print(f"{'餐饮推荐师':<20} {dining_time:<15.2f} {dining_meals:<15}")
        print(f"{'住宿顾问':<20} {accommodation_time:<15.2f} {'1个区域':<15}")
        print("-"*70)
        total_time = transport_time + dining_time + accommodation_time
        print(f"{'总计':<20} {total_time:<15.2f}")

        print("\n优化说明:")
        print("  交通规划: ~6-9次LLM调用 -> 1次批量调用")
        print("  餐饮推荐: ~6次LLM调用 -> 1次批量调用")
        print("  住宿推荐: 2次LLM调用 -> 1次批量调用")
        print(f"  总计优化: ~14-17次 -> ~3次 (减少约80%)")

    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
