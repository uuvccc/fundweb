#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import time
import requests

def check_app_running():
    """检查应用是否正在运行"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False

def run_unit_tests():
    """运行单元测试"""
    print("🧪 运行单元测试...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "unittest", "discover", "tests", "-v"
        ], capture_output=True, text=True)
        
        print("单元测试输出:")
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行单元测试失败: {e}")
        return False

def run_api_tests():
    """运行API测试"""
    print("\n🌐 运行API测试...")
    try:
        result = subprocess.run([
            sys.executable, "test_api.py"
        ], capture_output=True, text=True)
        
        print("API测试输出:")
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行API测试失败: {e}")
        return False

def run_manual_tests():
    """运行手动测试"""
    print("\n👆 手动测试指南:")
    print("1. 确保应用正在运行 (http://localhost:8000/)")
    print("2. 在浏览器中访问以下URL进行测试:")
    print("   - 主页: http://localhost:8000/")
    print("   - 基金数据: http://localhost:8000/login")
    print("   - 净值变化(处理后): http://localhost:8000/1445")
    print("   - 净值变化(未处理): http://localhost:8000/1446")
    print("   - 指定日期: http://localhost:8000/1447?date=20231201")
    print("   - 日期范围: http://localhost:8000/1448?datef=20231201&datet=20231202")
    print("   - 手动触发: http://localhost:8000/recordone")

def run_docker_tests():
    """运行Docker测试"""
    print("\n🐳 运行Docker测试...")
    
    # 检查Docker是否安装
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except:
        print("❌ Docker未安装或未在PATH中")
        return False
    
    # 检查docker-compose是否安装
    try:
        subprocess.run(["docker-compose", "--version"], check=True, capture_output=True)
    except:
        print("❌ docker-compose未安装或未在PATH中")
        return False
    
    print("✅ Docker环境检查通过")
    
    # 构建和启动容器
    print("构建和启动Docker容器...")
    try:
        subprocess.run(["docker-compose", "up", "--build", "-d"], check=True)
        print("✅ Docker容器启动成功")
        
        # 等待应用启动
        print("等待应用启动...")
        for i in range(30):
            if check_app_running():
                print("✅ 应用启动成功")
                break
            time.sleep(2)
        else:
            print("❌ 应用启动超时")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Docker测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 基金监控系统测试套件")
    print("=" * 50)
    
    # 检查应用是否运行
    if not check_app_running():
        print("⚠️  应用未运行，请先启动应用")
        print("启动方式:")
        print("1. Docker: docker-compose up --build")
        print("2. 本地: python run.py")
        print("\n是否要启动Docker测试? (y/n): ", end="")
        choice = input().lower()
        if choice == 'y':
            if run_docker_tests():
                print("✅ Docker测试完成")
            else:
                print("❌ Docker测试失败")
        return
    
    # 运行单元测试
    unit_success = run_unit_tests()
    
    # 运行API测试
    api_success = run_api_tests()
    
    # 显示手动测试指南
    run_manual_tests()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"单元测试: {'✅ 通过' if unit_success else '❌ 失败'}")
    print(f"API测试: {'✅ 通过' if api_success else '❌ 失败'}")
    
    if unit_success and api_success:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败，请检查应用状态")

if __name__ == "__main__":
    main() 