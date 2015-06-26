from registry.config.defaults import LOG_CONF

# Disable CSRF for easier testing
WTF_CSRF_ENABLED = False

# App specific settings
LOG_CONF['loggers']['root']['level'] = 'DEBUG'

# Uncomment to have SQL statements and migration steps logged
# LOG_CONF['loggers']['sqlalchemy.engine'] = {
#     'level': 'DEBUG',
#     'handlers': ['stderr']
# }
# SQLALCHEMY_ECHO = True
# LOG_CONF['loggers']['alembic.migration'] = {
#     'level': 'ERROR',
#     'handlers': ['file'],
#     'propagate': False
# }
