from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
import logging
import os
from redis import Redis
import rq
import rq_dashboard

app = Flask(__name__)

if os.getenv('RQ_ACCESS') == 'True':
    app.config.from_object(rq_dashboard.default_settings)
app.config.from_object(Config)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('btcqbo', connection=app.redis)
bootstrap = Bootstrap(app)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)
app.logger.setLevel(logging.INFO)

from app import routes
