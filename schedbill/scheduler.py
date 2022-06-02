from pytz import utc
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.events import EVENT_SCHEDULER_STARTED, EVENT_SCHEDULER_SHUTDOWN, EVENT_EXECUTOR_ADDED, \
    EVENT_EXECUTOR_REMOVED, EVENT_JOBSTORE_ADDED, EVENT_JOBSTORE_REMOVED, EVENT_JOB_ADDED, EVENT_JOB_REMOVED, \
    EVENT_JOB_MODIFIED, EVENT_JOB_SUBMITTED, EVENT_JOB_MAX_INSTANCES, EVENT_JOB_EXECUTED, EVENT_JOB_ERROR, \
    EVENT_JOB_MISSED
from flask import current_app, g
import logging
import config

logger = logging.getLogger()


def scheduler_hooks(event):
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


def load():
    """Setup the scheduler's configuration and start it"""

    job_stores = {
        'mongo': MongoDBJobStore()
    }

    executors = {
        'default': ThreadPoolExecutor(current_app.config.get('SCHEDULER_MAX_THREADS'))
    }

    job_defaults = {
        'coalesce': current_app.config.get('SCHEDULER_JOB_COALESCE'),
        'misfire_grace_time': current_app.config.get('SCHEDULER_MISFIRE_GRACE_TIME'),
        'max_instances': 1,
        'replace_existing': True
    }

    g.scheduler = BackgroundScheduler()

    g.scheduler.add_listener(scheduler_hooks, EVENT_SCHEDULER_STARTED | EVENT_SCHEDULER_SHUTDOWN |
                             EVENT_EXECUTOR_ADDED | EVENT_EXECUTOR_REMOVED | EVENT_JOBSTORE_ADDED |
                             EVENT_JOBSTORE_REMOVED | EVENT_JOB_ADDED | EVENT_JOB_REMOVED | EVENT_JOB_MODIFIED |
                             EVENT_JOB_SUBMITTED | EVENT_JOB_MAX_INSTANCES | EVENT_JOB_EXECUTED |
                             EVENT_JOB_ERROR | EVENT_JOB_MISSED
                             )

    g.scheduler.configure(
        job_stores=job_stores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=current_app.config.get('SCHEDULER_TIMEZONE')
    )

    g.scheduler.start()
