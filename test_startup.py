#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

def test_imports():
    """测试关键模块导入"""
    print("🔍 测试模块导入...")
    
    try:
        import flask
        print("✅ Flask 导入成功")
    except ImportError as e:
        print(f"❌ Flask 导入失败: {e}")
        return False
    
    try:
        import flask_sqlalchemy
        print("✅ Flask-SQLAlchemy 导入成功")
    except ImportError as e:
        print(f"❌ Flask-SQLAlchemy 导入失败: {e}")
        return False
    
    try:
        import requests
        print("✅ Requests 导入成功")
    except ImportError as e:
        print(f"❌ Requests 导入失败: {e}")
        return False
    
    try:
        import sqlite3
        print("✅ SQLite 导入成功")
    except ImportError as e:
        print(f"❌ SQLite 导入失败: {e}")
        return False
    
    return True

def test_app_import():
    """测试应用模块导入"""
    print("\n🔍 测试应用模块导入...")
    
    try:
        from app import create_app
        print("✅ 应用模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 应用模块导入失败: {e}")
        return False

def test_app_creation():
    """测试应用创建"""
    print("\n🔍 测试应用创建...")
    
    try:
        from app import create_app
        app = create_app('development')
        print("✅ 应用创建成功")
        return True
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        return False

def main():
    print("🚀 基金监控系统启动测试")
    print("=" * 40)
    
    # 设置环境变量
    os.environ['FLASK_CONFIG'] = 'development'
    
    # 测试模块导入
    if not test_imports():
        print("\n❌ 模块导入测试失败")
        return False
    
    # 测试应用模块导入
    if not test_app_import():
        print("\n❌ 应用模块导入测试失败")
        return False
    
    # 测试应用创建
    if not test_app_creation():
        print("\n❌ 应用创建测试失败")
        return False
    
    print("\n🎉 所有测试通过！应用可以正常启动")
    print("现在可以运行: python run.py")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 