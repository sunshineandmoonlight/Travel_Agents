"""
学习中心API路由

提供旅行规划系统的学习资料和文档管理功能
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel

from app.routers.auth_db import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/learning", tags=["学习中心"])


# ============================================================
# 数据模型
# ============================================================

class ArticleCategory(BaseModel):
    """文章分类"""
    id: str
    name: str
    display_name: str
    description: str
    icon: str
    color: str
    article_count: int
    sort_order: int


class ArticleInfo(BaseModel):
    """文章信息"""
    id: str
    title: str
    category: str
    category_display: str
    description: str
    content: str
    read_time: str
    difficulty: str
    views: int
    sort_order: int
    related_articles: List[str] = []
    tags: List[str] = []


class ArticleListResponse(BaseModel):
    """文章列表响应"""
    category: str
    category_display: str
    articles: List[ArticleInfo]


# ============================================================
# 文章数据（旅行学习中心）
# ============================================================

LEARNING_CATEGORIES = [
    {
        "id": "ai-basics",
        "name": "ai-travel-basics",
        "display_name": "AI旅行基础",
        "description": "了解AI旅行规划的基本概念和工作原理",
        "icon": "🤖",
        "color": "primary",
        "sort_order": 1
    },
    {
        "id": "destination-guide",
        "name": "destination-guide",
        "display_name": "目的地指南",
        "description": "如何描述旅行需求，选择合适的目的地",
        "icon": "🗺️",
        "color": "success",
        "sort_order": 2
    },
    {
        "id": "agent-system",
        "name": "agent-system",
        "display_name": "多智能体系统",
        "description": "深入了解每个Agent的工作原理",
        "icon": "🔧",
        "color": "warning",
        "sort_order": 3
    },
    {
        "id": "prompt-guide",
        "name": "prompt-guide",
        "display_name": "使用指南",
        "description": "学习如何更好地使用旅行规划系统",
        "icon": "✍️",
        "color": "info",
        "sort_order": 4
    },
    {
        "id": "best-practices",
        "name": "best-practices",
        "display_name": "最佳实践",
        "description": "获取更好的旅行规划结果的技巧",
        "icon": "⭐",
        "color": "success",
        "sort_order": 5
    },
    {
        "id": "tutorials",
        "name": "tutorials",
        "display_name": "实战教程",
        "description": "通过实际案例学习如何使用系统",
        "icon": "🎓",
        "color": "primary",
        "sort_order": 6
    },
    {
        "id": "faq",
        "name": "faq",
        "display_name": "常见问题",
        "description": "快速找到常见问题的答案",
        "icon": "❓",
        "color": "info",
        "sort_order": 7
    },
    {
        "id": "resources",
        "name": "resources",
        "display_name": "相关资源",
        "description": "旅行API资源、开源项目链接等",
        "icon": "📚",
        "color": "default",
        "sort_order": 8
    }
]

# 文章内容存储
ARTICLES = {
    # AI旅行基础
    "what-is-ai-travel": {
        "id": "what-is-ai-travel",
        "title": "什么是AI旅行规划？",
        "category": "ai-basics",
        "category_display": "AI旅行基础",
        "description": "了解AI旅行规划的基本概念，以及它如何改变你的旅行方式",
        "content": "AI旅行规划是利用人工智能技术，特别是大语言模型(LLM)和多智能体系统，自动为你生成个性化旅行方案的过程...",
        "read_time": "10分钟",
        "difficulty": "入门",
        "views": 1250,
        "sort_order": 1,
        "tags": ["AI", "旅行", "入门"],
        "related_articles": ["multi-agent-intro", "how-to-describe"]
    },
    "multi-agent-intro": {
        "id": "multi-agent-intro",
        "title": "多智能体系统详解",
        "category": "agent-system",
        "category_display": "多智能体系统",
        "description": "深入了解多智能体系统如何协作完成旅行规划",
        "content": "多智能体系统是由多个智能Agent组成的协作系统，每个Agent负责特定的任务...",
        "read_time": "15分钟",
        "difficulty": "中级",
        "views": 890,
        "sort_order": 1,
        "tags": ["多智能体", "架构", "技术"],
        "related_articles": ["what-is-ai-travel", "attraction-analyst"]
    },
    "how-to-describe": {
        "id": "how-to-describe",
        "title": "如何写好旅行需求描述",
        "category": "prompt-guide",
        "category_display": "使用指南",
        "description": "学会用清晰的语言描述你的旅行需求，获得更好的规划结果",
        "content": "写好旅行需求描述是获得优质AI规划的第一步。以下是几个关键要点...",
        "read_time": "8分钟",
        "difficulty": "入门",
        "views": 2100,
        "sort_order": 1,
        "tags": ["提示词", "需求描述", "入门"],
        "related_articles": ["what-is-ai-travel", "interest-tags"]
    },
    "interest-tags": {
        "id": "interest-tags",
        "title": "兴趣标签使用指南",
        "category": "prompt-guide",
        "category_display": "使用指南",
        "description": "了解如何使用兴趣标签获得更精准的推荐",
        "content": "兴趣标签是AI理解你旅行偏好的关键，包括自然、历史、美食、艺术等...",
        "read_time": "6分钟",
        "difficulty": "入门",
        "views": 1650,
        "sort_order": 2,
        "tags": ["标签", "兴趣", "推荐"],
        "related_articles": ["how-to-describe", "best-practices"]
    },
    "hangzhou-case": {
        "id": "hangzhou-case",
        "title": "实战案例：杭州三日游完整规划",
        "category": "tutorials",
        "category_display": "实战教程",
        "description": "从输入到攻略，完整演示杭州三日游的规划过程",
        "content": "让我们通过一个完整的案例来了解AI旅行规划的工作流程。用户输入：'杭州3天，喜欢自然'...",
        "read_time": "20分钟",
        "difficulty": "入门",
        "views": 3200,
        "sort_order": 1,
        "tags": ["案例", "杭州", "实战"],
        "related_articles": ["what-is-ai-travel", "how-to-describe"]
    },
    "overseas-travel": {
        "id": "overseas-travel",
        "title": "海外旅行规划指南",
        "category": "tutorials",
        "category_display": "实战教程",
        "description": "如何规划海外旅行，包括签证、机票、住宿等注意事项",
        "content": "海外旅行规划需要考虑更多因素，如签证、机票预订、当地交通等...",
        "read_time": "25分钟",
        "difficulty": "中级",
        "views": 1800,
        "sort_order": 2,
        "tags": ["海外", "国际", "签证"],
        "related_articles": ["how-to-describe", "best-practices"]
    },
    "budget-tips": {
        "id": "budget-tips",
        "title": "旅行省钱攻略",
        "category": "best-practices",
        "category_display": "最佳实践",
        "description": "AI帮你找到最经济的旅行方案，还有实用省钱技巧",
        "content": "旅行预算控制是很多旅行者关心的问题。AI可以通过多种方式帮你省钱...",
        "read_time": "12分钟",
        "difficulty": "入门",
        "views": 4500,
        "sort_order": 1,
        "tags": ["预算", "省钱", "技巧"],
        "related_articles": ["hangzhou-case", "how-to-describe"]
    },
    "season-guide": {
        "id": "season-guide",
        "title": "最佳旅行时间选择",
        "category": "best-practices",
        "category_display": "最佳实践",
        "description": "不同目的地在不同季节的特点，帮你选择最佳出行时间",
        "content": "选择合适的旅行时间能让你的旅行体验大大提升。不同季节有不同的风景和特点...",
        "read_time": "10分钟",
        "difficulty": "入门",
        "views": 2300,
        "sort_order": 2,
        "tags": ["季节", "天气", "时间"],
        "related_articles": ["how-to-describe", "destination-selection"]
    },
    "faq-general": {
        "id": "faq-general",
        "title": "常见问题解答",
        "category": "faq",
        "category_display": "常见问题",
        "description": "API配置、行程修改、数据源等常见问题的解答",
        "content": "Q: 如何配置DeepSeek API？\nA: 在设置页面添加LLM提供商，输入API密钥即可...\n\nQ: 行程不满意怎么办？\nA: 可以一键重新生成或指定修改某部分...",
        "read_time": "15分钟",
        "difficulty": "入门",
        "views": 5600,
        "sort_order": 1,
        "tags": ["FAQ", "问题", "解答"],
        "related_articles": ["how-to-describe", "budget-tips"]
    },
    "api-resources": {
        "id": "api-resources",
        "title": "旅行API资源汇总",
        "category": "resources",
        "category_display": "相关资源",
        "description": "高德地图、SerpAPI、Amadeus等旅行相关API资源介绍",
        "content": "以下是旅行规划常用的API资源汇总：\n\n1. 高德地图API - 国内景点和路线规划\n2. SerpAPI - 国际景点搜索\n3. Amadeus API - 机票酒店预订...",
        "read_time": "18分钟",
        "difficulty": "中级",
        "views": 980,
        "sort_order": 1,
        "tags": ["API", "资源", "开发者"],
        "related_articles": ["faq-general", "multi-agent-intro"]
    }
}


# ============================================================
# API端点
# ============================================================

@router.get("/categories", response_model=List[ArticleCategory])
async def get_learning_categories():
    """
    获取所有学习分类

    返回学习中心的所有文章分类信息
    """
    categories_with_count = []
    for cat in LEARNING_CATEGORIES:
        count = sum(1 for art in ARTICLES.values() if art["category"] == cat["id"])
        categories_with_count.append({
            **cat,
            "article_count": count
        })

    return [ArticleCategory(**cat) for cat in categories_with_count]


@router.get("/articles", response_model=List[ArticleInfo])
async def get_articles(
    category: Optional[str] = Query(None, description="按分类筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取文章列表

    参数：
    - category: 可选，按分类筛选
    - limit: 返回数量限制，默认20
    """
    articles = list(ARTICLES.values())

    # 按分类筛选
    if category:
        articles = [art for art in articles if art["category"] == category]

    # 按排序字段排序
    articles.sort(key=lambda x: x["sort_order"])

    # 限制数量
    articles = articles[:limit]

    return [ArticleInfo(**art) for art in articles]


