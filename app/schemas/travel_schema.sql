-- ============================================================
-- TravelAgents-CN - 旅行规划系统 PostgreSQL Schema
-- 攻略中心数据库表设计
-- ============================================================

-- 设置搜索路径
SET search_path = public;

-- ============================================================
-- 1. 用户表
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    -- 基本信息
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,

    -- 基本信息
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100),
    avatar_url VARCHAR(500),

    -- 偏好设置 (JSONB格式)
    preferences JSONB DEFAULT '{}'::jsonb,

    -- 统计
    guides_count INTEGER DEFAULT 0,
    bookmarks_count INTEGER DEFAULT 0,
    likes_count INTEGER DEFAULT 0,

    -- 权限
    role VARCHAR(20) DEFAULT 'user',
    is_verified BOOLEAN DEFAULT FALSE,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,
    bio TEXT,

    -- 约束
    CONSTRAINT users_username_check CHECK (username ~* '^[a-zA-Z0-9_]{3,50}$'),
    CONSTRAINT users_email_check CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 用户表索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role) WHERE role != 'user';


-- ============================================================
-- 2. 旅行攻略表 (核心表)
-- ============================================================

CREATE TABLE IF NOT EXISTS travel_guides (
    -- 基本信息
    id SERIAL PRIMARY KEY,
    uuid UUID DEFAULT gen_random_uuid() UNIQUE,
    title VARCHAR(200) NOT NULL,
    description TEXT,

    -- 目的地信息
    destination VARCHAR(100) NOT NULL,
    destination_type VARCHAR(20) NOT NULL, -- 'domestic' | 'international'
    city_code VARCHAR(50),
    country_code VARCHAR(10),

    -- 行程信息
    days INTEGER NOT NULL,
    budget_level VARCHAR(20), -- 'low' | 'medium' | 'high'
    total_budget INTEGER,
    travelers_count INTEGER DEFAULT 2,

    -- 风格标签
    travel_style VARCHAR(50), -- 'immersive' | 'exploration' | 'relaxed'
    interest_tags TEXT[], -- ['历史', '美食', '购物', '自然']

    -- 详细内容 (JSONB格式)
    itinerary JSONB DEFAULT '{}'::jsonb,
    budget_breakdown JSONB DEFAULT '{}'::jsonb,
    attractions JSONB DEFAULT '[]'::jsonb,
    accommodation JSONB,
    transportation JSONB,

    -- 媒体资源
    cover_image VARCHAR(500),
    images TEXT[],

    -- 生成信息
    generation_method VARCHAR(50) DEFAULT 'ai', -- 'ai' | 'manual' | 'hybrid'
    generation_config JSONB,

    -- 统计信息
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    copy_count INTEGER DEFAULT 0,

    -- 评分
    rating_avg DECIMAL(3,2) DEFAULT 0,
    rating_count INTEGER DEFAULT 0,

    -- 状态
    status VARCHAR(20) DEFAULT 'draft', -- 'draft' | 'published' | 'archived'
    is_featured BOOLEAN DEFAULT FALSE,
    is_editor_pick BOOLEAN DEFAULT FALSE,

    -- SEO
    slug VARCHAR(200) UNIQUE,
    keywords VARCHAR(500),
    meta_description VARCHAR(500),

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,

    -- 作者
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    username VARCHAR(100),

    -- 季节性信息
    best_seasons VARCHAR(50)[], -- ['spring', 'summer', 'autumn', 'winter']
    weather_info JSONB,

    -- 标签和分类
    tags TEXT[],
    category VARCHAR(50),

    -- 地理位置
    geo_latitude DECIMAL(10, 8),
    geo_longitude DECIMAL(11, 8),

    -- 约束
    CONSTRAINT travel_guides_slug_check CHECK (slug ~* '^[a-z0-9-]+$'),
    CONSTRAINT travel_guides_status_check CHECK (status IN ('draft', 'published', 'archived'))
);

