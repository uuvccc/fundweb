#-*-coding:utf-8-*- 
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import requests
import xml.dom.minidom
import json
import threading
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta
import pytz
from sqlalchemy import func
from flask import jsonify
from flask import request
from config import app_config
import sqlite3
from flask import render_template
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from passlib.hash import pbkdf2_sha256
import os
from dotenv import load_dotenv

db = SQLAlchemy()
# login_manager = LoginManager()
lock = threading.Lock()

load_dotenv()  # Add this after imports

def map_frontend_custno_to_actual(custnos):
    """
    Map frontend custno to actual custno.
    The actual custnos are stored in DEFAULT_CUSTNOS env var as comma-separated values.
    """
    default_custnos = os.environ.get('DEFAULT_CUSTNOS', '').split(',')
    
    # If custno matches the position in DEFAULT_CUSTNOS, return that value
    if len(custnos) == 1 and custnos[0] == 'custno1' and len(default_custnos) > 0:
        return [default_custnos[0]]
    elif len(custnos) == 1 and custnos[0] == 'custno2' and len(default_custnos) > 1:
        return [default_custnos[1]]
    
    # If no mapping found, return original custno
    return custnos

class Config:
    """
    Common configurations
    """
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


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config["default"])
    # app.config.from_pyfile('config.py')
    # app.config.from_object(Config())
    db.init_app(app)

    scheduler = APScheduler()                  # 实例化 APScheduler
    # it is also possible to enable the API directly
    scheduler.api_enabled = True
    scheduler.init_app(app)                    # 把任务列表放入 flask
    scheduler.start()                          # 启动任务列表

    # --- flask-login setup ---
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    # --- end flask-login setup ---

    # app.run()

    # 初始化数据库
    with app.app_context():
        try:
            # 创建所有数据库表
            db.create_all()
            print("✅ 数据库表创建成功")
        except Exception as e:
            print(f"⚠️  数据库初始化警告: {e}")

    # 主页
    @app.route('/')
    @login_required
    def home():
        return render_template('index.html')

    # 健康检查
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'fund-monitoring-system'
        })

    # 获取今日基金变化（文本格式）
    @app.route('/api/funds/today-changes', methods=['GET', 'POST'])
    @login_required
    def get_today_fund_changes():
        from app.models import JsonString
        custno = request.args.get("custno")
        if not custno:
            return "缺少 custno 参数", 400
        # Find the latest record
        peter1 = JsonString.query.filter_by(custno=custno).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
        if not peter1:
            return "该 custno 暂无数据", 404
        # Find the previous record with a different date
        lastpeter1 = JsonString.query.filter(JsonString.custno==custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
        if not lastpeter1:
            return f"无有效对比数据：找不到 {peter1.date} 之前的数据"
        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return "基金数据格式错误", 500
        navInfo = {}
        for item in jsonObject[0]:
            navInfo[item["fundcode"]] = float(item["nav"])
        volInfo = {}
        for item in jsonObject[0]:
            if item["fundcode"] in volInfo:
                volInfo[item["fundcode"]] = volInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                volInfo[item["fundcode"]] = float(item["fundvol"])
        lastVolInfo = {}
        for item in lastJsonObject[0]:
            if item["fundcode"] in lastVolInfo:
                lastVolInfo[item["fundcode"]] = lastVolInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                lastVolInfo[item["fundcode"]] = float(item["fundvol"])
        newVolInfo = {}
        for k, v in volInfo.items():
            newVolInfo[k] = volInfo[k] - lastVolInfo.get(k, 0)
        # Show both dates in the result
        result_string = f'基金份额变化 (custno={custno})\n日期对比: {peter1.date} vs {lastpeter1.date}\n'
        for k, v in newVolInfo.items():
            if v != 0.0:
                result_string = result_string + f"{k}: 份额变化 {v}, 金额变化 {v * navInfo[k]}\n"
        if result_string == f'基金份额变化 (custno={custno})\n日期对比: {peter1.date} vs {lastpeter1.date}\n':
            result_string += "今日无基金变化"
        return result_string

    # 获取基金净值变化（处理后，JSON格式）
    @app.route('/api/funds/nav-changes', methods=['GET', 'POST'])
    @login_required
    def get_fund_nav_changes():
        from app.models import JsonString
        # Get custno parameter if provided
        custno = request.args.get("custno")
        
        tz = pytz.timezone('Asia/Shanghai')
        nowdate = (datetime.now(tz) + timedelta(days=0)).strftime('%Y%m%d')
        lastday = (datetime.now(tz) + timedelta(days=-1)).strftime('%Y%m%d')
        print("date: " + nowdate + " " + lastday)

        # Query data for specific custno if provided, otherwise get any latest data
        if custno:
            # Convert frontend custno to actual custno
            actual_custno = map_frontend_custno_to_actual([custno])[0]
            # Find the latest record for this custno
            peter1 = JsonString.query.filter_by(custno=actual_custno).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not peter1:
                return jsonify({"error": f"客户 {custno} 暂无数据"}), 404
            
            # Find the previous record with a different date for this custno
            lastpeter1 = JsonString.query.filter(JsonString.custno==actual_custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not lastpeter1:
                return jsonify({"error": f"客户 {custno} 无有效对比数据：找不到 {peter1.date} 之前的数据"}), 404
        else:
            # 检查是否有数据
            max_id = db.session.query(func.max(JsonString.id)).scalar()
            if not max_id:
                return jsonify({"error": "暂无基金数据，请先运行数据获取任务"}), 404

            peter1 = JsonString.query.filter_by(id=max_id).first()
            if not peter1:
                return jsonify({"error": "无法获取最新基金数据"}), 404

            # 检查是否有前一天的数据
            if max_id <= 1:
                return jsonify({"error": "暂无足够的历史数据进行比较"}), 404

            lastpeter1 = JsonString.query.filter_by(id=max_id - 1).first()
            if not lastpeter1:
                return jsonify({"error": "无法获取历史基金数据"}), 404

        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return jsonify({"error": "基金数据格式错误"}), 500

        navInfo = {}
        for item in jsonObject[0]:
            navInfo[item["fundcode"]] = float(item["nav"])

        volInfo = {}
        for item in jsonObject[0]:
            if item["fundcode"] in volInfo:
                volInfo[item["fundcode"]] = volInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                volInfo[item["fundcode"]] = float(item["fundvol"])

        for k, v in volInfo.items():
            print(str(k) + " : " + str(v))

        lastVolInfo = {}
        for item in lastJsonObject[0]:
            if item["fundcode"] in lastVolInfo:
                lastVolInfo[item["fundcode"]] = lastVolInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                lastVolInfo[item["fundcode"]] = float(item["fundvol"])

        newVolInfo = {}
        for k, v in volInfo.items():
            if k in volInfo and k not in lastVolInfo:
                newVolInfo[k] = volInfo[k]
            elif k not in volInfo and k in lastVolInfo:
                newVolInfo[k] = 0 - lastVolInfo[k]
            else:
                newVolInfo[k] = volInfo[k] - lastVolInfo.get(k, 0)

        returnVolInfo = {}
        for k, v in newVolInfo.items():
            if v != 0.0:  # 只包含份额变化不为0的基金
                returnVolInfo[k] = v * navInfo[k]

        returnVolInfo["description"] = "processed"
        returnVolInfo["date"] = peter1.date
        if custno:
            returnVolInfo["custno"] = actual_custno

        return jsonify(returnVolInfo)

    # 获取基金净值变化（未处理，JSON格式）
    @app.route('/api/funds/volume-changes', methods=['GET', 'POST'])
    @login_required
    def get_fund_volume_changes():
        from app.models import JsonString
        # Get custno parameter if provided
        custno = request.args.get("custno")
        
        tz = pytz.timezone('Asia/Shanghai')
        nowdate = (datetime.now(tz) + timedelta(days=0)).strftime('%Y%m%d')
        lastday = (datetime.now(tz) + timedelta(days=-1)).strftime('%Y%m%d')
        print("date: " + nowdate + " " + lastday)

        # 初始化 max_id
        max_id = db.session.query(func.max(JsonString.id)).scalar()
        if not max_id:
            return jsonify({"error": "暂无基金数据，请先运行数据获取任务"}), 404

        # Query data for specific custno if provided, otherwise get any latest data
        if custno:
            # Convert frontend custno to actual custno
            actual_custno = map_frontend_custno_to_actual([custno])[0]
            # Find the latest record for this custno
            peter1 = JsonString.query.filter_by(custno=actual_custno).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not peter1:
                return jsonify({"error": f"客户 {custno} 暂无数据"}), 404
            
            # Find the previous record with a different date for this custno
            lastpeter1 = JsonString.query.filter(JsonString.custno==actual_custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not lastpeter1:
                return jsonify({"error": f"客户 {custno} 无有效对比数据：找不到 {peter1.date} 之前的数据"}), 404
        else:
            peter1 = JsonString.query.filter_by(id=max_id).first()
            if not peter1:
                return jsonify({"error": "无法获取最新基金数据"}), 404

            # 检查是否有前一天的数据
            if max_id <= 1:
                return jsonify({"error": "暂无足够的历史数据进行比较"}), 404

            lastpeter1 = JsonString.query.filter_by(id=max_id - 1).first()
            if not lastpeter1:
                return jsonify({"error": "无法获取历史基金数据"}), 404

        print("max id - 1  : " + str(max_id - 1))

        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return jsonify({"error": "基金数据格式错误"}), 500

        print("peter id   : " + str(peter1.id) + " " + str(lastpeter1.id))

        navInfo = {}
        for item in jsonObject[0]:
            navInfo[item["fundcode"]] = float(item["nav"])

        volInfo = {}
        for item in jsonObject[0]:
            if item["fundcode"] in volInfo:
                volInfo[item["fundcode"]] = volInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                volInfo[item["fundcode"]] = float(item["fundvol"])

        for k, v in volInfo.items():
            print(str(k) + " : " + str(v))

        lastVolInfo = {}
        for item in lastJsonObject[0]:
            if item["fundcode"] in lastVolInfo:
                lastVolInfo[item["fundcode"]] = lastVolInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                lastVolInfo[item["fundcode"]] = float(item["fundvol"])

        for k, v in lastVolInfo.items():
            print(str(k) + " : " + str(v))

        newVolInfo = {}
        for k, v in volInfo.items():
            if k in volInfo and k not in lastVolInfo:
                newVolInfo[k] = volInfo[k]
            elif k not in volInfo and k in lastVolInfo:
                newVolInfo[k] = 0 - lastVolInfo[k]
            else:
                newVolInfo[k] = volInfo[k] - lastVolInfo.get(k, 0)

        filtered_vol_info = {}
        for k, v in newVolInfo.items():
            if isinstance(v, (int, float)) and v != 0.0:  # 只包含份额变化不为0的基金
                filtered_vol_info[k] = v

        filtered_vol_info["description"] = "no processed"
        filtered_vol_info["date"] = peter1.date
        if custno:
            filtered_vol_info["custno"] = actual_custno

        return jsonify(filtered_vol_info)

    # 获取指定日期的基金数据
    @app.route('/api/funds/by-date', methods=['GET', 'POST'])
    @login_required
    def get_funds_by_date():
        from app.models import JsonString

        str_date = request.args.get("date")
        if not str_date:
            return jsonify({"error": "日期参数不能为空"}), 400

        peter1 = JsonString.query.filter_by(date = str_date).first()
        if not peter1:
            return jsonify({"error": f"未找到日期 {str_date} 的数据"}), 404

        jsonObject = json.loads(peter1.jsonString)

        navInfo = {}
        for item in jsonObject[0]:
            navInfo[item["fundcode"]] = float(item["nav"])

        volInfo = {}
        for item in jsonObject[0]:
            if item["fundcode"] in volInfo:
                volInfo[item["fundcode"]] = volInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                volInfo[item["fundcode"]] = float(item["fundvol"])

        volInfo["description"] = "special date"
        volInfo["date"] = peter1.date

        return jsonify(volInfo)

    # 获取日期范围的基金数据对比
    @app.route('/api/funds/compare', methods=['GET', 'POST'])
    @login_required
    def compare_funds_by_date_range():
        from app.models import JsonString

        str_datef = request.args.get("datef")
        str_datet = request.args.get("datet")
        
        if not str_datef or not str_datet:
            return jsonify({"error": "开始日期和结束日期参数不能为空"}), 400

        peter1 = JsonString.query.filter_by(date = str_datet).first()
        lastpeter1 = JsonString.query.filter_by(date = str_datef).first()
        
        if not peter1 or not lastpeter1:
            return jsonify({"error": "未找到指定日期的数据"}), 404

        jsonObject = json.loads(peter1.jsonString)
        lastJsonObject = json.loads(lastpeter1.jsonString)

        navInfo = {}
        for item in jsonObject[0]:
            navInfo[item["fundcode"]] = float(item["nav"])

        volInfo = {}
        for item in jsonObject[0]:
            if item["fundcode"] in volInfo:
                volInfo[item["fundcode"]] = volInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                volInfo[item["fundcode"]] = float(item["fundvol"])

        lastVolInfo = {}
        for item in lastJsonObject[0]:
            if item["fundcode"] in lastVolInfo:
                lastVolInfo[item["fundcode"]] = lastVolInfo[item["fundcode"]] + float(item["fundvol"])
            else:
                lastVolInfo[item["fundcode"]] = float(item["fundvol"])

        newVolInfo = {}
        for k, v in volInfo.items():
            if k in volInfo and k not in lastVolInfo:
                newVolInfo[k] = volInfo[k]
            elif k not in volInfo and k in lastVolInfo:
                newVolInfo[k] = 0 - lastVolInfo[k]
            else:
                newVolInfo[k] = volInfo[k] - lastVolInfo[k]

        amoutInfo = {}
        for k, v in newVolInfo.items():
            if v != 0.0:  # 只包含份额变化不为0的基金
                amoutInfo[k] = v * navInfo[k]

        amoutInfo["description"] = "arbitrarily / no processed amount : vol"
        amoutInfo["date"] = peter1.date
        amoutInfo["amountInfo"] = {k: v for k, v in newVolInfo.items() if v != 0.0}  # 过滤amountInfo中的0值

        return jsonify(amoutInfo)

    # 手动触发数据获取
    @app.route('/api/funds/refresh', methods=['GET', 'POST'])
    @login_required
    def refresh_fund_data():
        from app.models import JsonString
        # Get all custnos in the database
        custnos_in_db = [row[0] for row in db.session.query(JsonString.custno).distinct().all()]
        # Get latest date for each custno
        latest_dates = {}
        for custno in custnos_in_db:
            latest = db.session.query(JsonString).filter_by(custno=custno).order_by(JsonString.date.desc()).first()
            latest_dates[custno] = latest.date if latest else None
        # Get requested custno
        custno = request.args.get('custno') or request.form.get('custno')
        if custno:
            fetch_and_store_fund_data_for_custnos([custno])
            fetch_result = f"已获取 {custno} 的最新数据"
        else:
            # Get default custnos from environment variable
            default_custnos = os.environ.get('DEFAULT_CUSTNOS', 'custno1,custno2').split(',')
            fetch_and_store_fund_data_for_custnos(custnos_in_db if custnos_in_db else default_custnos)
            fetch_result = "已获取全部 custno 的最新数据"
        return jsonify({
            "latest_dates": latest_dates,
            "fetch_result": fetch_result,
            "timestamp": datetime.now().isoformat()
        })

    # 简化的刷新路由
    @app.route('/refresh', methods=['GET', 'POST'])
    @login_required
    def refresh_fund_data_simple():
        return refresh_fund_data()

    migrate = Migrate(app,db)

    from app import models

    # db.app = app

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        from app.models import User
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and pbkdf2_sha256.verify(password, user.password_hash):
                login_user(user)
                return render_template('index.html')
            else:
                return render_template('login.html', error='Invalid username or password')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return render_template('login.html', error='Logged out')

    @app.route('/changes')
    @login_required
    def changes():
        return render_template('changes.html')

    @app.route('/demo')
    @login_required
    def demo():
        return render_template('demo.html')

    @app.route('/by-date')
    @login_required
    def by_date():
        return render_template('by_date.html')

    @app.route('/compare')
    @login_required
    def compare():
        return render_template('compare.html')

    @app.route('/refresh')
    @login_required
    def refresh():
        return render_template('refresh.html')

    return app

# @aps.task('cron', id='job1', day='*', hour='14', minute='46', second='00')
def fetch_and_store_fund_data(a, b):                          # 运行的定时任务的函数
    from app.models import JsonString
    from app.models import Employee
    import os
    from os.path import join, dirname
    from app import create_app
    from datetime import datetime

    log_msg = f"[APScheduler job1] Executed at {datetime.now()}\n"
    print("==== APScheduler job1 (fetch_and_store_fund_data) START ====")
    print(log_msg.strip())
    with open("apscheduler_job1.log", "a") as f:
        f.write(log_msg)

    if not lock.acquire(False):
        print("------------------skip-job1--------------------")
        return

    config_name = os.getenv('FLASK_CONFIG')
    app = create_app(config_name)

    with app.app_context():
        print("send request +++")
        # Get custnos from environment variable
        custnos = os.environ.get('DEFAULT_CUSTNOS', 'custno1,custno2').split(',')
        # Add more custno as needed
        for custno in custnos:
            # Get API URL from environment variable
            api_url = os.environ.get('FUND_API_URL', 'https://example.com/api/getAssetsListNew')
            url = f"{api_url}?custno={custno}"
            r = requests.get(url)
            print(f"send request for custno {custno} ---")

            DOMTree = xml.dom.minidom.parseString(r.text.encode("raw_unicode_escape").decode("raw_unicode_escape").encode("utf8")).documentElement.getElementsByTagName("return")

            tz = pytz.timezone('Asia/Shanghai')
            nowdate = datetime.now(tz).strftime('%Y%m%d')
            data2 = json.loads(DOMTree[0].childNodes[0].data)
            print(f"get date --- and construct jsonstring for custno {custno} +++")
            jsonString = JsonString(date=nowdate, navdate=data2[0][0]["navdate"], jsonString=DOMTree[0].childNodes[0].data, custno=custno)

            db.session.add(jsonString)
            db.session.commit()

            print(f"add and commit for custno {custno} ---")

    lock.release()

    print("==== APScheduler job1 (fetch_and_store_fund_data) END ====")


def demo_task_one(var_one, var_two):
    """Demo job function.
    :param var_two:
    :param var_two:
    """
    # print(str(var_one) + " " + str(var_two))
    p = 1

def job3(var_one, var_two):
    """Demo job function.
    :param var_two:
    :param var_two:
    """
    print("str(var_one) + " " + str(var_two)")

def fetch_and_store_fund_data_for_custnos(custnos):
    from app.models import JsonString
    import os
    from os.path import join, dirname
    from app import create_app
    from datetime import datetime
    tz = pytz.timezone('Asia/Shanghai')
    nowdate = datetime.now(tz).strftime('%Y%m%d')
    # Get API URL from environment variable
    api_url = os.environ.get('FUND_API_URL', 'https://example.com/api/getAssetsListNew')
    for custno in custnos:
        url = f"{api_url}?custno={custno}"
        r = requests.get(url)
        DOMTree = xml.dom.minidom.parseString(r.text.encode("raw_unicode_escape").decode("raw_unicode_escape").encode("utf8")).documentElement.getElementsByTagName("return")
        data2 = json.loads(DOMTree[0].childNodes[0].data)
        jsonString = JsonString(date=nowdate, navdate=data2[0][0]["navdate"], jsonString=DOMTree[0].childNodes[0].data, custno=custno)
        db.session.add(jsonString)
        db.session.commit()