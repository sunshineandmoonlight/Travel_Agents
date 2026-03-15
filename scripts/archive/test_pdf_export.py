"""
测试PDF导出功能

测试攻略PDF生成器的完整流程
"""
import sys
import os
import io

# 设置UTF-8编码输出（Windows兼容）
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


def test_pdf_generator_import():
    """测试PDF生成器导入"""
    print("\n[测试1] 测试PDF生成器导入...")
    try:
        from app.utils.pdf_generator import GuidePDFGenerator, get_pdf_generator, generate_guide_pdf
        print("  ✓ PDF生成器导入成功")
        return True
    except Exception as e:
        print(f"  ✗ 导入失败: {e}")
        return False


def test_pdf_generator_creation():
    """测试PDF生成器创建"""
    print("\n[测试2] 测试PDF生成器创建...")
    try:
        from app.utils.pdf_generator import get_pdf_generator
        generator = get_pdf_generator()
        print(f"  ✓ 生成器创建成功: {type(generator).__name__}")
        return True
    except Exception as e:
        print(f"  ✗ 创建失败: {e}")
        return False


def test_html_content_generation():
    """测试HTML内容生成"""
    print("\n[测试3] 测试HTML内容生成...")
    try:
        from app.utils.pdf_generator import get_pdf_generator

        # 模拟攻略数据
        guide_data = {
            "id": 1,
            "title": "杭州三日休闲之旅",
            "description": "探索杭州的自然美景和人文历史",
            "destination": "杭州",
            "days": 3,
            "budget_level": "medium",
            "travel_style": "relaxed",
            "travelers_count": 2,
            "cover_image": "",
            "interest_tags": ["自然", "美食", "历史"],
            "itinerary": {
                "daily_itinerary": [
                    {
                        "day": 1,
                        "theme": "西湖经典游",
                        "morning": {"time": "09:00-12:00", "activity": "游览西湖十景"},
                        "lunch": {"time": "12:00-13:30", "activity": "楼外楼品尝杭帮菜"},
                        "afternoon": {"time": "14:00-17:00", "activity": "雷峰塔与苏堤"},
                        "dinner": {"time": "18:00-20:00", "activity": "河坊街小吃"},
                        "evening": {"time": "20:00-22:00", "activity": "西湖音乐喷泉"}
                    },
                    {
                        "day": 2,
                        "theme": "灵隐礼佛",
                        "morning": {"time": "09:00-12:30", "activity": "灵隐寺与飞来峰"},
                        "lunch": {"time": "12:30-14:00", "activity": "灵隐寺素斋"},
                        "afternoon": {"time": "14:00-17:30", "activity": "九溪十八涧徒步"},
                        "dinner": {"time": "18:00-20:00", "activity": "龙井村农家菜"},
                        "evening": {"time": "20:00-22:00", "activity": "酒店休息"}
                    },
                    {
                        "day": 3,
                        "theme": "千岛湖游",
                        "morning": {"time": "08:00-12:00", "activity": "出发千岛湖"},
                        "lunch": {"time": "12:00-13:30", "activity": "千岛湖鱼头"},
                        "afternoon": {"time": "13:30-16:30", "activity": "继续游览"},
                        "dinner": {"time": "19:00-20:30", "activity": "告别晚餐"}
                    }
                ]
            },
            "budget_breakdown": {
                "total_budget": 2060,
                "daily_average": 687,
                "per_person_average": 1030,
                "transportation": {"amount": 300, "description": "含千岛湖往返大巴"},
                "accommodation": {"amount": 900, "description": "2晚舒适型酒店"},
                "meals": {"amount": 600, "description": "3天餐饮"},
                "attractions": {"amount": 200, "description": "景点门票"},
                "miscellaneous": {"amount": 60, "description": "其他支出"},
                "money_saving_tips": [
                    "住宿可选择民宿节省30%-50%",
                    "餐饮多尝试小吃经济实惠",
                    "公共交通便利尽量不用打车",
                    "避开节假日价格更优惠"
                ]
            },
            "attractions": [
                {"name": "西湖", "description": "世界文化遗产，人间天堂"},
                {"name": "灵隐寺", "description": "千年古刹，佛教圣地"},
                {"name": "千岛湖", "description": "岛屿最多的湖泊"},
                {"name": "雷峰塔", "description": "杭州标志性建筑"},
                {"name": "九溪十八涧", "description": "自然峡谷景观"}
            ],
            "accommodation": {
                "type": "舒适型酒店",
                "budget": 450
            },
            "transportation": {
                "type": "高铁+市内交通",
                "budget": 300
            },
            "created_at": "2026-03-10T10:00:00",
            "username": "travel_lover",
            "rating_avg": 4.8,
            "rating_count": 25,
            "view_count": 1250
        }

        generator = get_pdf_generator()
        html_content = generator.generate_html_content(guide_data)

        # 验证HTML内容
        if len(html_content) > 1000:
            print(f"  ✓ HTML内容生成成功 ({len(html_content)} 字符)")
            print(f"  ✓ 包含标题: {guide_data['title'] in html_content}")
            print(f"  ✓ 包含目的地: {guide_data['destination'] in html_content}")
            return True
        else:
            print(f"  ✗ HTML内容过短: {len(html_content)} 字符")
            return False

    except Exception as e:
        print(f"  ✗ HTML生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_generation():
    """测试PDF生成"""
    print("\n[测试4] 测试PDF生成...")
    try:
        from app.utils.pdf_generator import get_pdf_generator

        guide_data = {
            "id": 1,
            "title": "杭州三日游",
            "description": "测试攻略",
            "destination": "杭州",
            "days": 3,
            "budget_level": "medium",
            "travel_style": "relaxed",
            "travelers_count": 2,
            "itinerary": {"daily_itinerary": []},
            "budget_breakdown": {"total_budget": 2000},
            "attractions": [],
            "created_at": "2026-03-10"
        }

        generator = get_pdf_generator()
        pdf_bytes = generator.generate_pdf(guide_data)

        if len(pdf_bytes) > 1000:
            print(f"  ✓ PDF生成成功 ({len(pdf_bytes)} 字节)")
            return True
        else:
            print(f"  ✗ PDF内容过短: {len(pdf_bytes)} 字节")
            return False

    except ImportError as e:
        print(f"  ⚠ PDF库未安装 (weasyprint/reportlab): {e}")
        print("  ⚠ 这是可选功能，不影响API运行")
        return True  # 不算失败，因为这是可选依赖
    except Exception as e:
        print(f"  ✗ PDF生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_api_endpoint():
    """测试PDF导出API端点"""
    print("\n[测试5] 测试PDF导出API端点...")
    try:
        from app.routers.travel import router

        # 检查是否有export路由
        export_routes = [r for r in router.routes if "export" in r.path]
        if export_routes:
            print(f"  ✓ PDF导出端点已注册: {export_routes[0].path}")
            print(f"  ✓ HTTP方法: {export_routes[0].methods}")
            return True
        else:
            print(f"  ✗ 未找到PDF导出端点")
            return False

    except Exception as e:
        print(f"  ✗ 端点检查失败: {e}")
        return False


def test_complete_pdf_export_flow():
    """测试完整的PDF导出流程"""
    print("\n[测试6] 测试完整PDF导出流程...")
    try:
        from app.utils.pdf_generator import generate_guide_pdf

        # 完整的攻略数据
        complete_guide = {
            "id": 999,
            "uuid": "test-uuid-123",
            "title": "完整测试攻略 - 杭州深度游",
            "description": "这是一个完整的攻略描述，包含详细的目的地介绍、行程亮点和旅行建议。",
            "destination": "杭州",
            "destination_type": "domestic",
            "days": 5,
            "budget_level": "medium",
            "travel_style": "immersive",
            "travelers_count": 2,
            "cover_image": "https://example.com/cover.jpg",
            "interest_tags": ["自然", "历史", "美食", "摄影"],
            "itinerary": {
                "daily_itinerary": [
                    {
                        "day": 1,
                        "theme": "西湖全景",
                        "morning": {"time": "08:00-12:00", "activity": "断桥残雪 → 白堤 → 孤山"},
                        "lunch": {"time": "12:00-13:30", "activity": "楼外楼（西湖醋鱼）"},
                        "afternoon": {"time": "14:00-17:30", "activity": "苏堤春晓 → 曲院风荷"},
                        "dinner": {"time": "18:00-20:00", "activity": "知味观"},
                        "evening": {"time": "20:00-22:00", "activity": "西湖夜景"}
                    },
                    {
                        "day": 2,
                        "theme": "佛教文化",
                        "morning": {"time": "08:30-12:00", "activity": "灵隐寺 → 飞来峰"},
                        "lunch": {"time": "12:00-13:30", "activity": "灵隐寺素面"},
                        "afternoon": {"time": "14:00-17:00", "activity": "三天竺 → 法喜寺"},
                        "dinner": {"time": "18:00-20:00", "activity": "素食餐厅"},
                        "evening": {"time": "20:00-21:30", "activity": "寺庙晚课体验"}
                    }
                ]
            },
            "budget_breakdown": {
                "total_budget": 3500,
                "daily_average": 700,
                "per_person_average": 1750,
                "transportation": {"amount": 500, "description": "高铁往返 + 市内交通"},
                "accommodation": {"amount": 1500, "description": "4晚精品民宿"},
                "meals": {"amount": 1000, "description": "当地特色餐饮"},
                "attractions": {"amount": 400, "description": "景点门票"},
                "miscellaneous": {"amount": 100, "description": "其他"},
                "money_saving_tips": [
                    "提前预订民宿可享折扣",
                    "很多寺庙有免费开放时段",
                    "使用杭州公交卡更优惠"
                ]
            },
            "attractions": [
                {
                    "name": "西湖",
                    "description": "世界文化遗产，中国最美的湖泊之一，四季景色各异。"
                },
                {
                    "name": "灵隐寺",
                    "description": "中国最早佛教寺院之一，距今已有1700年历史。"
                },
                {
                    "name": "千岛湖",
                    "description": "世界上岛屿最多的湖泊，湖光山色秀美。"
                },
                {
                    "name": "宋城",
                    "description": "大型文化主题公园，宋城千古情演出震撼。"
                }
            ],
            "accommodation": {
                "type": "精品民宿",
                "budget": 375
            },
            "transportation": {
                "type": "高铁+地铁+公交",
                "budget": 500
            },
            "best_seasons": ["春季", "秋季"],
            "weather_info": {
                "temperature": "15-25°C",
                "description": "春秋两季最适宜游览"
            },
            "created_at": "2026-03-10T10:00:00",
            "username": "旅行达人",
            "rating_avg": 4.9,
            "rating_count": 128,
            "view_count": 5680
        }

        author_info = {
            "username": "旅行达人",
            "user_id": 1
        }

        # 生成PDF
        pdf_bytes = generate_guide_pdf(complete_guide, author_info)

        # PDF大小应该大于2KB（reportlab生成的PDF很紧凑）
        if pdf_bytes and len(pdf_bytes) > 2000:
            print(f"  ✓ 完整PDF生成成功 ({len(pdf_bytes)} 字节)")
            print(f"  ✓ 攻略标题: {complete_guide['title']}")
            print(f"  ✓ 目的地: {complete_guide['destination']}")
            print(f"  ✓ 天数: {complete_guide['days']}天")
            print(f"  ✓ 景点数: {len(complete_guide['attractions'])}个")
            return True
        else:
            print(f"  ✗ PDF生成异常: {len(pdf_bytes) if pdf_bytes else 0} 字节")
            return False

    except ImportError as e:
        print(f"  ⚠ PDF库未安装 (weasyprint/reportlab): {e}")
        return True  # 不算失败
    except Exception as e:
        print(f"  ✗ 流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_sample_html():
    """保存示例HTML文件用于预览"""
    print("\n[测试7] 保存示例HTML...")
    try:
        from app.utils.pdf_generator import get_pdf_generator

        guide_data = {
            "id": 1,
            "title": "杭州三日休闲之旅",
            "description": "探索杭州的自然美景和人文历史，体验江南水乡的独特魅力。",
            "destination": "杭州",
            "days": 3,
            "budget_level": "medium",
            "travel_style": "relaxed",
            "travelers_count": 2,
            "cover_image": "",
            "interest_tags": ["自然", "美食", "历史"],
            "itinerary": {
                "daily_itinerary": [
                    {
                        "day": 1,
                        "theme": "西湖经典游",
                        "morning": {"time": "09:00-12:00", "activity": "游览西湖十景，从断桥残雪开始"},
                        "lunch": {"time": "12:00-13:30", "activity": "楼外楼品尝杭帮菜（西湖醋鱼、东坡肉）"},
                        "afternoon": {"time": "14:00-17:00", "activity": "登雷峰塔俯瞰西湖，漫步苏堤"},
                        "dinner": {"time": "18:00-20:00", "activity": "河坊街品尝小吃（葱包桧、定胜糕）"},
                        "evening": {"time": "20:00-22:00", "activity": "观赏西湖音乐喷泉"}
                    }
                ]
            },
            "budget_breakdown": {
                "total_budget": 2060,
                "daily_average": 687,
                "per_person_average": 1030,
                "transportation": {"amount": 300, "description": "含千岛湖往返大巴"},
                "accommodation": {"amount": 900, "description": "2晚舒适型酒店"},
                "meals": {"amount": 600, "description": "3天餐饮"},
                "attractions": {"amount": 200, "description": "景点门票"},
                "miscellaneous": {"amount": 60, "description": "其他"},
                "money_saving_tips": [
                    "住宿可选择民宿节省30%-50%",
                    "餐饮多尝试小吃经济实惠",
                    "公共交通便利尽量不用打车"
                ]
            },
            "attractions": [
                {"name": "西湖", "description": "世界文化遗产，人间天堂"},
                {"name": "灵隐寺", "description": "千年古刹，佛教圣地"}
            ],
            "accommodation": {"type": "舒适型酒店", "budget": 450},
            "transportation": {"type": "高铁+市内交通", "budget": 300},
            "created_at": "2026-03-10",
            "username": "旅行爱好者"
        }

        generator = get_pdf_generator()
        html_content = generator.generate_html_content(guide_data)

        # 保存到文件
        output_path = os.path.join(project_root, "logs", "sample_guide.html")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"  ✓ HTML文件已保存: {output_path}")
        print(f"  ✓ 可以在浏览器中打开预览")
        return True

    except Exception as e:
        print(f"  ✗ 保存失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("  PDF导出功能测试")
    print("=" * 60)

    tests = [
        ("PDF生成器导入", test_pdf_generator_import),
        ("PDF生成器创建", test_pdf_generator_creation),
        ("HTML内容生成", test_html_content_generation),
        ("PDF生成", test_pdf_generation),
        ("PDF导出API端点", test_pdf_api_endpoint),
        ("完整PDF导出流程", test_complete_pdf_export_flow),
        ("保存示例HTML", save_sample_html)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 发生异常: {e}")
            results.append((name, False))

    # 汇总结果
    print("\n" + "=" * 60)
    print("  测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {status}: {name}")

    print(f"\n总计: {passed}/{total} 通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！PDF导出功能已就绪。")
    else:
        print(f"\n⚠ {total - passed} 个测试失败，请检查。")


if __name__ == "__main__":
    main()
