import unittest

from copy import deepcopy

from parserutils.collections import accumulate_items, setdefaults
from parserutils.collections import filter_empty, flatten_items, rfind, rindex, reduce_value, wrap_value
from parserutils.strings import EMPTY_BIN, EMPTY_STR


class DictsTestCase(unittest.TestCase):

    def test_accumulate_items(self):
        """ Tests accumulate_items with general inputs """

        # Test with empty items
        self.assertEqual(accumulate_items(None), {})
        self.assertEqual(accumulate_items(EMPTY_BIN), {})
        self.assertEqual(accumulate_items(EMPTY_STR), {})
        self.assertEqual(accumulate_items(dict()), {})
        self.assertEqual(accumulate_items(list()), {})
        self.assertEqual(accumulate_items(set()), {})
        self.assertEqual(accumulate_items(tuple()), {})
        self.assertEqual(accumulate_items(x for x in EMPTY_BIN), {})
        self.assertEqual(accumulate_items((x for x in EMPTY_STR)), {})

        # Test with items containing single key/val
        self.assertEqual(accumulate_items({(None, None)}), {None: [None]})
        self.assertEqual(accumulate_items([(EMPTY_BIN, EMPTY_STR)]), {EMPTY_BIN: [EMPTY_STR]})
        self.assertEqual(accumulate_items(([EMPTY_STR, EMPTY_BIN],)), {EMPTY_STR: [EMPTY_BIN]})
        self.assertEqual(accumulate_items((k, v) for k, v in [['key', 'val']]), {'key': ['val']})
        self.assertEqual(accumulate_items(((k, v) for k, v in [(0, 1)])), {0: [1]})

        # Test with items containing single key/val, reducing each
        self.assertEqual(accumulate_items({(None, None)}, reduce_each=True), {None: None})
        self.assertEqual(accumulate_items([(EMPTY_BIN, EMPTY_STR)], reduce_each=True), {EMPTY_BIN: EMPTY_STR})
        self.assertEqual(accumulate_items(([EMPTY_STR, EMPTY_BIN],), reduce_each=True), {EMPTY_STR: EMPTY_BIN})
        self.assertEqual(accumulate_items(((k, v) for k, v in [['key', 'val']]), reduce_each=True), {'key': 'val'})
        self.assertEqual(accumulate_items(((k, v) for k, v in [(0, 1)]), reduce_each=True), {0: 1})

        # Test with items containing single vals under multiple keys, with and without reduction
        self.assertEqual(
            accumulate_items([('key1', 'val'), ('key2', 'val'), ('key3', 'val')]),
            {'key1': ['val'], 'key2': ['val'], 'key3': ['val']}
        )
        self.assertEqual(
            accumulate_items([('key1', 'val'), ('key2', 'val'), ('key3', 'val')], reduce_each=True),
            {'key1': 'val', 'key2': 'val', 'key3': 'val'}
        )

        # Test with items containing multiple vals under a single key, with and without reduction
        self.assertEqual(
            accumulate_items([('key', 'val1'), ('key', 'val2'), ('key', 'val3')]),
            {'key': ['val1', 'val2', 'val3']}
        )
        self.assertEqual(
            accumulate_items([('key', 'val1'), ('key', 'val2'), ('key', 'val3')], reduce_each=True),
            {'key': ['val1', 'val2', 'val3']}
        )
        self.assertEqual(
            accumulate_items(
                [('key', 'val1'), ('key', 'val2'), ('key2', ['val1', 'val2']), ('key3', 'val3')], reduce_each=True
            ),
            {'key': ['val1', 'val2'], 'key2': ['val1', 'val2'], 'key3': 'val3'}
        )

        # Test with items containing multiple vals under multiple keys, with and without reduction
        self.assertEqual(
            accumulate_items([('key3', 'val1'), ('key2', 'val2'), ('key1', 'val3')]),
            {'key1': ['val3'], 'key2': ['val2'], 'key3': ['val1']}
        )
        self.assertEqual(
            accumulate_items([('key3', 'val1'), ('key2', 'val2'), ('key1', 'val3')], reduce_each=True),
            {'key1': 'val3', 'key2': 'val2', 'key3': 'val1'}
        )

    def test_setdefaults(self):
        """ Tests setdefaults with general inputs """

        # Test with invalid dict and empty defaults
        self.assertEqual(setdefaults(None, None), None)
        self.assertEqual(setdefaults(EMPTY_BIN, None), EMPTY_BIN)
        self.assertEqual(setdefaults(EMPTY_STR, None), EMPTY_STR)
        self.assertEqual(setdefaults({}, None), {})
        self.assertEqual([x for x in setdefaults((c for c in 'abc'), None)], [c for c in 'abc'])

        # Test with invalid dict and valid defaults
        self.assertEqual(setdefaults(None, 'x'), None)
        self.assertEqual(setdefaults(EMPTY_BIN, 'y'), EMPTY_BIN)
        self.assertEqual(setdefaults(EMPTY_STR, 'z'), EMPTY_STR)
        self.assertEqual([x for x in setdefaults((c for c in 'abc'), 'xyz')], [c for c in 'abc'])

        # Test with empty dict and valid defaults
        self.assertEqual(setdefaults({}, 'a'), {'a': None})
        self.assertEqual(setdefaults({}, ['b']), {'b': None})
        self.assertEqual(setdefaults({}, {'c': None}), {'c': None})
        self.assertEqual(setdefaults({}, {'c': False}), {'c': False})
        self.assertEqual(setdefaults({}, {'c': True}), {'c': True})
        self.assertEqual(setdefaults({}, {'c': 0}), {'c': 0})
        self.assertEqual(setdefaults({}, {'c': 1}), {'c': 1})
        self.assertEqual(setdefaults({}, {'c': 2.3}), {'c': 2.3})
        self.assertEqual(setdefaults({}, {'d': 'ddd'}), {'d': 'ddd'})
        self.assertEqual(setdefaults({}, [{'e': 'eee'}, {'f': 'fff'}]), {'e': 'eee', 'f': 'fff'})
        self.assertEqual(setdefaults({}, {'x': 'xxx', 'y': 'yyy'}), {'x': 'xxx', 'y': 'yyy'})
        self.assertEqual(setdefaults({'z': 'zzz'}, None), {'z': 'zzz'})

    def test_setdefaults_str(self):
        """ Tests setdefaults with defaults specified as strings """

        inputs = 'a.b'

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)                       # Output should equal input
        self.assertEqual(o, {'a': {'b': None}})      # Test against a hard value
        self.assertEqual(setdefaults(d, inputs), o)  # Test unchanged with multiple runs

        d = {'a': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': 'xxx'})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': {'b': 'xxx'}})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'c': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': {'b': None}, 'c': 'xxx'})
        self.assertEqual(setdefaults(d, inputs), o)

        inputs = 'a.b.c'

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': {'b': {'c': None}}})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': {'c': 'xxx'}}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': {'b': {'c': 'xxx'}}})
        self.assertEqual(setdefaults(d, inputs), o)

    def test_setdefaults_dict_nested(self):
        """ Tests setdefaults with nested defaults specified as dicts """

        inputs = {'a.b': 'bbb', 'a.c': 'ccc'}

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)                                # Output should equal input
        self.assertEqual(o, {'a': {'b': 'bbb', 'c': 'ccc'}})  # Test against a hard value
        self.assertEqual(setdefaults(d, inputs), o)           # Test unchanged with multiple runs

        d = {'a': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': 'xxx'})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a']['c'], 'ccc')
        self.assertEqual(o['a']['b'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'c': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a']['b'], 'bbb')
        self.assertEqual(o['a']['c'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'c': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a'], {'b': 'bbb', 'c': 'ccc'})
        self.assertEqual(o['a']['c'], 'ccc')
        self.assertEqual(o['c'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)

        inputs = {'a.b.c': True, 'd.e.f': [123.456]}

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a'], {'b': {'c': True}})
        self.assertEqual(o['d'], {'e': {'f': [123.456]}})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': {'c': 'xxx'}}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a'], {'b': {'c': 'xxx'}})
        self.assertEqual(o['d'], {'e': {'f': [123.456]}})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'d': {'e': {'f': 'xxx'}}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a'], {'b': {'c': True}})
        self.assertEqual(o['d'], {'e': {'f': 'xxx'}})
        self.assertEqual(setdefaults(d, inputs), o)

    def test_setdefaults_dict_overlapping(self):
        """ Tests setdefaults with overlapping defaults specified as dicts """

        inputs = {'a.b.c': 'ccc', 'a.c.d.e': 'eee'}

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)                                                     # Output should equal input
        self.assertEqual(o, {'a': {'b': {'c': 'ccc'}, 'c': {'d': {'e': 'eee'}}}})  # Test against a hard value
        self.assertEqual(setdefaults(d, inputs), o)                                # Test unchanged with multiple runs

        d = {'a': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o, {'a': 'xxx'})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a']['b'], 'xxx')
        self.assertEqual(o['a']['c'], {'d': {'e': 'eee'}})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'c': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a']['b'], {'c': 'ccc'})
        self.assertEqual(o['a']['c'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'c': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(o['a'], {'b': {'c': 'ccc'}, 'c': {'d': {'e': 'eee'}}})
        self.assertEqual(o['c'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)

    def test_setdefaults_other(self):
        """ Tests setdefaults with defaults specified as list, set, and tuple """

        inputs = ['a.b', 'a.c']

        d = {}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)                                                   # Output should equal input
        self.assertEqual(setdefaults(d, inputs), {'a': {'b': None, 'c': None}})  # Test against a hard value
        self.assertEqual(setdefaults(d, inputs), o)                              # Test unchanged with multiple runs

        d = {'a': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(setdefaults(d, inputs), {'a': 'xxx'})
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'a': {'b': 'xxx'}}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(setdefaults(d, inputs)['a']['b'], 'xxx')
        self.assertEqual(setdefaults(d, inputs)['a']['c'], None)
        self.assertEqual(setdefaults(d, inputs), o)

        d = {'c': 'xxx'}
        o = deepcopy(setdefaults(d, inputs))
        self.assertEqual(d, o)
        self.assertEqual(setdefaults(d, inputs)['a'], {'b': None, 'c': None})
        self.assertEqual(setdefaults(d, inputs)['c'], 'xxx')
        self.assertEqual(setdefaults(d, inputs), o)


class ListTupleSetTestCase(unittest.TestCase):

    def test_filter_empty(self):
        """ Tests filter_empty with general inputs """

        # Test None case: nothing to filter but default applies
        self.assertEqual(filter_empty(None), None)
        self.assertEqual(filter_empty(None, 'None'), 'None')

        # Test empty string case: nothing to filter but default applies
        self.assertEqual(filter_empty(EMPTY_BIN), None)
        self.assertEqual(filter_empty(EMPTY_BIN, 'None'), 'None')
        self.assertEqual(filter_empty(EMPTY_STR), None)
        self.assertEqual(filter_empty(EMPTY_STR, 'None'), 'None')

        # Test empty collections case: nothing to filter but default applies
        self.assertEqual(filter_empty(list()), None)
        self.assertEqual(filter_empty(list(), 'None'), 'None')
        self.assertEqual(filter_empty(set()), None)
        self.assertEqual(filter_empty(set(), 'None'), 'None')
        self.assertEqual(filter_empty(tuple()), None)
        self.assertEqual(filter_empty(tuple(), 'None'), 'None')
        self.assertEqual(filter_empty(x for x in ''), None)
        self.assertEqual(filter_empty((x for x in ''), 'None'), 'None')

        # Test when there's nothing to filter
        self.assertEqual(filter_empty(False), False)
        self.assertEqual(filter_empty(True), True)
        self.assertEqual(filter_empty(0), 0)
        self.assertEqual(filter_empty(1), 1)
        self.assertEqual(filter_empty('a'), 'a')
        self.assertEqual(filter_empty('abc'), 'abc')
        self.assertEqual(filter_empty({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual(filter_empty({'b': 'bbb', 'c': 'ccc'}), {'b': 'bbb', 'c': 'ccc'})
        self.assertEqual(filter_empty(c for c in 'abc'), ['a', 'b', 'c'])
        self.assertEqual(filter_empty((c for c in 'abc')), ['a', 'b', 'c'])

        # Test when there's nothing to filter, but with unused default
        self.assertEqual(filter_empty(0, '0'), 0)
        self.assertEqual(filter_empty(1, '1'), 1)
        self.assertEqual(filter_empty('a', 'None'), 'a')
        self.assertEqual(filter_empty('abc', 'None'), 'abc')
        self.assertEqual(filter_empty((c for c in 'abc'), 'None'), ['a', 'b', 'c'])

        # Test with filterable values
        self.assertEqual(filter_empty([None]), None)
        self.assertEqual(filter_empty({None}), None)
        self.assertEqual(filter_empty((None,)), None)
        self.assertEqual(filter_empty([EMPTY_BIN]), None)
        self.assertEqual(filter_empty({EMPTY_BIN}), None)
        self.assertEqual(filter_empty((EMPTY_BIN,)), None)
        self.assertEqual(filter_empty([EMPTY_STR]), None)
        self.assertEqual(filter_empty({EMPTY_STR}), None)
        self.assertEqual(filter_empty((EMPTY_STR,)), None)
        self.assertEqual(filter_empty(x for x in (None, EMPTY_BIN, EMPTY_STR)), None)
        self.assertEqual(filter_empty((x for x in (None, EMPTY_BIN, EMPTY_STR))), None)

        # Test with filterable values and defaults
        self.assertEqual(filter_empty([None, EMPTY_BIN, EMPTY_STR], {}), {})
        self.assertEqual(filter_empty({EMPTY_BIN, None, EMPTY_STR}, []), [])
        self.assertEqual(filter_empty((EMPTY_BIN, EMPTY_STR, None), []), [])
        self.assertEqual(filter_empty([list(), set(), tuple(), dict()], {}), {})
        self.assertEqual(filter_empty((tuple(), dict(), list(), set()), []), [])
        self.assertEqual(filter_empty(x for x in (None, EMPTY_BIN, EMPTY_STR)), None)
        self.assertEqual(filter_empty((x for x in (tuple(), dict(), list(), set())), {}), {})

        # Test with values that should not be filtered
        self.assertEqual(filter_empty([0]), [0])
        self.assertEqual(filter_empty([1]), [1])
        self.assertEqual(filter_empty(['x']), ['x'])
        self.assertEqual(filter_empty({'y'}), {'y'})
        self.assertEqual(filter_empty(('z',)), ('z',))
        self.assertEqual(filter_empty(c for c in '0'), ['0'])
        self.assertEqual(filter_empty((c for c in '1')), ['1'])

        # Test with combinations of values
        self.assertEqual(filter_empty([None, 0, EMPTY_STR, 1]), [0, 1])
        self.assertEqual(filter_empty(['a', None, 'b', EMPTY_BIN, 'c']), ['a', 'b', 'c'])
        self.assertEqual(filter_empty({None, EMPTY_STR, 'a', 'b', 'c'}), {'a', 'b', 'c'})
        self.assertEqual(filter_empty(('a', 'b', None, 'c', EMPTY_BIN)), ('a', 'b', 'c'))
        self.assertEqual(filter_empty(t for t in ('a', 'b', tuple(), 'c', set())), ['a', 'b', 'c'])
        self.assertEqual(filter_empty((t for t in ('a', 'b', 'c', set(), list()))), ['a', 'b', 'c'])

        # Test with non-filterable collections
        self.assertEqual(filter_empty({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual([x for x in filter_empty(c for c in 'abc')], ['a', 'b', 'c'])
        self.assertEqual([x for x in filter_empty((c for c in 'xyz'))], ['x', 'y', 'z'])

    def test_flatten_items(self):
        """ Tests flatten_items with general inputs """

        # Test None case: nothing to filter but default applies
        self.assertEqual(flatten_items(None), None)
        self.assertEqual(flatten_items(None, True), None)

        # Test empty string case: nothing to filter but default applies
        self.assertEqual(flatten_items(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(flatten_items(EMPTY_BIN, True), EMPTY_BIN)
        self.assertEqual(flatten_items(EMPTY_STR), EMPTY_STR)
        self.assertEqual(flatten_items(EMPTY_STR, True), EMPTY_STR)
        self.assertEqual(flatten_items(dict()), dict())
        self.assertEqual(flatten_items(dict(), True), dict())

        # Test empty collections case: nothing to flatten but default applies
        self.assertEqual(flatten_items(list()), list())
        self.assertEqual(flatten_items(list(), True), list())
        self.assertEqual(flatten_items(set()), set())
        self.assertEqual(flatten_items(set(), True), set())
        self.assertEqual(flatten_items(tuple()), tuple())
        self.assertEqual(flatten_items(tuple(), True), tuple())

        # Test when there's nothing to flatten
        self.assertEqual(flatten_items(False), False)
        self.assertEqual(flatten_items(False, True), False)
        self.assertEqual(flatten_items(True), True)
        self.assertEqual(flatten_items(True, True), True)
        self.assertEqual(flatten_items(0), 0)
        self.assertEqual(flatten_items(0, True), 0)
        self.assertEqual(flatten_items(1), 1)
        self.assertEqual(flatten_items(1, True), 1)
        self.assertEqual(flatten_items('a'), 'a')
        self.assertEqual(flatten_items('a', True), 'a')
        self.assertEqual(flatten_items('abc'), 'abc')
        self.assertEqual(flatten_items('abc', True), 'abc')
        self.assertEqual(flatten_items({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual(flatten_items({'a': 'aaa'}, True), {'a': 'aaa'})
        self.assertEqual(flatten_items({'b': 'bbb', 'c': 'ccc'}), {'b': 'bbb', 'c': 'ccc'})
        self.assertEqual(flatten_items({'b': 'bbb', 'c': 'ccc'}, True), {'b': 'bbb', 'c': 'ccc'})

        # Test with single value collections with nothing to flatten, without defaults
        for flat in (None, EMPTY_BIN, EMPTY_STR, 'abc', 0, 1, True, False):
            self.assertEqual(flatten_items([flat]), [flat])
            self.assertEqual(flatten_items([flat], True), [flat])

            self.assertEqual(flatten_items({flat}), {flat})
            self.assertEqual(flatten_items({flat}, True), {flat})
            self.assertEqual(flatten_items((flat,)), (flat,))
            self.assertEqual(flatten_items((flat,), True), (flat,))

            self.assertEqual(flatten_items(f for f in [flat]), [flat])
            self.assertEqual(flatten_items((f for f in (flat,)), True), [flat])

        # Test with multiple values with nothing to flatten
        for flat in ([None, EMPTY_BIN, EMPTY_STR], (False, True, 0, 1, 'a'), {'False', 'True', '0', '1', 'a'}):
            for flat_type in (list, tuple, set):
                flat_in = flat_type(flat)
                flat_out = flat_in

                self.assertEqual(flatten_items(flat_in), flat_out)
                self.assertEqual(flatten_items(flat_in, True), flat_out)

                self.assertEqual(flatten_items(f for f in flat_in), list(flat_out))
                self.assertEqual(flatten_items((f for f in flat_in), True), list(flat_out))

        # Test with collection values (some unhashable) that should be flattened, but not recursed

        for flat_type in (list, tuple):
            flat_in = flat_type([tuple(), 'a', set(), 'bc', list(), b'xyz', dict()])
            flat_out = flat_in

            self.assertEqual(flatten_items(flat_in), flat_out)
            self.assertEqual(flatten_items(flat_in, True), flat_out)

            self.assertEqual(flatten_items(f for f in flat_in), list(flat_out))
            self.assertEqual(flatten_items((f for f in flat_in), True), list(flat_out))

        # Test with values that should be flattened and recursed in many combinations

        self.assertEqual(flatten_items([('a', 'b', 'c'), 'd', {'e'}, ['f', 'g']]), ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
        self.assertEqual(flatten_items((0, [1, 2, 3], 4, 5, {6}, 7)), (0, 1, 2, 3, 4, 5, 6, 7))
        self.assertEqual(
            flatten_items(x for x in ((False, True), {'xyz'}, 7, 8, 9, ['10'])), [False, True, 'xyz', 7, 8, 9, '10']
        )

        not_yet_flat = [tuple(c for c in 'abc'), 'd', list(c for c in '123'), [None, {False}, {True}]]

        for flat_type in (list, tuple):
            flat_to_recurse = flat_type(not_yet_flat)

            flat_no_recurse = flat_type(['a', 'b', 'c', 'd', '1', '2', '3', None, {False}, {True}])
            flat_after_recurse = flat_type(['a', 'b', 'c', 'd', '1', '2', '3', None, False, True])

            self.assertEqual(flatten_items(flat_to_recurse), flat_no_recurse)
            self.assertEqual(flatten_items(flat_to_recurse, True), flat_after_recurse)

            self.assertEqual(flatten_items(f for f in flat_to_recurse), list(flat_no_recurse))
            self.assertEqual(flatten_items((f for f in flat_to_recurse), True), list(flat_after_recurse))

    def test_rfind(self):
        """ Tests rfind with general inputs """

        # Test empty cases: nothing to find
        self.assertEqual(rfind(None, 'x'), -1)
        self.assertEqual(rfind(EMPTY_BIN, 'x'), -1)
        self.assertEqual(rfind(EMPTY_BIN, b'x'), -1)
        self.assertEqual(rfind(EMPTY_STR, 'x'), -1)
        self.assertEqual(rfind(EMPTY_STR, b'x'), -1)
        self.assertEqual(rfind(list(), 'x'), -1)
        self.assertEqual(rfind(tuple(), 'x'), -1)
        self.assertEqual(rfind(set(), 'x'), -1)
        self.assertEqual(rfind(dict(), 'x'), -1)

        # Test missing cases: still nothing to find
        self.assertEqual(rfind(b'abc', 'x'), -1)
        self.assertEqual(rfind(b'abc', b'x'), -1)
        self.assertEqual(rfind(u'abc', 'x'), -1)
        self.assertEqual(rfind(u'abc', b'x'), -1)
        self.assertEqual(rfind(['a', 'b', 'c'], 'x'), -1)
        self.assertEqual(rfind(('a', 'b', 'c'), 'x'), -1)
        self.assertEqual(rfind({'a', 'b', 'c'}, 'x'), -1)
        self.assertEqual(rfind({'a': 'aaa', 'b': 'bbb', 'c': 'ccc'}, 'x'), -1)

        # Test invalid cases: still nothing to find
        self.assertEqual(rfind({'x', 'y', 'z'}, 'x'), -1)
        self.assertEqual(rfind({'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}, 'x'), -1)

        # Test one match cases: find at first, middle and last
        self.assertEqual(rfind(b'xyz', 'x'), 0)
        self.assertEqual(rfind(b'yxz', 'x'), 1)
        self.assertEqual(rfind(b'zyx', 'x'), 2)
        self.assertEqual(rfind(b'xyz', b'x'), 0)
        self.assertEqual(rfind(b'yxz', b'x'), 1)
        self.assertEqual(rfind(b'zyx', b'x'), 2)
        self.assertEqual(rfind(u'xyz', 'x'), 0)
        self.assertEqual(rfind(u'yxz', 'x'), 1)
        self.assertEqual(rfind(u'zyx', 'x'), 2)
        self.assertEqual(rfind(u'xyz', b'x'), 0)
        self.assertEqual(rfind(u'yxz', b'x'), 1)
        self.assertEqual(rfind(u'zyx', b'x'), 2)
        self.assertEqual(rfind(['x', 'y', 'z'], 'x'), 0)
        self.assertEqual(rfind(['y', 'x', 'z'], 'x'), 1)
        self.assertEqual(rfind(['z', 'y', 'x'], 'x'), 2)
        self.assertEqual(rfind(('x', 'y', 'z'), 'x'), 0)
        self.assertEqual(rfind(('y', 'x', 'z'), 'x'), 1)
        self.assertEqual(rfind(('z', 'y', 'x'), 'x'), 2)

        # Test multiple match cases: find at middle and last
        self.assertEqual(rfind(b'xxz', 'x'), 1)
        self.assertEqual(rfind(b'xyx', 'x'), 2)
        self.assertEqual(rfind(b'xxz', b'x'), 1)
        self.assertEqual(rfind(b'xyx', b'x'), 2)
        self.assertEqual(rfind(u'xxz', 'x'), 1)
        self.assertEqual(rfind(u'xyx', 'x'), 2)
        self.assertEqual(rfind(u'xxz', b'x'), 1)
        self.assertEqual(rfind(u'xyx', b'x'), 2)
        self.assertEqual(rfind(['x', 'x', 'z'], 'x'), 1)
        self.assertEqual(rfind(['x', 'y', 'x'], 'x'), 2)
        self.assertEqual(rfind(('x', 'x', 'z'), 'x'), 1)
        self.assertEqual(rfind(('x', 'y', 'x'), 'x'), 2)

    def test_rindex(self):
        """ Tests rindex with general inputs """

        # Test valid empty cases: raise ValueError
        for empty in (EMPTY_BIN, EMPTY_STR, list(), tuple()):
            with self.assertRaises(ValueError):
                rindex(empty, b'x')
            with self.assertRaises(ValueError):
                rindex(empty, u'x')

        # Test invalid empty cases: raise TypeError
        for empty in (None, set(), dict()):
            with self.assertRaises(TypeError):
                rindex(empty, b'x')
            with self.assertRaises(TypeError):
                rindex(empty, u'x')

        # Test valid missing cases: raise ValueError
        for empty in (b'abc', u'abc', ['a', 'b', 'c'], ('a', 'b', 'c')):
            with self.assertRaises(ValueError):
                rindex(empty, b'x')
            with self.assertRaises(ValueError):
                rindex(empty, u'x')

        # Test invalid missing cases: raise TypeError
        for empty in ({'a', 'b', 'c'}, {'a': 'aaa', 'b': 'bbb', 'c': 'ccc'}):
            with self.assertRaises(TypeError):
                rindex(empty, 'x')

        # Test invalid matching cases: raise TypeError
        for empty in ({'x', 'y', 'z'}, {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}):
            with self.assertRaises(TypeError):
                rindex(empty, 'x')

        # Test one match cases: find at first, middle and last
        self.assertEqual(rindex(b'xyz', 'x'), 0)
        self.assertEqual(rindex(b'yxz', 'x'), 1)
        self.assertEqual(rindex(b'zyx', 'x'), 2)
        self.assertEqual(rindex(b'xyz', b'x'), 0)
        self.assertEqual(rindex(b'yxz', b'x'), 1)
        self.assertEqual(rindex(b'zyx', b'x'), 2)
        self.assertEqual(rindex(u'xyz', 'x'), 0)
        self.assertEqual(rindex(u'yxz', 'x'), 1)
        self.assertEqual(rindex(u'zyx', 'x'), 2)
        self.assertEqual(rindex(u'xyz', b'x'), 0)
        self.assertEqual(rindex(u'yxz', b'x'), 1)
        self.assertEqual(rindex(u'zyx', b'x'), 2)
        self.assertEqual(rindex(['x', 'y', 'z'], 'x'), 0)
        self.assertEqual(rindex(['y', 'x', 'z'], 'x'), 1)
        self.assertEqual(rindex(['z', 'y', 'x'], 'x'), 2)
        self.assertEqual(rindex(('x', 'y', 'z'), 'x'), 0)
        self.assertEqual(rindex(('y', 'x', 'z'), 'x'), 1)
        self.assertEqual(rindex(('z', 'y', 'x'), 'x'), 2)

        # Test multiple match cases: find at middle and last
        self.assertEqual(rfind(b'xxz', 'x'), 1)
        self.assertEqual(rfind(b'xyx', 'x'), 2)
        self.assertEqual(rfind(b'xxz', b'x'), 1)
        self.assertEqual(rfind(b'xyx', b'x'), 2)
        self.assertEqual(rfind(u'xxz', 'x'), 1)
        self.assertEqual(rfind(u'xyx', 'x'), 2)
        self.assertEqual(rfind(u'xxz', b'x'), 1)
        self.assertEqual(rfind(u'xyx', b'x'), 2)
        self.assertEqual(rfind(['x', 'x', 'z'], 'x'), 1)
        self.assertEqual(rfind(['x', 'y', 'x'], 'x'), 2)
        self.assertEqual(rfind(('x', 'x', 'z'), 'x'), 1)
        self.assertEqual(rfind(('x', 'y', 'x'), 'x'), 2)

    def test_reduce_value(self):
        """ Tests reduce_value with general inputs """

        # Test None case: nothing to reduce but default applies
        self.assertEqual(reduce_value(None), EMPTY_STR)
        self.assertEqual(reduce_value(None, 'None'), 'None')

        # Test empty string case: nothing to reduce but default applies
        self.assertEqual(reduce_value(EMPTY_BIN), EMPTY_STR)
        self.assertEqual(reduce_value(EMPTY_BIN, 'None'), 'None')
        self.assertEqual(reduce_value(EMPTY_STR), EMPTY_STR)
        self.assertEqual(reduce_value(EMPTY_STR, 'None'), 'None')

        # Test empty collections case: nothing to reduce but default applies
        self.assertEqual(reduce_value(list()), EMPTY_STR)
        self.assertEqual(reduce_value(list(), 'None'), 'None')
        self.assertEqual(reduce_value(set()), EMPTY_STR)
        self.assertEqual(reduce_value(set(), 'None'), 'None')
        self.assertEqual(reduce_value(tuple()), EMPTY_STR)
        self.assertEqual(reduce_value(tuple(), 'None'), 'None')

        # Test when there's nothing to reduce
        self.assertEqual(reduce_value(0), 0)
        self.assertEqual(reduce_value(1), 1)
        self.assertEqual(reduce_value('a'), 'a')
        self.assertEqual(reduce_value('abc'), 'abc')
        self.assertEqual(reduce_value({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual(reduce_value({'b': 'bbb', 'c': 'ccc'}), {'b': 'bbb', 'c': 'ccc'})

        # Test when there's nothing to reduce, but with unused default
        self.assertEqual(reduce_value(0, None), 0)
        self.assertEqual(reduce_value(1, None), 1)
        self.assertEqual(reduce_value('a', None), 'a')
        self.assertEqual(reduce_value('abc', None), 'abc')

        # Test with reducible values
        self.assertEqual(reduce_value([None]), None)
        self.assertEqual(reduce_value([EMPTY_BIN]), EMPTY_BIN)
        self.assertEqual(reduce_value([EMPTY_STR]), EMPTY_STR)
        self.assertEqual(reduce_value([0]), 0)
        self.assertEqual(reduce_value([1]), 1)
        self.assertEqual(reduce_value(['x']), 'x')
        self.assertEqual(reduce_value({'y'}), 'y')
        self.assertEqual(reduce_value(('z',)), 'z')

        # Test with non-reducible values
        self.assertEqual(reduce_value([None, None]), [None, None])
        self.assertEqual(reduce_value([EMPTY_BIN, EMPTY_STR]), [EMPTY_BIN, EMPTY_STR])
        self.assertEqual(reduce_value([0, 0]), [0, 0])
        self.assertEqual(reduce_value([1, 1]), [1, 1])
        self.assertEqual(reduce_value(['a', 'b', 'c']), ['a', 'b', 'c'])
        self.assertEqual(reduce_value({'a', 'b', 'c'}), {'a', 'b', 'c'})
        self.assertEqual(reduce_value(('a', 'b', 'c')), ('a', 'b', 'c'))

        # Test with non-reducible collections
        self.assertEqual(reduce_value({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual([x for x in reduce_value(c for c in 'abc')], [c for c in 'abc'])

    def test_wrap_value(self):
        """ Tests wrap_value with general inputs """

        # Test when there's nothing to wrap
        self.assertEqual(wrap_value(None), [])
        self.assertEqual(wrap_value(EMPTY_BIN), [])
        self.assertEqual(wrap_value(EMPTY_STR), [])

        # Test with wrappable values
        self.assertEqual(wrap_value(0), [0])
        self.assertEqual(wrap_value(1), [1])
        self.assertEqual(wrap_value('a'), ['a'])
        self.assertEqual(wrap_value('abc'), ['abc'])
        self.assertEqual(wrap_value({'a': 'aaa'}), [{'a': 'aaa'}])
        self.assertEqual(wrap_value({'b': 'bbb', 'c': 'ccc'}), [{'b': 'bbb', 'c': 'ccc'}])

        # Test with already wrapped values
        self.assertEqual(wrap_value([0]), [0])
        self.assertEqual(wrap_value([1]), [1])
        self.assertEqual(wrap_value(['x']), ['x'])
        self.assertEqual(wrap_value({'y'}), {'y'})
        self.assertEqual(wrap_value(('z',)), ('z',))

        # Test with empty collections
        self.assertEqual(wrap_value(dict()), [])
        self.assertEqual(wrap_value(list()), [])
        self.assertEqual(wrap_value(set()), [])
        self.assertEqual(wrap_value(tuple()), [])

        # Test with non-empty collections, filtering out empty
        self.assertEqual(wrap_value([None]), [])
        self.assertEqual(wrap_value([EMPTY_BIN]), [])
        self.assertEqual(wrap_value([EMPTY_STR]), [])
        self.assertEqual(wrap_value([None, None]), [])
        self.assertEqual(wrap_value([EMPTY_BIN, EMPTY_STR]), [])

        # Test with non-empty collections, preserving empty
        self.assertEqual(wrap_value([None], include_empty=True), [None])
        self.assertEqual(wrap_value([EMPTY_BIN], include_empty=True), [EMPTY_BIN])
        self.assertEqual(wrap_value([EMPTY_STR], include_empty=True), [EMPTY_STR])
        self.assertEqual(wrap_value([None, None], include_empty=True), [None, None])
        self.assertEqual(wrap_value([EMPTY_BIN, EMPTY_STR], include_empty=True), [EMPTY_BIN, EMPTY_STR])

        # Test with non-empty collections
        self.assertEqual(wrap_value([0, 1, 2]), [0, 1, 2])
        self.assertEqual(wrap_value({0, 1, 2}), {0, 1, 2})
        self.assertEqual(wrap_value((0, 1, 2)), (0, 1, 2))
        self.assertEqual(wrap_value(['a', 'b', 'c']), ['a', 'b', 'c'])
        self.assertEqual(wrap_value({'a', 'b', 'c'}), {'a', 'b', 'c'})
        self.assertEqual(wrap_value(('a', 'b', 'c')), ('a', 'b', 'c'))

        # Test with non-wrappable collections
        self.assertEqual([x for x in wrap_value(c for c in 'abc')], [c for c in 'abc'])

    def test_reduce_wrap_value(self):
        """ Tests reduce_value after wrapping """

        values = ([0], [1], ['a'], ['abc'], [{'a': 'aaa'}], [{'b': 'bbb', 'c': 'ccc'}])
        for value in values:
            self.assertEqual(wrap_value(reduce_value(value)), value)

    def test_wrap_reduce_value(self):
        """ Tests wrap_value after reducing """

        values = (0, 1, 'a', 'abc', {'a': 'aaa'}, {'b': 'bbb', 'c': 'ccc'})
        for value in values:
            self.assertEqual(reduce_value(wrap_value(value)), value)
