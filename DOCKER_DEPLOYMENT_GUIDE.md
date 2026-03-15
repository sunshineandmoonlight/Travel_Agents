# TravelAgents Docker 部署指南

## 📋 前置要求

### 服务器要求
- **操作系统**: Linux (Ubuntu 20.04+ 推荐)
- **CPU**: 2 核心以上
- **内存**: 4GB 以上
- **磁盘**: 20GB 以上
- **网络**: 公网 IP 或内网可访问

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+

---

## 🚀 快速部署

### 步骤 1：安装 Docker 和 Docker Compose

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com | bash
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 步骤 2：克隆项目

```bash
git clone https://github.com/sunshineandmoonlight/Travel_Agents.git
cd Travel_Agents
```

### 步骤 3：配置环境变量

编辑 `.env.docker` 文件，配置必要的 API 密钥：

```bash
# 编辑配置文件
nano .env.docker
```

**必须配置的项**：
```env
# LLM API（至少配置一个）
DEEPSEEK_API_KEY=your-actual-api-key-here

# JWT 密钥（生产环境必须修改）
JWT_SECRET=your-random-secret-key-here
```

**可选配置**：
```env
# 外部 API（不配置也能运行，但功能受限）
TIANAPI_TOKEN=your-tianapi-token
UNSPLASH_ACCESS_KEY=your-unsplash-key
```

### 步骤 4：启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 查看服务状态
docker-compose ps
```

### 步骤 5：验证部署

访问以下地址验证服务：

| 服务 | 地址 | 说明 |
|------|------|------|
| **前端** | http://your-server-ip:4000 | Vue 3 前端界面 |
| **后端 API** | http://your-server-ip:8005 | FastAPI 后端 |
| **API 文档** | http://your-server-ip:8005/docs | Swagger 文档 |
| **Redis 管理** | http://your-server-ip:8081 | Redis Commander（可选）|
| **MongoDB 管理** | http://your-server-ip:8082 | Mongo Express（可选）|

---

## 🔧 常用命令

### 服务管理

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose stop

# 重启所有服务
docker-compose restart

# 停止并删除容器
docker-compose down

# 停止并删除容器和数据卷
docker-compose down -v
```

### 日志查看

```bash
# 查看所有日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs frontend

# 实时查看日志
docker-compose logs -f backend

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入 MongoDB 容器
docker-compose exec mongodb bash

# 进入 Redis 容器
docker-compose exec redis sh
```

---

## 🌐 生产环境配置

### 域名配置

1. **配置 DNS**
   - 将域名 `your-domain.com` 解析到服务器 IP

2. **配置 Nginx 反向代理**（推荐）

```bash
# 安装 Nginx
sudo apt install nginx

# 创建配置文件
sudo nano /etc/nginx/sites-available/travel-agents
```

配置内容：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端
    location / {
        proxy_pass http://localhost:4000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://localhost:8005/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/travel-agents /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

3. **配置 HTTPS**（使用 Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

### 安全配置

1. **修改默认密码**
   - MongoDB 密码: `docker-compose.yml` 中的 `MONGO_INITDB_ROOT_PASSWORD`
   - Redis 密码: `docker-compose.yml` 中的 `redis` 密码
   - JWT 密钥: `.env.docker` 中的 `JWT_SECRET`

2. **防火墙配置**
```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

3. **关闭管理界面端口**（生产环境）
```bash
# 在 docker-compose.yml 中注释掉以下服务：
# - redis-commander
# - mongo-express
```

---

## 📊 监控和维护

### 性能监控

```bash
# 查看容器资源使用
docker stats

# 查看磁盘使用
docker system df

# 清理未使用的镜像和容器
docker system prune -a
```

### 数据备份

```bash
# 备份 MongoDB
docker-compose exec mongodb mongodump --username=admin --password=travel123 --authenticationDatabase=admin --archive=/data/db/backup-$(date +%Y%m%d).tar

# 备份 Redis
docker-compose exec redis redis-cli --rdb /data/dump-$(date +%Y%m%d).rdb

# 恢复 MongoDB
docker-compose exec mongodb mongorestore --username=admin --password=travel123 --authenticationDatabase=admin --archive=/data/db/backup-20250316.tar
```

### 日志管理

```bash
# 查看日志文件大小
du -sh ./logs/

# 清理旧日志
find ./logs/ -name "*.log" -mtime +7 -delete
```

---

## 🐛 故障排查

### 常见问题

#### 1. 容器无法启动

```bash
# 查看详细日志
docker-compose logs backend

# 检查配置
docker-compose config

# 重新构建
docker-compose build --no-cache
docker-compose up -d
```

#### 2. 数据库连接失败

```bash
# 检查 MongoDB 状态
docker-compose ps mongodb
docker-compose logs mongodb

# 测试连接
docker-compose exec mongodb mongo -u admin -p travel123 --authenticationDatabase admin
```

#### 3. LLM API 调用失败

```bash
# 检查 API 密钥配置
docker-compose exec backend env | grep API

# 测试 API 连接
docker-compose exec backend python -c "import requests; print(requests.get('https://api.deepseek.com/v1/models', headers={'Authorization': 'Bearer YOUR_KEY'}))"
```

#### 4. 前端无法访问后端

```bash
# 检查 CORS 配置
docker-compose logs backend | grep CORS

# 检查网络连接
docker-compose exec frontend ping backend
```

---

## 📈 性能优化

### 1. 增加 Worker 进程

编辑 `docker-compose.yml`:
```yaml
backend:
  command: ["python", "-m", "uvicorn", "app.travel_main:app", "--host", "0.0.0.0", "--port", "8005", "--workers", "4"]
```

### 2. 启用 Redis 缓存

确保 `.env.docker` 中配置：
```env
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=travel123
```

### 3. 调整内存限制

编辑 `docker-compose.yml`:
```yaml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
      reservations:
        memory: 1G
```

---

## 🔄 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose build
docker-compose up -d

# 查看更新状态
docker-compose ps
```

---

## 📞 支持

如有问题，请访问：
- **GitHub Issues**: https://github.com/sunshineandmoonlight/Travel_Agents/issues
- **项目文档**: https://github.com/sunshineandmoonlight/Travel_Agents/blob/main/README.md
