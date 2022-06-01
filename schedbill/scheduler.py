from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app, g
import config


def load():
    """Setup the scheduler's configuration and start it"""

    job_stores = {
        'mongo': MongoDBJobStore()
    }

    executors = {
        'default': ThreadPoolExecutor(current_app.config.get('SCHEDULER_MAX_THREADS'))
    }

    job_defaults = {
        'coalesce': current_app.config.get('SCHEDULER_JOB_COALESCE')
    }

    g.scheduler = BackgroundScheduler()

    g.scheduler.configure(
        job_stores=job_stores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=current_app.config.get('SCHEDULER_TIMEZONE')
    )

    g.scheduler.start()
