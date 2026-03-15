"""
旅行系统 API 测试脚本

测试所有旅行相关的 API 端点
"""

import httpx
import asyncio
import json
from typing import Optional, Dict, Any


class TravelAPITester:
    """旅行 API 测试器"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)
        self.auth_token: Optional[str] = None

    async def close(self):
        """关闭客户端"""
        await self.client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """发送请求"""
        url = f"{self.base_url}{path}"
        headers = {}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            if method.upper() == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, headers=headers)
            else:
                raise ValueError(f"不支持的 HTTP 方法: {method}")

            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e)}

    async def test_health(self):
        """测试健康检查"""
        print("\n[测试] 健康检查...")
        result = await self.request("GET", "/health")
        print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return "error" not in result

    async def test_create_travel_plan(self):
        """测试创建旅行规划"""
        print("\n[测试] 创建旅行规划...")

        data = {
            "destination": "北京",
            "days": 5,
            "budget": "medium",
            "travelers": 2,
            "interest_type": "历史",
            "selected_style": "immersive",
            "save_as_guide": True,
            "guide_title": "北京5日历史文化深度游"
        }

        result = await self.request("POST", "/api/travel/plan", data=data)
        print(f"  成功: {result.get('success')}")
        print(f"  消息: {result.get('message')}")

        if result.get("success"):
            print(f"  攻略ID: {result.get('guide_id')}")
            print(f"  攻略UUID: {result.get('guide_uuid')}")

            # 打印部分数据
            if result.get("data"):
                plan_data = result["data"]
                print(f"  目的地: {plan_data.get('destination')}")
                print(f"  天数: {plan_data.get('days')}")
                print(f"  预算: {plan_data.get('budget_breakdown', {}).get('total_budget')} 元")

        return result.get("success", False)

    async def test_get_guides(self):
        """测试获取攻略列表"""
        print("\n[测试] 获取攻略列表...")

        params = {
            "page": 1,
            "page_size": 10,
            "sort_by": "created_at",
            "sort_order": "desc"
        }

        result = await self.request("GET", "/api/travel/guides", params=params)
        print(f"  总数: {result.get('total')}")
        print(f"  当前页: {result.get('page')}")
        print(f"  攻略数: {len(result.get('items', []))}")

        if result.get("items"):
            print(f"  第一个攻略: {result['items'][0].get('title')}")

        return "error" not in result

    async def test_get_guide_detail(self, guide_id: int):
        """测试获取攻略详情"""
        print(f"\n[测试] 获取攻略详情 (ID: {guide_id})...")

        result = await self.request("GET", f"/api/travel/guides/{guide_id}")
        print(f"  标题: {result.get('title')}")
        print(f"  目的地: {result.get('destination')}")
        print(f"  天数: {result.get('days')}")
        print(f"  浏览量: {result.get('view_count')}")

        return "error" not in result

    async def test_search_guides(self):
        """测试搜索攻略"""
        print("\n[测试] 搜索攻略...")

        params = {
            "keyword": "北京",
            "page": 1,
            "page_size": 5
        }

        result = await self.request("GET", "/api/travel/guides/search/fulltext", params=params)
        print(f"  搜索结果: {result.get('total')} 条")
        print(f"  匹配攻略:")

        for item in result.get("items", [])[:3]:
            print(f"    - {item.get('title')} ({item.get('destination')})")

        return "error" not in result

    async def test_get_stats(self):
        """测试获取统计数据"""
        print("\n[测试] 获取统计数据...")

        result = await self.request("GET", "/api/travel/stats")
        print(f"  总攻略数: {result.get('total_guides')}")
        print(f"  已发布: {result.get('published_guides')}")
        print(f"  总浏览: {result.get('total_views')}")
        print(f"  总点赞: {result.get('total_likes')}")
        print(f"  热门目的地:")

        for dest in result.get("top_destinations", [])[:5]:
            print(f"    - {dest.get('destination')}: {dest.get('count')}")

        return "error" not in result

    async def test_like_guide(self, guide_id: int):
        """测试点赞攻略"""
        print(f"\n[测试] 点赞攻略 (ID: {guide_id})...")

        result = await self.request("POST", f"/api/travel/guides/{guide_id}/like")
        print(f"  已点赞: {result.get('is_liked')}")
        print(f"  点赞数: {result.get('like_count')}")

        # 再次点赞测试取消
        result2 = await self.request("POST", f"/api/travel/guides/{guide_id}/like")
        print(f"  取消后点赞: {result2.get('is_liked')}")
        print(f"  点赞数: {result2.get('like_count')}")

        return "error" not in result

    async def test_bookmark_guide(self, guide_id: int):
        """测试收藏攻略"""
        print(f"\n[测试] 收藏攻略 (ID: {guide_id})...")

        data = {
            "notes": "这是一个测试收藏",
            "folder_name": "测试收藏夹"
        }

        result = await self.request("POST", f"/api/travel/guides/{guide_id}/bookmark", data=data)
        print(f"  收藏成功: {result.get('notes')}")
        print(f"  收藏夹: {result.get('folder_name')}")

        # 取消收藏
        await self.request("DELETE", f"/api/travel/guides/{guide_id}/bookmark")
        print("  已取消收藏")

        return "error" not in result

    async def test_get_recommendations(self, guide_id: int):
        """测试获取推荐"""
        print(f"\n[测试] 获取相似攻略推荐 (ID: {guide_id})...")

        result = await self.request("GET", f"/api/travel/guides/{guide_id}/recommendations")
        print(f"  推荐数量: {len(result)}")

        for guide in result[:3]:
            print(f"    - {guide.get('title')} ({guide.get('destination')})")

        return "error" not in result

    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("旅行系统 API 测试")
        print("=" * 60)

        tests = [
            ("健康检查", self.test_health),
            ("创建旅行规划", self.test_create_travel_plan),
            ("获取攻略列表", self.test_get_guides),
            ("搜索攻略", self.test_search_guides),
            ("获取统计", self.test_get_stats),
        ]

        results = {}
        guide_id = None

        for name, test_func in tests:
            try:
                success = await test_func()
                results[name] = success

                # 获取攻略ID用于后续测试
                if name == "获取攻略列表":
                    # 这里应该从实际的API响应中获取ID
                    pass

            except Exception as e:
                print(f"  错误: {e}")
                results[name] = False

        # 输出测试结果
        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)

        for name, success in results.items():
            status = "PASS" if success else "FAIL"
            print(f"  [{status}] {name}")

        all_passed = all(results.values())
        print("\n" + "=" * 60)
        if all_passed:
            print("所有测试通过!")
        else:
            print("部分测试失败")
        print("=" * 60)


async def main():
    """主函数"""
    tester = TravelAPITester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.close()


if __name__ == "__main__":
    asyncio.run(main())
