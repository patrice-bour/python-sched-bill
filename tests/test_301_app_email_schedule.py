import time
import flask_unittest
from flask import Flask
from fixtures.col import drop_collections
from schedbill import create_app, config, db, scheduler, timing
from schedbill.controllers import UserController, EMailController
import mongoengine
from apscheduler.events import (
    SchedulerEvent,
    EVENT_JOB_ADDED,
    EVENT_JOB_REMOVED,
    EVENT_JOB_MODIFIED,
    EVENT_JOB_SUBMITTED,
    EVENT_JOB_MAX_INSTANCES,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_ERROR,
    EVENT_JOB_MISSED
)
from datetime import datetime


class EMailSchedulingTestApp(flask_unittest.AppTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pass

    def create_app(self) -> None:
        app = create_app(config.TestingConfiguration)
        with app.app_context():
            self.db = db.get_db()
            self.raw_db = mongoengine.connection.get_db()
            self.scheduler = scheduler.get_scheduler()
            self.scheduler.start()
            yield app

    def setUp(self, app: Flask) -> None:
        def error_listener(event: SchedulerEvent) -> None:
            self.fail(f"Scheduler Error : {event.code} -- {event.job_id}")

        def job_listener(event: SchedulerEvent) -> None:
            received_events.append(event)

        drop_collections(self.raw_db)
        received_events: list[SchedulerEvent] = []

    def tearDown(self, app: Flask) -> None:
        pass

    def create_email(self, time_to_send) -> None:
        """"""
        user = UserController.create_user({
            'emailAddress': 'foobar@foo.bar',
            'firstName': 'Foo',
            'lastName': 'Bar',
        })

        self.email = EMailController.create_email({
            'sender': user.id,
            'recipient': 'customer@foobar.baz',
            'title': 'Test email',
            'content': 'Test content',
            'sendAt': time_to_send
        })

    def test_email_save_schedule(self, app: Flask):
        self.create_email(datetime.now().timestamp() + 10)
        try:
            sched_job = self.scheduler.get_job(str(self.email.id))
            self.assertEqual(timing.TimeCalc.arg_to_timestamp(sched_job.next_run_time), self.email.sendAt)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {self.email.id} : {exc}")

    def test_email_update_schedule(self, app: Flask):
        self.create_email(datetime.now().timestamp() + 20)
        try:
            sched_job = self.scheduler.get_job(str(self.email.id))
            self.assertEqual(timing.TimeCalc.arg_to_timestamp(sched_job.next_run_time), self.email.sendAt)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {self.email.id} : {exc}")

        email = EMailController.update_email(str(self.email.id), {"sendAt": datetime.now().timestamp() + 300})
        try:
            sched_job = self.scheduler.get_job(str(email.id))
            self.assertEqual(timing.TimeCalc.arg_to_timestamp(sched_job.next_run_time), email.sendAt)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {email.id} : {exc}")

        email = EMailController.update_email(str(email.id), {"sendAt": 0})
        try:
            sched_job = self.scheduler.get_job(str(email.id))
            self.assertIsNone(sched_job)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {email.id} : {exc}")

    def test_email_delete_schedule(self, app: Flask):
        self.create_email(datetime.now().timestamp() + 10)
        try:
            sched_job = self.scheduler.get_job(str(self.email.id))
            self.assertEqual(timing.TimeCalc.arg_to_timestamp(sched_job.next_run_time), self.email.sendAt)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {self.email.id} : {exc}")
        EMailController.delete_email(str(self.email.id))
        try:
            sched_job = self.scheduler.get_job(str(self.email.id))
            self.assertIsNone(sched_job)
        except Exception as exc:
            self.fail(f"exception when retrieving job id {self.email.id} : {exc}")