@router.get("/articles/{article_id}", response_model=ArticleInfo)
async def get_article(article_id: str):
    """
    获取文章详情

    参数：
    - article_id: 文章ID
    """
    if article_id not in ARTICLES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章不存在: {article_id}"
        )

    article = ARTICLES[article_id].copy()

    # 增加阅读次数
    article["views"] += 1
    ARTICLES[article_id]["views"] = article["views"]

    return ArticleInfo(**article)


@router.get("/recommended", response_model=List[ArticleInfo])
async def get_recommended_articles(
    limit: int = Query(5, ge=1, le=10, description="返回数量")
):
    """
    获取推荐文章

    返回最受欢迎的文章列表
    """
    articles = list(ARTICLES.values())
    articles.sort(key=lambda x: x["views"], reverse=True)
    articles = articles[:limit]

    return [ArticleInfo(**art) for art in articles]


@router.get("/search", response_model=List[ArticleInfo])
async def search_articles(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    category: Optional[str] = Query(None, description="按分类筛选")
):
    """
    搜索文章

    参数：
    - keyword: 搜索关键词
    - category: 可选，按分类筛选
    """
    keyword_lower = keyword.lower()

    articles = []
    for art in ARTICLES.values():
        # 分类筛选
        if category and art["category"] != category:
            continue

        # 关键词匹配
        if (keyword_lower in art["title"].lower() or
            keyword_lower in art["description"].lower() or
            any(keyword_lower in tag.lower() for tag in art["tags"])):
            articles.append(art)

    return [ArticleInfo(**art) for art in articles]


