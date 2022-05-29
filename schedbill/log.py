from flask import current_app
from logging.config import dictConfig


def init():
    """Configure logging using the Flak app context and configuration"""
    dictConfig(current_app.config.get('LOG_CONFIG', {}))
