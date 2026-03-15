#!/usr/bin/env python3
"""
测试C组智能体完整流程
验证修复后的代码是否工作正常
"""

import sys
import os
import io

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("测试C组智能体完整流程 (修复后)")
print("=" * 80)

# 准备测试数据
destination_cn = "韩国"
dest_data = {
    "destination": "韩国",
    "highlights": ["首尔", "济州岛", "釜山"],
    "best_season": "春季、秋季",
    "tags": ["购物", "美食", "文化"]
}

style_proposal = {
    "style_name": "探索式",
    "style_type": "exploration",
    "style_description": "多元打卡",
    "daily_pace": "快节奏",
    "intensity_level": 3
}

user_portrait = {
    "description": "喜欢文化和美食",
    "budget_level": "medium"
}

days = 3
start_date = "2025-04-01"

# 导入并测试
print("\n1. 测试schedule_attractions...")
try:
    from tradingagents.agents.group_c import schedule_attractions
    result = schedule_attractions(destination_cn, dest_data, style_proposal, days, start_date, None)
    print(f"   返回类型: {type(result)}")
    print(f"   包含键: {list(result.keys())}")

    scheduled_attractions = result.get("scheduled_attractions", [])
    print(f"   ✅ scheduled_attractions类型: {type(scheduled_attractions)}")
    print(f"   ✅ scheduled_attractions长度: {len(scheduled_attractions)}")

    # 测试切片
    test_slice = scheduled_attractions[:2]
    print(f"   ✅ 切片测试成功: {len(test_slice)} 天")

except Exception as e:
    print(f"   ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n2. 测试plan_transport...")
try:
    from tradingagents.agents.group_c import plan_transport
    result = plan_transport(destination_cn, scheduled_attractions, "medium", None)
    print(f"   ✅ 返回类型: {type(result)}")
    print(f"   ✅ 包含键: {list(result.keys())}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n3. 测试recommend_dining...")
try:
    from tradingagents.agents.group_c import recommend_dining
    result = recommend_dining(destination_cn, scheduled_attractions, "medium", None)
    print(f"   ✅ 返回类型: {type(result)}")
    print(f"   ✅ 包含键: {list(result.keys())}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n4. 测试recommend_accommodation...")
try:
    from tradingagents.agents.group_c import recommend_accommodation
    result = recommend_accommodation(destination_cn, days, "medium", 2, None)
    print(f"   ✅ 返回类型: {type(result)}")
    print(f"   ✅ 包含键: {list(result.keys())}")
except Exception as e:
    print(f"   ❌ 失败: {e}")

print("\n5. 测试format_detailed_guide...")
try:
    from tradingagents.agents.group_c import format_detailed_guide

    transport_plan = {"transport_type": "mixed"}
    dining_plan = {"recommendations": []}
    accommodation_plan = {"recommended_area": "市中心"}
    user_requirements = {"user_portrait": user_portrait}

    result = format_detailed_guide(
        destination_cn,
        style_proposal,
        scheduled_attractions,
        transport_plan,
        dining_plan,
        accommodation_plan,
        user_requirements,
        None
    )
    print(f"   ✅ 返回类型: {type(result)}")
    print(f"   ✅ 包含键: {list(result.keys())}")
    print(f"   ✅ 攻略标题: {result.get('title', '未知')[:50]}")
except Exception as e:
    print(f"   ❌ 失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ C组智能体测试完成")
print("=" * 80)
