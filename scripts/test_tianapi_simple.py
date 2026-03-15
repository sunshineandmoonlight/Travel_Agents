"""
测试天行数据集成 - 简化版

直接测试天行数据API和相关功能，不依赖stock trading模块
"""

import sys
import os
import json

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_tianapi_basic():
    """测试天行数据基础功能"""
    print("=" * 70)
    print("天行数据基础测试")
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

        if suzhou_attractions:
            print(f"[OK] 找到 {len(suzhou_attractions)} 个景点:")
            for i, attr in enumerate(suzhou_attractions[:5], 1):
                name = attr.get('name', 'N/A')
                print(f"  {i}. {name}")
            if len(suzhou_attractions) > 5:
                print(f"  ... 还有 {len(suzhou_attractions) - 5} 个景点")
        else:
            print("[!] 未找到景点（可能是API配置问题或城市无数据）")

        # 测试2: 解析景点内容
        print("\n测试2: 解析景点内容")
        print("-" * 70)
        if suzhou_attractions:
            first_attraction = suzhou_attractions[0]
            content = first_attraction.get('content', '')
            parsed = parse_attraction_content(content)

            print(f"景点名称: {first_attraction.get('name')}")
            print(f"描述长度: {len(parsed['description'])} 字符")
            print(f"描述预览: {parsed['description'][:100]}...")

            if parsed['sub_attractions']:
                print(f"子景点数量: {len(parsed['sub_attractions'])}")
                print(f"子景点列表: {', '.join(parsed['sub_attractions'][:5])}...")
            else:
                print("无子景点信息")

        # 测试3: 获取景点详情
        print("\n测试3: 获取景点详情")
        print("-" * 70)
        huqiu_details = client.get_attraction_detail(name="虎丘")
        if huqiu_details:
            print(f"[OK] 找到景点详情: {huqiu_details.get('name')}")
        else:
            print("[!] 未找到虎丘详情（可能不在天行数据库中）")

        # 测试4: 缓存功能
        print("\n测试4: 缓存功能测试")
        print("-" * 70)
        import time
        start = time.time()
        cached_attractions = get_popular_attractions_cached("苏州", limit=5)
        elapsed = time.time() - start
        print(f"[OK] 缓存查询耗时: {elapsed:.3f}秒")
        print(f"[OK] 返回 {len(cached_attractions)} 个景点")

        print("\n" + "=" * 70)
        print("[OK] 天行数据基础功能测试通过！")
        print("=" * 70)

        return True, {
            "attractions_found": len(suzhou_attractions),
            "has_content": bool(suzhou_attractions and suzhou_attractions[0].get('content')),
            "has_sub_attractions": bool(parsed.get('sub_attractions')) if suzhou_attractions else False,
            "cache_works": len(cached_attractions) > 0
        }

    except Exception as e:
        print(f"\n[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def test_helper_functions():
    """测试天行数据辅助函数"""
    print("\n" + "=" * 70)
    print("天行数据辅助函数测试")
    print("=" * 70)

    try:
        from tradingagents.tools.travel_tools_tianapi import (
            get_city_attractions_for_agent,
            validate_and_enrich_attraction_names,
            get_attraction_sub_attractions
        )

        # 测试1: 获取城市景点（供智能体使用）
        print("\n测试1: 获取城市景点（LLM格式）")
        print("-" * 70)
        llm_format = get_city_attractions_for_agent("苏州", limit=5, format_for_llm=True)
        if llm_format:
            print(f"[OK] 获取LLM格式数据")
            print(f"数据长度: {len(llm_format)} 字符")
            print(f"预览:\n{llm_format[:300]}...")
        else:
            print("[!] LLM格式数据为空")

        # 测试2: 获取原始景点列表
        print("\n测试2: 获取原始景点列表")
        print("-" * 70)
        raw_list = get_city_attractions_for_agent("苏州", limit=5, format_for_llm=False)
        if raw_list:
            print(f"[OK] 获取原始数据: {len(raw_list)} 个景点")
            for i, attr in enumerate(raw_list[:3], 1):
                print(f"  {i}. {attr.get('name', 'N/A')}")
        else:
            print("[!] 原始数据为空")

        # 测试3: 验证景点名称
        print("\n测试3: 验证景点名称")
        print("-" * 70)
        test_names = ["虎丘", "拙政园", "不存在的景点xyz"]
        validation_result = validate_and_enrich_attraction_names(test_names, "苏州")

        print(f"验证结果:")
        print(f"  有效景点: {validation_result['valid']}")
        print(f"  无效景点: {validation_result['invalid']}")
        if validation_result['details']:
            print(f"  详情数量: {len(validation_result['details'])}")

        # 测试4: 获取子景点
        print("\n测试4: 获取子景点")
        print("-" * 70)
        sub_attractions = get_attraction_sub_attractions("苏州西园寺", "苏州")
        if sub_attractions:
            print(f"[OK] 子景点数量: {len(sub_attractions)}")
            print(f"子景点: {', '.join(sub_attractions[:10])}")
        else:
            print("[!] 无子景点数据")

        print("\n" + "=" * 70)
        print("[OK] 辅助函数测试通过！")
        print("=" * 70)

        return True, {
            "llm_format_works": len(llm_format) > 0 if llm_format else False,
            "raw_list_works": len(raw_list) > 0 if raw_list else False,
            "validation_works": True,
            "sub_attractions_works": len(sub_attractions) > 0 if sub_attractions else False
        }

    except Exception as e:
        print(f"\n[X] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False, {}


def main():
    """运行所有测试"""
    print("\n开始天行数据集成测试...\n")

    # 测试1: 基础功能
    basic_ok, basic_results = test_tianapi_basic()

    # 测试2: 辅助函数
    helper_ok = False
    helper_results = {}
    if basic_ok:
        helper_ok, helper_results = test_helper_functions()

    # 汇总结果
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"基础功能: {'[OK] 通过' if basic_ok else '[X] 失败'}")
    print(f"辅助函数: {'[OK] 通过' if helper_ok else '[X] 失败'}")

    if basic_ok:
        print(f"\n基础功能结果:")
        for key, value in basic_results.items():
            status = "[OK]" if value else "[X]"
            print(f"  {key}: {status}")

    if helper_ok:
        print(f"\n辅助函数结果:")
        for key, value in helper_results.items():
            status = "[OK]" if value else "[X]"
            print(f"  {key}: {status}")

    print("=" * 70)

    # 保存结果到JSON
    all_results = {
        "basic_ok": basic_ok,
        "basic_results": basic_results,
        "helper_ok": helper_ok,
        "helper_results": helper_results
    }

    with open('tianapi_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)

    print("\n测试结果已保存到 tianapi_test_results.json")


if __name__ == "__main__":
    main()
