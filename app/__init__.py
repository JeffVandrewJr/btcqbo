from config import Config
from flask import Flask
from flask_apscheduler import APScheduler
from flask_bootstrap import Bootstrap
import logging
from redis import Redis

app = Flask(__name__)

app.config.from_object(Config)
app.redis = Redis.from_url(app.config['REDIS_URL'])
scheduler = APScheduler()
bootstrap = Bootstrap(app)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

from app import routes
