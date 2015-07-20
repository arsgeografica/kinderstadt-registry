import datetime
import logging.config
import logging.handlers
import os.path
from flask import Flask
from registry.extensions import db, migrate
from registry import __version__
from registry import models
from registry import views
from registry.views import chart, passport


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
        apc = models.Passport.active_passes().count()
        return dict(
            active_passport_count=apc,
            __version__=__version__)

    db.init_app(app)
    migrations_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  'migrations')
    migrate.init_app(app, db, directory=migrations_dir)

    app.add_url_rule('/',
                     'home',
                     views.home)
    app.add_url_rule('/passport',
                     'passport.home',
                     passport.home,
                     methods=['GET', 'POST'])
    app.add_url_rule('/passport/query',
                     'passport.query',
                     passport.query,
                     methods=['POST'])
    app.add_url_rule('/passport/current',
                     'passport.current',
                     passport.current)
    app.add_url_rule('/passport/current/sweep',
                     'passport.sweep',
                     passport.sweep,
                     methods=['GET', 'POST'])
    app.add_url_rule('/passport/<int:pass_id>/activate',
                     'passport.activate',
                     passport.activate,
                     methods=['GET', 'POST'])
    app.add_url_rule('/passport/<int:pass_id>',
                     'passport.passport',
                     passport.passport,
                     methods=['GET', 'POST'])
    app.add_url_rule('/passport/<int:pass_id>/confirm/<action>',
                     'passport.confirm_transaction',
                     passport.confirm_transaction,
                     methods=['GET', 'POST'])
    app.add_url_rule('/passport/<int:pass_id>/edit',
                     'passport.edit',
                     passport.edit,
                     methods=['GET', 'POST'])
    app.add_url_rule('/chart/',
                     'chart.chart',
                     chart.chart)

    return app
