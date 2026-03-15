"""
测试FastAPI旅行相关端点

验证所有旅行规划和目的地情报API是否正常工作
"""
import sys
import os
import io
import subprocess
import time
import requests

# 设置UTF-8编码输出
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# API基础URL
BASE_URL = "http://localhost:8000"


def check_server_running():
    """检查FastAPI服务器是否运行"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        return response.status_code == 200
    except:
        return False


def start_server():
    """启动FastAPI服务器"""
    print("\n正在启动FastAPI服务器...")
    print("   这可能需要几秒钟...")
    print()

    # 设置环境变量 - 跳过数据库连接并使用UTF-8编码
    env = os.environ.copy()
    env["SKIP_DATABASE"] = "true"
    env["PYTHONIOENCODING"] = "utf-8"
    env["NEWS_SOURCE"] = "tianapi"
    env["TIANAPI_KEY"] = "8879cb7f41e435e278a404fe2be791ae"

    # 使用项目根目录启动服务器
    cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

    # Windows下需要特殊处理
    if sys.platform == 'win32':
        # 使用CREATE_NEW_PROCESS_GROUP避免Ctrl+C影响子进程
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            env=env,
            creationflags=creation_flags,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        process = subprocess.Popen(
            cmd,
            cwd=project_root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    # 等待服务器启动
    for i in range(30):
        time.sleep(1)
        if check_server_running():
            print(f"[OK] FastAPI服务器已启动 (pid: {process.pid})")
            print()
            return process
        print(f"   等待中... {i+1}/30")

    print("[!] 服务器启动超时，请检查是否有错误")
    return None


def test_endpoint(name, method, endpoint, data=None, params=None):
    """测试单个API端点"""
    url = f"{BASE_URL}{endpoint}"

    try:
        if method == "GET":
            response = requests.get(url, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            return False, None

        status_emoji = "[OK]" if response.status_code < 400 else "[!]"
        print(f"{status_emoji} {method:4} {endpoint:50} - {response.status_code}")

        if response.status_code == 200:
            try:
                result = response.json()
                return True, result
            except:
                return True, response.text
        else:
            try:
                error = response.json()
                return False, error
            except:
                return False, response.status_code

    except requests.exceptions.Timeout:
        print(f"[超时] {method:4} {endpoint:50} - 请求超时")
        return False, "timeout"
    except Exception as e:
        print(f"[FAIL] {method:4} {endpoint:50} - {str(e)[:30]}")
        return False, str(e)


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("  FastAPI旅行端点测试")
    print("="*70)
    print(f"\nAPI基础URL: {BASE_URL}")

    # 检查服务器是否已运行
    if not check_server_running():
        print("\n[!] FastAPI服务器未运行，正在自动启动...")
        server_process = start_server()
        if not server_process:
            print("\n[FAIL] 无法启动服务器，请手动启动:")
            print("   cd app && python -m uvicorn main:app --reload")
            return

        input("\n按Enter键继续测试...")

    # 测试端点列表
    tests = [
        # 基础端点
        ("根路径", "GET", "/", None),

        # 旅行规划端点
        ("创建旅行规划", "POST", "/travel/plan", {
            "destination": "杭州",
            "days": 3,
            "budget": "medium",
            "travelers": 2,
            "interest_type": "风景",
            "save_as_guide": False
        }),

        # 目的地情报端点
        ("目的地情报-杭州", "GET", "/travel/intelligence/杭州"),
        ("目的地情报-北京", "GET", "/travel/intelligence/北京"),
        ("目的地情报-新闻", "GET", "/travel/intelligence/杭州/news"),
        ("目的地情报-风险", "GET", "/travel/intelligence/杭州/risks"),
        ("目的地情报-活动", "GET", "/travel/intelligence/杭州/events"),
        ("目的地情报-文化", "GET", "/travel/intelligence/杭州/culture"),
        ("目的地情报-统计", "GET", "/travel/intelligence/stats"),

        # 其他旅行端点
        ("获取攻略列表", "GET", "/travel/guides"),
        ("标签列表", "GET", "/travel/tags"),
        ("消息列表", "GET", "/travel/messages"),
        ("缓存统计", "GET", "/travel/cache/stats"),
        ("操作日志", "GET", "/travel/logs/list"),
        ("任务队列统计", "GET", "/travel/queue/stats"),
        ("通知列表", "GET", "/travel/notifications"),
    ]

    print("\n开始测试...")
    print("-" * 70)

    results = []
    for name, method, endpoint, *args in tests:
        data = args[0] if args and method == "POST" else None
        success, result = test_endpoint(name, method, endpoint, data)
        results.append((name, success, result))

    # 汇总结果
    print("\n" + "="*70)
    print("  测试结果汇总")
    print("="*70)

    passed = sum(1 for _, s, _ in results if s)
    total = len(results)

    for name, success, result in results:
        status = "[OK] 通过" if success else "[FAIL] 失败"
        print(f"  {status}: {name}")
        if not success and isinstance(result, dict):
            error = result.get("detail", result)
            print(f"       错误: {error}")

    print(f"\n总计: {passed}/{total} 通过")
    print("="*70)

    # 详细展示一些重要结果
    print("\n" + "="*70)
    print("  重要端点详情")
    print("="*70)

    for name, success, result in results:
        if success and isinstance(result, dict) and "data" in result:
            print(f"\n[结果] {name}:")
            if "destination_intelligence" in result.get("data", {}):
                intel = result["data"]["destination_intelligence"]
                print(f"  - 风险等级: {intel.get('risk_level', 'N/A')}/5")
                print(f"  - 新闻数量: {intel.get('news_count', 0)}")
                print(f"  - 活动数量: {intel.get('events_count', 0)}")
                if intel.get('latest_news'):
                    print(f"  - 最新新闻: {intel['latest_news'][0].get('title', 'N/A')}")

    if passed == total:
        print("\n[成功] 所有端点测试通过！FastAPI工作正常。")
    else:
        print(f"\n[!] {total - passed} 个端点失败，请检查。")

    print("\n[提示] 下一步：前端设计")
    print("   - 旅行规划页面")
    print("   - 目的地情报展示页面")
    print("   - 攻略管理页面")


if __name__ == "__main__":
    main()
