from flask import current_app, g
from datetime import datetime
from dateutil.parser import *
from helpers import is_float
import pytz


class TimeCalc:
    """"""
    HUMAN_TZ = 'Europe/Paris'
    STORE_TZ = 'utc'

    @classmethod
    def convert_to_store(cls, date_arg):
        """Convert the date argument to a timestamp as stored in the system

        :param date_arg: a string representation of a date (could be a timestamp)
        :return: the corresponding timestamp
        """
        if str.isnumeric(str(date_arg)) or is_float(date_arg):
            return int(datetime.utcfromtimestamp(int(date_arg)).timestamp())  # Let's get rid of microseconds if any
        human_time = pytz.timezone(TimeCalc.HUMAN_TZ).localize(parse(date_arg))
        store_time = human_time.astimezone(pytz.timezone(TimeCalc.STORE_TZ))
        return store_time.timestamp()

    @classmethod
    def convert_to_human(cls, date_arg):
        """Convert the date argument to the timezone of the user

        :param date_arg: a string representation of a date (could be a timestamp)
        :return: the corresponding user's date
        """
        store_time = None
        if str.isnumeric(str(date_arg)) or is_float(date_arg):
            store_time = datetime.fromtimestamp(int(date_arg))  # Let's get rid of microseconds if any
        else:
            store_time = pytz.timezone(TimeCalc.STORE_TZ).localize(parse(date_arg))
        human_time = store_time.astimezone(pytz.timezone(TimeCalc.HUMAN_TZ))
        return human_time
