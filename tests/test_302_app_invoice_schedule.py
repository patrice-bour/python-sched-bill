import time
import flask_unittest
from flask import Flask
from fixtures.col import drop_collections
from schedbill import create_app, config, db, scheduler, timing
from schedbill.controllers import UserController, EMailController, InvoiceController
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


class InvoiceSchedulingTestApp(flask_unittest.AppTestCase):
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

    def create_invoice(self) -> None:
        """"""
        sender = UserController.create_user({
            'emailAddress': 'foobar@foo.bar',
            'firstName': 'Foo',
            'lastName': 'Bar',
        })

        recipient = UserController.create_user({
            'emailAddress': 'barfoo@bar.bar',
            'firstName': 'Bar',
            'lastName': 'Bar',
        })

        self.invoice = InvoiceController.create_invoice({
            'sender': sender.id,
            'recipient': recipient.id,
            'reference': 'Invoice IX',
            'periodicity': 10,  # seconds
            'notify': 'True',
            # 'notifyAt':  3600 * 8  # seconds since midnight (-1 = do not schedule) -- 08 AM here
            'notifyAt': 0
        })

    def test_generate_invoice(self, app: Flask) -> None:
        self.create_invoice()
        InvoiceController.generate_invoice(str(self.invoice.id))
        # try:
        #     sched_job = self.scheduler.get_job(str(self.invoice.id))
        #     self.assertEqual(timing.TimeCalc.arg_to_timestamp(sched_job.next_run_time), self.email.sendAt)
        # except Exception as exc:
        #     self.fail(f"exception when retrieving job id {self.email.id} : {exc}")
        pass