@router.post("/articles/{article_id}/view")
async def mark_article_viewed(article_id: str):
    """
    标记文章已查看

    用于记录用户阅读历史（未来可扩展）
    """
    if article_id not in ARTICLES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"文章不存在: {article_id}"
        )

    # 增加浏览量
    ARTICLES[article_id]["views"] += 1

    return {
        "success": True,
        "article_id": article_id,
        "views": ARTICLES[article_id]["views"]
    }


@router.get("/stats")
async def get_learning_stats():
    """
    获取学习中心统计信息

    返回文章总数、分类数、总阅读量等
    """
    total_articles = len(ARTICLES)
    total_views = sum(art["views"] for art in ARTICLES.values())
    total_categories = len(LEARNING_CATEGORIES)

    # 按分类统计
    category_stats = {}
    for cat in LEARNING_CATEGORIES:
        count = sum(1 for art in ARTICLES.values() if art["category"] == cat["id"])
        category_stats[cat["display_name"]] = count

    return {
        "total_articles": total_articles,
        "total_views": total_views,
        "total_categories": total_categories,
        "category_stats": category_stats,
        "popular_articles": [
            {"id": art_id, "title": art["title"], "views": art["views"]}
            for art_id, art in sorted(
                ARTICLES.items(),
                key=lambda x: x[1]["views"],
                reverse=True
            )[:5]
        ]
    }
