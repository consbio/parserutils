import datetime
import unittest

from ..dates import parse_dates


class DateTestCase(unittest.TestCase):

    def test_parse_dates(self):
        """ Tests parse_dates with general inputs """

        today = datetime.datetime.today()
        now = datetime.datetime.now()

        anonymous_obj = type('Anonymous', (), {})
        already_dates = (today, now)
        invalid_dates = (None, b'', '', 'not a date', anonymous_obj)
        parsing_dates = (0, 1.1, b'2', '3', b'4.4', '5.5')

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
