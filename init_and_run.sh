#!/bin/bash

# 1. 激活虚拟环境（如果有）
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# 2. 安装依赖
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# 3. 初始化数据库（如果有 init_db.py）
if [ -f "init_db.py" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# 4. 启动 Flask 项目
echo "Starting Flask app..."
export FLASK_APP=run.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000 