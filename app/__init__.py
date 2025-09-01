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

    scheduler = APScheduler()                  # Instantiate APScheduler
    # it is also possible to enable the API directly
    scheduler.api_enabled = True
    scheduler.init_app(app)                    # Put the job list into flask
    scheduler.start()                          # Start the job list

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

    # Initialize database
    with app.app_context():
        try:
            # Create all database tables
            db.create_all()
            print("✅ Database tables created successfully")
        except Exception as e:
            print(f"⚠️  Database initialization warning: {e}")

    # Home page
    @app.route('/')
    @login_required
    def home():
        return render_template('index.html')

    # Health check
    @app.route('/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'service': 'fund-monitoring-system'
        })

    # Get today's fund changes (text format)
    @app.route('/api/funds/today-changes', methods=['GET', 'POST'])
    @login_required
    def get_today_fund_changes():
        from app.models import JsonString
        custno = request.args.get("custno")
        if not custno:
            return "Missing custno parameter", 400
            
        # Map frontend custno to actual custno
        actual_custno = map_frontend_custno_to_actual([custno])[0]
        
        # Find the latest record
        peter1 = JsonString.query.filter_by(custno=actual_custno).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
        if not peter1:
            return "No data for this custno", 404
        # Find the previous record with a different date
        lastpeter1 = JsonString.query.filter(JsonString.custno==actual_custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
        if not lastpeter1:
            return f"No valid comparison data: could not find data before {peter1.date}"
        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return "Fund data format error", 500
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
        result_string = f'Fund share changes (custno={custno})\nDate comparison: {peter1.date} vs {lastpeter1.date}\n'
        for k, v in newVolInfo.items():
            if v != 0.0:
                result_string = result_string + f"{k}: Share change {v}, Amount change {v * navInfo[k]}\n"
        if result_string == f'Fund share changes (custno={custno})\nDate comparison: {peter1.date} vs {lastpeter1.date}\n':
            result_string += "No fund changes today"
        return result_string

    # Get fund net asset value changes (processed, JSON format)
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
                return jsonify({"error": f"Customer {custno} has no data"}), 404
            
            # Find the previous record with a different date for this custno
            lastpeter1 = JsonString.query.filter(JsonString.custno==actual_custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not lastpeter1:
                return jsonify({"error": f"Customer {custno} has no valid comparison data: could not find data before {peter1.date}"}), 404
        else:
            # Check if there is data
            max_id = db.session.query(func.max(JsonString.id)).scalar()
            if not max_id:
                return jsonify({"error": "No fund data available, please run the data fetching task first"}), 404

            peter1 = JsonString.query.filter_by(id=max_id).first()
            if not peter1:
                return jsonify({"error": "Unable to get latest fund data"}), 404

            # Check if there is previous day's data
            if max_id <= 1:
                return jsonify({"error": "Not enough historical data for comparison"}), 404

            lastpeter1 = JsonString.query.filter_by(id=max_id - 1).first()
            if not lastpeter1:
                return jsonify({"error": "Unable to get historical fund data"}), 404

        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return jsonify({"error": "Fund data format error"}), 500

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
            if v != 0.0:  # Only include funds with non-zero share changes
                returnVolInfo[k] = v * navInfo[k]

        returnVolInfo["description"] = "processed"
        returnVolInfo["date"] = peter1.date
        if custno:
            returnVolInfo["custno"] = actual_custno

        return jsonify(returnVolInfo)

    # Get fund net asset value changes (unprocessed, JSON format)
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

        # Initialize max_id
        max_id = db.session.query(func.max(JsonString.id)).scalar()
        if not max_id:
            return jsonify({"error": "No fund data available, please run the data fetching task first"}), 404

        # Query data for specific custno if provided, otherwise get any latest data
        if custno:
            # Convert frontend custno to actual custno
            actual_custno = map_frontend_custno_to_actual([custno])[0]
            # Find the latest record for this custno
            peter1 = JsonString.query.filter_by(custno=actual_custno).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not peter1:
                return jsonify({"error": f"Customer {custno} has no data"}), 404
            
            # Find the previous record with a different date for this custno
            lastpeter1 = JsonString.query.filter(JsonString.custno==actual_custno, JsonString.date < peter1.date).order_by(JsonString.date.desc(), JsonString.id.desc()).first()
            if not lastpeter1:
                return jsonify({"error": f"Customer {custno} has no valid comparison data: could not find data before {peter1.date}"}), 404
        else:
            peter1 = JsonString.query.filter_by(id=max_id).first()
            if not peter1:
                return jsonify({"error": "Unable to get latest fund data"}), 404

            # Check if there is previous day's data
            if max_id <= 1:
                return jsonify({"error": "Not enough historical data for comparison"}), 404

            lastpeter1 = JsonString.query.filter_by(id=max_id - 1).first()
            if not lastpeter1:
                return jsonify({"error": "Unable to get historical fund data"}), 404

        print("max id - 1  : " + str(max_id - 1))

        try:
            jsonObject = json.loads(peter1.jsonString)
            lastJsonObject = json.loads(lastpeter1.jsonString)
        except json.JSONDecodeError:
            return jsonify({"error": "Fund data format error"}), 500

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
            if isinstance(v, (int, float)) and v != 0.0:  # Only include funds with non-zero share changes
                filtered_vol_info[k] = v

        filtered_vol_info["description"] = "no processed"
        filtered_vol_info["date"] = peter1.date
        if custno:
            filtered_vol_info["custno"] = actual_custno

        return jsonify(filtered_vol_info)

    # Get fund data for a specific date
    @app.route('/api/funds/by-date', methods=['GET', 'POST'])
    @login_required
    def get_funds_by_date():
        from app.models import JsonString

        str_date = request.args.get("date")
        if not str_date:
            return jsonify({"error": "Date parameter cannot be empty"}), 400

        peter1 = JsonString.query.filter_by(date = str_date).first()
        if not peter1:
            return jsonify({"error": f"Data for date {str_date} not found"}), 404

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

    # Get fund data comparison for a date range
    @app.route('/api/funds/compare', methods=['GET', 'POST'])
    @login_required
    def compare_funds_by_date_range():
        from app.models import JsonString

        str_datef = request.args.get("datef")
        str_datet = request.args.get("datet")
        
        if not str_datef or not str_datet:
            return jsonify({"error": "Start date and end date parameters cannot be empty"}), 400

        peter1 = JsonString.query.filter_by(date = str_datet).first()
        lastpeter1 = JsonString.query.filter_by(date = str_datef).first()
        
        if not peter1 or not lastpeter1:
            return jsonify({"error": "Data for the specified dates not found"}), 404

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
            if v != 0.0:  # Only include funds with non-zero share changes
                amoutInfo[k] = v * navInfo[k]

        amoutInfo["description"] = "arbitrarily / no processed amount : vol"
        amoutInfo["date"] = peter1.date
        amoutInfo["amountInfo"] = {k: v for k, v in newVolInfo.items() if v != 0.0}  # Filter 0 values in amountInfo

        return jsonify(amoutInfo)

    # Manually trigger data fetching
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
            fetch_result = f"Got latest data for {custno}"
        else:
            # Get default custnos from environment variable
            default_custnos = os.environ.get('DEFAULT_CUSTNOS', 'custno1,custno2').split(',')
            fetch_and_store_fund_data_for_custnos(custnos_in_db if custnos_in_db else default_custnos)
            fetch_result = "Got latest data for all custno"
        return jsonify({
            "latest_dates": latest_dates,
            "fetch_result": fetch_result,
            "timestamp": datetime.now().isoformat()
        })

    # Simplified refresh route
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
def fetch_and_store_fund_data(a, b):                          # Function to run the scheduled task
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
        
        # Check if DOMTree has elements before accessing
        if not DOMTree or len(DOMTree) == 0:
            print(f"Warning: No data received for custno {custno}")
            continue
            
        # Check if DOMTree[0] has child nodes
        if not DOMTree[0].hasChildNodes():
            print(f"Warning: No child nodes in response for custno {custno}")
            continue
            
        try:
            data2 = json.loads(DOMTree[0].childNodes[0].data)
            # Check if data2 has the expected structure
            if not data2 or len(data2) == 0 or len(data2[0]) == 0 or "navdate" not in data2[0][0]:
                print(f"Warning: Unexpected data structure for custno {custno}")
                continue
                
            jsonString = JsonString(date=nowdate, navdate=data2[0][0]["navdate"], jsonString=DOMTree[0].childNodes[0].data, custno=custno)
            db.session.add(jsonString)
            db.session.commit()
        except (IndexError, KeyError, json.JSONDecodeError) as e:
            print(f"Error processing data for custno {custno}: {str(e)}")
            continue
