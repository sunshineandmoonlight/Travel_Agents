"""
测试所有Group B Designer - 验证改进1完成状态

验证所有4个Designer都使用实时API + LLM描述
"""

import os
import sys
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  测试所有Group B Designer - 改进1完成验证")
print("=" * 70)

# 测试API配置
print("\n【1】API配置检查")
print("-" * 70)

serpapi_key = os.getenv("SERPAPI_KEY")
opentripmap_key = os.getenv("OPENTRIPMAP_API_KEY")

print(f"SerpAPI: {'[OK] 已配置' if serpapi_key and serpapi_key != 'your_serpapi_key_here' else '[WARN] 未配置'}")
print(f"OpenTripMap: {'[OK] 已配置' if opentripmap_key and opentripmap_key != 'your_opentripmap_key_here' else '[WARN] 未配置'}")

# 导入所有Designer
from tradingagents.agents.group_b.immersive_designer import design_immersive_style
from tradingagents.agents.group_b.exploration_designer import design_exploration_style
from tradingagents.agents.group_b.relaxation_designer import design_relaxation_style
from tradingagents.agents.group_b.hidden_gem_designer import design_hidden_gem_style

# 创建LLM
llm = None
try:
    from tradingagents.graph.trading_graph import create_llm_by_provider
    llm = create_llm_by_provider(
        provider=os.getenv("LLM_PROVIDER", "siliconflow"),
        model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
        backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
        temperature=0.7,
        max_tokens=2000,
        timeout=60
    )
    print("\n[OK] LLM实例创建成功")
except Exception as e:
    print(f"\n[WARN] LLM创建失败: {e}")

# 测试数据
destination = "成都"
dest_data = {
    "tags": ["历史文化", "美食"],
    "highlights": ["大熊猫繁育研究基地", "宽窄巷子", "锦里古街", "武侯祠", "杜甫草堂"],
    "budget_level": {"low": 300, "medium": 500, "high": 800}
}
user_portrait = {
    "travel_type": "情侣游",
    "primary_interests": ["历史文化", "美食"],
    "budget": "medium",
    "days": 5,
    "total_travelers": 2
}

# 测试所有4个Designer
designers = [
    ("ImmersiveDesigner", design_immersive_style, "沉浸式", "immersive"),
    ("ExplorationDesigner", design_exploration_style, "探索式", "exploration"),
    ("RelaxationDesigner", design_relaxation_style, "松弛式", "relaxation"),
    ("HiddenGemDesigner", design_hidden_gem_style, "小众宝藏", "hidden_gem"),
]

results = []

for designer_name, designer_func, style_cn, style_key in designers:
    print(f"\n【{len(results) + 1}】测试 {designer_name} ({style_cn})")
    print("-" * 70)

    try:
        print(f"设计{destination}的{style_cn}方案...")

        result = designer_func(
            destination=destination,
            dest_data=dest_data,
            user_portrait=user_portrait,
            days=5,
            llm=llm
        )

        # 提取关键信息
        data_source = result.get('data_source', 'unknown')
        api_sources = result.get('api_sources_used', [])
        llm_desc = result.get('llm_description', '')
        agent_info = result.get('agent_info', {})

        print(f"\n[结果] 方案设计完成:")
        print(f"  风格: {result.get('style_name')}")
        print(f"  节奏: {result.get('daily_pace')}")
        print(f"  每日行程: {len(result.get('daily_itinerary', []))} 天")
        print(f"  数据来源: {data_source}")
        print(f"  API来源: {api_sources}")
        print(f"  景点数量: {len([a for day in result.get('daily_itinerary', []) for a in day.get('attractions', [])])}")

        # LLM描述
        if llm_desc:
            print(f"\n[LLM描述] ({len(llm_desc)} 字符):")
            print(f"  {llm_desc[:150]}..." if len(llm_desc) > 150 else f"  {llm_desc}")
        else:
            print(f"\n[LLM描述] 未生成")

        # Agent信息
        if agent_info:
            print(f"\n[Agent信息]:")
            print(f"  中文名: {agent_info.get('name_cn')}")
            print(f"  英文名: {agent_info.get('name_en')}")
            # 图标可能有emoji，编码后显示
            icon = agent_info.get('icon', '')
            try:
                print(f"  图标: {icon}")
            except:
                print(f"  图标: [emoji]")
            print(f"  分组: Group {agent_info.get('group')}")
            print(f"  LLM启用: {agent_info.get('llm_enabled')}")

        # 验证改进1完成度
        has_api = data_source == "realtime_api" and len(api_sources) > 0
        has_llm = len(llm_desc) > 50  # 至少50字符
        has_agent_info = len(agent_info) > 0

        completion = {
            "name": designer_name,
            "api_enabled": has_api,
            "api_sources": api_sources,
            "llm_enabled": has_llm,
            "llm_length": len(llm_desc),
            "agent_info": has_agent_info,
            "score": sum([has_api, has_llm, has_agent_info])
        }
        results.append(completion)

        print(f"\n[完成度] {completion['score']}/3:")
        print(f"  [{'OK' if has_api else 'X'}] API工具启用")
        print(f"  [{'OK' if has_llm else 'X'}] LLM描述生成")
        print(f"  [{'OK' if has_agent_info else 'X'}] Agent信息字段")

    except Exception as e:
        print(f"\n[ERROR] {designer_name} 测试失败: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            "name": designer_name,
            "error": str(e),
            "score": 0
        })

# 总结
print("\n" + "=" * 70)
print("  改进1 - Group B API工具加强 - 完成报告")
print("=" * 70)

total_score = sum(r.get('score', 0) for r in results)
max_score = len(results) * 3

print(f"\n总体完成度: {total_score}/{max_score} ({int(total_score/max_score*100)}%)")
print("\n各Designer状态:")
print("-" * 70)

for result in results:
    name = result.get('name', 'Unknown')
    score = result.get('score', 0)
    api_sources = result.get('api_sources', [])
    llm_length = result.get('llm_length', 0)

    status = "[OK]" if score == 3 else "[PARTIAL]" if score > 0 else "[FAIL]"

    print(f"\n{status} {name} ({score}/3):")
    if score > 0:
        print(f"  API: {', '.join(api_sources) if api_sources else '未启用'}")
        print(f"  LLM: {llm_length} 字符" if llm_length > 0 else "  LLM: 未生成")
        print(f"  Agent信息: {'已添加' if result.get('agent_info') else '缺失'}")

print("\n" + "=" * 70)
print("  改进效果对比")
print("=" * 70)

print("""
| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 数据来源 | 静态数据库 | 实时API (SerpAPI + OpenTripMap) |
| 景点数量 | 有限（预定义） | 丰富（实时搜索15-30个） |
| 景点质量 | 基本信息 | 评分、地址、坐标等详情 |
| 方案描述 | 模板化 | LLM个性化生成 |
| 可扩展性 | 低 | 高（API工具基类） |
""")

if total_score >= max_score * 0.75:
    print("\n[SUCCESS] 改进1 基本完成，可以投入使用！")
    print("\n下一步:")
    print("  1. 开始改进2 - 智能体间通信机制")
    print("  2. 实现PubSub系统和ServiceRegistry")
else:
    print("\n[WARNING] 改进1 部分完成，需要进一步调试")

print("\n" + "=" * 70)
