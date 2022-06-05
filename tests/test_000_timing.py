import unittest
from schedbill import create_app, config
from flask import Flask
from datetime import datetime, timezone, timedelta
from dateutil.parser import *
import pytz
from timing import TimeCalc


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.test_string_locale = '2022-06-01 18:10:00'
        cls.test_string_with_tz = '2022-06-01 18:10:00 +02:00'
        cls.test_string_utc = '2022-06-01 16:10:00 +00:00'
        cls.test_string_int_timestamp = '1654099800'
        cls.test_string_float_timestamp = '1654099800.000'
        cls.test_int_timestamp = 1654099800
        cls.test_float_timestamp = 1654099800.000
        cls.locale_time_delta = timedelta(hours=2)
        cls.est_time_delta = timedelta(hours=-5)
        cls.test_datetime_locale = datetime(2022, 6, 1, 18, 10, 0, tzinfo=timezone(cls.locale_time_delta))
        cls.test_datetime_utc = datetime(2022, 6, 1, 16, 10, 0, tzinfo=timezone.utc)
        cls.test_datetime_est = datetime(2022, 6, 1, 11, 10, 0, tzinfo=timezone(cls.est_time_delta))  # UTC - 5

    def test_datetime_arg_to_ts(self) -> None:
        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_datetime_locale)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_datetime_utc)
        )

    def test_numeric_arg_to_ts(self) -> None:
        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_int_timestamp)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_float_timestamp)
        )

    def test_string_arg_to_ts(self) -> None:
        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_string_locale)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_string_with_tz)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_string_utc)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_string_int_timestamp)
        )

        self.assertEqual(
            self.test_int_timestamp,
            TimeCalc.arg_to_timestamp(self.test_string_float_timestamp)
        )

    def test_timestamp_to_datetime(self):
        self.assertEqual(
            self.test_datetime_locale,
            TimeCalc.timestamp_to_datetime(self.test_int_timestamp)
        )

        self.assertEqual(
            self.test_datetime_utc,
            TimeCalc.timestamp_to_datetime(self.test_int_timestamp, tz='UTC')
        )

        self.assertEqual(
            self.test_datetime_est,
            TimeCalc.timestamp_to_datetime(self.test_int_timestamp, tz='EST')
        )