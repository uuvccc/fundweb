@echo off
chcp 65001 >nul
echo 等待MySQL启动...

REM 注释掉Linux特定的命令
REM while ! nc -z db 3306; do
REM  sleep 0.5
REM done
REM systemctl restart mariadb.service
REM systemctl start mariadb.service

echo MySQL已启动

REM 初始化数据库
echo 初始化数据库...
flask db init

REM 创建数据库迁移
echo 创建数据库迁移...
flask db migrate

REM 应用数据库迁移
echo 应用数据库迁移...
flask db upgrade

REM 启动Flask应用
echo 启动Flask应用...
python run.py

pause 