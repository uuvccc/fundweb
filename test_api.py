#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基金监控系统 API 测试脚本
测试所有新的 RESTful API 接口
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz

# 配置
BASE_URL = "http://localhost:5000"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def print_separator(title):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_health_check():
    """测试健康检查接口"""
    print_separator("健康检查测试")
    
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 健康检查测试通过")
        else:
            print(f"❌ 健康检查测试失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 健康检查测试异常: {e}")

def test_today_changes():
    """测试获取今日基金变化接口"""
    print_separator("今日基金变化测试")
    
    try:
        # 测试 GET 方法
        print("测试 GET 方法:")
        response = requests.get(f"{BASE_URL}/api/funds/today-changes", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        # 测试 POST 方法
        print("\n测试 POST 方法:")
        response = requests.post(f"{BASE_URL}/api/funds/today-changes", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        if response.status_code in [200, 404]:  # 404 表示没有数据，也是正常情况
            print("✅ 今日基金变化测试通过")
        else:
            print(f"❌ 今日基金变化测试失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 今日基金变化测试异常: {e}")

def test_nav_changes():
    """测试获取基金净值变化接口"""
    print_separator("基金净值变化测试")
    
    try:
        # 测试 GET 方法
        print("测试 GET 方法:")
        response = requests.get(f"{BASE_URL}/api/funds/nav-changes", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 基金净值变化测试通过")
        elif response.status_code == 404:
            print("响应: 没有找到数据（正常情况）")
            print("✅ 基金净值变化测试通过")
        else:
            print(f"❌ 基金净值变化测试失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 基金净值变化测试异常: {e}")

def test_volume_changes():
    """测试获取基金份额变化接口"""
    print_separator("基金份额变化测试")
    
    try:
        # 测试 GET 方法
        print("测试 GET 方法:")
        response = requests.get(f"{BASE_URL}/api/funds/volume-changes", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 基金份额变化测试通过")
        elif response.status_code == 404:
            print("响应: 没有找到数据（正常情况）")
            print("✅ 基金份额变化测试通过")
        else:
            print(f"❌ 基金份额变化测试失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 基金份额变化测试异常: {e}")

def test_by_date():
    """测试获取指定日期基金数据接口"""
    print_separator("指定日期基金数据测试")
    
    # 获取今天的日期
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).strftime('%Y%m%d')
    yesterday = (datetime.now(tz) - timedelta(days=1)).strftime('%Y%m%d')
    
    test_dates = [today, yesterday, "20240101"]  # 测试多个日期
    
    for date in test_dates:
        print(f"\n测试日期: {date}")
        try:
            response = requests.get(f"{BASE_URL}/api/funds/by-date?date={date}", headers=HEADERS)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("响应数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print(f"✅ 日期 {date} 测试通过")
            elif response.status_code == 404:
                print(f"响应: 没有找到日期 {date} 的数据（正常情况）")
                print(f"✅ 日期 {date} 测试通过")
            elif response.status_code == 400:
                print(f"响应: 参数错误 - {response.text}")
                print(f"✅ 日期 {date} 参数验证通过")
            else:
                print(f"❌ 日期 {date} 测试失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 日期 {date} 测试异常: {e}")

def test_compare():
    """测试基金数据对比接口"""
    print_separator("基金数据对比测试")
    
    # 获取今天的日期
    tz = pytz.timezone('Asia/Shanghai')
    today = datetime.now(tz).strftime('%Y%m%d')
    yesterday = (datetime.now(tz) - timedelta(days=1)).strftime('%Y%m%d')
    day_before = (datetime.now(tz) - timedelta(days=2)).strftime('%Y%m%d')
    
    test_cases = [
        (yesterday, today),
        (day_before, today),
        ("20240101", "20240102"),
        ("invalid", "date")  # 测试无效参数
    ]
    
    for datef, datet in test_cases:
        print(f"\n测试日期范围: {datef} 到 {datet}")
        try:
            response = requests.get(f"{BASE_URL}/api/funds/compare?datef={datef}&datet={datet}", headers=HEADERS)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("响应数据:")
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print(f"✅ 日期范围 {datef}-{datet} 测试通过")
            elif response.status_code == 404:
                print(f"响应: 没有找到日期范围 {datef}-{datet} 的数据（正常情况）")
                print(f"✅ 日期范围 {datef}-{datet} 测试通过")
            elif response.status_code == 400:
                print(f"响应: 参数错误 - {response.text}")
                print(f"✅ 日期范围 {datef}-{datet} 参数验证通过")
            else:
                print(f"❌ 日期范围 {datef}-{datet} 测试失败: {response.text}")
                
        except Exception as e:
            print(f"❌ 日期范围 {datef}-{datet} 测试异常: {e}")

def test_refresh():
    """测试手动触发数据获取接口"""
    print_separator("手动触发数据获取测试")
    
    try:
        # 测试 GET 方法
        print("测试 GET 方法:")
        response = requests.get(f"{BASE_URL}/api/funds/refresh", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 手动触发数据获取测试通过")
        else:
            print(f"❌ 手动触发数据获取测试失败: {response.text}")
            
        # 测试 POST 方法
        print("\n测试 POST 方法:")
        response = requests.post(f"{BASE_URL}/api/funds/refresh", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 手动触发数据获取测试通过")
        else:
            print(f"❌ 手动触发数据获取测试失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 手动触发数据获取测试异常: {e}")

def test_error_handling():
    """测试错误处理"""
    print_separator("错误处理测试")
    
    # 测试缺少参数的情况
    print("测试缺少日期参数:")
    try:
        response = requests.get(f"{BASE_URL}/api/funds/by-date", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 缺少参数错误处理测试通过")
        else:
            print(f"❌ 缺少参数错误处理测试失败: {response.text}")
    except Exception as e:
        print(f"❌ 缺少参数错误处理测试异常: {e}")
    
    # 测试缺少比较参数的情况
    print("\n测试缺少比较参数:")
    try:
        response = requests.get(f"{BASE_URL}/api/funds/compare", headers=HEADERS)
        print(f"状态码: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            print("✅ 缺少比较参数错误处理测试通过")
        else:
            print(f"❌ 缺少比较参数错误处理测试失败: {response.text}")
    except Exception as e:
        print(f"❌ 缺少比较参数错误处理测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 开始测试基金监控系统 API")
    print(f"测试目标: {BASE_URL}")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ 服务正在运行")
        else:
            print(f"⚠️  服务响应异常: {response.status_code}")
    except Exception as e:
        print(f"❌ 无法连接到服务: {e}")
        print("请确保服务正在运行: python run.py")
        return
    
    # 执行所有测试
    test_health_check()
    test_today_changes()
    test_nav_changes()
    test_volume_changes()
    test_by_date()
    test_compare()
    test_refresh()
    test_error_handling()
    
    print_separator("测试完成")
    print("🎉 所有测试已完成！")
    print("\n注意事项:")
    print("- 某些测试可能返回404，这是正常情况（表示没有对应日期的数据）")
    print("- 手动触发数据获取可能需要较长时间")
    print("- 建议在有数据的情况下重新运行测试以获得更好的结果")

if __name__ == "__main__":
    main() 