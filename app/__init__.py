import os
from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from redis import Redis
from flask_httpauth import HTTPBasicAuth
import rq
import rq_dashboard

app = Flask(__name__)
auth = HTTPBasicAuth()

if os.getenv('RQ_ACCESS') == 'True':
    app.config.from_object(rq_dashboard.default_settings)
# after rq blueprint registers, override config to the app's config
app.config.from_object(Config)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('btcqbo', connection=app.redis)
bootstrap = Bootstrap(app)

from app import routes
