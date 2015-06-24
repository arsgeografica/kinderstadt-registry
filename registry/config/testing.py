import logging

# App specific settings
LOG_LEVEL = logging.DEBUG
SQLALCHEMY_ECHO = True

# Disable CSRF for easier testing
WTF_CSRF_ENABLED = False
