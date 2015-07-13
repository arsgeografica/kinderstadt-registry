from path import Path
import datetime


_BASE_DIR = Path(__file__).abspath().dirname().dirname()

SECRET_KEY = '5m34a58x(3^$np08v!si#!a1btp$(h$a0qa-j_c)^!-ah=ypqs'

# Database settings
SQLALCHEMY_DATABASE_URI = 'postgresql://kinderstadt@localhost/registry?client_encoding=utf8'

# Logging settings
LOG_CONF = {
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(name)s - %(levelname)s @ %(asctime)s] %(message)s'
        }
    },
    'handlers': {
        'stdout': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stdout'
        },
        'stderr': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': 'ext://sys.stderr'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'default',
            'filename': _BASE_DIR / '../registry.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5
        }
    },
    'loggers': {
        'root': {
            'level': 'WARN',
            'handlers': ['stderr', 'file']
        }
    }
}

# Flags settings
FLAGS = {
    'disabled': {
        'label': 'Gesperrt',
        'can_checkin': False
    },
    'pickup': {
        'label': 'Abholung erforderlich',
        'can_checkout': False
    }
}

START_DATE = datetime.date.today() - datetime.timedelta(days=3)
END_DATE = datetime.date.today() + datetime.timedelta(days=3)
