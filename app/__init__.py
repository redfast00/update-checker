from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager
import os

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('UPDATE_CHECKER_SETTINGS', silent=True)
db = SQLAlchemy(app)
scheduler = BackgroundScheduler()

login_manager = LoginManager()
login_manager.init_app(app)

from app import models, scraper, views, tasks, forms, login, utils

if os.environ.get('WERKZEUG_RUN_MAIN'):
    scheduler.start()
