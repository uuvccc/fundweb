#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def main():
    print("🚀 基金监控系统依赖安装脚本")
    print("=" * 50)
    
    # 升级pip
    if not run_command("python -m pip install --upgrade pip", "升级pip"):
        print("⚠️  pip升级失败，继续执行...")
    
    # 安装基础依赖（不指定版本）
    basic_deps = [
        "flask",
        "flask-sqlalchemy", 
        "flask-migrate",
        "flask-login",
        "requests",
        "python-dotenv",
        "pytz",
        "flask-apscheduler",
        "passlib"
    ]
    
    print("\n📦 安装基础依赖...")
    for dep in basic_deps:
        if not run_command(f"pip install {dep}", f"安装 {dep}"):
            print(f"⚠️  {dep} 安装失败，继续执行...")
    
    # SQLite 是 Python 内置的，不需要额外安装
    print("\n🗄️  数据库配置...")
    print("✅ 使用 SQLite 数据库（Python 内置，无需额外安装）")
    
    # 验证关键依赖
    print("\n🔍 验证关键依赖...")
    try:
        import flask
        print("✅ Flask: 已安装")
    except ImportError:
        print("❌ Flask 未安装")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy: 已安装")
    except ImportError:
        print("❌ Flask-SQLAlchemy 未安装")
        return False
    
    try:
        import requests
        print(f"✅ Requests: {requests.__version__}")
    except ImportError:
        print("❌ Requests 未安装")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite: Python 内置支持")
    except ImportError:
        print("❌ SQLite 未可用")
        return False
    
    print("\n🎉 依赖安装完成！")
    print("数据库将保存为: fundweb.db")
    print("现在可以运行应用了：")
    print("  python run.py")
    print("  或")
    print("  .\\run.ps1")
    print("  或")
    print("  run_simple.bat")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 