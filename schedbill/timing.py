from datetime import datetime
from dateutil.parser import parse
from helpers import is_float
import pytz


class TimeCalc:
    """This class provides class methods to ease timestamp and datetime conversions."""

    @classmethod
    def arg_to_timestamp(cls, date_arg):
        """Convert the argument to a timestamp, getting rid of microseconds if any

        :param date_arg: the date as a string or numeric, representing a parsable date or a timestamp
        :return: the timestamp representation of the date
        """

        if isinstance(date_arg, datetime):  # the argument is a datetime
            return int(date_arg.timestamp())
        elif isinstance(date_arg, str):
            if str.isnumeric(date_arg) :  # the argument is a string which represents a timestamp
                return int(date_arg)
            elif is_float(date_arg):  # the argument is a string which represents a timestamp with milliseconds
                return int(float(date_arg))
            else: # the argument is a string which has to represent a date and time
                dtfs = parse(date_arg)
                return int(dtfs.timestamp())
        elif is_float(date_arg):  # the argument is already a timestamp
            return int(date_arg)


    @classmethod
    def timestamp_to_datetime(cls, ts, tz='utc'):
        """Convert the timestamp argument to a datetime object with a timezone information

        :param ts: the timestamp to convert
        :param tz: the timezone to use for the conversion (default to UTC)
        :return: the datetime object representing the timestamp converted in the destination timezone
        """
        local_date = datetime.fromtimestamp(ts)
        target_tz = pytz.timezone(tz)
        return local_date.astimezone(target_tz)
