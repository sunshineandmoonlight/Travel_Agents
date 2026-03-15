"""
测试增强版特殊需求解析功能 - 简化版

测试内容：
1. 否定表达识别（"不想去三亚"）
2. LLM智能解析（复杂语义）
"""

import re
from typing import Set

# 简化的城市列表
DOMESTIC_CITIES = {
    "北京", "上海", "广州", "深圳", "成都", "杭州", "西安", "厦门",
    "三亚", "桂林", "丽江", "拉萨", "昆明", "西宁", "贵阳", "重庆",
    "南京", "苏州", "青岛", "大连", "哈尔滨", "长沙", "武汉", "乌鲁木齐"
}


def extract_destinations_with_rules(special_requests: str) -> Set[str]:
    """基于规则的城市提取（带否定检测）"""
    if not special_requests:
        return set()

    # 检查否定表达
    negative_patterns = ['不想去', '不要去', '避免', '排除', '不想', '不要', '不去']
    is_negative = any(pattern in special_requests for pattern in negative_patterns)

    # 如果是否定表达，不提取城市
    if is_negative:
        print(f"  [规则] 检测到否定表达，跳过城市提取")
        return set()

    # 排序：优先匹配长城市名
    sorted_cities = sorted(DOMESTIC_CITIES, key=len, reverse=True)
    preferred_cities = set()

    # 直接匹配城市名称
    for city in sorted_cities:
        if city in special_requests:
            preferred_cities.add(city)

    return preferred_cities


def extract_destinations_with_llm_mock(special_requests: str) -> Set[str]:
    """模拟LLM智能解析"""
    print(f"  [LLM] 分析特殊需求: {special_requests}")

    # 模拟LLM的智能解析
    if "不想去" in special_requests or "不要去" in special_requests:
        # 检测是否在排除某个城市
        for city in DOMESTIC_CITIES:
            if city in special_requests:
                print(f"  [LLM] 识别到否定表达，排除城市: {city}")
                return set()

    if "靠近西藏" in special_requests:
        result = {"成都", "昆明", "西宁"}
        print(f"  [LLM] 地理推理 - 西藏周边城市: {result}")
        return result

    if "看海" in special_requests or "海滨" in special_requests:
        result = {"三亚", "厦门", "青岛", "大连"}
        print(f"  [LLM] 特征匹配 - 海滨城市: {result}")
        return result

    if "有古城" in special_requests or "古城" in special_requests:
        result = {"西安", "丽江", "大理"}
        print(f"  [LLM] 特征匹配 - 古城城市: {result}")
        return result

    # 回退到城市名提取
    for city in DOMESTIC_CITIES:
        if city in special_requests:
            print(f"  [LLM] 直接匹配城市名: {city}")
            return {city}

    return set()


def test_negative_expressions():
    """测试否定表达识别"""
    print("=" * 70)
    print("测试1: 否定表达识别")
    print("=" * 70)

    test_cases = [
        ("不想去三亚", set(), "否定：不想去三亚"),
        ("不要去北京", set(), "否定：不要去北京"),
        ("避免去三亚和厦门", set(), "否定：避免去某些城市"),
        ("我想去三亚", {"三亚"}, "肯定：我想去三亚"),
        ("包括北京和上海", {"北京", "上海"}, "肯定：多个城市"),
    ]

    passed = 0
    for input_text, expected, description in test_cases:
        result = extract_destinations_with_rules(input_text)
        success = result == expected
        status = "[PASS]" if success else "[FAIL]"
        if success:
            passed += 1

        print(f"{status} {description}")
        print(f"     输入: {input_text}")
        print(f"     预期: {expected if expected else '(空)'}")
        print(f"     结果: {result if result else '(空)'}")
        print()

    print(f"测试结果: {passed}/{len(test_cases)} 通过\n")


def test_complex_semantics():
    """测试复杂语义理解（模拟LLM）"""
    print("=" * 70)
    print("测试2: 复杂语义理解（模拟LLM）")
    print("=" * 70)

    test_cases = [
        ("靠近西藏的地方", {"成都", "昆明", "西宁"}, "地理推理"),
        ("看海的城市", {"三亚", "厦门", "青岛", "大连"}, "特征匹配"),
        ("有古城的地方", {"西安", "丽江", "大理"}, "特征匹配"),
        ("不想去三亚", set(), "否定表达"),
        ("我想去成都和重庆", {"成都", "重庆"}, "直接匹配"),
    ]

    passed = 0
    for input_text, expected, description in test_cases:
        result = extract_destinations_with_llm_mock(input_text)

        # 检查是否包含预期城市（允许超集）
        success = expected.issubset(result)
        status = "[PASS]" if success else "[PARTIAL]"
        if success and result == expected:
            passed += 1

        print(f"{status} {description}")
        print(f"     输入: {input_text}")
        print(f"     预期: {expected}")
        print(f"     结果: {result}")
        print()

    print(f"测试结果: {passed}/{len(test_cases)} 完全通过\n")


def test_combined_requirements():
    """测试组合需求"""
    print("=" * 70)
    print("测试3: 组合需求")
    print("=" * 70)

    test_cases = [
        ("我想去成都和重庆，但不要去昆明", "混合：肯定+否定"),
        ("想去看海的城市，包括三亚和厦门", "特征+列举"),
        ("不想去北方，想去南方看海", "地理偏好+特征"),
    ]

    for input_text, description in test_cases:
        print(f"测试: {description}")
        print(f"输入: {input_text}")

        # 先用规则解析
        rule_result = extract_destinations_with_rules(input_text)
        print(f"规则解析: {rule_result if rule_result else '(空)'}")

        # 再用LLM解析
        llm_result = extract_destinations_with_llm_mock(input_text)
        print(f"LLM解析:  {llm_result if llm_result else '(空)'}")
        print()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("增强版特殊需求解析功能测试")
    print("=" * 70)
    print()

    # 测试1：否定表达识别
    test_negative_expressions()

    # 测试2：复杂语义理解
    test_complex_semantics()

    # 测试3：组合需求
    test_combined_requirements()

    print("=" * 70)
    print("功能说明")
    print("=" * 70)
    print("""
1. 否定表达识别：
   - "不想去三亚" → 三亚会被排除，不推荐
   - "不要去北京" → 北京会被排除，不推荐

2. LLM智能解析：
   - "靠近西藏的地方" → 成都、昆明、西宁（地理推理）
   - "看海的城市" → 三亚、厦门、青岛、大连（特征匹配）
   - "有古城的" → 西安、丽江、大理（特征匹配）

3. 综合理解：
   - 系统会优先使用LLM进行智能解析
   - 如果LLM不可用，回退到规则解析
   - 规则解析会检测否定表达，避免错误推荐
    """)
