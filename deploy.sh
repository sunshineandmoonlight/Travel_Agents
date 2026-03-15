#!/bin/bash

# TravelAgents v3.0 Docker 部署脚本
# 智能旅行规划系统

set -e

echo "======================================"
echo "TravelAgents v3.0 Docker 部署脚本"
echo "======================================"
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    echo "安装命令: curl -fsSL https://get.docker.com | bash"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"
echo ""

# 检查 .env.docker 文件
if [ ! -f .env.docker ]; then
    echo "❌ 找不到 .env.docker 文件"
    echo "请先复制并编辑配置文件："
    echo "  cp .env.docker.example .env.docker"
    echo "  nano .env.docker"
    exit 1
fi

echo "📝 检查配置文件..."
# 检查是否配置了 LLM API
if grep -q "your-deepseek-api-key-here" .env.docker; then
    echo "⚠️  警告: 请在 .env.docker 中配置你的 LLM API 密钥"
    echo "   编辑命令: nano .env.docker"
    read -p "是否继续？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "🚀 开始部署..."
echo ""

# 创建必要的目录
mkdir -p logs data config

# 停止旧容器（如果存在）
echo "🛑 停止旧容器..."
docker-compose down 2>/dev/null || true

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "▶️  启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "======================================"
echo "✅ 部署完成！"
echo "======================================"
echo ""
echo "访问地址:"
echo "  前端: http://localhost:4000"
echo "  后端: http://localhost:8005"
echo "  API文档: http://localhost:8005/docs"
echo ""
echo "查看日志:"
echo "  docker-compose logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose stop"
echo ""
echo "重启服务:"
echo "  docker-compose restart"
echo ""
