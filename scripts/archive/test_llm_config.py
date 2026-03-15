"""
LLM配置测试脚本

用于验证LLM配置是否正确，以及智能体是否能够调用LLM
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 加载.env文件
from dotenv import load_dotenv
load_dotenv()

def test_env_config():
    """测试环境变量配置"""
    print("=" * 60)
    print("  1. 环境变量配置检查")
    print("=" * 60)

    # 检查API Key是否有效
    def check_key(key_value, placeholder):
        if key_value and key_value != placeholder and not key_value.startswith("your_"):
            return "*** (已配置)"
        return "[X] 未配置或为占位符"

    env_vars = {
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "未设置"),
        "SILICONFLOW_API_KEY": check_key(os.getenv("SILICONFLOW_API_KEY"), "your_siliconflow_key_here"),
        "OPENAI_API_KEY": check_key(os.getenv("OPENAI_API_KEY"), "your_openai_key_here"),
        "DEEPSEEK_API_KEY": check_key(os.getenv("DEEPSEEK_API_KEY"), "your_deepseek_key_here"),
        "GOOGLE_API_KEY": check_key(os.getenv("GOOGLE_API_KEY"), "your_google_key_here"),
        "DASHSCOPE_API_KEY": check_key(os.getenv("DASHSCOPE_API_KEY"), "your_dashscope_key_here"),
    }

    for key, value in env_vars.items():
        print(f"{key}: {value}")

    has_valid_key = any("已配置" in str(value) for value in env_vars.values())
    print(f"\n状态: {'[OK] 有有效的LLM配置' if has_valid_key else '[X] 没有有效的LLM配置'}")

    return has_valid_key


def test_llm_creation():
    """测试LLM实例创建"""
    print("\n" + "=" * 60)
    print("  2. LLM实例创建测试")
    print("=" * 60)

    try:
        from tradingagents.graph.trading_graph import create_llm_by_provider

        # 测试OpenAI
        print("\n测试OpenAI...")
        try:
            llm = create_llm_by_provider(
                provider="openai",
                model="gpt-3.5-turbo",
                backend_url="",
                temperature=0.7,
                max_tokens=100,
                timeout=30
            )
            print(f"[OK] OpenAI LLM创建成功: {type(llm)}")
        except Exception as e:
            print(f"[X] OpenAI LLM创建失败: {e}")

        # 测试DeepSeek
        print("\n测试DeepSeek...")
        try:
            llm = create_llm_by_provider(
                provider="deepseek",
                model="deepseek-chat",
                backend_url="https://api.deepseek.com",
                temperature=0.7,
                max_tokens=100,
                timeout=30
            )
            print(f"[OK] DeepSeek LLM创建成功: {type(llm)}")
        except Exception as e:
            print(f"[X] DeepSeek LLM创建失败: {e}")

        # 测试SiliconFlow
        print("\n测试SiliconFlow...")
        try:
            llm = create_llm_by_provider(
                provider="siliconflow",
                model="Qwen/Qwen2.5-7B-Instruct",
                backend_url="https://api.siliconflow.cn/v1",
                temperature=0.7,
                max_tokens=100,
                timeout=30
            )
            print(f"[OK] SiliconFlow LLM创建成功: {type(llm)}")
        except Exception as e:
            print(f"[X] SiliconFlow LLM创建失败: {e}")

    except Exception as e:
        print(f"❌ 导入失败: {e}")


def test_llm_invoke():
    """测试LLM调用"""
    print("\n" + "=" * 60)
    print("  3. LLM调用测试")
    print("=" * 60)

    try:
        from tradingagents.graph.trading_graph import create_llm_by_provider
        from langchain_core.messages import HumanMessage

        provider = os.getenv("LLM_PROVIDER", "openai")

        print(f"\n使用provider: {provider}")

        # 尝试调用LLM
        llm = create_llm_by_provider(
            provider=provider,
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            backend_url=os.getenv("OPENAI_BASE_URL", ""),
            temperature=0.7,
            max_tokens=100,
            timeout=30
        )

        print("发送测试请求...")
        response = llm.invoke([HumanMessage(content="你好，请回复'测试成功'")])

        print(f"[OK] LLM调用成功!")
        print(f"响应: {response.content[:100]}")

    except Exception as e:
        print(f"[X] LLM调用失败: {e}")


def test_agent_llm_usage():
    """测试智能体LLM使用情况"""
    print("\n" + "=" * 60)
    print("  4. 智能体LLM使用测试")
    print("=" * 60)

    try:
        from tradingagents.agents.group_a.destination_matcher import (
            calculate_match_score_with_llm,
            estimate_budget_with_llm
        )
        from tradingagents.graph.trading_graph import create_llm_by_provider

        # 创建测试数据
        destination = {
            "destination": "成都",
            "highlights": ["大熊猫繁育研究基地", "宽窄巷子", "锦里古街"],
            "suitable_for": ["美食爱好者", "休闲度假"]
        }
        user_portrait = {
            "primary_interests": ["美食", "休闲"],
            "budget": "medium",
            "travel_type": "情侣游",
            "days": 5,
            "total_travelers": 2
        }

        # 测试无LLM情况
        print("\n【测试1】无LLM实例 (规则fallback)")
        score = calculate_match_score_with_llm(destination, user_portrait, llm=None)
        budget = estimate_budget_with_llm("成都", destination, user_portrait, llm=None)
        print(f"评分: {score} (规则计算)")
        print(f"预算: {budget} (规则计算)")

        # 测试有LLM情况
        print("\n【测试2】有LLM实例")
        try:
            provider = os.getenv("LLM_PROVIDER", "openai")
            llm = create_llm_by_provider(
                provider=provider,
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                backend_url=os.getenv("OPENAI_BASE_URL", ""),
                temperature=0.7,
                max_tokens=100,
                timeout=30
            )

            score = calculate_match_score_with_llm(destination, user_portrait, llm=llm)
            budget = estimate_budget_with_llm("成都", destination, user_portrait, llm=llm)

            print(f"评分: {score} (LLM计算)")
            print(f"预算: {budget} (LLM计算)")

        except Exception as e:
            print(f"[X] LLM测试失败: {e}")
            print("   系统会自动fallback到规则计算")

    except Exception as e:
        print(f"[X] 测试失败: {e}")


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  LLM配置测试工具")
    print("  用于检查TravelAgents系统的LLM配置状态")
    print("=" * 60)

    # 1. 检查环境变量
    has_valid_key = test_env_config()

    if not has_valid_key:
        print("\n" + "[!] " * 20)
        print("警告: 未检测到有效的LLM API Key!")
        print("系统将使用规则引擎(fallback)运行。")
        print("\n请配置以下任一LLM提供商的API Key:")
        print("  - SILICONFLOW_API_KEY (硅基流动 + 千问2.5 - 推荐)")
        print("  - DEEPSEEK_API_KEY (DeepSeek)")
        print("  - OPENAI_API_KEY (OpenAI GPT)")
        print("  - GOOGLE_API_KEY (Google Gemini)")
        print("  - DASHSCOPE_API_KEY (阿里云通义千问)")
        print("\n配置方法:")
        print("  1. 打开 .env 文件")
        print("  2. 将对应的 your_xxx_key_here 替换为实际API Key")
        print("  3. 保存后重启服务")
        print("[!] " * 20)
        return

    # 2. 测试LLM创建
    test_llm_creation()

    # 3. 测试LLM调用
    test_llm_invoke()

    # 4. 测试智能体使用
    test_agent_llm_usage()

    print("\n" + "=" * 60)
    print("  测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
