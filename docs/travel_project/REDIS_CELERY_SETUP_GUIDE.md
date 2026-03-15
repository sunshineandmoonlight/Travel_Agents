# Redis缓存和Celery异步任务设置指南

## 一、Redis缓存设置

### 1.1 快速开始（Docker）

**Windows/Linux/Mac通用：**
```bash
# 启动Redis（Docker）
docker run -d --name travelagents-redis -p 6379:6379 redis:7-alpine

# 验证运行
docker ps | grep travelagents-redis

# 查看日志
docker logs travelagents-redis
```

### 1.2 本地安装Redis

**Windows:**
```bash
# 使用Chocolatey
choco install redis-64

# 或下载MSI安装包
# https://github.com/microsoftarchive/redis/releases
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# 启动服务
sudo systemctl start redis
sudo systemctl enable redis
```

**Mac:**
```bash
# 使用Homebrew
brew install redis
brew services start redis
```

### 1.3 配置环境变量

在 `.env` 文件中添加：
```bash
# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=              # 可选，如果设置了密码
REDIS_CACHE_DB=1             # 缓存使用DB1
REDIS_CELERY_DB=2            # Celery使用DB2
```

### 1.4 验证Redis缓存

启动应用后访问：
```bash
# 检查缓存系统状态
curl http://localhost:8005/api/debug/system/status

# 响应应包含:
{
  "cache": {
    "cache_backend": "redis",  # 确认是redis
    "hit_rate": 0.653
  }
}
```

---

## 二、Celery异步任务队列设置

### 2.1 安装依赖

```bash
# 安装Celery和Redis客户端
pip install -r requirements-celery.txt
```

### 2.2 启动Celery Worker

**Windows:**
```bash
# 使用批处理脚本
scripts\start_celery_worker.bat

# 或直接启动
celery -A app.celery_app worker --loglevel=info --concurrency=2
```

**Linux/Mac:**
```bash
# 使用shell脚本
chmod +x scripts/start_celery_worker.sh
./scripts/start_celery_worker.sh

# 或直接启动
celery -A app.celery_app worker --loglevel=info --concurrency=4
```

### 2.3 验证Celery状态

```bash
# 检查Celery连接状态
curl http://localhost:8005/api/travel/async/status

# 检查Worker状态
curl http://localhost:8005/api/travel/async/workers
```

---

## 三、完整启动流程

### 开发环境启动

```bash
# 终端1: 启动Redis
docker run -d -p 6379:6379 redis:7-alpine

# 终端2: 启动Celery Worker
celery -A app.celery_app worker --loglevel=info

# 终端3: 启动FastAPI后端
cd app && python -m uvicorn travel_main:app --reload --port 8005
```

### 生产环境启动

**使用Supervisor管理进程：**

```ini
# /etc/supervisor/conf.d/travelagents.conf

[program:travelagents-api]
command=/path/to/venv/bin/uvicorn app.travel_main:app --host 0.0.0.0 --port 8005
directory=/path/to/TradingAgents-CN
user=www-data
autostart=true
autorestart=true

[program:travelagents-celery]
command=/path/to/venv/bin/celery -A app.celery_app worker --loglevel=info
directory=/path/to/TradingAgents-CN
user=www-data
autostart=true
autorestart=true
```

---

## 四、API使用示例

### 4.1 异步生成攻略

**提交任务：**
```bash
curl -X POST http://localhost:8005/api/travel/async/generate-guide \
  -H "Content-Type: application/json" \
  -d '{
    "destination_type": "domestic",
    "days": 3,
    "budget": "medium",
    "travelers": 2,
    "travel_type": "leisure",
    "primary_interests": ["历史", "文化"]
  }'
```

