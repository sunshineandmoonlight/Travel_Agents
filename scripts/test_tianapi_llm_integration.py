"""
测试天行数据集成到 LLMGuideWriter
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tianapi_integration():
    """测试天行数据集成"""
    from tradingagents.agents.group_c.llm_guide_writer import (
        _get_real_attractions_context,
        _get_real_attraction_description,
        _verify_attraction_from_tianapi,
        _get_attraction_sub_attractions_list
    )

    print("=" * 70)
    print("天行数据集成测试")
    print("=" * 70)

    # 测试1: 获取城市景点列表
    print("\n测试1: 获取苏州景点列表")
    print("-" * 70)
    context = _get_real_attractions_context("苏州")
    print(context[:500] if len(context) > 500 else context)
    print("..." if len(context) > 500 else "")

    # 测试2: 获取景点描述
    print("\n测试2: 获取虎丘描述")
    print("-" * 70)
    desc = _get_real_attraction_description("虎丘", "苏州")
    print(desc[:300] if desc else "未找到描述")
    print("..." if desc and len(desc) > 300 else "")

    # 测试3: 验证景点
    print("\n测试3: 验证景点存在性")
    print("-" * 70)
    test_attractions = ["虎丘", "拙政园", "不存在的景点"]
    for name in test_attractions:
        is_valid = _verify_attraction_from_tianapi(name, "苏州")
        status = "✓ 存在" if is_valid else "✗ 不存在"
        print(f"{name}: {status}")

    # 测试4: 获取子景点
    print("\n测试4: 获取子景点列表")
    print("-" * 70)
    sub_attractions = _get_attraction_subactions_list("虎丘", "苏州")
    if sub_attractions:
        print(f"虎丘子景点: {', '.join(sub_attractions[:10])}")
    else:
        print("虎丘没有子景点信息")

    print("\n" + "=" * 70)
    print("测试完成！")
    print("=" * 70)

    # 返回测试结果
    return {
        "suzhou_context": len(context) > 0,
        "huqiu_desc": desc is not None,
        "虎丘": _verify_attraction_from_tianapi("虎丘", "苏州"),
        "拙政园": _verify_attraction_from_tianapi("拙政园", "苏州"),
        "不存在的景点": not _verify_attraction_from_tianapi("不存在的景点", "苏州"),
        "虎丘子景点": len(sub_attractions) > 0
    }


if __name__ == "__main__":
    results = test_tianapi_integration()

    print("\n测试结果汇总:")
    print(f"  苏州景点上下文: {'✅' if results['suzhou_context'] else '❌'}")
    print(f"  虎丘描述: {'✅' if results['huqiu_desc'] else '❌'}")
    print(f"  虎丘验证: {'✅' if results['虎丘'] else '❌'}")
    print(f"  拙政园验证: {'✅' if results['拙政园'] else '❌'}")
    print(f"  不存在景点验证: {'✅' if not results['不存在的景点'] else '❌'}")
    print(f"  虎丘子景点: {'✅' if results['虎丘子景点'] else '❌'}")
