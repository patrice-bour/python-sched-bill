"""Flask configuration."""
from dotenv import load_dotenv
from os import environ, path

app_dir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(app_dir, '.env'))


class Configuration:
    """Default Configuration"""

    LOG_CONFIG = {
        'version': 1,
        'formatters': {
            'default': {
                'format': '[%(asctime)s] %(levelname)s (%(module)s) : %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default'
            },
            'schedbill_logfile': {
                'class': 'logging.handlers.TimedRotatingFileHandler',
                'formatter': 'default',
                'filename': path.join(app_dir, 'var/log/schedbill.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 5
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console', 'schedbill_logfile'],
            'propagate': True
        }
    }
    DB_HOST = 'cluster0.xdxzo.mongodb.net'
    DB_USER = environ.get('DB_USER')
    DB_SECRET = environ.get('DB_PASSWORD')
    MONGO_URI = 'mongodb+srv://{}:{}@{}/?retryWrites=true&w=majority'.format(
        DB_USER,
        DB_SECRET,
        DB_HOST
    )


class ProductionConfiguration(Configuration):
    """Configuration for the production environment"""


class DevelopmentConfiguration(Configuration):
    """Configuration for the development environment"""
    Configuration.LOG_CONFIG['root']['level'] = 'DEBUG'
