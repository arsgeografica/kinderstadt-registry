from flask.ext.migrate import Migrate
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()
migrate = Migrate()
