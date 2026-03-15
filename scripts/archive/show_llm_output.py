"""
展示智能体的LLM自然语言输出

对比结构化数据和LLM生成的自然语言描述
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

# 导入
from tradingagents.graph.trading_graph import create_llm_by_provider
from tradingagents.agents.group_a import UserRequirementAnalyst
from tradingagents.agents.group_b import ImmersiveDesignerAgent

# 创建LLM
llm = create_llm_by_provider(
    provider=os.getenv("LLM_PROVIDER", "siliconflow"),
    model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
    backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
    temperature=0.7,
    max_tokens=2000,
    timeout=60
)

requirements = {
    'travel_scope': 'domestic',
    'days': 5,
    'adults': 2,
    'budget': 'medium',
    'interests': ['历史文化', '美食']
}

dest_data = {
    "tags": ["历史文化", "美食"],
    "highlights": ["兵马俑", "大雁塔"],
    "budget_level": {"medium": 500}
}

print("=" * 70)
print("  智能体输出模式演示")
print("  结构化数据 + LLM自然语言")
print("=" * 70)

# A1: 需求分析
print("\n【A1】UserRequirementAnalyst 输出:")
print("-" * 70)

analyst = UserRequirementAnalyst(llm=llm)
analyst.initialize()
portrait = analyst.analyze_requirements(requirements)
analyst.shutdown()

print("\n[结构化字段] - 用于程序处理:")
print(f"  travel_type: {portrait['travel_type']}")
print(f"  pace_preference: {portrait['pace_preference']}")
print(f"  budget_level: {portrait['budget_level']}")
print(f"  primary_interests: {portrait['primary_interests']}")

print("\n[LLM自然语言] - 用于用户阅读:")
print(f"  {portrait['portrait_description'][:150]}...")

# B1: 沉浸式设计
print("\n" + "=" * 70)
print("【B1】ImmersiveDesigner 输出:")
print("-" * 70)

designer = ImmersiveDesignerAgent(llm=llm)
designer.initialize()
proposal = designer.create_proposal("西安", dest_data, portrait, 5)
designer.shutdown()

print("\n[结构化字段] - 用于前端渲染:")
print(f"  style_name: {proposal['style_name']}")
print(f"  daily_pace: {proposal['daily_pace']}")
print(f"  intensity_level: {proposal['intensity_level']}")
print(f"  estimated_cost: {proposal['estimated_cost']}")

print("\n[LLM自然语言] - 用于方案介绍:")
if 'llm_description' in proposal:
    desc = proposal['llm_description']
elif 'description' in proposal:
    desc = proposal['description']
else:
    desc = str(proposal.get('preview_itinerary', ''))

print(f"  {desc[:200]}...")

print("\n" + "=" * 70)
print("  输出模式总结")
print("=" * 70)

print("""
【结构化数据】
- 用途: API返回、前端渲染、数据存储
- 特点: 机器可读、格式固定、便于处理
- 示例: {"travel_type": "情侣游", "days": 5}

【LLM自然语言】
- 用途: 向用户展示、提供个性化解释
- 特点: 人类可读、个性化、有温度
- 示例: "这是一对向往深度文化之旅的情侣..."

【混合模式优势】
1. 前端可以用结构化数据渲染卡片
2. 同时显示LLM生成的描述增加可读性
3. API调用返回完整的JSON数据
4. 既有程序的精准性，又有AI的灵活性
""")

print("=" * 70)
