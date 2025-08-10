@echo off
chcp 65001 >nul
echo.
echo ========================================
echo    基金监控系统 - 初始化并启动
echo ========================================
echo.

echo 🔧 步骤1: 初始化数据库...
python init_db.py init
if %errorlevel% neq 0 (
    echo ❌ 数据库初始化失败！
    pause
    exit /b 1
)

echo.
echo ✅ 数据库初始化成功！
echo.
echo 🚀 步骤2: 启动应用...
echo.
echo 应用启动后，请访问以下地址：
echo - 主页: http://localhost:5000/
echo - 健康检查: http://localhost:5000/health
echo - 手动获取数据: http://localhost:5000/api/funds/refresh
echo - 查看基金变化: http://localhost:5000/api/funds/today-changes
echo.
echo 按 Ctrl+C 停止应用
echo.

python run.py 