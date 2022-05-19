import logging
from logging.config import dictConfig
from . import config
from flask import Flask
from flask_pymongo import PyMongo


def create_app():
    """Boilerplate for the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config.DevelopmentConfiguration)
    dictConfig(app.config.get('LOG_CONFIG', {}))
    log = logging.getLogger()
    log.debug('Configuration loaded.')

    mongo = PyMongo(app)
    log.debug('Database configuration loaded')

    @app.route('/')
    def home():
        return 'Working flask'

    return app
