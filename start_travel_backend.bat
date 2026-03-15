@echo off
REM ============================================================
REM TravelAgents-CN 旅游专用后端启动脚本
REM ============================================================

echo.
echo ========================================
echo   TravelAgents-CN 旅游后端启动
echo ========================================
echo.

REM 设置项目目录
set PROJECT_DIR=D:\projet\agent_project\Web_Agent_System\TradingAgents-CN
cd /d "%PROJECT_DIR%"

REM 备份当前.env文件
if exist .env (
    copy .env .env.backup.stock >nul 2>&1
    echo [*] 已备份当前.env文件
)

REM 使用旅游专用配置
if exist .env.travel-only (
    copy /Y .env.travel-only .env >nul
    echo [*] 已应用旅游专用配置
) else (
    echo [!] 警告: .env.travel-only 不存在
)

REM 清理Python缓存
echo [*] 清理Python缓存...
if exist app\__pycache__ rmdir /s /q app\__pycache__
if exist tradingagents\__pycache__ rmdir /s /q tradingagents\__pycache__
if exist tradingagents\services\__pycache__ rmdir /s /q tradingagents\services\__pycache__

REM 检查端口占用
echo [*] 检查端口8005...
netstat -an | findstr ":8005" | findstr "LISTENING" >nul
if %errorlevel% == 0 (
    echo [!] 端口8005已被占用，正在关闭...
    npx kill-port 8005
    timeout /t 2 /nobreak >nul
)

REM 启动后端
echo.
echo [*] 启动旅游专用后端...
echo [*] 访问地址: http://127.0.0.1:8005
echo [*] API文档: http://127.0.0.1:8005/docs
echo.
echo 按 Ctrl+C 停止服务器
echo.

python -m uvicorn app.travel_main:app --host 127.0.0.1 --port 8005 --reload

pause
