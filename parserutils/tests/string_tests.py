import unittest

from parserutils.strings import _ASCII_PUNCTUATION_MAP, ALPHANUMERIC, EMPTY_BIN, EMPTY_STR
from parserutils.strings import camel_to_constant, camel_to_snake, constant_to_camel, snake_to_camel
from parserutils.strings import to_ascii_equivalent


class StringCasingTestCase(unittest.TestCase):

    def test_camel_to_constant(self):
        """ Tests camel_to_constant with general inputs """

        self.assertEqual(camel_to_constant(None), None)
        self.assertEqual(camel_to_constant(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(camel_to_constant(EMPTY_STR), EMPTY_STR)
        self.assertEqual(camel_to_constant('123'), '123')
        self.assertEqual(camel_to_constant('test'), 'TEST')
        self.assertEqual(camel_to_constant('TEST'), 'TEST')
        self.assertEqual(camel_to_constant('abcDef'), 'ABC_DEF')
        self.assertEqual(camel_to_constant('AbcDef'), 'ABC_DEF')
        self.assertEqual(camel_to_constant('ABCDef'), 'ABC_DEF')
        self.assertEqual(camel_to_constant('abcDEF'), 'ABC_DEF')
        self.assertEqual(camel_to_constant('aBcDEF'), 'A_BC_DEF')
        self.assertEqual(camel_to_constant('ABcDEF'), 'A_BC_DEF')
        self.assertEqual(camel_to_constant('abcDefGhi'), 'ABC_DEF_GHI')
        self.assertEqual(camel_to_constant('abcDEFGhi'), 'ABC_DEF_GHI')
        self.assertEqual(camel_to_constant('One1Two2Three3'), 'ONE1_TWO2_THREE3')
        self.assertEqual(camel_to_constant('1One2Two3Three'), '1_ONE2_TWO3_THREE')
        self.assertEqual(camel_to_constant('11Twelve13Fourteen15'), '11_TWELVE13_FOURTEEN15')

    def test_camel_to_snake(self):
        """ Tests camel_to_snake with general inputs """

        self.assertEqual(camel_to_snake(None), None)
        self.assertEqual(camel_to_snake(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(camel_to_snake(EMPTY_STR), EMPTY_STR)
        self.assertEqual(camel_to_snake('123'), '123')
        self.assertEqual(camel_to_snake('test'), 'test')
        self.assertEqual(camel_to_snake('TEST'), 'test')
        self.assertEqual(camel_to_snake('abcDef'), 'abc_def')
        self.assertEqual(camel_to_snake('AbcDef'), 'abc_def')
        self.assertEqual(camel_to_snake('ABCDef'), 'abc_def')
        self.assertEqual(camel_to_snake('abcDEF'), 'abc_def')
        self.assertEqual(camel_to_snake('aBcDEF'), 'a_bc_def')
        self.assertEqual(camel_to_snake('ABcDEF'), 'a_bc_def')
        self.assertEqual(camel_to_snake('abcDefGhi'), 'abc_def_ghi')
        self.assertEqual(camel_to_snake('abcDEFGhi'), 'abc_def_ghi')
        self.assertEqual(camel_to_snake('One1Two2Three3'), 'one1_two2_three3')
        self.assertEqual(camel_to_snake('1One2Two3Three'), '1_one2_two3_three')
        self.assertEqual(camel_to_snake('11Twelve13Fourteen15'), '11_twelve13_fourteen15')

    def test_camel_to_snake_to_camel(self):
        """ Tests camel_to_snake and back """

        values = (
            None, EMPTY_BIN, EMPTY_STR,
            '123', 'test', 'abcDef', 'aBcDef', 'abcDefGhi',
            'one1Two2Three3', '1One2Two3Three', '11Twelve13Fourteen15'
        )
        for value in values:
            self.assertEqual(snake_to_camel(camel_to_snake(value)), value)

    def test_constant_to_camel(self):
        """ Tests constant_to_camel with general inputs """

        self.assertEqual(constant_to_camel(None), None)
        self.assertEqual(constant_to_camel(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(constant_to_camel(EMPTY_STR), EMPTY_STR)
        self.assertEqual(constant_to_camel('123'), '123')
        self.assertEqual(constant_to_camel('test'), 'test')
        self.assertEqual(constant_to_camel('TEST'), 'test')
        self.assertEqual(constant_to_camel('ABC_DEF'), 'abcDef')
        self.assertEqual(constant_to_camel('ABC__DEF'), 'abcDef')
        self.assertEqual(constant_to_camel('ABC___DEF'), 'abcDef')
        self.assertEqual(constant_to_camel('_ABC_DEF_'), 'abcDef')
        self.assertEqual(constant_to_camel('__ABC_DEF'), 'abcDef')
        self.assertEqual(constant_to_camel('ABC_DEF__'), 'abcDef')
        self.assertEqual(constant_to_camel('A_BC_DEF'), 'aBcDef')
        self.assertEqual(constant_to_camel('ABC_DEF_GHI'), 'abcDefGhi')
        self.assertEqual(constant_to_camel('ONE1_TWO2_THREE3'), 'one1Two2Three3')
        self.assertEqual(constant_to_camel('1_ONE2_TWO3_THREE'), '1One2Two3Three')
        self.assertEqual(constant_to_camel('11_TWELVE13_FOURTEEN15'), '11Twelve13Fourteen15')

    def test_snake_to_camel(self):
        """ Tests snake_to_camel with general inputs """

        self.assertEqual(snake_to_camel(None), None)
        self.assertEqual(snake_to_camel(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(snake_to_camel(EMPTY_STR), EMPTY_STR)
        self.assertEqual(snake_to_camel('123'), '123')
        self.assertEqual(snake_to_camel('test'), 'test')
        self.assertEqual(snake_to_camel('TEST'), 'test')
        self.assertEqual(snake_to_camel('abc_def'), 'abcDef')
        self.assertEqual(snake_to_camel('abc__def'), 'abcDef')
        self.assertEqual(snake_to_camel('abc___def'), 'abcDef')
        self.assertEqual(snake_to_camel('_abc_def_'), 'abcDef')
        self.assertEqual(snake_to_camel('__abc_def'), 'abcDef')
        self.assertEqual(snake_to_camel('abc_def__'), 'abcDef')
        self.assertEqual(snake_to_camel('a_bc_def'), 'aBcDef')
        self.assertEqual(snake_to_camel('abc_def_ghi'), 'abcDefGhi')
        self.assertEqual(snake_to_camel('one1_two2_three3'), 'one1Two2Three3')
        self.assertEqual(snake_to_camel('1_one2_two3_three'), '1One2Two3Three')
        self.assertEqual(snake_to_camel('11_twelve13_fourteen15'), '11Twelve13Fourteen15')

    def test_snake_to_camel_to_snake(self):
        """ Tests snake_to_camel and back """

        values = (
            None, EMPTY_BIN, EMPTY_STR,
            '123', 'test', 'abc_def', 'a_bc_def', 'abc_def_ghi',
            'one1_two2_three3', '1_one2_two3_three', '11_twelve13_fourteen15'
        )
        for value in values:
            self.assertEqual(camel_to_snake(snake_to_camel(value)), value)


class StringConversionTestCase(unittest.TestCase):

    def test_to_ascii_equivalent(self):
        """ Tests to_ascii_equivalent with general inputs """

        # Test legal empty inputs
        self.assertEqual(to_ascii_equivalent(None), None)
        self.assertEqual(to_ascii_equivalent(EMPTY_BIN), EMPTY_STR)
        self.assertEqual(to_ascii_equivalent(EMPTY_STR), EMPTY_STR)

        # Test that ASCII is unchanged
        alphanumeric = EMPTY_STR.join(ALPHANUMERIC)
        self.assertEqual(to_ascii_equivalent(alphanumeric), alphanumeric)

        # Test that known issues are handled
        known_issues = [
            u'\u2010', u'\u2011',             # Hyphens
            u'\u2012', u'\u2013', u'\u2014',  # Dashes
            u'\u02b9', u'\u02bb', u'\u02bc',  # Single Quotes
            u'\u02bd', u'\u2018', u'\u2019',  # Single Quotes
            u'\u02ba', u'\u201d', u'\u201c',  # Double Quotes
            u'\u3001',                        # Commas
            u'\u2e32', u'\u2e34', u'\u2e41',  # Commas
            u'\ufe11', u'\ufe10', u'\ufe50',  # Commas
            u'\ufe51', u'\uff64', u'\uff0c',  # Commas
        ]
        for issue in known_issues:
            self.assertEqual(to_ascii_equivalent(issue), _ASCII_PUNCTUATION_MAP[issue])


if __name__ == '__main__':
    unittest.main()
