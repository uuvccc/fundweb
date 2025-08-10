# FundWeb - 基金监控系统

这是一个基于 Flask 的基金监控系统，用于监控基金净值和份额变化。

## 功能特性

- 自动获取基金数据
- 显示基金净值变化
- 显示基金份额变化
- 提供 API 接口
- 定时任务执行
- Web 界面展示

## 环境变量

在使用此系统前，需要配置以下环境变量：

- `SECRET_KEY` - Flask 应用的密钥
- `FUND_API_URL` - 基金数据 API 地址
- `DEFAULT_CUSTNOS` - 默认的客户号列表，以逗号分隔，例如: `custno1,custno2`

## 安装和运行

### 使用 Docker (推荐)

```bash
docker-compose up --build
```

### 本地运行

1. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

2. 配置环境变量:
   ```bash
   # 复制示例配置文件
   cp .env.sample .env
   
   # 编辑 .env 文件，填入实际值
   # 在 Windows 上可以使用编辑器打开，在 Linux/Mac 上可以使用:
   # nano .env 或 vim .env
   ```

3. 运行应用:
   ```bash
   python run.py
   ```

## API 接口

- `GET /api/funds/today-changes?custno=<custno>` - 获取今日基金变化
- `GET /api/funds/nav-changes?custno=<custno>` - 获取基金净值变化
- `GET /api/funds/volume-changes?custno=<custno>` - 获取基金份额变化
- `GET /api/funds/by-date?date=<date>` - 获取指定日期的基金数据
- `GET /api/funds/compare?datef=<date_from>&datet=<date_to>` - 获取日期范围的基金数据对比
- `POST /api/funds/refresh` - 手动触发数据获取

## 定时任务

系统使用 APScheduler 来执行定时任务，默认配置为每天 18:25 执行数据获取任务。

## 安全说明

为了安全起见，所有敏感信息（如 API 地址、客户号等）都应通过环境变量配置，不要在代码中硬编码。

## 许可证

MIT