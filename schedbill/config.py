"""Flask configuration."""
from dotenv import load_dotenv
from os import environ, path
import pytz

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
    APP_TIMEZONE = pytz.timezone('Europe/Paris')
    DB_HOST = 'cluster0.xdxzo.mongodb.net'
    DB_USER = environ.get('DB_USER')
    DB_SECRET = environ.get('DB_PASSWORD')
    DB_NAME = 'intiaDevDB'
    DB_URI_FORMAT = 'mongodb+srv://{user}:{secret}@{host}/{db}?retryWrites=true&w=majority'
    SCHEDULER_MAX_THREADS = 20
    # False = missed executions can lead to multiple executions in a row later on. True = only one execution anyway.
    SCHEDULER_JOB_COALESCE = True
    SCHEDULER_MISFIRE_GRACE_TIME = None  # Run the late job no matter how late it is
    SCHEDULER_TIMEZONE = pytz.utc


class ProductionConfiguration(Configuration):
    """Configuration for the production environment"""
    DB_NAME = 'intiaProdDB'


class DevelopmentConfiguration(Configuration):
    """Configuration for the development environment"""
    Configuration.LOG_CONFIG['root']['level'] = 'DEBUG'
    DB_NAME = 'intiaDevDB'
    SCHEDULER_MAX_THREADS = 5


class TestingConfiguration(Configuration):
    """Configuration for the development environment"""
    Configuration.LOG_CONFIG['root']['level'] = 'DEBUG'
    DB_NAME = 'intiaTestDB'
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
                'filename': path.join(app_dir, 'var/log/schedbill_testing.log'),
                'when': 'midnight',
                'interval': 1,
                'backupCount': 5
            }
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['schedbill_logfile'],
            'propagate': True
        }
    }
    SCHEDULER_MAX_THREADS = 5
