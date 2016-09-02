import unittest

from six import binary_type, text_type

from parserutils.numbers import is_number
from parserutils.strings import EMPTY_BIN, EMPTY_STR


class NumberTestCase(unittest.TestCase):

    def test_is_number(self):
        """ Tests is_number with general inputs """

        for bad in (None, EMPTY_BIN, EMPTY_STR, {}, [], set(), tuple(), float('+inf'), float('-inf'), float('nan')):
            self.assertFalse(is_number(bad))

        for num in (0, 1.1, binary_type('2'.encode()), text_type('3'), binary_type('4.4'.encode()), text_type('5.5')):
            self.assertTrue(is_number(num))


if __name__ == '__main__':
    unittest.main()
