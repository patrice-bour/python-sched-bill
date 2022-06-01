from flask import Flask
import logging
from . import config
from . import errors
from . import db
from . import views
from . import log
from . import scheduler


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
        db.get_db()
        logger.debug('Database connected')
        views.load()
        logger.debug('Routes initialized')
        scheduler.load()
        logger.debug('Scheduler initialized and started')
        return app


if __name__ == '__main__':
    create_app(config.DevelopmentConfiguration)