-- 攻略表索引
CREATE INDEX idx_guides_destination ON travel_guides(destination);
CREATE INDEX idx_guides_type ON travel_guides(destination_type);
CREATE INDEX idx_guides_style ON travel_guides(travel_style);
CREATE INDEX idx_guides_status ON travel_guides(status);
CREATE INDEX idx_guides_featured ON travel_guides(is_featured) WHERE is_featured = TRUE;
CREATE INDEX idx_guides_editor_pick ON travel_guides(is_editor_pick) WHERE is_editor_pick = TRUE;
CREATE INDEX idx_guides_user ON travel_guides(user_id);
CREATE INDEX idx_guides_tags ON travel_guides USING GIN(tags);
CREATE INDEX idx_guides_interests ON travel_guides USING GIN(interest_tags);
CREATE INDEX idx_guides_created ON travel_guides(created_at DESC);
CREATE INDEX idx_guides_rating ON travel_guides(rating_avg DESC) WHERE rating_avg > 0;

-- 全文搜索索引
CREATE INDEX idx_guides_fulltext ON travel_guides
    USING GIN(to_tsvector('simple', title || ' ' || COALESCE(description, '')));


-- ============================================================
-- 3. 攻略收藏表
-- ============================================================

CREATE TABLE IF NOT EXISTS user_bookmarks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,

    -- 收藏信息
    notes TEXT,
    folder_name VARCHAR(100) DEFAULT '默认收藏夹',

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 联合唯一索引
    CONSTRAINT user_bookmarks_unique UNIQUE(user_id, guide_id)
);

CREATE INDEX idx_bookmarks_user ON user_bookmarks(user_id);
CREATE INDEX idx_bookmarks_guide ON user_bookmarks(guide_id);


