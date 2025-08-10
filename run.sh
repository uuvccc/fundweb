#!/usr/bin/env bash

# export FLASK_ENV=production

echo "Waiting for MySQL..."

#while ! nc -z db 3306; do
 # sleep 0.5
#done
#systemctl restart mariadb.service
#systemctl start mariadb.service

echo "MySQL started"

flask db init
flask db migrate
flask db upgrade

python run.py
