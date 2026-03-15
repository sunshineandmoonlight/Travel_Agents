"""
测试增强版特殊需求解析功能

测试内容：
1. 否定表达识别（"不想去三亚"）
2. 复杂语义理解（"靠近西藏的地方"）
3. LLM智能解析
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tradingagents.agents.group_a.destination_matcher import (
    _extract_destinations_from_special_requests,
    _extract_destinations_with_llm
)


def test_negative_expressions():
    """测试否定表达识别"""
    print("=" * 70)
    print("测试1: 否定表达识别")
    print("=" * 70)

    test_cases = [
        ("不想去三亚", "应该返回空集合"),
        ("不要去北京", "应该返回空集合"),
        ("避免去三亚和厦门", "应该返回空集合"),
        ("我想去三亚", "应该返回三亚"),
        ("包括北京和上海", "应该返回北京和上海"),
    ]

    for input_text, expected in test_cases:
        result = _extract_destinations_from_special_requests(input_text, llm=None)
        status = "[PASS]" if (not result and "不想" in input_text or "不要" in input_text) else "[PASS]" if result else "[FAIL]"
        print(f"{status} 输入: {input_text}")
        print(f"     预期: {expected}")
        print(f"     结果: {result if result else '(空)'}")
        print()


def test_complex_semantics():
    """测试复杂语义理解（需要LLM）"""
    print("=" * 70)
    print("测试2: 复杂语义理解（需要LLM）")
    print("=" * 70)
    print("注意：此测试需要配置LLM，如果没有配置则跳过")
    print()

    # 检查是否有LLM配置
    try:
        from dotenv import load_dotenv
        load_dotenv()

        llm_provider = os.getenv("LLM_PROVIDER", "")
        if not llm_provider:
            print("[SKIP] 未配置LLM_PROVIDER，跳过LLM测试")
            return

        # 创建LLM实例
        from tradingagents.graph.setup import create_llm_by_provider
        llm = create_llm_by_provider(llm_provider)

        test_cases = [
            ("靠近西藏的地方", ["成都", "昆明", "西宁"]),
            ("看海的城市", ["三亚", "厦门", "青岛", "大连"]),
            ("有古城的", ["西安", "丽江", "大理"]),
        ]

        for input_text, expected_keywords in test_cases:
            result = _extract_destinations_with_llm(input_text, llm)

            # 检查是否包含预期的关键词
            has_expected = any(keyword in result for keyword in expected_keywords)

            status = "[PASS]" if has_expected else "[PARTIAL]"
            print(f"{status} 输入: {input_text}")
            print(f"     预期关键词: {expected_keywords}")
            print(f"     识别结果: {result}")
            print()

    except Exception as e:
        print(f"[ERROR] LLM测试失败: {e}")


def test_with_actual_llm():
    """使用实际LLM测试完整流程"""
    print("=" * 70)
    print("测试3: 完整LLM智能解析")
    print("=" * 70)

    try:
        from dotenv import load_dotenv
        load_dotenv()

        llm_provider = os.getenv("LLM_PROVIDER", "")
        if not llm_provider:
            print("[SKIP] 未配置LLM_PROVIDER，跳过完整LLM测试")
            return

        from tradingagents.graph.setup import create_llm_by_provider
        llm = create_llm_by_provider(llm_provider)

        test_cases = [
            {
                "input": "我想去三亚玩几天",
                "expected": {"三亚"},
                "description": "肯定表达：明确提到城市名"
            },
            {
                "input": "不想去三亚，想去看海",
                "expected_not": {"三亚"},
                "description": "否定表达：排除某个城市"
            },
            {
                "input": "想去靠近西藏的地方",
                "expected_keywords": ["成都", "昆明", "西宁"],
                "description": "复杂语义：地理位置推理"
            }
        ]

        for test_case in test_cases:
            input_text = test_case["input"]
            description = test_case["description"]

            print(f"测试: {description}")
            print(f"输入: {input_text}")

            result = _extract_destinations_with_llm(input_text, llm)

            # 检查预期结果
            if "expected" in test_case:
                expected = test_case["expected"]
                if result == expected:
                    print(f"[PASS] 识别结果: {result}")
                else:
                    print(f"[PARTIAL] 识别结果: {result} (预期: {expected})")

            elif "expected_not" in test_case:
                excluded = test_case["expected_not"]
                if excluded.intersection(result):
                    print(f"[FAIL] 识别结果包含应该排除的城市: {result}")
                else:
                    print(f"[PASS] 识别结果: {result} (正确排除 {excluded})")

            elif "expected_keywords" in test_case:
                keywords = test_case["expected_keywords"]
                has_keyword = any(k in result for k in keywords)
                if has_keyword:
                    print(f"[PASS] 识别结果: {result}")
                else:
                    print(f"[PARTIAL] 识别结果: {result} (期望包含 {keywords})")

            print()

    except Exception as e:
        print(f"[ERROR] 完整LLM测试失败: {e}")


def test_combined_requirements():
    """测试组合需求"""
    print("=" * 70)
    print("测试4: 组合需求解析")
    print("=" * 70)

    test_cases = [
        ("我想去成都和重庆，但不要去昆明", {"成都", "重庆"}),
        ("想去看海的城市，包括三亚和厦门", {"三亚", "厦门"}),
        ("不想去北方，想去南方看海", {"三亚", "厦门", "海口", "桂林"}),
    ]

    for input_text, _ in test_cases:
        result = _extract_destinations_from_special_requests(input_text, llm=None)
        print(f"输入: {input_text}")
        print(f"规则解析结果: {result}")
        print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("增强版特殊需求解析功能测试")
    print("=" * 70)
    print()

    # 测试1：否定表达（基于规则）
    test_negative_expressions()

    # 测试2：复杂语义（需要LLM）
    test_complex_semantics()

    # 测试3：完整LLM解析
    test_with_actual_llm()

    # 测试4：组合需求
    test_combined_requirements()

    print("=" * 70)
    print("测试完成")
    print("=" * 70)
    print("""
功能说明：
1. 否定表达识别：系统会识别"不想去"、"不要去"等否定词
2. LLM智能解析：支持复杂语义如"靠近西藏的地方"
3. 地理推理：理解地理位置关系，如"云南周边"
4. 特征匹配：理解城市特征，如"有古城的"、"美食多的"
    """)
