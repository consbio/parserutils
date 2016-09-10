import datetime
import unittest

from six import binary_type, text_type

from parserutils.dates import parse_dates
from parserutils.strings import EMPTY_BIN, EMPTY_STR


class DateTestCase(unittest.TestCase):

    def test_parse_dates(self):
        """ Tests parse_dates with general inputs """

        today = datetime.datetime.today()
        now = datetime.datetime.now()

        anonymous_obj = type('Anonymous', (), {})
        already_dates = (today, now)
        invalid_dates = (None, EMPTY_BIN, EMPTY_STR, 'not a date', anonymous_obj)
        parsing_dates = (
            0, 1.1, binary_type('2'.encode()), text_type('3'), binary_type('4.4'.encode()), text_type('5.5')
        )

        # Test values that should come back unchanged
        for val in already_dates:
            self.assertEqual(parse_dates(val), val)
            self.assertEqual(parse_dates(val, 'xxx'), val)

        # Test values that default to a datetime of today
        for val in invalid_dates:
            self.assertEqual(parse_dates(val).date(), today.date())
            self.assertEqual(parse_dates(val, 'xxx'), 'xxx')

        # Ensure that numbers produce datetimes
        for val in parsing_dates:
            self.assertEqual(type(parse_dates(val)), type(now))
            self.assertEqual(type(parse_dates(val, 'xxx')), type(now))

        # Test iterables with dates already parsed, with and without defaults
        self.assertEqual(parse_dates(already_dates), list(already_dates))
        self.assertEqual(parse_dates(already_dates, 'xxx'), list(already_dates))

        # Test iterables with invalid dates, with and without defaults
        self.assertEqual([d.date() for d in parse_dates(invalid_dates)], [today.date()] * len(invalid_dates))
        self.assertEqual(parse_dates(invalid_dates, 'xxx'), ['xxx'] * len(invalid_dates))

        # Test iterables with parsable dates, with and without defaults
        self.assertEqual([type(d) for d in parse_dates(parsing_dates)], [type(now)] * len(parsing_dates))
        self.assertEqual([type(d) for d in parse_dates(parsing_dates, 'xxx')], [type(now)] * len(parsing_dates))
