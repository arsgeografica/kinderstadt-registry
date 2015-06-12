import logging
from path import Path


_BASE_DIR = Path(__file__).abspath().dirname().dirname()

SECRET_KEY = '5m34a58x(3^$np08v!si#!a1btp$(h$a0qa-j_c)^!-ah=ypqs'

# Database settings
SQLALCHEMY_DATABASE_URI = 'postgresql://kinderstadt@localhost/registry'

# Logging settings
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = logging.INFO
LOG_FILE = _BASE_DIR / '../registry.log'
LOG_FILE_MAX_BYTES = 10 * 1024*1024
LOG_FILE_BACKUP_COUNT = 5
LOG_FILE_LOG_LEVEL = LOG_LEVEL
