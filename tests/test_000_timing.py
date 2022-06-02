import flask_unittest
from schedbill import create_app, config
from flask import Flask
from datetime import datetime
from dateutil.parser import *
import pytz
from timing import TimeCalc


class MyTestCase(flask_unittest.AppTestCase):

    def create_app(self):
        app = create_app(config.TestingConfiguration)
        with app.app_context():
            yield app

    @classmethod
    def setUpClass(cls) -> None:
        cls.locale_test_string = '2022-06-01 18:10:00'
        cls.locale_test_date = parse(cls.locale_test_string)
        cls.system_test_date = cls.locale_test_date.astimezone(pytz.timezone('utc'))
        cls.locale_test_timestamp = cls.locale_test_date.timestamp()
        cls.system_test_timestamp = cls.system_test_date.timestamp()

    def test_convert_to_human(self, app: Flask) -> None:
        self.assertEqual(
            self.__class__.locale_test_string,
            TimeCalc.convert_to_human(self.__class__.locale_test_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        )

        self.assertEqual(
            self.__class__.locale_test_string,
            TimeCalc.convert_to_human(self.__class__.system_test_timestamp).strftime('%Y-%m-%d %H:%M:%S')
        )

    def test_convert_to_store(self, app: Flask) -> None:
        self.assertEqual(
            self.__class__.system_test_timestamp,
            TimeCalc.convert_to_store(self.__class__.locale_test_string)
        )