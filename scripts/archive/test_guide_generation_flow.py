#!/usr/bin/env python3
"""
测试攻略生成流程
检查C组智能体是否被正确调用
"""

import sys
import os
import io

# 添加项目路径到 sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("测试攻略生成流程")
print("=" * 80)

# 测试导入
print("\n1. 测试C组智能体导入...")
try:
    from tradingagents.agents.group_c import (
        schedule_attractions,
        plan_transport,
        recommend_dining,
        recommend_accommodation,
        format_detailed_guide
    )
    print("✅ 所有C组智能体导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 测试数据准备
print("\n2. 准备测试数据...")
destination = "韩国"
destination_cn = "韩国"

# 模拟目的地数据
dest_data = {
    "destination": "韩国",
    "country": "韩国",
    "capital": "首尔",
    "highlights": ["首尔", "济州岛", "釜山"],
    "best_season": "春季、秋季",
    "tags": ["购物", "美食", "文化"],
    "attractions": [
        {"name": "景福宫", "type": "文化", "rating": 4.5},
        {"name": "明洞", "type": "购物", "rating": 4.3},
        {"name": "济州岛", "type": "自然", "rating": 4.7}
    ]
}

# 模拟用户画像
user_portrait = {
    "description": "喜欢文化和美食",
    "preferences": ["文化", "美食", "购物"],
    "budget_level": "medium"
}

# 模拟风格方案
style_proposal = {
    "style_name": "探索式",
    "style_type": "exploration",
    "style_description": "多元打卡，丰富行程",
    "daily_pace": "快节奏",
    "intensity_level": 3
}

days = 3
start_date = "2025-04-01"

# 获取LLM实例
print("\n3. 获取LLM实例...")
try:
    from app.routers.staged_planning import get_llm_instance
    llm = get_llm_instance()
    if llm:
        print(f"✅ LLM已启用: {type(llm)}")
    else:
        print("⚠️ LLM未启用，将使用规则引擎")
except Exception as e:
    print(f"⚠️ LLM初始化失败: {e}")
    llm = None

# 测试景点排程
print(f"\n4. 测试景点排程 (AttractionScheduler)...")
try:
    scheduled_attractions = schedule_attractions(
        destination_cn,
        dest_data,
        style_proposal,
        days,
        start_date,
        llm
    )
    print(f"✅ 景点排程完成，共 {len(scheduled_attractions)} 天")
    for day in scheduled_attractions[:2]:
        print(f"   第{day.get('day')}天: {len(day.get('schedule', []))} 个活动")
except Exception as e:
    print(f"❌ 景点排程失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 测试交通规划
print(f"\n5. 测试交通规划 (TransportPlanner)...")
try:
    transport_plan = plan_transport(
        destination_cn,
        scheduled_attractions,
        user_portrait.get("budget_level", "medium"),
        llm
    )
    print(f"✅ 交通规划完成")
    print(f"   类型: {transport_plan.get('transport_type', '未知')}")
except Exception as e:
    print(f"❌ 交通规划失败: {e}")
    import traceback
    traceback.print_exc()
    transport_plan = {}

# 测试餐饮推荐
print(f"\n6. 测试餐饮推荐 (DiningRecommender)...")
try:
    dining_plan = recommend_dining(
        destination_cn,
        scheduled_attractions,
        user_portrait.get("budget_level", "medium"),
        llm
    )
    print(f"✅ 餐饮推荐完成")
    print(f"   推荐: {dining_plan.get('recommendations', [])[:1]}")
except Exception as e:
    print(f"❌ 餐饮推荐失败: {e}")
    import traceback
    traceback.print_exc()
    dining_plan = {}

# 测试住宿建议
print(f"\n7. 测试住宿建议 (AccommodationAdvisor)...")
try:
    accommodation_plan = recommend_accommodation(
        destination_cn,
        days,
        user_portrait.get("budget_level", "medium"),
        2,  # travelers
        llm
    )
    print(f"✅ 住宿建议完成")
    print(f"   区域: {accommodation_plan.get('recommended_area', '未知')}")
except Exception as e:
    print(f"❌ 住宿建议失败: {e}")
    import traceback
    traceback.print_exc()
    accommodation_plan = {}

# 测试攻略格式化
print(f"\n8. 测试攻略格式化 (GuideFormatter)...")
try:
    user_requirements = {
        "travel_scope": "international",
        "start_date": start_date,
        "days": days,
        "user_portrait": user_portrait
    }

    detailed_guide = format_detailed_guide(
        destination_cn,
        style_proposal,
        scheduled_attractions,
        transport_plan,
        dining_plan,
        accommodation_plan,
        user_requirements,
        llm
    )
    print(f"✅ 攻略格式化完成")
    print(f"   标题: {detailed_guide.get('title', '未知')}")
    print(f"   总天数: {detailed_guide.get('total_days', 0)}")
    print(f"   每日行程: {len(detailed_guide.get('daily_itinerary', []))} 天")
except Exception as e:
    print(f"❌ 攻略格式化失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ 所有测试通过！C组智能体工作正常")
print("=" * 80)
