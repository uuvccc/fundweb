@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 基金监控系统 - Windows 启动脚本
echo ========================================

REM 检查Python是否安装
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)
echo ✅ Python环境检查通过

REM 检查pip是否可用
echo 检查pip包管理器...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到pip，请检查Python安装
    pause
    exit /b 1
)
echo ✅ pip包管理器检查通过

REM 检查是否在正确的目录
if not exist "app\__init__.py" (
    echo ❌ 错误: 请在项目根目录运行此脚本
    pause
    exit /b 1
)
echo ✅ 项目目录检查通过

REM 检查虚拟环境（可选）
if exist "venv\Scripts\activate.bat" (
    echo 发现虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未发现虚拟环境，使用系统Python
)

REM 安装依赖（如果需要）
echo 检查项目依赖...
if not exist "requirements.txt" (
    echo ❌ 错误: 未找到requirements.txt文件
    pause
    exit /b 1
)

echo 安装Python依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 错误: 依赖安装失败
    pause
    exit /b 1
)
echo ✅ 依赖安装完成

REM 设置环境变量
echo 设置环境变量...
set FLASK_CONFIG=development
echo ✅ 环境变量设置完成

REM 检查数据库配置
echo 检查数据库配置...
if exist "instance\config.py" (
    echo 发现实例配置文件
) else (
    echo 创建实例配置目录...
    mkdir instance 2>nul
)

REM 等待MySQL启动（如果使用Docker）
echo 等待MySQL服务启动...
timeout /t 3 /nobreak >nul

REM 数据库迁移
echo ========================================
echo 执行数据库迁移...
echo ========================================

echo 初始化数据库...
flask db init
if errorlevel 1 (
    echo ⚠️  数据库可能已经初始化过，继续执行...
)

echo 创建数据库迁移...
flask db migrate
if errorlevel 1 (
    echo ⚠️  迁移创建失败或无需迁移，继续执行...
)

echo 应用数据库迁移...
flask db upgrade
if errorlevel 1 (
    echo ⚠️  迁移应用失败，继续执行...
)

echo ✅ 数据库迁移完成

REM 启动应用
echo ========================================
echo 启动Flask应用...
echo ========================================

echo 应用将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止应用
echo.

python run.py

if errorlevel 1 (
    echo ❌ 应用启动失败
    echo 请检查:
    echo 1. 数据库连接配置
    echo 2. 端口8000是否被占用
    echo 3. 依赖包是否正确安装
    pause
    exit /b 1
)

pause 