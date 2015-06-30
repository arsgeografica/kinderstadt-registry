import datetime
import logging.config
import logging.handlers
import os.path
from flask import Flask
from registry.extensions import db, migrate
from registry import __version__
from registry import models
from registry import views
from registry.views import desk


def check_flags(app):
    flags = app.config.get('FLAGS', {})
    for key, config in flags.items():
        if 'label' not in config:
            raise ValueError('No label in FLAG config')
        cci = ('can_checkin' in config and config['can_checkin'] == False)
        cco = ('can_checkout' in config and config['can_checkout'] == False)
        if not (cci or cco):
            raise ValueError('can_checkin or can_checkout must be False')


def check_event_duration(app):
    event_from = app.config['EVENT_FROM']
    assert isinstance(event_from, datetime.date)
    event_to = app.config['EVENT_TO']
    assert isinstance(event_to, datetime.date)


def factory(config=None):
    app = Flask(__name__.split('.')[0])

    app.config.from_object('registry.config.defaults')
    if config:
        app.config.from_object(config)

    logging.config.dictConfig(app.config['LOG_CONF'])

    check_flags(app)

    @app.context_processor
    def inject_version():
        return dict(__version__=__version__)

    db.init_app(app)
    migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'migrations')
    migrate.init_app(app, db, directory=migrations_dir)

    app.add_url_rule('/', 'home', views.home)
    app.add_url_rule('/desk', 'desk.home', desk.home, methods=['GET', 'POST'])
    app.add_url_rule('/desk/current', 'desk.current', desk.current)
    app.add_url_rule('/desk/<int:pass_id>/activate', 'desk.activate',
                     desk.activate, methods=['GET', 'POST'])
    app.add_url_rule('/desk/<int:pass_id>', 'desk.passport', desk.passport,
                     methods=['GET', 'POST'])
    app.add_url_rule('/desk/<int:pass_id>/confirm/<action>',
                     'desk.confirm_transaction', desk.confirm_transaction,
                     methods=['GET', 'POST'])
    app.add_url_rule('/desk/<int:pass_id>/edit', 'desk.edit', desk.edit,
                     methods=['GET', 'POST'])
    return app