-- ============================================================
-- 4. 攻略评论表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_reviews (
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 状态
    is_visible BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_reviews_guide ON guide_reviews(guide_id);
CREATE INDEX idx_reviews_user ON guide_reviews(user_id);
CREATE INDEX idx_reviews_rating ON guide_reviews(rating);
CREATE INDEX idx_reviews_created ON guide_reviews(created_at DESC);


-- ============================================================
-- 5. 攻略点赞表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_likes (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT guide_likes_unique UNIQUE(guide_id, user_id)
);

CREATE INDEX idx_likes_guide ON guide_likes(guide_id);
CREATE INDEX idx_likes_user ON guide_likes(user_id);


-- ============================================================
-- 6. 攻略分享表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_shares (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,

    -- 分享信息
    share_type VARCHAR(20) NOT NULL, -- 'wechat' | 'weibo' | 'link' | 'qrcode'
    share_title VARCHAR(200),

    -- 统计
    click_count INTEGER DEFAULT 0,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_shares_guide ON guide_shares(guide_id);


-- ============================================================
-- 7. 攻略版本历史表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_versions (
    id SERIAL PRIMARY KEY,
    guide_id INTEGER NOT NULL REFERENCES travel_guides(id) ON DELETE CASCADE,

    -- 版本信息
    version_number INTEGER NOT NULL,
    change_description TEXT,

    -- 快照数据
    snapshot JSONB NOT NULL,

    -- 操作信息
    operated_by VARCHAR(100),
    operated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT guide_versions_unique UNIQUE(guide_id, version_number)
);

CREATE INDEX idx_versions_guide ON guide_versions(guide_id);


-- ============================================================
-- 8. 景点数据库表
-- ============================================================

CREATE TABLE IF NOT EXISTS attractions_database (
    id SERIAL PRIMARY KEY,

    -- 基本信息
    name VARCHAR(200) NOT NULL,
    name_en VARCHAR(200),
    name_aliases TEXT[],

    -- 地理位置
    country VARCHAR(50),
    city VARCHAR(100),
    province VARCHAR(100),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),

    -- 分类标签
    category VARCHAR(50),
    tags TEXT[],
    interest_types TEXT[],

    -- 详细信息
    description TEXT,
    highlights TEXT[],
    opening_hours JSONB,
    ticket_info JSONB,
    official_website VARCHAR(500),

    -- 媒体
    cover_image VARCHAR(500),
    images TEXT[],

    -- 评分
    rating_avg DECIMAL(3,2),
    review_count INTEGER DEFAULT 0,
    popularity_score INTEGER DEFAULT 0,

    -- 实用信息
    recommended_duration VARCHAR(50),
    best_time_to_visit VARCHAR(100),
    tips TEXT[],

    -- 价格信息
    price_range VARCHAR(50), -- 'free' | 'low' | 'medium' | 'high'
    ticket_price_min INTEGER,
    ticket_price_max INTEGER,

    -- 交通信息
    nearby_subway TEXT[],
    parking_info TEXT,

    -- 联系信息
    phone VARCHAR(50),
    email VARCHAR(100),

    -- 数据来源
    data_source VARCHAR(50),
    source_id VARCHAR(100),
    last_verified_at TIMESTAMP WITH TIME ZONE,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- 全文搜索向量
    search_vector tsvector GENERATED ALWAYS AS (
        to_tsvector('simple', name || ' ' || COALESCE(description, ''))
    ) STORED
);

-- 景点表索引
CREATE INDEX idx_attractions_city ON attractions_database(city);
CREATE INDEX idx_attractions_category ON attractions_database(category);
CREATE INDEX idx_attractions_tags ON attractions_database USING GIN(tags);
CREATE INDEX idx_attractions_rating ON attractions_database(rating_avg DESC);
CREATE INDEX idx_attractions_search ON attractions_database USING GIN(search_vector);


-- ============================================================
-- 9. 攻略模板表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_templates (
    id SERIAL PRIMARY KEY,

    -- 基本信息
    name VARCHAR(200) NOT NULL,
    description TEXT,

    -- 模板类型
    template_type VARCHAR(50),
    destination_type VARCHAR(20),

    -- 推荐天数
    min_days INTEGER,
    max_days INTEGER,

    -- 预算范围
    budget_level VARCHAR(20)[],

    -- 模板内容
    template_structure JSONB NOT NULL,
    prompts JSONB,

    -- 样例数据
    example_destination VARCHAR(100),
    example_output JSONB,

    -- 使用统计
    usage_count INTEGER DEFAULT 0,

    -- 状态
    is_active BOOLEAN DEFAULT TRUE,

    -- 时间戳
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- ============================================================
-- 10. 攻略推荐关系表
-- ============================================================

CREATE TABLE IF NOT EXISTS guide_recommendations (
    id SERIAL PRIMARY KEY,

    -- 推荐关系
    source_guide_id INTEGER REFERENCES travel_guides(id),
    target_guide_id INTEGER REFERENCES travel_guides(id),

    -- 推荐理由
    reason TEXT,
    similarity_score DECIMAL(3,2),

    -- 推荐类型
    recommendation_type VARCHAR(50),
    position INTEGER,

    created_at TIMESTAMP WITH TIME_zone DEFAULT NOW(),

    CONSTRAINT guide_recommendations_unique UNIQUE(source_guide_id, target_guide_id, recommendation_type)
);

CREATE INDEX idx_recommendations_source ON guide_recommendations(source_guide_id);
CREATE INDEX idx_recommendations_target ON guide_recommendations(target_guide_id);


-- ============================================================
-- 触发器和函数
-- ============================================================

-- 更新 updated_at 的触发器函数
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 应用触发器
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_guides_updated_at BEFORE UPDATE ON travel_guides
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reviews_updated_at BEFORE UPDATE ON guide_reviews
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_templates_updated_at BEFORE UPDATE ON guide_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- 视图（简化查询）
-- ============================================================

-- 攻略列表视图
CREATE OR REPLACE VIEW v_published_guides AS
SELECT
    g.id,
    g.uuid,
    g.title,
    g.destination,
    g.destination_type,
    g.days,
    g.total_budget,
    g.travel_style,
    g.cover_image,
    g.view_count,
    g.like_count,
    g.bookmark_count,
    g.rating_avg,
    g.rating_count,
    g.is_featured,
    g.is_editor_pick,
    g.created_at,
    g.published_at,
    g.username,
    u.nickname as author_nickname,
    u.avatar_url as author_avatar
FROM travel_guides g
LEFT JOIN users u ON g.user_id = u.id
WHERE g.status = 'published';

-- 用户收藏的攻略视图
CREATE OR REPLACE VIEW v_user_bookmarks AS
SELECT
    ub.id,
    ub.user_id,
    ub.guide_id,
    ub.notes,
    ub.folder_name,
    ub.created_at as bookmarked_at,
    g.title,
    g.destination,
    g.days,
    g.total_budget,
    g.travel_style,
    g.cover_image,
    g.created_at as guide_created_at
FROM user_bookmarks ub
JOIN travel_guides g ON ub.guide_id = g.id
ORDER BY ub.created_at DESC;


-- ============================================================
-- 初始化数据
-- ============================================================

-- 插入默认用户 (测试用)
INSERT INTO users (username, email, password_hash, nickname, role)
VALUES
    ('admin', 'admin@travel.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCW7UhCkq7YQ4FpQH8Ie1v8', '系统管理员', 'admin')
ON CONFLICT (username) DO NOTHING;

-- 插入示例攻略模板
INSERT INTO guide_templates (name, description, template_type, destination_type, min_days, max_days, budget_level, template_structure, prompts, example_destination, is_active)
VALUES
(
    '历史文化5日游模板',
    '适合历史文化爱好者的5日深度游行程模板',
    'cultural',
    'domestic',
    3,
    7,
    ARRAY['low', 'medium'],
    '{
        "daily_structure": {
            "morning": {"time_range": "09:00-12:00", "activity_type": "attraction"},
            "lunch": {"time_range": "12:00-13:30", "activity_type": "meal"},
            "afternoon": {"time_range": "14:00-17:00", "activity_type": "attraction"},
            "dinner": {"time_range": "18:00-20:00", "activity_type": "meal"},
            "evening": {"time_range": "20:00-22:00", "activity_type": "free_time"}
        },
        "budget_allocation": {
            "attraction": 0.25,
            "meal": 0.25,
            "accommodation": 0.30,
            "transportation": 0.20
        }
    }'::jsonb,
    '{
        "system": "你是一位专业的旅行规划师，请根据用户需求生成详细的每日行程。",
        "user_input_format": "目的地={destination}, 天数={days}, 预算={budget}, 兴趣={interests}",
        "output_format": "JSON格式的每日行程"
    }'::jsonb,
    '北京',
    '{
        "daily_itinerary": [
            {
                "day": 1,
                "theme": "历史文化探索",
                "morning": {"attraction": "故宫博物院", "activity": "参观紫禁城，了解明清历史"},
                "lunch": {"restaurant": "故宫附近老北京炸酱面", "cost": 50},
                "afternoon": {"attraction": "景山公园", "activity": "登山健身，俯瞰故宫全景"}
            }
        ]
    }'::jsonb,
    TRUE
) ON CONFLICT DO NOTHING;


