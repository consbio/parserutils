import unittest

from six import binary_type, text_type

from parserutils.numbers import is_number
from parserutils.strings import EMPTY_BIN, EMPTY_STR


class NumberTestCase(unittest.TestCase):

    def test_is_number(self):
        """ Tests is_number with general inputs """

        # Test invalid values with parameter that allows Booleans
        invalid = (None, EMPTY_BIN, EMPTY_STR, {}, [], float('+inf'), float('-inf'), float('nan'))
        for bad in invalid:
            self.assertFalse(is_number(bad, if_bool=True), '"{0}" is actually a number'.format(type(bad).__name__))

        # Test invalid values without parameter that allows Booleans
        invalid += (True, False)
        for bad in invalid:
            self.assertFalse(is_number(bad), '"{0}" is actually a number'.format(type(bad).__name__))

        # Test valid values without parameter that allows Booleans
        valid = (0, 1.1, binary_type('2'.encode()), text_type('3'), binary_type('4.4'.encode()), text_type('5.5'))
        for num in valid:
            self.assertTrue(is_number(num), '"{0}" is not a number'.format(type(num).__name__))

        # Test valid values with parameter that allows Booleans
        valid += (True, False)
        for num in valid:
            self.assertTrue(is_number(num, if_bool=True), '"{0}" is not a number'.format(type(num).__name__))
