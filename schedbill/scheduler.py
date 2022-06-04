from pytz import utc
from apscheduler.schedulers.background import BaseScheduler, BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import (
    SchedulerEvent, EVENT_SCHEDULER_STARTED, EVENT_SCHEDULER_SHUTDOWN, EVENT_EXECUTOR_ADDED, EVENT_EXECUTOR_REMOVED,
    EVENT_JOBSTORE_ADDED, EVENT_JOBSTORE_REMOVED, EVENT_JOB_ADDED, EVENT_JOB_REMOVED, EVENT_JOB_MODIFIED,
    EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, EVENT_JOB_MISSED
)
from flask import current_app, g
import logging
import config

logger = logging.getLogger()


def scheduler_hooks(event: SchedulerEvent) -> None:
    """Events listeners handlers"""
    handlers = {
        # class apscheduler.events.SchedulerEvent(code, alias=None)
        EVENT_SCHEDULER_STARTED: lambda: logger.info(
            f"Scheduler started : {event.code}"
        ),
        EVENT_SCHEDULER_SHUTDOWN: lambda: logger.info(
            f"Scheduler stopped : {event.code}"
        ),
        EVENT_EXECUTOR_ADDED: lambda: logger.info(
            f"Scheduler executor added : {event.alias} ({event.code})"
        ),
        EVENT_EXECUTOR_REMOVED: lambda: logger.info(
            f"Scheduler executor removed : {event.alias} ({event.code})"
        ),
        EVENT_JOBSTORE_ADDED: lambda: logger.info(
            f"Scheduler jobstore added : {event.alias} ({event.code})"
        ),
        EVENT_JOBSTORE_REMOVED: lambda: logger.info(
            f"Scheduler jobstore removed : {event.alias} ({event.code})"
        ),
        # class apscheduler.events.JobEvent(code, job_id, jobstore)
        EVENT_JOB_ADDED: lambda: logger.debug(
            f"Scheduler job {event.job_id} ({event.code}) added on jobstore {event.jobstore}"
        ),
        EVENT_JOB_REMOVED: lambda: logger.debug(
            f"Scheduler job {event.job_id} ({event.code}) removed from jobstore {event.jobstore}"
        ),
        EVENT_JOB_MODIFIED: lambda: logger.debug(
            f"Scheduler job {event.job_id} ({event.code}) modified on jobstore {event.jobstore}"
        ),
        # class apscheduler.events.JobSubmissionEvent(code, job_id, jobstore, scheduled_run_times)
        EVENT_JOB_SUBMITTED: lambda: logger.debug(
            f"Scheduler job {event.job_id} ({event.code}) submitted from jobstore {event.jobstore}"
        ),
        EVENT_JOB_MAX_INSTANCES: lambda: logger.error(
            f"""Scheduler job {event.job_id} ({event.code}) refused from executor on jobstore {event.jobstore}
            MAX instances reached"""
        ),
        # class apscheduler.events.JobExecutionEvent(code, job_id, jobstore, scheduled_run_time, retval=None,
        #                                            exception=None, traceback=None)
        EVENT_JOB_EXECUTED: lambda: logger.info(
            f"Scheduler job {event.job_id} ({event.code}) executed on jobstore {event.jobstore}"
        ),
        EVENT_JOB_ERROR: lambda: logger.error(
            f"Scheduler job {event.job_id} ({event.code}) on jobstore {event.jobstore} exception : {event.exception}"
        ),
        EVENT_JOB_MISSED: lambda: logger.error(
            f"""Scheduler job {event.job_id} ({event.code}) missed on jobstore {event.jobstore} 
            exception : {event.exception}"""
        ),
    }

    handlers.get(event.code, lambda : logger.warning(f"Unhandled event trapped : {event.code}"))()


def setup_scheduler(max_threads: int = 25, job_coalesce: bool = False, misfire_grace_time: int = 15,
                    timezone='Europe/Paris') -> BaseScheduler:
    """ Set the scheduler's configuration up and return it

    :param max_threads: maximum threads in a ThreadPoolExecutor
    :param job_coalesce: if False a same job won't be replayed several times if late
    :param misfire_grace_time: the grace time for a misfired job
    :param timezone: the timezone of the scheduler
    :return: the configured scheduler
    """

    job_stores = {
        'mongo': MongoDBJobStore()
    }

    executors = {
        'default': ThreadPoolExecutor(max_threads)
    }

    job_defaults = {
        'coalesce': job_coalesce,
        'misfire_grace_time': misfire_grace_time,
        'max_instances': 1,
        'replace_existing': True
    }

    app_scheduler = BackgroundScheduler()

    app_scheduler.add_listener(scheduler_hooks, EVENT_SCHEDULER_STARTED | EVENT_SCHEDULER_SHUTDOWN |
                           EVENT_EXECUTOR_ADDED | EVENT_EXECUTOR_REMOVED | EVENT_JOBSTORE_ADDED |
                           EVENT_JOBSTORE_REMOVED | EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED |
                           EVENT_JOB_SUBMITTED | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_EXECUTED |
                           EVENT_JOB_ERROR | EVENT_JOB_MISSED
                           )

    app_scheduler.configure(
        job_stores=job_stores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=timezone
    )

    return app_scheduler


def get_scheduler() -> BaseScheduler:
    """Register the scheduler's setup in flask.g or returns it if already existing

    :return: the scheduler
    """

    app_scheduler = getattr(g, 'app_scheduler', None)
    if app_scheduler is None:
        app_scheduler = g.scheduler = setup_scheduler(
                max_threads=current_app.config.get('SCHEDULER_MAX_THREADS'),
                job_coalesce=current_app.config.get('SCHEDULER_JOB_COALESCE'),
                misfire_grace_time=current_app.config.get('SCHEDULER_MISFIRE_GRACE_TIME'),
                timezone=current_app.config.get('SCHEDULER_TIMEZONE')
            )
    return app_scheduler