-- ============================================================
-- 完成提示
-- ============================================================

COMMENT ON TABLE travel_guides IS '旅行攻略主表，存储用户生成的完整旅行攻略';
COMMENT ON TABLE user_bookmarks IS '用户收藏的攻略';
COMMENT ON TABLE guide_reviews IS '攻略评论';
COMMENT ON TABLE guide_likes IS '攻略点赞';
COMMENT ON TABLE guide_shares IS '攻略分享统计';
COMMENT ON TABLE guide_versions IS '攻略版本历史';
COMMENT ON TABLE attractions_database IS '景点数据库，支持全文搜索';
COMMENT ON TABLE guide_templates IS '攻略模板，用于AI生成';

COMMENT ON COLUMN travel_guides.itinerary IS '详细行程数据，JSONB格式，包含每日活动、餐饮、住宿等信息';
COMMENT ON COLUMN travel_guides.budget_breakdown IS '预算分解，JSONB格式，包含交通、住宿、餐饮、景点等费用';
COMMENT ON COLUMN travel_guides.interest_tags IS '兴趣标签数组，如 ["历史", "美食", "购物"]';
COMMENT ON COLUMN travel_guides.travel_style IS '旅行风格：immersive(深度沉浸), exploration(全面探索), relaxed(休闲度假)';
COMMENT ON COLUMN users.preferences IS '用户偏好设置，JSONB格式，包含预算、兴趣、旅行风格等';
COMMENT ON COLUMN travel_guides.search_vector IS '全文搜索向量，用于攻略搜索功能';
