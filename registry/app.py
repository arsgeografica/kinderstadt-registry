import logging
import logging.handlers
import os.path
from flask import Flask
from registry.extensions import db, migrate
from registry import __version__
from registry import models
from registry import views
from registry.views import desk


def setup_logging(app):
    formatter = logging.Formatter(app.config['LOG_FORMAT'])
    app.debug_log_format = app.config['LOG_FORMAT']

    if app.config.get('LOG_FILE'):
        file_handler = logging.handlers.RotatingFileHandler(
                        filename=app.config['LOG_FILE'],
                        maxBytes=app.config['LOG_FILE_MAX_BYTES'],
                        backupCount=app.config['LOG_FILE_BACKUP_COUNT'])
        file_handler.setFormatter(formatter)
        file_handler.setLevel(app.config['LOG_FILE_LOG_LEVEL'])
        app.logger.addHandler(file_handler)

    app.logger.setLevel(app.config['LOG_LEVEL'])


def factory(config=None):

    app = Flask(__name__.split('.')[0])

    app.config.from_object('registry.config.defaults')
    if config:
        app.config.from_object(config)

    setup_logging(app)

    @app.context_processor
    def inject_version():
        return dict(__version__=__version__)

    db.init_app(app)
    migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'migrations')
    migrate.init_app(app, db, directory=migrations_dir)

    app.add_url_rule('/', 'home', views.home)
    app.add_url_rule('/desk', 'desk.home', desk.home, methods=['GET', 'POST'])
    app.add_url_rule('/desk/<int:pass_id>/activate', 'desk.activate',
                     desk.activate, methods=['GET', 'POST'])
    app.add_url_rule('/desk/<int:pass_id>', 'desk.passport', desk.passport,
                     methods=['GET', 'POST'])

    return app
