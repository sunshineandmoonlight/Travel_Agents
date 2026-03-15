#!/bin/bash
# ============================================================
# TravelAgents-CN 旅游专用后端启动脚本 (Linux/Mac)
# ============================================================

echo ""
echo "========================================"
echo "  TravelAgents-CN 旅游后端启动"
echo "========================================"
echo ""

# 设置项目目录
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

# 备份当前.env文件
if [ -f .env ]; then
    cp .env .env.backup.stock
    echo "[*] 已备份当前.env文件"
fi

# 使用旅游专用配置
if [ -f .env.travel-only ]; then
    cp -f .env.travel-only .env
    echo "[*] 已应用旅游专用配置"
else
    echo "[!] 警告: .env.travel-only 不存在"
fi

# 清理Python缓存
echo "[*] 清理Python缓存..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# 检查端口占用
echo "[*] 检查端口8005..."
if command -v lsof >/dev/null 2>&1; then
    PORT_PID=$(lsof -ti:8005)
    if [ ! -z "$PORT_PID" ]; then
        echo "[!] 端口8005已被占用，正在关闭..."
        kill -9 $PORT_PID 2>/dev/null
        sleep 2
    fi
fi

# 启动后端
echo ""
echo "[*] 启动旅游专用后端..."
echo "[*] 访问地址: http://127.0.0.1:8005"
echo "[*] API文档: http://127.0.0.1:8005/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

python -m uvicorn app.travel_main:app --host 127.0.0.1 --port 8005 --reload
