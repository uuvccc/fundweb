# 基金监控系统 API 文档

## 概述

基金监控系统提供RESTful API接口，用于获取基金数据、监控基金变化和触发数据更新。

## 基础信息

- **基础URL**: `http://localhost:5000`
- **数据格式**: JSON
- **时区**: 亚洲/上海 (Asia/Shanghai)

## API 端点

### 1. 系统状态

#### 健康检查
```
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "service": "fund-monitoring-system"
}
```

### 2. 基金数据接口

#### 获取今日基金变化（文本格式）
```
GET/POST /api/funds/today-changes
```

**描述**: 获取今日基金份额和金额变化，返回易读的文本格式

**响应示例**:
```
今日基金变化情况:
000001: 份额变化 100.5, 金额变化 105.52
000002: 份额变化 -50.0, 金额变化 -52.50
```

#### 获取基金净值变化（处理后，JSON格式）
```
GET/POST /api/funds/nav-changes
```

**描述**: 获取基金净值变化，返回处理后的金额变化数据

**响应示例**:
```json
{
  "000001": 105.52,
  "000002": -52.50,
  "description": "processed",
  "date": "20240115"
}
```

#### 获取基金净值变化（未处理，JSON格式）
```
GET/POST /api/funds/volume-changes
```

**描述**: 获取基金份额变化，返回未处理的份额变化数据

**响应示例**:
```json
{
  "000001": 100.5,
  "000002": -50.0,
  "description": "no processed",
  "date": "20240115"
}
```

#### 获取指定日期的基金数据
```
GET/POST /api/funds/by-date?date=YYYYMMDD
```

**参数**:
- `date` (必需): 日期，格式为YYYYMMDD

**响应示例**:
```json
{
  "000001": 1000.0,
  "000002": 500.0,
  "description": "special date",
  "date": "20240115"
}
```

#### 获取日期范围的基金数据对比
```
GET/POST /api/funds/compare?datef=YYYYMMDD&datet=YYYYMMDD
```

**参数**:
- `datef` (必需): 开始日期，格式为YYYYMMDD
- `datet` (必需): 结束日期，格式为YYYYMMDD

**响应示例**:
```json
{
  "000001": 105.52,
  "000002": -52.50,
  "description": "arbitrarily / no processed amount : vol",
  "date": "20240115",
  "amountInfo": "{'000001': 100.5, '000002': -50.0}"
}
```

#### 手动触发数据获取
```
GET/POST /api/funds/refresh
```

**描述**: 手动触发基金数据获取任务

**响应示例**:
```json
{
  "message": "数据获取任务已触发",
  "timestamp": "2024-01-15T10:30:00"
}
```

## 数据说明

### 基金代码格式
- 基金代码为6位数字，如：000001, 000002

### 数据字段说明
- `nav`: 基金净值
- `fundvol`: 基金份额
- `fundcode`: 基金代码
- `navdate`: 净值日期

### 计算逻辑
- **份额变化**: 当前份额 - 上一日份额
- **金额变化**: 份额变化 × 当前净值

## 错误处理

### 常见错误响应

#### 400 Bad Request
```json
{
  "error": "日期参数不能为空"
}
```

#### 404 Not Found
```json
{
  "error": "未找到日期 20240115 的数据"
}
```

## 使用示例

### Python 示例
```python
import requests

# 获取今日基金变化
response = requests.get('http://localhost:5000/api/funds/today-changes')
print(response.text)

# 获取指定日期数据
response = requests.get('http://localhost:5000/api/funds/by-date?date=20240115')
data = response.json()
print(data)

# 比较日期范围
response = requests.get('http://localhost:5000/api/funds/compare?datef=20240114&datet=20240115')
data = response.json()
print(data)
```

### cURL 示例
```bash
# 获取今日基金变化
curl -X GET http://localhost:5000/api/funds/today-changes

# 获取指定日期数据
curl -X GET "http://localhost:5000/api/funds/by-date?date=20240115"

# 比较日期范围
curl -X GET "http://localhost:5000/api/funds/compare?datef=20240114&datet=20240115"

# 手动刷新数据
curl -X POST http://localhost:5000/api/funds/refresh
```

## 定时任务

系统配置了定时任务，每天18:25自动获取基金数据。

## 注意事项

1. 所有日期参数使用YYYYMMDD格式
2. 系统使用SQLite数据库存储数据
3. 数据获取基于中国基金网API
4. 时区设置为亚洲/上海
5. 建议在生产环境中配置适当的日志记录和监控 