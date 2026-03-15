"""
Agent 分析过程展示演示

展示旅行规划中每个Agent的执行过程和详细分析报告
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from tradingagents.graph.travel_graph_with_llm_enhanced import create_travel_graph_with_llm_enhanced


def print_agent_report(agent_log: dict):
    """打印单个Agent的分析报告"""
    print("\n" + "=" * 70)
    print(f"  {agent_log['agent_display_name']}")
    print("=" * 70)

    print(f"状态: {agent_log['status'].upper()}")
    print(f"执行时间: {agent_log['duration_ms']}ms")
    print(f"LLM模型: {agent_log.get('llm_model', 'N/A')}")

    if agent_log.get('analysis_report'):
        print("\n" + "-" * 70)
        print(agent_log['analysis_report'])

    if agent_log.get('output_data'):
        print("\n" + "-" * 70)
        print("输出数据:")
        print(json.dumps(agent_log['output_data'], ensure_ascii=False, indent=2)[:500] + "...")


def main():
    """主函数"""
    print("\n")
    print("*" * 70)
    print("  旅行规划系统 - Agent 分析过程展示")
    print("*" * 70)

    # 创建增强版旅行规划图
    graph = create_travel_graph_with_llm_enhanced(
        llm_provider="deepseek",
        llm_model="deepseek-chat"
    )

    # 规划旅行
    print("\n正在规划杭州之旅...")
    print("-" * 70)

    result = graph.plan(
        destination="杭州",
        days=3,
        budget="medium",
        travelers=2,
        interest_type="自然",
        selected_style="relaxed"
    )

    # 展示Agent执行日志
    agent_logs = result.get("agent_logs", [])

    print("\n")
    print("*" * 70)
    print(f"  Agent 执行日志 (共 {len(agent_logs)} 个Agent)")
    print("*" * 70)

    for log in agent_logs:
        print_agent_report(log)

    # 显示规划结果摘要
    print("\n" + "=" * 70)
    print("  规划结果摘要")
    print("=" * 70)

    print(f"\n目的地: {result.get('destination')}")
    print(f"类型: {result.get('destination_type')}")
    print(f"天数: {result.get('days')}")

    if result.get("budget_breakdown"):
        budget = result["budget_breakdown"]
        print(f"\n预算: {budget.get('total_budget')} 元")
        print(f"  - 交通: {budget.get('transportation', {}).get('amount', 0)} 元")
        print(f"  - 住宿: {budget.get('accommodation', {}).get('amount', 0)} 元")
        print(f"  - 餐饮: {budget.get('meals', {}).get('amount', 0)} 元")
        print(f"  - 景点: {budget.get('attractions', {}).get('amount', 0)} 元")

    # 统计信息
    completed_count = sum(1 for log in agent_logs if log['status'] == 'completed')
    failed_count = sum(1 for log in agent_logs if log['status'] == 'error')
    total_time = sum(log.get('duration_ms', 0) for log in agent_logs)

    print("\n" + "=" * 70)
    print("  执行统计")
    print("=" * 70)
    print(f"总Agent数: {len(agent_logs)}")
    print(f"成功: {completed_count}")
    print(f"失败: {failed_count}")
    print(f"总耗时: {total_time}ms ({total_time/1000:.2f}秒)")

    print("\n" + "*" * 70)
    print("  分析完成！")
    print("*" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
