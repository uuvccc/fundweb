import os

class Config:
    JOBS = [
        {
            'id': 'job1',
            'func': 'app.__init__:fetch_and_store_fund_data',
            'args': (1, 2),
            'trigger': 'cron',
            'day_of_week': 'mon-sun',
            'hour': 18,
            'minute': 25
        }
    ]
    SCHEDULER_API_ENABLED = True
    SCHEDULER_TIMEZONE = 'Asia/Shanghai'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///fundweb.db'
    SQLALCHEMY_ECHO = True
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

app_config = {
    'default': Config
}