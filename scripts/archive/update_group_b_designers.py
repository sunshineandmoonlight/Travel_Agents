"""
快速更新脚本：批量更新Group B所有Designer使用API工具

将ImmersiveDesigner的改进应用到其他Designer
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

print("=" * 70)
print("  批量更新Group B Designer使用API工具")
print("=" * 70)

# 要更新的Designer列表
designers_to_update = [
    ("exploration_designer", "ExplorationDesigner", "探索式", "exploration", "打卡热门景点"),
    ("relaxation_designer", "RelaxationDesigner", "松弛式", "relaxation", "公园休闲轻松"),
    ("hidden_gem_designer", "HiddenGemDesigner", "小众宝藏", "hidden_gem", "小众冷门景点"),
]

for designer_file, class_name, style_name, style_key, style_keywords in designers_to_update:
    print(f"\n【更新】{class_name} ({style_name})")
    print("-" * 70)

    try:
        # 读取原始文件
        with open(f"tradingagents/agents/group_b/{designer_file}.py", "r", encoding="utf-8") as f:
            content = f.read()

        # 检查是否已经更新过
        if "from .api_tools" in content:
            print(f"  [SKIP] {class_name} 已经更新过")
            continue

        # 在import部分添加API工具导入
        import_section = """from typing import Dict, Any, List
import logging
import asyncio
import os

logger = logging.getLogger('travel_agents')"""

        new_import_section = """from typing import Dict, Any, List
import logging
import asyncio
import os

logger = logging.getLogger('travel_agents')

# 导入API工具
from .api_tools.serpapi_tool import SerpAPITool
from .api_tools.opentripmap_tool import OpenTripMapTool
"""

        content = content.replace(import_section, new_import_section)

        # 更新_get_real_attractions函数（如果存在）
        old_attraction_func = """def _get_real_attractions(destination: str, days: int, keywords: str) -> List[Dict[str, Any]]:"""
        new_attraction_func = f"""def _get_real_attractions(destination: str, days: int, keywords: str) -> List[Dict[str, Any]]:
    \"\"\"
    使用新的API工具获取实时景点数据

    Args:
        destination: 目的地名称
        days: 天数
        keywords: 搜索关键词

    Returns:
        景点列表
    \"\"\"
    all_attractions = []

    # 优先使用SerpAPI
    if os.getenv("SERPAPI_KEY") and os.getenv("SERPAPI_KEY") != "your_serpapi_key_here":
        try:
            serpapi_tool = SerpAPITool()
            serp_results = asyncio.run(serpapi_tool.search_attractions(
                destination=destination,
                keywords=keywords,
                days=days,
                style="{style_key}"
            ))

            if serp_results:
                all_attractions.extend(serp_results)
                logger.info(f"[{class_name}] SerpAPI搜索到 {{len(serp_results)}} 个景点")
        except Exception as e:
            logger.warning(f"[{class_name}] SerpAPI搜索失败: {{e}}")

    # 补充OpenTripMap数据
    if os.getenv("OPENTRIPMAP_API_KEY") and os.getenv("OPENTRIPMAP_API_KEY") != "your_opentripmap_key_here":
        try:
            opentripmap_tool = OpenTripMapTool()
            otm_results = asyncio.run(opentripmap_tool.search_attractions(
                destination=destination,
                keywords=keywords,
                days=days,
                style="{style_key}"
            ))

            if otm_results:
                # 去重（基于名称）
                existing_names = {{a.get("name", "") for a in all_attractions}}
                for otm_attr in otm_results:
                    if otm_attr.get("name", "") not in existing_names:
                        all_attractions.append(otm_attr)

                logger.info(f"[{class_name}] OpenTripMap搜索到 {{len(otm_results)}} 个景点")
        except Exception as e:
            logger.warning(f"[{class_name}] OpenTripMap搜索失败: {{e}}")

    if all_attractions:
        logger.info(f"[{class_name}] 总共获取 {{len(all_attractions)}} 个实时景点")
    else:
        logger.warning(f"[{class_name}] 未获取到实时景点数据")

    return all_attractions
