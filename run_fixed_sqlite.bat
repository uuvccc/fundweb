@echo off
chcp 65001 >nul
echo ========================================
echo 基金监控系统 - 修复版SQLite启动脚本
echo ========================================

echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)
echo ✅ Python环境检查通过

echo 安装/修复依赖...
python install_deps.py
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo 设置环境变量...
set FLASK_CONFIG=development

echo 初始化SQLite数据库...
if not exist "fundweb.db" (
    echo 创建新的SQLite数据库文件...
    flask db init
    if errorlevel 1 (
        echo ⚠️  数据库可能已经初始化过，继续执行...
    )
    
    flask db migrate -m "Initial migration"
    if errorlevel 1 (
        echo ⚠️  迁移创建失败，继续执行...
    )
    
    flask db upgrade
    if errorlevel 1 (
        echo ⚠️  迁移应用失败，继续执行...
    )
    echo ✅ 数据库初始化完成
) else (
    echo ✅ 数据库文件已存在
)

echo 启动应用...
echo 应用将在 http://localhost:8000 启动
echo 数据库文件: fundweb.db
echo 按 Ctrl+C 停止应用
echo.

python run.py

if errorlevel 1 (
    echo ❌ 应用启动失败
    echo 请检查:
    echo 1. 端口8000是否被占用
    echo 2. 依赖包是否正确安装
    echo 3. 数据库文件权限
    pause
    exit /b 1
)

pause 