from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config
from redis import Redis
import rq
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)
app.redis = Redis.from_url(app.config['REDIS_URL'])
app.task_queue = rq.Queue('btcqbo', connection=app.redis)
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models

