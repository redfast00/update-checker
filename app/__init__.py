from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from flask_login import LoginManager
import os
from logging.handlers import RotatingFileHandler
from logging import StreamHandler

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('UPDATE_CHECKER_SETTINGS', silent=True)

handler = RotatingFileHandler(app.config["LOG_FILE"], maxBytes=10000, backupCount=1)
app.logger.setLevel(app.config["LOG_LEVEL"])
app.logger.addHandler(handler)
streamer = StreamHandler()
app.logger.addHandler(handler)

db = SQLAlchemy(app)
scheduler = BackgroundScheduler()

login_manager = LoginManager()
login_manager.init_app(app)

from app import models, scraper, views, tasks, forms, login, utils

if os.environ.get('WERKZEUG_RUN_MAIN') or not app.debug:
    app.logger.info("Scheduler started")
    scheduler.start()
else:
    app.logger.warning("Scheduler not started")
