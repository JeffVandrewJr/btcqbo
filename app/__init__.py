from flask import Flask
from flask_bootstrap import Bootstrap
from configuration import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
