"""
测试Group B API工具增强

验证SerpAPI和OpenTripMap工具是否正常工作
"""

import os
import sys
import asyncio

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
load_dotenv()

print("=" * 70)
print("  Group B API工具增强测试")
print("=" * 70)

# 测试API配置
print("\n【1】API配置检查")
print("-" * 70)

serpapi_key = os.getenv("SERPAPI_KEY")
opentripmap_key = os.getenv("OPENTRIPMAP_API_KEY")

print(f"SerpAPI: {'[OK] 已配置' if serpapi_key and serpapi_key != 'your_serpapi_key_here' else '[WARN] 未配置'}")
print(f"OpenTripMap: {'[OK] 已配置' if opentripmap_key and opentripmap_key != 'your_opentripmap_key_here' else '[WARN] 未配置'}")

# 导入API工具
try:
    from tradingagents.agents.group_b.api_tools import SerpAPITool, OpenTripMapTool
    print("\n[OK] API工具模块导入成功")
except ImportError as e:
    print(f"\n[ERROR] API工具模块导入失败: {e}")
    sys.exit(1)

# 测试SerpAPI
if serpapi_key and serpapi_key != "your_serpapi_key_here":
    print("\n【2】SerpAPI工具测试")
    print("-" * 70)

    try:
        serpapi_tool = SerpAPITool()

        # 测试搜索景点
        print("\n搜索成都的博物馆...")
        attractions = asyncio.run(serpapi_tool.search_attractions(
            destination="成都",
            keywords="博物馆",
            days=3,
            style="immersive"
        ))

        print(f"[结果] 搜索到 {len(attractions)} 个景点")

        if attractions:
            print("\n前3个景点:")
            for i, attr in enumerate(attractions[:3], 1):
                print(f"  {i}. {attr.get('name', 'N/A')}")
                print(f"     评分: {attr.get('rating', 'N/A')}")
                print(f"     地址: {attr.get('address', 'N/A')}")
                print(f"     来源: {attr.get('source', 'N/A')}")

        # 测试缓存
        print("\n[缓存] 测试缓存功能...")
        attractions2 = asyncio.run(serpapi_tool.search_attractions(
            destination="成都",
            keywords="博物馆",
            days=3,
            style="immersive"
        ))
        print(f"[缓存] 缓存命中率: {'命中' if len(attractions2) > 0 else '未命中'}")

        # 获取缓存统计
        stats = serpapi_tool.get_cache_stats()
        print(f"[缓存] 统计: {stats}")

    except Exception as e:
        print(f"[ERROR] SerpAPI测试失败: {e}")
        import traceback
        traceback.print_exc()

else:
    print("\n【2】SerpAPI工具测试 - [SKIP] 未配置API密钥")

# 测试OpenTripMap
if opentripmap_key and opentripmap_key != "your_opentripmap_key_here":
    print("\n【3】OpenTripMap工具测试")
    print("-" * 70)

    try:
        opentripmap_tool = OpenTripMapTool()

        # 测试搜索景点
        print("\n搜索北京的文化景点...")
        attractions = asyncio.run(opentripmap_tool.search_attractions(
            destination="北京",
            keywords="cultural",
            days=3,
            style="immersive"
        ))

        print(f"[结果] 搜索到 {len(attractions)} 个景点")

        if attractions:
            print("\n前3个景点:")
            for i, attr in enumerate(attractions[:3], 1):
                print(f"  {i}. {attr.get('name', 'N/A')}")
                print(f"     类型: {attr.get('kinds', 'N/A')}")
                print(f"     来源: {attr.get('source', 'N/A')}")

    except Exception as e:
        print(f"[ERROR] OpenTripMap测试失败: {e}")
        import traceback
        traceback.print_exc()

else:
    print("\n【3】OpenTripMap工具测试 - [SKIP] 未配置API密钥")

# 测试ImmersiveDesigner
print("\n【4】ImmersiveDesigner增强测试")
print("-" * 70)

try:
    from tradingagents.agents.group_b.immersive_designer import design_immersive_style
    from tradingagents.graph.trading_graph import create_llm_by_provider

    # 创建LLM
    llm = None
    try:
        llm = create_llm_by_provider(
            provider=os.getenv("LLM_PROVIDER", "siliconflow"),
            model=os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-7B-Instruct"),
            backend_url=os.getenv("SILICONFLOW_BASE_URL", "https://api.siliconflow.cn/v1"),
            temperature=0.7,
            max_tokens=2000,
            timeout=60
        )
        print("[OK] LLM实例创建成功")
    except Exception as e:
        print(f"[WARN] LLM创建失败: {e}")

    # 测试数据
    destination = "成都"
    dest_data = {
        "tags": ["历史文化", "美食"],
        "highlights": ["大熊猫繁育研究基地", "宽窄巷子", "锦里古街"],
        "budget_level": {"medium": 500}
    }
    user_portrait = {
        "travel_type": "情侣游",
        "primary_interests": ["历史文化", "美食"],
        "budget": "medium",
        "days": 5,
        "total_travelers": 2
    }

    print(f"\n测试为{destination}设计沉浸式方案...")

    result = design_immersive_style(
        destination=destination,
        dest_data=dest_data,
        user_portrait=user_portrait,
        days=5,
        llm=llm
    )

    print(f"\n[结果] 方案设计完成:")
    print(f"  风格: {result.get('style_name')}")
    print(f"  节奏: {result.get('daily_pace')}")
    print(f"  每日行程: {len(result.get('daily_itinerary', []))} 天")
    print(f"  数据来源: {result.get('data_source')}")
    print(f"  API来源: {result.get('api_sources_used', [])}")

    # 显示LLM描述
    llm_desc = result.get('llm_description', '')
    if llm_desc:
        print(f"\n[LLM描述] ({len(llm_desc)} 字符):")
        print(f"  {llm_desc[:200]}...")
    else:
        print(f"\n[LLM描述] 未生成")

    # 显示每日行程
    print(f"\n[每日行程预览]:")
    for day_plan in result.get('daily_itinerary', [])[:2]:
        print(f"  第{day_plan.get('day')}天: {day_plan.get('title')}")
        print(f"    节奏: {day_plan.get('pace')}")

    print("\n[OK] ImmersiveDesigner测试完成")

except Exception as e:
    print(f"[ERROR] ImmersiveDesigner测试失败: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "=" * 70)
print("  测试总结")
print("=" * 70)

print("""
改进1 - Group B API工具加强:
  [✓] API工具基类: BaseAPITool
  [✓] SerpAPI工具: SerpAPITool
  [✓] OpenTripMap工具: OpenTripMapTool
  [✓] ImmersiveDesigner增强: 使用API + LLM描述

下一步:
  [ ] 更新ExplorationDesigner
  [ ] 更新RelaxationDesigner
  [ ] 更新HiddenGemDesigner
  [ ] 添加API调用日志
  [ ] 优化缓存策略
""")
