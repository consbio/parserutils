import unittest

from ..numbers import is_number


class NumberTestCase(unittest.TestCase):

    def test_is_number(self):
        """ Tests is_number with general inputs """

        # Test invalid values with parameter that allows Booleans
        invalid = (None, b'', '', {}, [], float('+inf'), float('-inf'), float('nan'))
        for bad in invalid:
            self.assertFalse(is_number(bad, if_bool=True), '"{0}" is actually a number'.format(type(bad).__name__))

        # Test invalid values without parameter that allows Booleans
        invalid += (True, False)
        for bad in invalid:
            self.assertFalse(is_number(bad), '"{0}" is actually a number'.format(type(bad).__name__))

        # Test valid values without parameter that allows Booleans
        valid = (0, 1.1, b'2', '3', b'4.4', '5.5')
        for num in valid:
            self.assertTrue(is_number(num), '"{0}" is not a number'.format(type(num).__name__))

        # Test valid values with parameter that allows Booleans
        valid += (True, False)
        for num in valid:
            self.assertTrue(is_number(num, if_bool=True), '"{0}" is not a number'.format(type(num).__name__))
