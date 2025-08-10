#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import json
import os
from datetime import datetime, timedelta
from app import create_app, db
from app.models import JsonString

class FundWebTestCase(unittest.TestCase):
    """基金监控系统测试用例"""

    def setUp(self):
        """测试前设置"""
        # 使用测试配置
        os.environ['FLASK_CONFIG'] = 'development'
        self.app = create_app('development')
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            self._create_test_data()

    def tearDown(self):
        """测试后清理"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def _create_test_data(self):
        """创建测试数据"""
        # 创建今天的测试数据
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        
        # 今天的基金数据
        today_data = {
            "0": [
                {"fundcode": "000001", "nav": "1.2345", "fundvol": "1000.0"},
                {"fundcode": "000002", "nav": "2.3456", "fundvol": "2000.0"},
                {"fundcode": "000003", "nav": "3.4567", "fundvol": "1500.0"}
            ]
        }
        
        # 昨天的基金数据
        yesterday_data = {
            "0": [
                {"fundcode": "000001", "nav": "1.2000", "fundvol": "900.0"},
                {"fundcode": "000002", "nav": "2.3000", "fundvol": "1800.0"},
                {"fundcode": "000003", "nav": "3.4000", "fundvol": "1200.0"}
            ]
        }
        
        # 保存到数据库
        today_record = JsonString(
            date=today,
            navdate=today,
            jsonString=json.dumps(today_data)
        )
        yesterday_record = JsonString(
            date=yesterday,
            navdate=yesterday,
            jsonString=json.dumps(yesterday_data)
        )
        
        db.session.add(today_record)
        db.session.add(yesterday_record)
        db.session.commit()

    def test_home_page(self):
        """测试主页"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Hello World', response.data.decode('utf-8'))

    def test_login_endpoint(self):
        """测试基金数据查询端点"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('have update today', response.data.decode('utf-8'))

    def test_1445_endpoint(self):
        """测试基金净值变化（处理后）端点"""
        response = self.client.get('/1445')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('des', data)
        self.assertIn('date', data)

    def test_1446_endpoint(self):
        """测试基金净值变化（未处理）端点"""
        response = self.client.get('/1446')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('des', data)
        self.assertIn('date', data)

    def test_1447_endpoint_with_date(self):
        """测试指定日期数据端点"""
        today = datetime.now().strftime('%Y%m%d')
        response = self.client.get(f'/1447?date={today}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('des', data)
        self.assertEqual(data['des'], 'special date')

    def test_1448_endpoint_with_date_range(self):
        """测试日期范围数据端点"""
        today = datetime.now().strftime('%Y%m%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
        response = self.client.get(f'/1448?datef={yesterday}&datet={today}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertIn('des', data)
        self.assertIn('amountInfo', data)

    def test_recordone_endpoint(self):
        """测试手动触发数据获取端点"""
        response = self.client.get('/recordone')
        self.assertEqual(response.status_code, 200)
        self.assertIn('result_string', response.data.decode('utf-8'))

    def test_invalid_date_1447(self):
        """测试无效日期的1447端点"""
        response = self.client.get('/1447?date=invalid_date')
        # 应该返回错误或空数据
        self.assertIn(response.status_code, [200, 404, 500])

    def test_missing_date_1447(self):
        """测试缺少日期参数的1447端点"""
        response = self.client.get('/1447')
        # 应该返回错误
        self.assertIn(response.status_code, [400, 404, 500])

    def test_missing_date_1448(self):
        """测试缺少日期参数的1448端点"""
        response = self.client.get('/1448')
        # 应该返回错误
        self.assertIn(response.status_code, [400, 404, 500])

if __name__ == '__main__':
    unittest.main() 