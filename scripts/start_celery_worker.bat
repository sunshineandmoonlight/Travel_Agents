@echo off
REM Celery Worker启动脚本 (Windows)

echo ======================================
echo TravelAgents Celery Worker 启动脚本
echo ======================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] Python未安装或未在PATH中
    exit /b 1
)

REM 检查Redis
echo [检查] Redis连接...
set REDIS_HOST=%REDIS_HOST%=localhost
set REDIS_PORT=%REDIS_PORT%=6379

powershell -Command "Test-NetConnection -ComputerName %REDIS_HOST% -Port %REDIS_PORT" >nul 2>&1
if errorlevel 1 (
    echo [警告] Redis未运行，请先启动Redis:
    echo    docker run -d -p 6379:6379 redis:7-alpine
    pause
    exit /b 1
)

echo [OK] Redis连接正常

REM 启动Celery Worker
echo [启动] Celery Worker...
celery -A app.celery_app worker --loglevel=info --concurrency=2 --pidfile=celery_worker.pid

pause
