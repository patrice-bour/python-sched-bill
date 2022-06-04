from flask import Flask, g
import logging
from . import config
from . import errors
from . import views
from . import log
from db import get_db
from scheduler import get_scheduler


def create_app(config_class=config.DevelopmentConfiguration):
    """Boilerplate for the Flask application"""

    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        log.init()
        logger = logging.getLogger()
        logger.debug('Configuration loaded')
        errors.load()
        logger.debug('Errors handlers loaded')
        get_db()
        logger.debug('Database connected')
        app_scheduler = get_scheduler()
        app_scheduler.start()
        logger.debug('Scheduler initialized and started')
        views.load()
        logger.debug('Routes initialized')
        return app


if __name__ == '__main__':
    create_app(config.DevelopmentConfiguration)