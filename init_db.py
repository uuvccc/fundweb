#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库表和初始数据
"""

import os
import sys
from app import create_app, db
from app.models import JsonString, Employee, Department, User
from passlib.hash import pbkdf2_sha256

def init_database():
    """初始化数据库"""
    print("🚀 开始初始化数据库...")
    
    # 创建应用上下文
    app = create_app('development')
    
    with app.app_context():
        try:
            # 检查表和数据是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            if 'jsonstring' in tables:
                count = JsonString.query.count()
                if count > 0:
                    print("⚠️  数据库已有数据，初始化将清空所有数据。请确认后再操作。")
                    confirm = input("是否继续初始化？(y/n): ")
                    if confirm.lower() != 'y':
                        print("已取消初始化。")
                        return False
            # 删除所有表（如果存在）
            print("🗑️  删除现有表...")
            db.drop_all()
            
            # 创建所有表
            print("📋 创建数据库表...")
            db.create_all()
            
            print("✅ 数据库表创建成功！")
            
            # 显示创建的表
            print("\n📊 已创建的表:")
            for table in db.metadata.tables.keys():
                print(f"  - {table}")
            
            print("\n🎉 数据库初始化完成！")
            print("\n下一步:")
            print("1. 运行应用: python run.py")
            print("2. 手动获取数据: 访问 http://localhost:5000/api/funds/refresh")
            print("3. 查看数据: 访问 http://localhost:5000/api/funds/today-changes")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败: {e}")
            return False
    
    return True

def check_database():
    """检查数据库状态"""
    print("🔍 检查数据库状态...")
    
    app = create_app('development')
    
    with app.app_context():
        try:
            # 检查表是否存在
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📋 现有表: {tables}")
            
            if 'jsonstring' in tables:
                # 检查数据
                count = JsonString.query.count()
                print(f"📊 jsonstring 表中的记录数: {count}")
                
                if count > 0:
                    # 显示最新的几条记录
                    latest_records = JsonString.query.order_by(JsonString.id.desc()).limit(3).all()
                    print("\n📅 最新记录:")
                    for record in latest_records:
                        print(f"  ID: {record.id}, 日期: {record.date}, 净值日期: {record.navdate}")
                else:
                    print("⚠️  表中暂无数据")
            else:
                print("❌ jsonstring 表不存在")
                
        except Exception as e:
            print(f"❌ 检查数据库失败: {e}")

def create_admin_user():
    """Create an initial admin user if not exists"""
    app = create_app('development')
    with app.app_context():
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', password_hash=pbkdf2_sha256.hash('admin123'))
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created: admin / admin123')
        else:
            print('ℹ️  Admin user already exists')

def main():
    """主函数"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            init_database()
        elif command == "check":
            check_database()
        elif command == "reset":
            print("🔄 重置数据库...")
            init_database()
        else:
            print("❌ 未知命令")
            print("可用命令:")
            print("  init   - 初始化数据库")
            print("  check  - 检查数据库状态")
            print("  reset  - 重置数据库")
    else:
        print("🔧 数据库管理工具")
        print("\n可用命令:")
        print("  python init_db.py init   - 初始化数据库")
        print("  python init_db.py check  - 检查数据库状态")
        print("  python init_db.py reset  - 重置数据库")
        print("\n示例:")
        print("  python init_db.py init")

if __name__ == "__main__":
    main()
    create_admin_user() 