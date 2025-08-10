# 基金监控系统 - PowerShell 启动脚本
param(
    [switch]$SkipDeps,
    [switch]$SkipMigrations,
    [switch]$Docker
)

# 设置控制台编码
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "基金监控系统 - PowerShell 启动脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 检查是否在正确的目录
if (-not (Test-Path "app\__init__.py")) {
    Write-Host "❌ 错误: 请在项目根目录运行此脚本" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查Python是否安装
Write-Host "检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误: 未找到Python，请先安装Python" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查pip是否可用
Write-Host "检查pip包管理器..." -ForegroundColor Yellow
try {
    $pipVersion = pip --version 2>&1
    Write-Host "✅ pip包管理器检查通过" -ForegroundColor Green
} catch {
    Write-Host "❌ 错误: 未找到pip，请检查Python安装" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

# 检查虚拟环境
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "发现虚拟环境，正在激活..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "⚠️  未发现虚拟环境，使用系统Python" -ForegroundColor Yellow
}

# 安装依赖
if (-not $SkipDeps) {
    Write-Host "检查项目依赖..." -ForegroundColor Yellow
    if (-not (Test-Path "requirements.txt")) {
        Write-Host "❌ 错误: 未找到requirements.txt文件" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }

    Write-Host "安装Python依赖包..." -ForegroundColor Yellow
    try {
        pip install -r requirements.txt
        Write-Host "✅ 依赖安装完成" -ForegroundColor Green
    } catch {
        Write-Host "❌ 错误: 依赖安装失败" -ForegroundColor Red
        Read-Host "按回车键退出"
        exit 1
    }
} else {
    Write-Host "跳过依赖安装" -ForegroundColor Yellow
}

# 设置环境变量
Write-Host "设置环境变量..." -ForegroundColor Yellow
$env:FLASK_CONFIG = "development"
Write-Host "✅ 环境变量设置完成" -ForegroundColor Green

# 检查数据库配置
Write-Host "检查数据库配置..." -ForegroundColor Yellow
if (Test-Path "instance\config.py") {
    Write-Host "发现实例配置文件" -ForegroundColor Green
} else {
    Write-Host "创建实例配置目录..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "instance" -Force | Out-Null
}

# 等待MySQL启动（如果使用Docker）
Write-Host "等待MySQL服务启动..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# 数据库迁移
if (-not $SkipMigrations) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "执行数据库迁移..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    Write-Host "初始化数据库..." -ForegroundColor Yellow
    try {
        flask db init
        Write-Host "✅ 数据库初始化完成" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  数据库可能已经初始化过，继续执行..." -ForegroundColor Yellow
    }

    Write-Host "创建数据库迁移..." -ForegroundColor Yellow
    try {
        flask db migrate
        Write-Host "✅ 迁移创建完成" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  迁移创建失败或无需迁移，继续执行..." -ForegroundColor Yellow
    }

    Write-Host "应用数据库迁移..." -ForegroundColor Yellow
    try {
        flask db upgrade
        Write-Host "✅ 迁移应用完成" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  迁移应用失败，继续执行..." -ForegroundColor Yellow
    }
} else {
    Write-Host "跳过数据库迁移" -ForegroundColor Yellow
}

# 启动应用
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "启动Flask应用..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "应用将在 http://localhost:8000 启动" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止应用" -ForegroundColor Yellow
Write-Host ""

try {
    python run.py
} catch {
    Write-Host "❌ 应用启动失败" -ForegroundColor Red
    Write-Host "请检查:" -ForegroundColor Red
    Write-Host "1. 数据库连接配置" -ForegroundColor Red
    Write-Host "2. 端口8000是否被占用" -ForegroundColor Red
    Write-Host "3. 依赖包是否正确安装" -ForegroundColor Red
    Read-Host "按回车键退出"
    exit 1
}

Read-Host "按回车键退出" 