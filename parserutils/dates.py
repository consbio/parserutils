import datetime

from dateutil import parser
from six import binary_type, string_types

from parserutils.numbers import is_number
from parserutils.strings import EMPTY_BIN, EMPTY_STR


def parse_dates(d):
    """ Parses one or more dates from d """

    if d is None:
        return None
    elif isinstance(d, (datetime.date, datetime.datetime)):
        return d
    elif is_number(d):
        # Treat as milliseconds since 1970
        d = d if isinstance(d, float) else float(d)
        return datetime.datetime.utcfromtimestamp(d)
    elif not isinstance(d, (binary_type, string_types)):
        # Assume more than one date for parsing
        return [parse_dates(s) for s in d]
    elif d in {EMPTY_BIN, EMPTY_STR}:
        # Behaves like dateutil.parser < version 2.5
        return datetime.datetime.today()

    try:
        return parser.parse(d)
    except (AttributeError, ValueError):
        return None
