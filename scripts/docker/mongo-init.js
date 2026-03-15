// MongoDB 初始化脚本
// 为 TravelAgents 旅行规划系统创建数据库和用户

// 切换到旅行规划数据库
db = db.getSiblingDB('travel_agents');

// 创建集合
db.createCollection('users');
db.createCollection('travel_plans');
db.createCollection('destinations');
db.createCollection('guides');
db.createCollection('agent_cache');

// 创建索引
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });
db.travel_plans.createIndex({ "user_id": 1 });
db.travel_plans.createIndex({ "created_at": -1 });
db.destinations.createIndex({ "city_name": 1 });
db.destinations.createIndex({ "province": 1 });
db.guides.createIndex({ "plan_id": 1 });
db.guides.createIndex({ "created_at": -1 });

// 插入示例数据（可选）
db.destinations.insertMany([
    {
        "city_name": "北京",
        "province": "北京",
        "country": "中国",
        "features": ["历史文化", "美食", "博物馆"],
        "score": 95,
        "created_at": new Date()
    },
    {
        "city_name": "上海",
        "province": "上海",
        "country": "中国",
        "features": ["现代都市", "购物", "美食"],
        "score": 92,
        "created_at": new Date()
    },
    {
        "city_name": "成都",
        "province": "四川",
        "country": "中国",
        "features": ["美食", "熊猫", "悠闲"],
        "score": 90,
        "created_at": new Date()
    }
]);

print('MongoDB 初始化完成！');
print('数据库: travel_agents');
print('集合: users, travel_plans, destinations, guides, agent_cache');
