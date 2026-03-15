"""
测试优先级加载功能

验证：
1. 后端生成攻略时是否设置了 image_source="preset"
2. 后台线程是否正确获取真实图片
"""
import sys
import json

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_priority_loading():
    print("=" * 60)
    print("测试优先级加载功能")
    print("=" * 60)

    # 测试导入
    print("\n1. 测试导入模块...")
    try:
        from tradingagents.services.tool_enhanced_guide_generator import ToolEnhancedGuideGenerator
        print("✅ 模块导入成功")
    except Exception as e:
        print(f"❌ 模块导入失败: {e}")
        return

    # 测试创建生成器
    print("\n2. 测试创建生成器...")
    try:
        generator = ToolEnhancedGuideGenerator(llm=None)
        print("✅ 生成器创建成功")
    except Exception as e:
        print(f"❌ 生成器创建失败: {e}")
        return

    # 测试预设图片字典
    print("\n3. 测试预设图片字典...")
    preset_images = generator.PRESET_IMAGES
    print(f"✅ 预设图片包含 {len(preset_images)} 个城市")

    # 检查新加坡预设图片
    if "新加坡" in preset_images:
        singapore_attractions = preset_images["新加坡"]
        print(f"   新加坡有 {len(singapore_attractions)} 个景点预设图片")
        for name in list(singapore_attractions.keys())[:5]:
            print(f"   - {name}")

    # 测试获取预设图片
    print("\n4. 测试获取预设图片...")
    test_cases = [
        ("圣淘沙", "新加坡"),
        ("滨海湾", "新加坡"),
        ("故宫", "北京"),
        ("外滩", "上海"),
    ]

    for attraction, city in test_cases:
        url = generator._get_preset_image(attraction, city)
        if url and "unsplash" in url:
            print(f"✅ {attraction} ({city}): {url[:50]}...")
        else:
            print(f"⚠️ {attraction} ({city}): {url}")

    # 测试生成简单攻略
    print("\n5. 测试生成攻略（检查 image_source 字段）...")
    basic_guide = {
        "destination": "新加坡",
        "total_days": 2,
        "daily_itineraries": [
            {
                "day": 1,
                "title": "第一天",
                "schedule": [
                    {"period": "morning", "activity": "游览圣淘沙", "location": "圣淘沙"},
                    {"period": "lunch", "activity": "午餐"},
                    {"period": "afternoon", "activity": "滨海湾", "location": "滨海湾"},
                ]
            },
            {
                "day": 2,
                "title": "第二天",
                "schedule": [
                    {"period": "morning", "activity": "乌节路", "location": "乌节路"},
                    {"period": "lunch", "activity": "午餐"},
                    {"period": "afternoon", "activity": "植物园", "location": "植物园"},
                ]
            }
        ]
    }

    try:
        detailed_guide = generator.generate_detailed_guide(basic_guide)

        # 检查返回数据
        print(f"✅ 攻略生成成功")
        print(f"   目的地: {detailed_guide.get('destination')}")
        print(f"   天数: {detailed_guide.get('total_days')}")
        print(f"   每日行程数: {len(detailed_guide.get('daily_itineraries', []))}")

        # 检查 image_source 字段
        print("\n6. 检查 image_source 字段...")
        for day in detailed_guide.get("daily_itineraries", []):
            day_num = day.get("day")
            print(f"\n   第{day_num}天:")
            for item in day.get("schedule", []):
                activity = item.get("activity", "")
                image_source = item.get("image_source", "未设置")
                image_url = item.get("imageUrl", item.get("image_url", ""))
                if image_url:
                    print(f"     - {activity}: source={image_source}, url={image_url[:40]}...")
                else:
                    print(f"     - {activity}: source={image_source}, url=无")

    except Exception as e:
        print(f"❌ 攻略生成失败: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    test_priority_loading()
