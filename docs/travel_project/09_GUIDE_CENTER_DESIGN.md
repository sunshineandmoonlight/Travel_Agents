# 攻略中心系统设计

## 数据库设计 (PostgreSQL)

### 1. 攻略表 (travel_guides)

存储用户生成的旅行计划/攻略

```sql
CREATE TABLE travel_guides (
    -- 基本信息
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,

    -- 目的地信息
    destination VARCHAR(100) NOT NULL,
    destination_type VARCHAR(20) NOT NULL, -- 'domestic' | 'international'
    city_code VARCHAR(50),                 -- 城市代码
    country_code VARCHAR(10),               -- 国家代码

    -- 行程信息
    days INTEGER NOT NULL,
    budget_level VARCHAR(20),               -- 'low' | 'medium' | 'high'
    total_budget INTEGER,
    travelers_count INTEGER DEFAULT 2,

    -- 风格标签
    travel_style VARCHAR(50),                -- 'immersive' | 'exploration' | 'relaxed'
    interest_tags TEXT[],                   -- ['历史', '美食', '购物', ...]

    -- 详细内容 (JSONB格式)
    itinerary JSONB,                        -- 详细行程数据
    budget_breakdown JSONB,                 -- 预算分解
    attractions JSONB,                      -- 景点列表
    accommodation JSONB,                     -- 住宿信息
    transportation JSONB,                   -- 交通信息

    -- 媒体资源
    cover_image VARCHAR(500),
    images TEXT[],                          -- 图片URL数组

    -- 生成信息
    generation_method VARCHAR(50) DEFAULT 'ai', -- 'ai' | 'manual' | 'hybrid'
    generation_config JSONB,                -- 生成配置

    -- 统计信息
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    copy_count INTEGER DEFAULT 0,           -- 被复制/使用次数

    -- 评分
    rating_avg DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,

    -- 状态
    status VARCHAR(20) DEFAULT 'draft',     -- 'draft' | 'published' | 'archived'
    is_featured BOOLEAN DEFAULT FALSE,      -- 是否精选攻略
    is_editor_pick BOOLEAN DEFAULT FALSE,   -- 是否编辑推荐

    -- SEO
    slug VARCHAR(200) UNIQUE,
    keywords VARCHAR(500),
    meta_description VARCHAR(500),

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    published_at TIMESTAMP,

    -- 作者
    user_id INTEGER,
    username VARCHAR(100),

    -- 季节性信息
    best_seasons VARCHAR(50)[],             -- ['spring', 'autumn']
    weather_info JSONB,

    -- 标签和分类
    tags TEXT[],
    category VARCHAR(50),                   -- 'city_break' | 'nature' | 'cultural' | ...

    -- 地理位置（用于地图展示）
    geo_latitude DECIMAL(10, 8),
    geo_longitude DECIMAL(11, 8),

    -- 索引
    CONSTRAINT travel_guides_slug_check CHECK (slug ~* '^[a-z0-9-]+$')
);

-- 索引
CREATE INDEX idx_guides_destination ON travel_guides(destination);
CREATE INDEX idx_guides_type ON travel_guides(destination_type);
CREATE INDEX idx_guides_style ON travel_guides(travel_style);
CREATE INDEX idx_guides_status ON travel_guides(status);
CREATE INDEX idx_guides_featured ON travel_guides(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_guides_tags ON travel_guides USING GIN(tags);
CREATE INDEX idx_guides_interests ON travel_guides USING GIN(interest_tags);
CREATE INDEX idx_guides_created ON travel_guides(created_at DESC);
CREATE INDEX idx_guides_rating ON travel_guides(rating_avg DESC) WHERE rating_avg > 0;

-- 全文搜索索引
CREATE INDEX idx_guides_fulltext ON travel_guides
    USING GIN(to_tsvector('simple', title || ' ' || description));

-- 地理位置索引 (需要 PostGIS)
-- CREATE INDEX idx_guides_geo ON travel_guides USING GIST(
--     ST_SetSRID(ST_MakePoint(geo_longitude, geo_latitude), 4326)
-- );

-- 触发器：更新 updated_at
CREATE TRIGGER update_guides_timestamp
BEFORE UPDATE ON travel_guides
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. 用户表 (users)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,

    -- 基本信息
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),

    -- 偏好设置
    preferences JSONB DEFAULT '{}',      -- 预算、兴趣、旅行风格等偏好

    -- 统计
    guides_count INTEGER DEFAULT 0,       -- 创建的攻略数
    bookmarks_count INTEGER DEFAULT 0,     -- 收藏的攻略数
    likes_count INTEGER DEFAULT 0,         -- 点赞的攻略数

    -- 权限
    role VARCHAR(20) DEFAULT 'user',       -- 'user' | 'editor' | 'admin'
    is_verified BOOLEAN DEFAULT FALSE,     -- 是否认证用户

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP,

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    bio TEXT
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

### 3. 攻略收藏表 (user_bookmarks)

```sql
CREATE TABLE user_bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,

    -- 收藏信息
    notes TEXT,                           -- 用户备注
    folder_name VARCHAR(100) DEFAULT '默认收藏夹',

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),

    -- 联合唯一索引
    UNIQUE(user_id, guide_id)
);

