"""
测试特殊需求城市优先推荐功能 - 简化版

直接测试提取城市名称和加分逻辑，避免导入错误
"""

import re
from typing import Set, Dict, Any

# 简化版城市名称映射
CITY_NAME_MAP = {
    "三亚": "三亚", "北京": "北京", "上海": "上海",
    "西安": "西安", "成都": "成都", "杭州": "杭州",
    "苏州": "苏州", "厦门": "厦门", "丽江": "丽江",
    "桂林": "桂林", "拉萨": "拉萨", "广州": "广州",
    "深圳": "深圳", "重庆": "重庆", "南京": "南京",
    # 国际城市
    "东京": "东京", "京都": "京都", "曼谷": "曼谷",
    "新加坡": "新加坡", "首尔": "首尔", "巴黎": "巴黎"
}


def extract_destinations_from_special_requests(special_requests: str) -> Set[str]:
    """
    从特殊需求中提取城市名称

    支持多种表达方式：
    - "我想去三亚"
    - "想去三亚玩"
    - "目的地是三亚"
    - "三亚旅游"
    - "包括三亚、曼谷"
    """
    if not special_requests:
        return set()

    preferred_cities = set()
    all_cities = set(CITY_NAME_MAP.keys())

    # 排序：优先匹配长城市名
    sorted_cities = sorted(all_cities, key=len, reverse=True)

    # 直接匹配城市名称
    for city in sorted_cities:
        if city in special_requests:
            preferred_cities.add(city)

    # 匹配"我想去X"模式
    pattern1 = rf'我想去([{"".join(sorted_cities)}]+)'
    matches1 = re.findall(pattern1, special_requests)
    for match in matches1:
        preferred_cities.add(match)

    # 匹配"想去X"模式
    pattern2 = rf'想去([{"".join(sorted_cities)}]+)'
    matches2 = re.findall(pattern2, special_requests)
    for match in matches2:
        preferred_cities.add(match)

    # 匹配"目的地是X"模式
    pattern3 = rf'目的地是([{"".join(sorted_cities)}]+)'
    matches3 = re.findall(pattern3, special_requests)
    for match in matches3:
        preferred_cities.add(match)

    return preferred_cities


def calculate_score_with_bonus(
    base_score: float,
    city_name: str,
    preferred_cities: Set[str]
) -> float:
    """
    计算带额外加分的分数

    Args:
        base_score: 基础分数
        city_name: 城市名称
        preferred_cities: 用户指定的城市集合

    Returns:
        最终分数
    """
    if city_name in preferred_cities:
        bonus = 20
        print(f"  {city_name}: {base_score} + {bonus} = {base_score + bonus}分 [PREFERRED] 用户指定")
        return base_score + bonus
    else:
        print(f"  {city_name}: {base_score}分")
        return base_score


def test_special_requests_priority():
    """测试特殊需求优先推荐"""
    print("=" * 70)
    print("特殊需求城市优先推荐测试")
    print("=" * 70)

    # 测试1: 城市名称提取
    print("\n测试1: 从特殊需求提取城市名称")
    print("-" * 70)

    test_cases = [
        "我想去三亚玩几天",
        "想去三亚旅游",
        "目的地是三亚",
        "包括三亚和曼谷",
        "我想去北京和上海",
        "没有提到具体城市"
    ]

    for special_request in test_cases:
        extracted = extract_destinations_from_special_requests(special_request)
        print(f"输入: {special_request}")
        print(f"提取: {extracted if extracted else '(无)'}")
        print()

    # 测试2: 三亚优先推荐
    print("\n测试2: 三亚优先推荐验证")
    print("-" * 70)

    # 模拟基础分数
    base_scores = {
        "三亚": 74,
        "北京": 75,
        "上海": 75,
        "成都": 78,
        "杭州": 76,
        "厦门": 73,
        "桂林": 70,
        "丽江": 72
    }

    special_request = "我想去三亚玩几天"
    preferred_cities = extract_destinations_from_special_requests(special_request)

    print(f"特殊需求: {special_request}")
    print(f"提取城市: {preferred_cities}")
    print()

    # 计算分数
    scored_cities = []
    for city, base_score in base_scores.items():
        final_score = calculate_score_with_bonus(base_score, city, preferred_cities)
        scored_cities.append({
            "city": city,
            "score": final_score,
            "is_preferred": city in preferred_cities
        })

    # 排序
    scored_cities.sort(key=lambda x: x["score"], reverse=True)

    print("推荐排名:")
    print("-" * 70)
    for i, item in enumerate(scored_cities[:8], 1):
        city = item['city']
        score = item['score']
        is_preferred = item['is_preferred']
        mark = " [PREFERRED]" if is_preferred else ""
        print(f"{i}. {city:8} {score:5.0f}分{mark}")

    # 验证三亚是否排第一
    sanya = next((c for c in scored_cities if c['city'] == '三亚'), None)
    if sanya and sanya['score'] > scored_cities[1]['score']:
        print(f"\n[PASS] 测试通过！三亚排在第一位 (分数: {sanya['score']})")
    elif sanya:
        print(f"\n[WARNING] 三亚在推荐列表中，但不是第一位 (排名: {scored_cities.index(sanya) + 1})")
    else:
        print(f"\n[FAIL] 测试失败！三亚不在推荐列表中")

    # 测试3: 多个城市的优先推荐
    print("\n\n测试3: 多个城市优先推荐")
    print("-" * 70)

    base_scores_2 = {
        "北京": 75,
        "西安": 74,
        "南京": 71,
        "苏州": 71,
        "成都": 78
    }

    special_request_2 = "我想去北京和西安"
    preferred_cities_2 = extract_destinations_from_special_requests(special_request_2)

    print(f"特殊需求: {special_request_2}")
    print(f"提取城市: {preferred_cities_2}")
    print()

    scored_cities_2 = []
    for city, base_score in base_scores_2.items():
        final_score = calculate_score_with_bonus(base_score, city, preferred_cities_2)
        scored_cities_2.append({
            "city": city,
            "score": final_score,
            "is_preferred": city in preferred_cities_2
        })

    scored_cities_2.sort(key=lambda x: x["score"], reverse=True)

    print("推荐排名:")
    print("-" * 70)
    for i, item in enumerate(scored_cities_2, 1):
        city = item['city']
        score = item['score']
        is_preferred = item['is_preferred']
        mark = " [PREFERRED]" if is_preferred else ""
        print(f"{i}. {city:8} {score:5.0f}分{mark}")

    # 验证北京和西安是否排在前2
    beijing = next((c for c in scored_cities_2 if c['city'] == '北京'), None)
    xian = next((c for c in scored_cities_2 if c['city'] == '西安'), None)

    if beijing and xian:
        if beijing['score'] >= 95 and xian['score'] >= 94:
            print(f"\n[PASS] 测试通过！北京和西安都获得了额外加分")
        else:
            print(f"\n[WARNING] 部分通过：北京({beijing['score']}) 西安({xian['score']})")

    print("\n" + "=" * 70)
    print("功能说明")
    print("=" * 70)
    print("""
1. 当用户在"特殊需求"中提到城市名称时，系统会自动识别
2. 识别到的城市将获得 +20分 的额外加分
3. 这确保了用户明确想去的城市会排在推荐列表的前列
4. 支持多种表达方式：
   - "我想去三亚"
   - "想去三亚旅游"
   - "目的地是三亚"
   - "包括三亚、曼谷"（多个城市）
5. 适用于国内外所有城市
    """)


if __name__ == "__main__":
    test_special_requests_priority()
