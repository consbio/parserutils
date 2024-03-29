import datetime

from dateutil import parser

from .numbers import is_number
from .strings import STRING_TYPES


DATE_TYPES = (datetime.date, datetime.datetime)


def parse_dates(d, default='today'):
    """ Parses one or more dates from d """

    if default == 'today':
        default = datetime.datetime.today()

    if d is None:
        return default

    elif isinstance(d, DATE_TYPES):
        return d

    elif is_number(d):
        # Treat as milliseconds since 1970
        d = d if isinstance(d, float) else float(d)
        return datetime.datetime.utcfromtimestamp(d)

    elif not isinstance(d, STRING_TYPES):
        if hasattr(d, '__iter__'):
            return [parse_dates(s, default) for s in d]
        else:
            return default

    elif len(d) == 0:
        # Behaves like dateutil.parser < version 2.5
        return default

    else:
        try:
            return parser.parse(d)
        except (AttributeError, ValueError):
            return default