CREATE INDEX idx_bookmarks_user ON user_bookmarks(user_id);
CREATE INDEX idx_bookmarks_guide ON user_bookmarks(guide_id);
```

### 4. 攻略评论表 (guide_reviews)

```sql
CREATE TABLE guide_reviews (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 评论内容
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    title VARCHAR(200),
    content TEXT NOT NULL,

    -- 图片
    images TEXT[],

    -- 统计
    helpful_count INTEGER DEFAULT 0,
    not_helpful_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- 状态
    is_visible BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_reviews_guide ON guide_reviews(guide_id);
CREATE INDEX idx_reviews_user ON guide_reviews(user_id);
CREATE INDEX idx_reviews_rating ON guide_reviews(rating);
```

### 5. 攻略点赞表 (guide_likes)

```sql
CREATE TABLE guide_likes (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(guide_id, user_id)
);

CREATE INDEX idx_likes_guide ON guide_likes(guide_id);
```

### 6. 攻略分享记录 (guide_shares)

```sql
CREATE TABLE guide_shares (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- 分享信息
    share_type VARCHAR(20) NOT NULL,       -- 'wechat' | 'weibo' | 'link' | 'qrcode'
    share_title VARCHAR(200),

    -- 统计
    click_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shares_guide ON guide_shares(guide_id);
```

### 7. 攻略版本历史 (guide_versions)

```sql
CREATE TABLE guide_versions (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,

    -- 版本信息
    version_number INTEGER NOT NULL,
    change_description TEXT,

    -- 快照数据
    snapshot JSONB NOT NULL,              -- 完整的攻略数据快照

    -- 操作信息
    operated_by VARCHAR(100),
    operated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(guide_id, version_number)
);

CREATE INDEX idx_versions_guide ON guide_versions(guide_id);
```

### 8. 景点数据库 (attractions_database)

```sql
CREATE TABLE attractions_database (
    id SERIAL PRIMARY KEY,

    -- 基本信息
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    name_aliases TEXT[],                  -- 别名

    -- 地理位置
    country VARCHAR(50),
    city VARCHAR(100),
    province VARCHAR(100),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- 分类标签
    category VARCHAR(50),                  -- 'scenic' | 'museum' | 'park' | ...
    tags TEXT[],
    interest_types TEXT[],               -- ['history', 'nature', ...]

    -- 详细信息
    description TEXT,
    highlights TEXT[],                      -- 亮点
    opening_hours JSONB,                   -- 营业时间
    ticket_info JSONB,                     -- 门票信息
    official_website VARCHAR(500),

    -- 媒体
    cover_image VARCHAR(500),
    images TEXT[],

    -- 评分和统计
    rating_avg DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    popularity_score INTEGER DEFAULT 0,     -- 热度分数

    -- 实用信息
    recommended_duration VARCHAR(50),      -- '2-3小时'
    best_time_to_visit VARCHAR(100),
    tips TEXT[],

    -- 价格信息
    price_range VARCHAR(50),               -- 'free' | 'low' | 'medium' | 'high'
    ticket_price_min INTEGER,
    ticket_price_max INTEGER,

    -- 交通信息
    nearby_subway TEXT[],                   -- 附近地铁
    parking_info TEXT,

    -- 联系信息
    phone VARCHAR(50),
    email VARCHAR(100),

    -- 数据来源
    data_source VARCHAR(50),               -- 'amap' | 'serpapi' | 'manual'
    source_id VARCHAR(100),                 -- 原平台的ID
    last_verified_at TIMESTAMP,

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- 全文搜索
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', name || ' ' || COALESCE(description, ''))
    ) STORED
);

-- 索引
CREATE INDEX idx_attractions_city ON attractions_database(city);
CREATE INDEX idx_attractions_category ON attractions_database(category);
CREATE INDEX idx_attractions_tags ON attractions_database USING GIN(tags);
CREATE INDEX idx_attractions_rating ON attractions_database(rating_avg DESC);
CREATE INDEX idx_attractions_search ON attractions_database USING GIN(search_vector);
```

### 9. 攻略模板表 (guide_templates)

```sql
CREATE TABLE guide_templates (
    id SERIAL PRIMARY KEY,

    -- 基本信息
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- 模板类型
    template_type VARCHAR(50),             -- 'city_break' | 'nature' | 'cultural' | ...
    destination_type VARCHAR(20),          -- 'domestic' | 'international'

    -- 推荐天数
    min_days INTEGER,
    max_days INTEGER,

    -- 预算范围
    budget_level VARCHAR(20)[],            -- ['medium', 'high']

    -- 模板内容
    template_structure JSONB NOT NULL,     -- 结构定义
    prompts JSONB,                          -- LLM提示词模板

    -- 样例数据
    example_destination VARCHAR(100),
    example_output JSONB,

    -- 使用统计
    usage_count INTEGER DEFAULT 0,

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,

    -- 时间戳
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 10. 攻略推荐表 (guide_recommendations)

```sql
CREATE TABLE guide_recommendations (
    id SERIAL PRIMARY KEY,

    -- 推荐关系
    source_guide_id INTEGER REFERENCES travel_guides(id),  -- 被推荐的攻略
    target_guide_id INTEGER REFERENCES travel_guides(id),  -- 推荐的攻略

    -- 推荐理由
    reason TEXT,
    similarity_score DECIMAL(3,2),       -- 相似度分数

    -- 推荐类型
    recommendation_type VARCHAR(50),       -- 'similar' | 'popular' | 'editor_pick'

    -- 位置
    position INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(source_guide_id, target_guide_id, recommendation_type)
);
```

---

## 功能设计

### 1. 攻略生成流程

```
用户输入
    ↓
[1] 收集需求 (目的地、天数、预算、兴趣)
    ↓
[2] 调用 Analysts 分析
    ├─ DestinationClassifier → 识别类型
    ├─ DataCollector → 收集景点、天气、交通
    ├─ AttractionAnalyst → 景点推荐 (LLM)
    ├─ ItineraryPlanner → 行程规划 (LLM)
    └─ BudgetAnalyst → 预算分析 (LLM)
    ↓
[3] 生成攻略数据
    ↓
[4] 保存到 travel_guides 表
    ↓
[5] 发布到攻略中心
```

### 2. 攻略中心功能

#### A. 攻略列表
```
浏览方式:
- 最新发布
- 最热门
- 精选推荐
- 按目的地筛选
- 按风格筛选 (沉浸/探索/休闲)
- 按预算筛选
- 按季节筛选
- 全文搜索
```

#### B. 攻略详情
```
展示内容:
- 标题、描述、封面图
- 目的地信息
- 行程天数、预算
- 每日详细行程
- 费用分解
- 景点列表
- 实用信息 (天气、交通、小贴士)
- 作者信息
- 点赞、收藏、分享
- 相关推荐
- 评论
```

#### C. 攻略创建/编辑
```
功能:
- 快速生成 (AI辅助)
- 手动编辑
- 拖拽式行程编辑
- 实时预览
- 保存草稿
- 发布
- 版本历史
```

#### D. 攻略互动
```
用户操作:
- 点赞
- 收藏
- 评论
- 复制/使用攻略 (创建自己的版本)
- 分享
- 打印/导出PDF
```

#### E. 个性化推荐
```
推荐算法:
- 基于用户历史
- 基于相似用户
- 基于内容相似度
- 基于地理位置
- 编辑精选
```

---

## API 设计

### 攻略 CRUD

```python
# POST /api/guides - 创建攻略
# PUT /api/guides/{id} - 更新攻略
# GET /api/guides/{id} - 获取攻略详情
# DELETE /api/guides/{id} - 删除攻略
# POST /api/guides/{id}/publish - 发布攻略
```

### 攻略列表和搜索

```python
# GET /api/guides - 攻略列表
# Query参数: destination, style, budget, sort, page, size

# GET /api/guides/search?q=北京 - 搜索攻略
# GET /api/guides/featured - 精选攻略
# GET /api/guides/popular - 热门攻略
```

### 攻略互动

```python
# POST /api/guides/{id}/like - 点赞
# DELETE /api/guides/{id}/like - 取消点赞
# POST /api/guides/{id}/bookmark - 收藏
# DELETE /api/guides/{id}/bookmark - 取消收藏
# POST /api/guides/{id}/reviews - 评论
```

### 攻略生成

```python
# POST /api/guides/generate - 生成攻略
# Body: {
#   "destination": "北京",
#   "days": 5,
#   "budget": "medium",
#   "travelers": 2,
#   "interest_type": "历史",
#   "style": "exploration"
# }
```

---

## 前端页面设计

### 1. 攻略中心首页

```
┌────────────────────────────────────────────────────────────┐
│  🏛️ 攻略中心                              [搜索框]          │
├────────────────────────────────────────────────────────────┤
│  分类筛选:                                                      │
│  ┌────┬────┬────┬────┬────┬────┬────┐                      │
│  │全部│国内│国际│精选│最新│最热││                      │
│  └────┴────┴────┴────┴────┴────┴────┘                      │
│                                                               │
│  热门目的地:                                                     │
│  ┌──────┬──────┬──────┬──────┬──────┬──────┐                    │
│  │北京 │上海 │西安 │成都 │日本  │泰国  │                    │
│  └──────┴──────┴──────┴──────┴──────┴──────┘                    │
│                                                               │
│  攻略列表:                                                      │
│  ┌─────────────────────┬─────────────────────┬──────────┐    │
│  │ [封面图] 北京5日深度游  │ [封面图] 日本7日游    │ ...      │    │
│  │ 作者: xxx           │ 作者: xxx          │          │    │
│  │ ⭐ 4.8 | 👁 1.2k    │ ⭐ 4.9 | 👁 856    │          │    │
│  │ 💰 5000元 | 📅 5天    │ 💰 8000元 | 📅 7天   │          │    │
│  │ [收藏] [使用]        │ [收藏] [使用]       │          │    │
│  └─────────────────────┴─────────────────────┴──────────┘    │
└────────────────────────────────────────────────────────────┘
```

### 2. 攻略详情页

```
┌────────────────────────────────────────────────────────────┐
│  ← 返回                     北京5日历史文化深度游             │
├────────────────────────────────────────────────────────────┤
│  [封面图 + 标题 + 描述]                                    │
│                                                               │
│  ┌─────┬─────┬─────┬─────┐                                 │
│  │天数 │预算 │风格 │作者 │                                 │
│  │5天  │5000│探索 │xxx │                                 │
│  └─────┴─────┴─────┴─────┘                                 │
│                                                               │
│  [📍 目的地] [📅 行程] [💰 预算] [💡 小贴士]              │
│                                                               │
│  📋 每日行程                                                  │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ Day 1: 故宫历史探索                                   ││
│  │ ┌─────────────────────────────────────────────────┐   ││
│  │ │ 09:00-12:00  天安门广场 + 故宫博物院               │   ││
│  │ │ 12:00-13:30  午餐: 故宫附近老北京炸酱面           │   ││
│  │ │ 14:00-17:00  景山公园登山健身                       │   ││
│  │ │ 18:00-20:00  晚餐: 全聚德烤鸭                       │   ││
│  │ │ 20:00-22:00  夜景: 长安街夜景                     │   ││
│  │ └─────────────────────────────────────────────────┘   ││
│  │ 预计费用: 800元                                      ││
│  └─────────────────────────────────────────────────────────┘│
│  [展开全部 ▼]                                               │
│                                                               │
│  💰 费用分解                                                  │
│  ┌──────┬──────┬──────┬──────┐                             │
│  │交通  │住宿  │餐饮  │景点  │                             │
│  │1000元│3000元│1000元│1000元│                             │
│  └──────┴──────┴──────┴──────┘                             │
│  总计: 6000元                                               │
│                                                               │
│  💡 实用信息                                                  │
│  - 最佳季节: 春季、秋季                                   │
│  - 天气准备: 查看天气预报                                 │
│  - 交通建议: 地铁 + 步行                                 │
│                                                               │
│  👍 点赞 (123) | ⭐ 收藏 (45) | 📤 分享 | 📋 复制攻略      │
│                                                               │
│  💬 评论 (12)                                                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ xxx: 这个攻略很实用，已经按照计划出行了，非常感谢！    ││
│  │     [👍 23] [回复]                                     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  🔗 相关推荐                                                  │
│  ┌──────────┬──────────┬──────────┐                      │
│  │北京7日游  │西安5日游 │上海美食  │                      │
│  └──────────┴──────────┴──────────┘                      │
└────────────────────────────────────────────────────────────┘
```

### 3. 创建攻略页

```
┌────────────────────────────────────────────────────────────┐
│  ← 创建攻略                          [草稿] [预览] [发布]   │
├────────────────────────────────────────────────────────────┤
│                                                               │
│  第一步: 基本信息                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ 攻略标题: [输入框]                                    ││
│  │ 目的地:   [选择城市]                                  ││
│  │ 天数:     [5] 天                                       ││
│  │ 预算:     [经济 ○ 舒适 ○ 豪华]                         ││
│  │ 人数:     [2] 人                                       ││
│  │ 风格:     [深度沉浸 ○ 全面探索 ○ 休闲度假]             ││
│  │ 兴趣标签: [历史] [美食] [购物] [+]                       ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  第二步: AI智能生成                                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                                                     ││
│  │            [🤖 AI 生成攻略]                             ││
│  │                                                     ││
│  │  基于您的需求，AI将为您生成详细的每日行程，包括:        ││
│  │  - 景点推荐和游览顺序                                    ││
│  │  - 行程时间安排                                        ││
│  │  - 费用估算                                            ││
│  │                                                     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  第三步: 编辑调整                                             │
│  ┌─────────────────────────────────────────────────────────┐│
│  │ [📋 编辑行程] [💰 调整预算] [🏨 更换住宿]              ││
│  │                                                     ││
│  │  您可以手动调整AI生成的内容，或完全自己编写。       ││
│  │                                                     ││
│  └─────────────────────────────────────────────────────────┘│
│                                                               │
│  [返回] [上一步] [下一步: 预览]                              │
└────────────────────────────────────────────────────────────┘
```

---

## 推荐算法设计

### 1. 协同过滤推荐

```sql
-- 找到相似用户喜欢的攻略
WITH user_favorites AS (
    SELECT guide_id, COUNT(*) as score
    FROM user_bookmarks
    WHERE user_id = ?
    GROUP BY guide_id
),
similar_users AS (
    SELECT ub.user_id, COUNT(*) as similarity
    FROM user_bookmarks ub
    JOIN user_favorites uf ON ub.guide_id = uf.guide_id
    WHERE ub.user_id != ?
    GROUP BY ub.user_id
    ORDER BY similarity DESC
    LIMIT 100
),
recommended_guides AS (
    SELECT ub.guide_id, COUNT(*) as recommendation_score
    FROM user_bookmarks ub
    JOIN similar_users su ON ub.user_id = su.user_id
    WHERE ub.guide_id NOT IN (SELECT guide_id FROM user_favorites)
    GROUP BY ub.guide_id
    ORDER BY recommendation_score DESC
    LIMIT 10
)
SELECT * FROM recommended_guides
JOIN travel_guides tg ON recommended_guides.guide_id = tg.id
ORDER BY recommendation_score DESC;
```

### 2. 内容相似度推荐

```sql
-- 基于标签和目的地的相似攻略
SELECT
    g.id,
    g.title,
    g.destination,
    COUNT(*) OVER() as position
FROM travel_guides g
WHERE
    g.status = 'published'
    AND g.id != ?
    AND (
        g.destination = (SELECT destination FROM travel_guides WHERE id = ?)
        OR g.travel_style = (SELECT travel_style FROM travel_guides WHERE id = ?)
        OR g.tags && (SELECT tags FROM travel_guides WHERE id = ?)
    )
ORDER BY
    CASE
        WHEN g.destination = (SELECT destination FROM travel_guides WHERE id = ?) THEN 1
        WHEN g.travel_style = (SELECT travel_style FROM travel_guides WHERE id = ?) THEN 2
        ELSE 3
    END
LIMIT 10;
```

### 3. 地理位置推荐

```sql
-- 附近城市的攻略（使用 PostGIS）
SELECT
    g.id,
    g.title,
    g.destination,
    ST_Distance(
        ST_MakePoint(?, ?),  -- 用户指定的位置
        ST_MakePoint(g.geo_longitude, g.geo_latitude)
    ) as distance
FROM travel_guides g
WHERE
    g.status = 'published'
    AND g.destination_type = 'domestic'
ORDER BY distance ASC
LIMIT 10;
```

---

## 数据迁移说明

### 从 MongoDB 迁移到 PostgreSQL

1. **导出 MongoDB 数据**
```python
# scripts/migrate_mongodb_to_postgres.py
```

2. **数据结构转换**
```python
# MongoDB document → PostgreSQL rows
{
    "_id": ObjectId("..."),
    "title": "北京5日游",
    "itinerary": [...],
    ...
}
↓
{
    "id": 1,
    "title": "北京5日游",
    "itinerary": JSONB [...],
    ...
}
```

### 初始化脚本

```python
# scripts/init_postgres.py
import asyncpg
import json

async def init_database():
    conn = await asyncpg.connect("postgres://user:pass@localhost/dbname")

    # 创建表
    with open('scripts/schema.sql') as f:
        await conn.execute(f.read())

    # 导入景点数据
    with open('data/attractions.json') as f:
        attractions = json.load(f)
        for attr in attractions:
            await conn.execute(
                "INSERT INTO attractions_database (...) VALUES (...)"
            )
```

---

## 下一步实现计划

1. **创建 PostgreSQL schema** (1天)
   - 编写 SQL 迁移脚本
   - 创建数据库初始化脚本

2. **创建后端 API** (2-3天)
   - 攻略 CRUD API
   - 攻略搜索和推荐 API
   - 评论、点赞、收藏 API

3. **创建前端页面** (3-4天)
   - 攻略中心首页
   - 攻略详情页
   - 创建攻略页
   - 用户个人中心（我的攻略、收藏）

4. **测试和优化** (1-2天)
   - 单元测试
   - 集成测试
   - 性能优化

---

## 总结

### 攻略中心核心价值

1. **用户生成内容** - 用户生成的攻略可以保存和分享
2. **社区互动** - 点赞、评论、收藏形成社区
3. **推荐系统** - 基于协同过滤和内容相似度推荐
4. **数据资产** - 随着用户增多，攻略库成为宝贵资产

### 技术优势

1. **PostgreSQL** - 强大的关系查询和全文搜索
2. **JSONB** - 灵活存储复杂行程数据
3. **PostGIS** - 地理位置查询
4. **成熟稳定** - 适合生产环境

---

这个设计可以添加到设计手册中，作为攻略中心的设计文档。
