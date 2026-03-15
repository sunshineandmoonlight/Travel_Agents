"""
快速测试 - 展示智能体输出结果
"""
import os
import sys
import json
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 80)
print("  旅行规划智能体输出展示")
print("=" * 80)

# 创建LLM
from tradingagents.graph.trading_graph import create_llm_by_provider
llm = create_llm_by_provider(
    provider=os.getenv("LLM_PROVIDER", "siliconflow"),
    model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
    backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
    temperature=0.7,
    max_tokens=2000,
    timeout=60
)

# 导入智能体
from tradingagents.agents.group_a import UserRequirementAnalyst, DestinationMatcher, RankingScorer
from tradingagents.agents.group_b import ImmersiveDesignerAgent

requirements = {
    'travel_scope': 'domestic',
    'days': 5,
    'adults': 2,
    'budget': 'medium',
    'interests': ['历史文化', '美食'],
    'start_date': '2024-04-15'
}

# 测试数据
dest_data = {
    "tags": ["历史文化", "美食"],
    "highlights": ["兵马俑", "大雁塔", "回民街"],
    "budget_level": {"medium": 500}
}

# A1: 需求分析
print("\n=== A1: UserRequirementAnalyst ===")
analyst = UserRequirementAnalyst(llm=llm)
analyst.initialize()
portrait = analyst.analyze_requirements(requirements)
analyst.shutdown()

print(json.dumps(portrait, ensure_ascii=False, indent=2))

# A2: 地区匹配
print("\n=== A2: DestinationMatcher ===")
matcher = DestinationMatcher(llm=llm)
matcher.initialize()
candidates = matcher.match_destinations(portrait, "domestic")
matcher.shutdown()

print(f"匹配到 {len(candidates)} 个目的地:")
for i, dest in enumerate(candidates[:5], 1):
    print(f"  {i}. {dest['destination']} - 匹配分: {dest['match_score']}")

# A3: 排名打分
print("\n=== A3: RankingScorer ===")
scorer = RankingScorer(llm=llm)
scorer.initialize()
ranked = scorer.rank_and_select_top(candidates, portrait, 4)
scorer.shutdown()

print(f"Top {len(ranked)} 目的地:")
for i, dest in enumerate(ranked, 1):
    print(f"  [{i}] {dest['destination']} - 综合得分: {dest.get('final_score', 0):.1f}")

selected_destination = ranked[0]['destination']
print(f"\n选择: {selected_destination}")

# B1: 沉浸式设计师
print("\n=== B1: ImmersiveDesigner ===")
designer = ImmersiveDesignerAgent(llm=llm)
designer.initialize()
proposal = designer.create_proposal(selected_destination, dest_data, portrait, 5)
designer.shutdown()

print(json.dumps(proposal, ensure_ascii=False, indent=2))

print("\n=== 测试完成 ===")
