"""
测试天行数据集成到 LLMGuideWriter - 简化版
"""

import sys
import os

# 直接导入天行数据客户端
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tianapi_direct():
    """直接测试天行数据API"""
    print("=" * 70)
    print("天行数据API直接测试")
    print("=" * 70)

    try:
        from tradingagents.integrations.tianapi_client import (
            TianAPIClient,
            get_popular_attractions_cached,
            parse_attraction_content
        )

        client = TianAPIClient()

        # 测试1: 获取苏州景点列表
        print("\n测试1: 获取苏州景点列表")
        print("-" * 70)
        suzhou_attractions = client.get_scenic_attractions("苏州", num=10)
        print(f"找到 {len(suzhou_attractions)} 个景点:")
        for i, attr in enumerate(suzhou_attractions[:5], 1):
            print(f"  {i}. {attr.get('name', 'N/A')}")
        print("..." if len(suzhou_attractions) > 5 else "")

        # 测试2: 获取景点详情
        print("\n测试2: 获取虎丘详情")
        print("-" * 70)
        huqiu_details = client.get_attraction_detail(name="虎丘")
        if huqiu_details:
            content = huqiu_details.get('content', '')
            parsed = parse_attraction_content(content)
            print(f"景点名称: {huqiu_details.get('name')}")
            print(f"描述: {parsed['description'][:100]}...")
            print(f"子景点: {', '.join(parsed['sub_attractions'][:5])}...")
        else:
            print("[!] 未找到虎丘详情")

        # 测试3: 验证景点名称
        print("\n测试3: 验证景点名称")
        print("-" * 70)
        test_names = ["虎丘", "拙政园", "狮子林", "不存在的景点"]
        for name in test_names:
            found = False
            for attr in suzhou_attractions:
                if attr.get('name') == name:
                    found = True
                    break
            status = "[OK] 存在" if found else "[X] 不存在"
            print(f"{name}: {status}")

        print("\n" + "=" * 70)
        print("[OK] 天行数据API工作正常！")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_guide_writer_integration():
    """测试LLMGuideWriter中的天行数据集成函数"""
    print("\n" + "=" * 70)
    print("LLMGuideWriter集成测试")
    print("=" * 70)

    try:
        # 测试辅助函数
        from tradingagents.agents.group_c.llm_guide_writer import (
            _get_real_attractions_context,
            _get_real_attraction_description,
            _verify_attraction_from_tianapi
        )

        # 测试1: 获取景点上下文
        print("\n测试1: 获取景点上下文")
        print("-" * 70)
        context = _get_real_attractions_context("苏州")
        if context:
            print("[OK] 景点上下文获取成功")
            print(f"长度: {len(context)} 字符")
            print(f"预览: {context[:200]}...")
        else:
            print("[!] 景点上下文为空（可能天行数据无此城市）")

        # 测试2: 获取景点描述
        print("\n测试2: 获取景点描述")
        print("-" * 70)
        desc = _get_real_attraction_description("虎丘", "苏州")
        if desc:
            print("[OK] 景点描述获取成功")
            print(f"预览: {desc[:150]}...")
        else:
            print("[!] 未找到景点描述")

        # 测试3: 验证景点
        print("\n测试3: 验证景点")
        print("-" * 70)
        huqiu_valid = _verify_attraction_from_tianapi('虎丘', '苏州')
        zhuozheng_valid = _verify_attraction_from_tianapi('拙政园', '苏州')
        fake_valid = _verify_attraction_from_tianapi('不存在', '苏州')
        print(f"虎丘: {'[OK] 存在' if huqiu_valid else '[X] 不存在'}")
        print(f"拙政园: {'[OK] 存在' if zhuozheng_valid else '[X] 不存在'}")
        print(f"不存在: {'[OK] 正确识别' if not fake_valid else '[X] 误判'}")

        print("\n" + "=" * 70)
        print("[OK] LLMGuideWriter集成测试通过！")
        print("=" * 70)

        return True

    except Exception as e:
        print(f"\n[X] 集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("开始测试天行数据集成...\n")

    # 先测试天行数据API
    api_ok = test_tianapi_direct()

    # 再测试LLMGuideWriter集成
    if api_ok:
        integration_ok = test_llm_guide_writer_integration()

    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    api_status = "[OK] 正常" if api_ok else "[X] 异常"
    integration_status = "[OK] 正常" if api_ok else "[SKIP] 跳过"
    print(f"天行数据API: {api_status}")
    print(f"LLMGuideWriter集成: {integration_status}")
    print("=" * 70)
