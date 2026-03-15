"""
旅行规划流程性能测试脚本
测试每个阶段的耗时并找出性能瓶颈
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, Any

# 设置输出编码为UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# API 基础地址
BASE_URL = "http://localhost:8005"

# 测试请求参数
TEST_REQUIREMENTS = {
    "travel_scope": "domestic",
    "start_date": "2025-05-01",
    "days": 3,
    "adults": 2,
    "children": 0,
    "budget": "medium",
    "interests": ["文化", "美食", "历史"],
    "special_requests": "希望行程不要太紧凑，有时间品尝当地美食"
}


class PerformanceTimer:
    """性能计时器"""

    def __init__(self):
        self.results = []

    def record(self, step_name: str, duration: float, details: Dict[str, Any] = None):
        """记录一个步骤的耗时"""
        self.results.append({
            "step": step_name,
            "duration": duration,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        })
        print(f"[TIME] {step_name}: {duration:.2f}秒")

    def print_summary(self):
        """打印性能摘要"""
        print("\n" + "="*70)
        print("性能测试报告")
        print("="*70)

        total_time = sum(r["duration"] for r in self.results)

        for i, result in enumerate(self.results, 1):
            percentage = (result["duration"] / total_time * 100) if total_time > 0 else 0
            print(f"\n{i}. {result['step']}")
            print(f"   耗时: {result['duration']:.2f}秒 ({percentage:.1f}%)")
            if result["details"]:
                for key, value in result["details"].items():
                    print(f"   {key}: {value}")

        print(f"\n总耗时: {total_time:.2f}秒")
        print("="*70)

        # 找出最慢的步骤
        slowest = max(self.results, key=lambda x: x["duration"])
        print(f"\n[WARNING] 最慢的步骤: {slowest['step']} ({slowest['duration']:.2f}秒)")


def test_get_destinations(timer: PerformanceTimer) -> Dict[str, Any]:
    """测试步骤1: 获取目的地推荐"""
    print("\n[STEP 1] 测试: 获取目的地推荐...")

    start_time = time.time()

    # 记录各个事件的时间
    event_times = {}
    progress_updates = 0

    try:
        response = requests.post(
            f"{BASE_URL}/api/travel/staged/get-destinations-stream",
            json=TEST_REQUIREMENTS,
            stream=True,
            timeout=300  # 5分钟超时
        )

        first_byte_time = time.time()
        timer.record("首个字节响应", first_byte_time - start_time)

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        event_type = data.get('type', '')

                        if event_type == 'progress':
                            progress_updates += 1
                            agent = data.get('agent', 'unknown')
                            step = data.get('step', 'unknown')
                            progress = data.get('progress', 0)

                            if progress not in event_times:
                                event_times[f"{agent}_{progress}"] = time.time() - start_time

                        elif event_type == 'complete':
                            complete_time = time.time() - start_time
                            destinations = data.get('destinations', [])
                            user_portrait = data.get('user_portrait', {})

                            timer.record("获取目的地推荐", complete_time, {
                                "进度更新次数": progress_updates,
                                "推荐目的地数": len(destinations),
                                "目的地": [d['destination'] for d in destinations[:3]]
                            })

                            return {
                                'destinations': destinations,
                                'user_portrait': user_portrait,
                                'selected_destination': destinations[0]['destination'] if destinations else '杭州'
                            }

                    except json.JSONDecodeError:
                        pass

    except requests.exceptions.Timeout:
        timer.record("获取目的地推荐(超时)", 300, {"error": "请求超时"})
        raise
    except Exception as e:
        timer.record("获取目的地推荐(错误)", time.time() - start_time, {"error": str(e)})
        raise


def test_get_styles(timer: PerformanceTimer, destination: str) -> Dict[str, Any]:
    """测试步骤2: 获取风格方案"""
    print("\n[STEP 2] 测试: 获取风格方案...")

    start_time = time.time()
    event_times = {}
    progress_updates = 0

    try:
        request_data = {
            "travel_scope": TEST_REQUIREMENTS["travel_scope"],
            "days": TEST_REQUIREMENTS["days"],
            "user_portrait": {
                "description": "文化旅游爱好者",
                "budget_level": TEST_REQUIREMENTS["budget"]
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/travel/staged/get-styles-stream",
            params={"destination": destination},
            json=request_data,
            stream=True,
            timeout=300
        )

        first_byte_time = time.time()
        timer.record("风格方案-首个字节", first_byte_time - start_time)

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        event_type = data.get('type', '')

                        if event_type == 'progress':
                            progress_updates += 1

                        elif event_type == 'complete':
                            complete_time = time.time() - start_time
                            styles = data.get('styles', [])

                            timer.record("获取风格方案", complete_time, {
                                "进度更新次数": progress_updates,
                                "风格方案数": len(styles),
                                "风格": [s.get('style_name', 'unknown') for s in styles[:3]]
                            })

                            return {
                                'styles': styles,
                                'selected_style': styles[0].get('style_name', '深度文化游') if styles else '深度文化游'
                            }

                        elif event_type == 'error':
                            error_msg = data.get('message', 'Unknown error')
                            print(f"[ERROR] API返回错误: {error_msg}")

                    except json.JSONDecodeError as e:
                        print(f"[WARN] JSON解析错误: {e}")

        # 如果没有收到complete事件，记录超时
        timer.record("获取风格方案(未完成)", time.time() - start_time, {
            "进度更新次数": progress_updates,
            "error": "未收到complete事件"
        })
        return {'styles': [], 'selected_style': '深度文化游'}

    except requests.exceptions.Timeout:
        timer.record("获取风格方案(超时)", 300, {"error": "请求超时"})
        return {'styles': [], 'selected_style': '深度文化游'}
    except Exception as e:
        timer.record("获取风格方案(错误)", time.time() - start_time, {"error": str(e)})
        return {'styles': [], 'selected_style': '深度文化游'}


def test_generate_guide(timer: PerformanceTimer, destination: str, style: str) -> Dict[str, Any]:
    """测试步骤3: 生成详细攻略"""
    print("\n[STEP 3] 测试: 生成详细攻略...")

    start_time = time.time()
    event_times = {}
    progress_updates = 0
    agent_steps = {}

    try:
        request_data = {
            "travel_scope": TEST_REQUIREMENTS["travel_scope"],
            "start_date": TEST_REQUIREMENTS["start_date"],
            "days": TEST_REQUIREMENTS["days"],
            "user_portrait": {
                "description": "文化旅游爱好者",
                "budget_level": TEST_REQUIREMENTS["budget"]
            }
        }

        response = requests.post(
            f"{BASE_URL}/api/travel/staged/generate-guide-stream",
            params={
                "destination": destination,
                "style_name": style
            },
            json=request_data,
            stream=True,
            timeout=600  # 10分钟超时
        )

        first_byte_time = time.time()
        timer.record("生成攻略-首个字节", first_byte_time - start_time)

        last_progress_time = start_time
        last_progress_value = 0

        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        event_type = data.get('type', '')

                        if event_type == 'start':
                            print(f"   开始生成: {data.get('message', '')}")

                        elif event_type == 'progress':
                            progress_updates += 1
                            agent = data.get('agent', 'unknown')
                            step = data.get('step', 'unknown')
                            progress = data.get('progress', 0)

                            # 记录每个智能体的进度
                            agent_key = f"{agent}_{progress}"
                            if agent_key not in event_times:
                                event_times[agent_key] = time.time() - start_time
                                print(f"   [{progress}%] {agent}: {step}")

                            # 检测进度停滞
                            if progress > last_progress_value:
                                last_progress_value = progress
                                last_progress_time = time.time()

                        elif event_type == 'step_result':
                            agent = data.get('agent', 'unknown')
                            step = data.get('step', 'unknown')
                            if agent not in agent_steps:
                                agent_steps[agent] = []
                            agent_steps[agent].append(step)

                        elif event_type == 'complete':
                            complete_time = time.time() - start_time
                            guide = data.get('guide', {})

                            # 分析智能体执行情况
                            agent_summary = {}
                            for agent, steps in agent_steps.items():
                                agent_summary[agent] = f"{len(steps)}个步骤"

                            timer.record("生成详细攻略", complete_time, {
                                "进度更新次数": progress_updates,
                                "涉及智能体": len(agent_steps),
                                "智能体详情": agent_summary,
                                "攻略天数": guide.get('total_days', 0)
                            })

                            return {'guide': guide}

                    except json.JSONDecodeError:
                        pass

    except requests.exceptions.Timeout:
        timer.record("生成详细攻略(超时)", 600, {"error": "请求超时"})
        raise
    except Exception as e:
        timer.record("生成详细攻略(错误)", time.time() - start_time, {"error": str(e)})
        raise


def main():
    """主测试函数"""
    print("="*70)
    print("旅行规划流程性能测试")
    print("="*70)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"API地址: {BASE_URL}")
    print("="*70)

    timer = PerformanceTimer()

    try:
        # 步骤1: 获取目的地推荐
        print("\n" + "="*70)
        print("开始测试完整流程...")
        print("="*70)

        result1 = test_get_destinations(timer)
        destination = result1['selected_destination']

        # 步骤2: 获取风格方案
        result2 = test_get_styles(timer, destination)
        style = result2['selected_style']

        # 步骤3: 生成详细攻略
        result3 = test_generate_guide(timer, destination, style)

        # 打印摘要
        timer.print_summary()

        # 性能建议
        print("\n[INFO] 性能优化建议:")
        total_time = sum(r["duration"] for r in timer.results)

        for result in timer.results:
            if result["duration"] > total_time * 0.3:
                print(f"\n[WARNING] {result['step']} 占用超过30%的时间，建议优化:")
                print(f"   - 考虑增加缓存")
                print(f"   - 优化后端逻辑")
                print(f"   - 使用并行处理")

    except KeyboardInterrupt:
        print("\n\n[WARNING] 测试被用户中断")
        timer.print_summary()
    except Exception as e:
        print(f"\n\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        timer.print_summary()


if __name__ == "__main__":
    main()