**响应：**
```json
{
  "status": "submitted",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "message": "攻略生成任务已提交",
  "check_url": "/api/travel/async/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**查询进度：**
```bash
curl http://localhost:8005/api/travel/async/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**进度响应：**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "state": "PROGRESS",
  "stage": "detailed_planning",
  "message": "正在规划详细行程...",
  "progress": 60,
  "phase": 4
}
```

**完成响应：**
```json
{
  "task_id": "...",
  "state": "SUCCESS",
  "result": {
    "status": "success",
    "guide": { /* 完整攻略 */ }
  },
  "message": "任务完成"
}
```

### 4.2 前端集成示例

```typescript
// frontend/src/api/asyncTravel.ts

interface AsyncResponse {
  status: string;
  task_id: string;
  check_url: string;
}

interface TaskStatus {
  task_id: string;
  state: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  stage?: string;
  message?: string;
  progress?: number;
  result?: any;
  error?: string;
}

// 提交异步任务
export async function submitGenerateGuide(requirement: TravelRequirement): Promise<AsyncResponse> {
  const response = await fetch('/api/travel/async/generate-guide', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requirement)
  });
  return response.json();
}

// 轮询任务状态
export async function pollTaskStatus(
  taskId: string,
  onProgress: (status: TaskStatus) => void,
  onComplete: (result: any) => void,
  onError: (error: string) => void
) {
  const poll = async () => {
    const response = await fetch(`/api/travel/async/tasks/${taskId}`);
    const status: TaskStatus = await response.json();

    if (status.state === 'PROGRESS') {
      onProgress(status);
      setTimeout(poll, 1000); // 继续轮询
    } else if (status.state === 'SUCCESS') {
      onComplete(status.result);
    } else if (status.state === 'FAILURE') {
      onError(status.error || '任务失败');
    } else {
      setTimeout(poll, 1000); // PENDING状态继续轮询
    }
  };

  poll();
}
```

---

## 五、监控和管理

### 5.1 Flower监控（可选）

```bash
# 安装Flower
pip install flower

# 启动Flower
celery -A app.celery_app flower --port=5555

# 访问
open http://localhost:5555
```

### 5.2 常用命令

```bash
# 查看活动任务
curl http://localhost:8005/api/travel/async/tasks/active

# 查看Worker状态
curl http://localhost:8005/api/travel/async/workers

# 取消任务
curl -X DELETE http://localhost:8005/api/travel/async/tasks/{task_id}

# 清空缓存
curl http://localhost:8005/api/debug/cache/clear
```

---

## 六、故障排查

### Redis连接失败
```bash
# 检查Redis是否运行
docker ps | grep redis
# 或
redis-cli ping

# 检查端口
netstat -an | grep 6379
```

### Celery Worker无法启动
```bash
# 检查Redis连接
redis-cli -h localhost -p 6379 ping

# 检查Python依赖
pip list | grep celery
pip list | grep redis

# 查看详细日志
celery -A app.celery_app worker --loglevel=debug
```

### 任务卡在PENDING状态
```bash
# 确认Worker正在运行
curl http://localhost:8005/api/travel/async/workers

# 检查Celery日志
tail -f logs/celery_worker.log
```

---

## 七、性能调优

### Redis优化
```bash
# redis.conf 优化配置
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Celery优化
```python
# 根据CPU核心数调整并发
# 生产环境推荐: CPU核心数 * 2
celery -A app.celery_app worker --concurrency=8 --prefetch-multiplier=4
```

---

## 八、文件清单

**新增文件：**
- `tradingagents/utils/redis_cache.py` - Redis缓存管理器
- `tradingagents/utils/cache_init.py` - 缓存系统初始化
- `tradingagents/utils/unified_cache.py` - 统一缓存抽象
- `app/celery_app.py` - Celery应用配置
- `app/tasks/travel_tasks.py` - 旅行异步任务
- `app/tasks/guide_tasks.py` - 攻略异步任务
- `app/routers/async_tasks.py` - 异步API路由
- `scripts/start_celery_worker.sh` - Celery启动脚本
- `scripts/start_celery_worker.bat` - Celery启动脚本
- `requirements-celery.txt` - 依赖文件

**修改文件：**
- `app/travel_main.py` - 添加缓存初始化和异步路由
- `app/routers/debug.py` - 支持Redis缓存统计
