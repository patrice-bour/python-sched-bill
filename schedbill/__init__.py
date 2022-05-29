from flask import Flask
import logging
from . import config


def create_app(config_class=config.DevelopmentConfiguration):
    """Boilerplate for the Flask application"""

    app = Flask(__name__)
    app.config.from_object(config_class)

    with app.app_context():
        from . import log
        from . import db
        from . import views

        log.init()
        logger = logging.getLogger()
        logger.debug('Configuration loaded')
        db.get_db()
        logger.debug('Database connected')
        views.load()
        logger.debug('Routes initialized')

        return app


if __name__ == '__main__':
    create_app(config.DevelopmentConfiguration)