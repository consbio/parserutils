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

        # Test values that should come back unchanged
        for val in (None, today, now):
            self.assertEqual(parse_dates(val), val)

        # Test values that produce a datetime of today
        for val in (EMPTY_BIN, EMPTY_STR):
            self.assertEqual(parse_dates(val).date(), today.date())

        # Ensure that numbers produce datetimes
        for val in (0, 1.1, binary_type('2'.encode()), text_type('3'), binary_type('4.4'.encode()), text_type('5.5')):
            self.assertEqual(type(parse_dates(val)), type(now))


if __name__ == '__main__':
    unittest.main()