"""

        if old_attraction_func in content:
            content = content.replace(old_attraction_func, new_attraction_func)
            print(f"  [OK] 更新 _get_real_attractions 函数")

        # 更新design_xxx_style函数，添加LLM描述
        old_return_start = """return {
        "style_name": """

        if old_return_start in content:
            # 找到return语句的位置
            start_idx = content.find(old_return_start)
            if start_idx > 0:
                # 在return语句之前添加LLM描述生成
                insert_pos = start_idx

                # 生成LLM描述函数调用
                llm_desc_code = f"""

    # 使用LLM生成方案描述
    llm_description = _generate_llm_description(
        destination,
        days,
        used_attractions[:5] if len(used_attractions) > 5 else used_attractions,
        user_portrait,
        llm
    )

"""

                content = content[:insert_pos] + llm_desc_code + content[insert_pos:]

                # 更新return语句添加新字段
                old_fields = """"data_source": data_source  # 标记数据来源
    }}"""

                new_fields = f"""data_source": data_source,
        "api_sources_used": api_sources_used,
        "llm_description": llm_description,
        "agent_info": {{
            "name_cn": "{style_name}设计师",
            "name_en": "{class_name}",
            "icon": "🎯" if "{style_key}" != "immersive" else "🎭",
            "group": "B",
            "llm_enabled": llm is not None
        }}
    }}"""

                content = content.replace(old_fields, new_fields)

                print(f"  [OK] 添加LLM描述和api_sources_used字段")

        # 添加LLM描述生成函数
        llm_func_pattern = f"def _generate_llm_description"
        if llm_func_pattern not in content:
            # 在文件末尾添加LLM描述函数
            llm_function = f"""

def _generate_llm_description(
    destination: str,
    days: int,
    attractions: List[str],
    user_portrait: Dict[str, Any],
    llm=None
) -> str:
    \"\"\"
    使用LLM生成{style_name}方案的自然语言描述

    Args:
        destination: 目的地
        days: 天数
        attractions: 主要景点列表
        user_portrait: 用户画像
        llm: LLM实例

    Returns:
        LLM生成的描述文本
    \"\"\"
    if llm:
        try:
            travel_type = user_portrait.get("travel_type", "")
            interests = user_portrait.get("primary_interests", [])
            interests_text = "、".join(interests) if interests else "{style_keywords}"

            prompt = f\"\"\"请为以下{style_name}旅行方案生成一段吸引人的描述（约150-200字）：

目的地：{{destination}}
旅行天数：{{days}}天
旅行类型：{{travel_type}}
用户兴趣：{{interests_text}}
核心景点：{{', '.join(attractions[:5])}}

方案特点：
- {style_keywords}
- 慢节奏，拒绝走马观花
- 专注于深度体验和探索

请生成一段能吸引旅行者的描述，突出这种旅行方式的独特魅力。

直接输出描述文字，不要标题。\"\"\"

            from langchain_core.messages import HumanMessage
            response = llm.invoke([HumanMessage(content=prompt)])
            description = response.content.strip()
            logger.info(f"[{class_name}] LLM生成描述成功: {{len(description)}}字")
            return description

        except Exception as e:
            logger.warning(f"[{class_name}] LLM生成描述失败: {{e}}")

    # 默认描述
    return f"""这是一场精彩的{style_name}之旅，在{{destination}}的{{days}}天里，您将体验最纯正的旅行方式。不同于传统的观光旅行，{style_name}之旅注重深度体验和探索，每个景点都值得您停留。在{{', '.join(attractions[:3])}}等经典地标，您将放慢脚步，细细品味每一处细节，让旅行成为一次难忘的回忆。\"\""

            content = content.rstrip() + "\n" + llm_function

            print(f"  [OK] 添加 _generate_llm_description 函数")

        # 写入更新后的文件
        with open(f"tradingagents/agents/group_b/{designer_file}.py", "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  [SUCCESS] {class_name} 更新完成")

    except Exception as e:
        print(f"  [ERROR] {class_name} 更新失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("  批量更新完成")
print("=" * 70)
print("""
下一步:
1. 测试所有Designer的API调用
2. 验证LLM描述生成
3. 更新前端显示API来源
4. 添加API调用日志监控
""")
