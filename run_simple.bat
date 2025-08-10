@echo off
chcp 65001 >nul
echo ========================================
echo 基金监控系统 - 简化启动脚本
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

echo 启动应用...
echo 应用将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止应用
echo.

python run.py

pause 