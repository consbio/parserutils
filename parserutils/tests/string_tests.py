import unittest

from parserutils.strings import _ASCII_PUNCTUATION_MAP, ALPHANUMERIC, EMPTY_BIN, EMPTY_STR
from parserutils.strings import camel_to_constant, camel_to_snake, constant_to_camel, snake_to_camel
from parserutils.strings import splitany, to_ascii_equivalent


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

        # Test valid empty inputs
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
        ascii_issues = u''.join(_ASCII_PUNCTUATION_MAP[c] for c in known_issues)
        joined_issues = u''.join(known_issues)

        self.assertEqual(to_ascii_equivalent(joined_issues), ascii_issues)
        for issue in known_issues:
            self.assertEqual(to_ascii_equivalent(issue), _ASCII_PUNCTUATION_MAP[issue])

        # Test non-strings

        self.assertEqual(to_ascii_equivalent(True), 'True')
        self.assertEqual(to_ascii_equivalent(0), '0')
        self.assertEqual(to_ascii_equivalent(1.1), '1.1')
        self.assertEqual(to_ascii_equivalent(dict()), '{}')


class StringOperationTestCase(unittest.TestCase):

    def test_splitany(self):
        """ Tests splitany with general inputs """

        # Test valid empty inputs

        self.assertEqual(splitany(None, None), [])

        self.assertEqual(splitany(EMPTY_BIN, EMPTY_BIN), [EMPTY_BIN])
        self.assertEqual(splitany(EMPTY_BIN, EMPTY_STR), [EMPTY_BIN])

        self.assertEqual(splitany(EMPTY_STR, EMPTY_BIN), [EMPTY_STR])
        self.assertEqual(splitany(EMPTY_STR, EMPTY_STR), [EMPTY_STR])

        # Test invalid strings to split

        for invalid in ({}, set(), (x for x in 'abc')):
            with self.assertRaises(TypeError):
                splitany(invalid, u'')
            with self.assertRaises(TypeError):
                splitany(invalid, b'')

        # Test invalid separators to split on

        for invalid in ({}, set(), [u'', b'', {}], (u'', b'', set())):
            with self.assertRaises(TypeError):
                splitany(u'', invalid)
            with self.assertRaises(TypeError):
                splitany(b'', invalid)

        # Test single inputs

        # No matches with unicode and binary combinations
        self.assertEqual(splitany(u'abc'), u'abc'.split())
        self.assertEqual(splitany(b'abc'), b'abc'.split())

        self.assertEqual(splitany(u'abc', u'x'), u'abc'.split(u'x'))
        self.assertEqual(splitany(b'abc', u'x'), b'abc'.split(b'x'))
        self.assertEqual(splitany(u'abc', b'x'), u'abc'.split(u'x'))
        self.assertEqual(splitany(b'abc', b'x'), b'abc'.split(b'x'))

        # One initial match with unicode and binary combinations
        self.assertEqual(splitany(u' abc'), u' abc'.split())
        self.assertEqual(splitany(b' abc'), b' abc'.split())

        self.assertEqual(splitany(u'xyz', u'x'), u'xyz'.split(u'x'))
        self.assertEqual(splitany(b'xyz', u'x'), b'xyz'.split(b'x'))
        self.assertEqual(splitany(u'xyz', b'x'), u'xyz'.split(u'x'))
        self.assertEqual(splitany(b'xyz', b'x'), b'xyz'.split(b'x'))
        self.assertEqual(splitany(u'xyz', b'x', 0), u'xyz'.split(u'x', 0))
        self.assertEqual(splitany(b'xyz', u'x', 1), b'xyz'.split(b'x', 1))
        self.assertEqual(splitany(u'xyz', u'x', 2), u'xyz'.split(u'x', 2))
        self.assertEqual(splitany(b'xyz', b'x', 3), b'xyz'.split(b'x', 3))

        # One complete match with unicode and binary combinations
        self.assertEqual(splitany(u' '), u' '.split())
        self.assertEqual(splitany(b' '), b' '.split())

        self.assertEqual(splitany(u'xyz', [u'xyz']), u'xyz'.split(u'xyz'))
        self.assertEqual(splitany(b'xyz', [u'xyz']), b'xyz'.split(b'xyz'))
        self.assertEqual(splitany(u'xyz', [b'xyz']), u'xyz'.split(u'xyz'))
        self.assertEqual(splitany(b'xyz', [b'xyz']), b'xyz'.split(b'xyz'))
        self.assertEqual(splitany(u'xyz', [b'xyz'], 0), u'xyz'.split(u'xyz', 0))
        self.assertEqual(splitany(b'xyz', [u'xyz'], 1), b'xyz'.split(b'xyz', 1))
        self.assertEqual(splitany(u'xyz', [u'xyz'], 2), u'xyz'.split(u'xyz', 2))
        self.assertEqual(splitany(b'xyz', [b'xyz'], 3), b'xyz'.split(b'xyz', 3))

        # Two internal matches with unicode and binary combinations
        self.assertEqual(splitany(u'abc def ghi'), u'abc def ghi'.split())
        self.assertEqual(splitany(b'abc def ghi'), b'abc def ghi'.split())

        self.assertEqual(splitany(u'xyzxyz', u'y'), u'xyzxyz'.split(u'y'))
        self.assertEqual(splitany(b'xyzxyz', u'y'), b'xyzxyz'.split(b'y'))
        self.assertEqual(splitany(u'xyzxyz', b'y'), u'xyzxyz'.split(u'y'))
        self.assertEqual(splitany(b'xyzxyz', b'y'), b'xyzxyz'.split(b'y'))
        self.assertEqual(splitany(u'xyzxyz', b'y', 0), u'xyzxyz'.split(u'y', 0))
        self.assertEqual(splitany(b'xyzxyz', u'y', 1), b'xyzxyz'.split(b'y', 1))
        self.assertEqual(splitany(u'xyzxyz', u'y', 2), u'xyzxyz'.split(u'y', 2))
        self.assertEqual(splitany(b'xyzxyz', b'y', 3), b'xyzxyz'.split(b'y', 3))

        # Two internal multi-char matches with unicode and binary combinations
        self.assertEqual(splitany(u'abc\n\tdef'), u'abc\n\tdef'.split())
        self.assertEqual(splitany(b'abc\n\tdef'), b'abc\n\tdef'.split())

        self.assertEqual(splitany(u'xyzxyz', [u'yz']), u'xyzxyz'.split(u'yz'))
        self.assertEqual(splitany(b'xyzxyz', [u'yz']), b'xyzxyz'.split(b'yz'))
        self.assertEqual(splitany(u'xyzxyz', [b'yz']), u'xyzxyz'.split(u'yz'))
        self.assertEqual(splitany(b'xyzxyz', [b'yz']), b'xyzxyz'.split(b'yz'))
        self.assertEqual(splitany(u'xyzxyz', [b'yz'], 0), u'xyzxyz'.split(u'yz', 0))
        self.assertEqual(splitany(b'xyzxyz', [u'yz'], 1), b'xyzxyz'.split(b'yz', 1))
        self.assertEqual(splitany(u'xyzxyz', [u'yz'], 2), u'xyzxyz'.split(u'yz', 2))
        self.assertEqual(splitany(b'xyzxyz', [b'yz'], 3), b'xyzxyz'.split(b'yz', 3))

        # Three internal and trailing matches with unicode and binary combinations
        self.assertEqual(splitany(u'abc def\tdef\n'), u'abc def\tdef\n'.split())
        self.assertEqual(splitany(b'abc def\tdef\n'), b'abc def\tdef\n'.split())

        self.assertEqual(splitany(u'xyzxyzxyz', u'z'), u'xyzxyzxyz'.split(u'z'))
        self.assertEqual(splitany(b'xyzxyzxyz', u'z'), b'xyzxyzxyz'.split(b'z'))
        self.assertEqual(splitany(u'xyzxyzxyz', b'z'), u'xyzxyzxyz'.split(u'z'))
        self.assertEqual(splitany(b'xyzxyzxyz', b'z'), b'xyzxyzxyz'.split(b'z'))
        self.assertEqual(splitany(u'xyzxyzxyz', b'z', 0), u'xyzxyzxyz'.split(u'z', 0))
        self.assertEqual(splitany(b'xyzxyzxyz', u'z', 1), b'xyzxyzxyz'.split(b'z', 1))
        self.assertEqual(splitany(u'xyzxyzxyz', b'z', 2), u'xyzxyzxyz'.split(u'z', 2))
        self.assertEqual(splitany(b'xyzxyzxyz', b'z', 3), b'xyzxyzxyz'.split(b'z', 3))
        self.assertEqual(splitany(u'xyzxyzxyz', u'z', 4), u'xyzxyzxyz'.split(u'z', 4))

        # Three internal and trailing multi-char matches with unicode and binary combinations
        self.assertEqual(splitany(u'abc\t\tdef  def\n\n'), u'abc\t\tdef  def\n\n'.split())
        self.assertEqual(splitany(b'abc\t\tdef  def\n\n'), b'abc\t\tdef  def\n\n'.split())

        self.assertEqual(splitany(u'xyzxyzxyz', [u'yz']), u'xyzxyzxyz'.split(u'yz'))
        self.assertEqual(splitany(b'xyzxyzxyz', [u'yz']), b'xyzxyzxyz'.split(b'yz'))
        self.assertEqual(splitany(u'xyzxyzxyz', [b'yz']), u'xyzxyzxyz'.split(u'yz'))
        self.assertEqual(splitany(b'xyzxyzxyz', [b'yz']), b'xyzxyzxyz'.split(b'yz'))
        self.assertEqual(splitany(u'xyzxyzxyz', [b'yz'], 0), u'xyzxyzxyz'.split(u'yz', 0))
        self.assertEqual(splitany(b'xyzxyzxyz', [u'yz'], 1), b'xyzxyzxyz'.split(b'yz', 1))
        self.assertEqual(splitany(u'xyzxyzxyz', [b'yz'], 2), u'xyzxyzxyz'.split(u'yz', 2))
        self.assertEqual(splitany(b'xyzxyzxyz', [b'yz'], 3), b'xyzxyzxyz'.split(b'yz', 3))
        self.assertEqual(splitany(u'xyzxyzxyz', [u'yz'], 4), u'xyzxyzxyz'.split(u'yz', 4))

        # Test multiple inputs expecting unicode

        split_mult = u'abc:d:;|w:xy;|z'
        split_once = u'abc,d,,,w,xy,,z'

        # Test unicode without maxsplit option to ensure equivalence to str.split
        self.assertEqual(splitany(split_mult, u';|:'), split_once.split(u','))
        self.assertEqual(splitany(split_mult, b';|:'), split_once.split(u','))
        self.assertEqual(splitany(split_mult, [x for x in u';|:']), split_once.split(u','))
        self.assertEqual(splitany(split_mult, [b';', b'|', b':']), split_once.split(u','))
        self.assertEqual(splitany(split_mult, [b'|', u':', b';']), split_once.split(u','))

        for i in range(7):
            target = split_once.split(u',', i)

            # Test unicode with maxsplit option to ensure equivalence to str.split
            for sep in (u';|:', b';|:', [x for x in u';|:'], [b';', b'|', b':'], [b'|', u':', b';']):
                source = splitany(split_mult, sep, i)
                length = len(source[i])
                index = split_mult.index(source[i])

                self.assertEqual(source[:i], target[:i])         # Parsed portions are equal
                self.assertEqual(length, len(target[i]))         # Remaining portions equal in length
                self.assertEqual(source[i], split_mult[index:])  # Remaining portion exists in original

        # Test multiple inputs expecting binary

        split_mult = b'abc:d:;|w:xy;|z'
        split_once = b'abc,d,,,w,xy,,z'

        # Test binary without maxsplit option to ensure equivalence to str.split
        self.assertEqual(splitany(split_mult, u';|:'), split_once.split(b','))
        self.assertEqual(splitany(split_mult, b';|:'), split_once.split(b','))
        self.assertEqual(splitany(split_mult, [x for x in u';|:']), split_once.split(b','))
        self.assertEqual(splitany(split_mult, [b';', b'|', b':']), split_once.split(b','))
        self.assertEqual(splitany(split_mult, [b'|', u':', b';']), split_once.split(b','))

        for i in range(7):
            target = split_once.split(b',', i)

            # Test binary with maxsplit option to ensure equivalence to str.split
            for sep in (u';|:', b';|:', [x for x in u';|:'], [b';', b'|', b':'], [b'|', u':', b';']):
                source = splitany(split_mult, sep, i)
                length = len(source[i])
                index = split_mult.index(source[i])

                self.assertEqual(source[:i], target[:i])         # Parsed portions are equal
                self.assertEqual(length, len(target[i]))         # Remaining portions equal in length
                self.assertEqual(source[i], split_mult[index:])  # Remaining portion exists in original

        # Test multiple character inputs with overlapping separators, with unicode and binary

        self.assertEqual(splitany(u'aabdabcd', [u'a']), [u'', u'', u'bd', u'bcd'])
        self.assertEqual(splitany(u'aabdabcd', [b'a']), [u'', u'', u'bd', u'bcd'])
        self.assertEqual(splitany(b'aabdabcd', [u'a']), [b'', b'', b'bd', b'bcd'])
        self.assertEqual(splitany(b'aabdabcd', [b'a']), [b'', b'', b'bd', b'bcd'])

        self.assertEqual(splitany(u'aabdabcd', [u'ab', u'a']), [u'', u'', u'd', u'cd'])
        self.assertEqual(splitany(b'aabdabcd', [b'ab', u'a']), [b'', b'', b'd', b'cd'])
        self.assertEqual(splitany(u'aabdabcd', [u'a', b'ab']), [u'', u'', u'd', u'cd'])
        self.assertEqual(splitany(b'aabdabcd', [b'a', b'ab']), [b'', b'', b'd', b'cd'])

        self.assertEqual(splitany(u'aabdabcd', [b'abc', u'ab', b'a']), [u'', u'', u'd', u'd'])
        self.assertEqual(splitany(b'aabdabcd', [u'abc', b'ab', u'a']), [b'', b'', b'd', b'd'])
        self.assertEqual(splitany(u'aabdabcd', [u'a', b'ab', u'abc']), [u'', u'', u'd', u'd'])
        self.assertEqual(splitany(b'aabdabcd', [b'a', u'ab', b'abc']), [b'', b'', b'd', b'd'])
