#!/bin/bash
# Celery Worker启动脚本 (Linux/Mac)

echo "======================================"
echo "TravelAgents Celery Worker 启动脚本"
echo "======================================"

# 激活虚拟环境（如果使用）
if [ -d "venv" ]; then
    echo "激活虚拟环境..."
    source venv/bin/activate
fi

# 检查Redis
echo "检查Redis连接..."
REDIS_HOST=${REDIS_HOST:-localhost}
REDIS_PORT=${REDIS_PORT:-6379}

if ! nc -z $REDIS_HOST $REDIS_PORT 2>/dev/null; then
    echo "⚠️  Redis未运行，请先启动Redis:"
    echo "   docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi

echo "✅ Redis连接正常"

# 启动Celery Worker
echo "启动Celery Worker..."
celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --pidfile=celery_worker.pid \
    --logfile=logs/celery_worker.log

echo "Celery Worker已停止"
