import unittest

from parserutils.collections import accumulate, setdefaults
from parserutils.collections import filter_empty, reduce_value, wrap_value
from parserutils.strings import EMPTY_BIN, EMPTY_STR


class DictsTestCase(unittest.TestCase):

    def test_accumulate(self):
        """ Tests accumulate with general inputs """

        # Test with empty items
        self.assertEqual(accumulate(None), {})
        self.assertEqual(accumulate(EMPTY_BIN), {})
        self.assertEqual(accumulate(EMPTY_STR), {})
        self.assertEqual(accumulate(dict()), {})
        self.assertEqual(accumulate(list()), {})
        self.assertEqual(accumulate(set()), {})
        self.assertEqual(accumulate(tuple()), {})
        self.assertEqual(accumulate(x for x in EMPTY_BIN), {})
        self.assertEqual(accumulate((x for x in EMPTY_STR)), {})

        # Test with items containing single key/val
        self.assertEqual(accumulate({(None, None)}), {None: [None]})
        self.assertEqual(accumulate([(EMPTY_BIN, EMPTY_STR)]), {EMPTY_BIN: [EMPTY_STR]})
        self.assertEqual(accumulate(([EMPTY_STR, EMPTY_BIN],)), {EMPTY_STR: [EMPTY_BIN]})
        self.assertEqual(accumulate((k, v) for k, v in [['key', 'val']]), {'key': ['val']})
        self.assertEqual(accumulate(((k, v) for k, v in [(0, 1)])), {0: [1]})

        # Test with items containing single key/val, reducing each
        self.assertEqual(accumulate({(None, None)}, reduce_each=True), {None: None})
        self.assertEqual(accumulate([(EMPTY_BIN, EMPTY_STR)], reduce_each=True), {EMPTY_BIN: EMPTY_STR})
        self.assertEqual(accumulate(([EMPTY_STR, EMPTY_BIN],), reduce_each=True), {EMPTY_STR: EMPTY_BIN})
        self.assertEqual(accumulate(((k, v) for k, v in [['key', 'val']]), reduce_each=True), {'key': 'val'})
        self.assertEqual(accumulate(((k, v) for k, v in [(0, 1)]), reduce_each=True), {0: 1})

        # Test with items containing single vals under multiple keys, with and without reduction
        self.assertEqual(
            accumulate([('key1', 'val'), ('key2', 'val'), ('key3', 'val')]),
            {'key1': ['val'], 'key2': ['val'], 'key3': ['val']}
        )
        self.assertEqual(
            accumulate([('key1', 'val'), ('key2', 'val'), ('key3', 'val')], reduce_each=True),
            {'key1': 'val', 'key2': 'val', 'key3': 'val'}
        )

        # Test with items containing multiple vals under a single key, with and without reduction
        self.assertEqual(
            accumulate([('key', 'val1'), ('key', 'val2'), ('key', 'val3')]),
            {'key': ['val1', 'val2', 'val3']}
        )
        self.assertEqual(
            accumulate([('key', 'val1'), ('key', 'val2'), ('key', 'val3')], reduce_each=True),
            {'key': ['val1', 'val2', 'val3']}
        )
        self.assertEqual(
            accumulate(
                [('key', 'val1'), ('key', 'val2'), ('key2', ['val1', 'val2']), ('key3', 'val3')], reduce_each=True
            ),
            {'key': ['val1', 'val2'], 'key2': ['val1', 'val2'], 'key3': 'val3'}
        )

        # Test with items containing multiple vals under multiple keys, with and without reduction
        self.assertEqual(
            accumulate([('key3', 'val1'), ('key2', 'val2'), ('key1', 'val3')]),
            {'key1': ['val3'], 'key2': ['val2'], 'key3': ['val1']}
        )
        self.assertEqual(
            accumulate([('key3', 'val1'), ('key2', 'val2'), ('key1', 'val3')], reduce_each=True),
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
        self.assertEqual(setdefaults({}, {'d': 'ddd'}), {'d': 'ddd'})
        self.assertEqual(setdefaults({}, [{'e': 'eee'}, {'f': 'fff'}]), {'e': 'eee', 'f': 'fff'})
        self.assertEqual(setdefaults({}, {'x': 'xxx', 'y': 'yyy'}), {'x': 'xxx', 'y': 'yyy'})
        self.assertEqual(setdefaults({'z': 'zzz'}, None), {'z': 'zzz'})

    def test_setdefaults_str(self):
        """ Tests setdefaults with defaults specified as strings """

        d = {}
        inputs, outputs = 'a.b', {'a': {'b': None}}
        self.assertEqual(setdefaults(d, inputs), outputs)

        d = {'a': 'xxx'}
        self.assertEqual(setdefaults(d, inputs), d)

        d = {'a': {'b': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs), d)

        d = {'c': 'xxx'}
        self.assertEqual(setdefaults(d, inputs)['a'], outputs['a'])

    def test_setdefaults_dict_nested(self):
        """ Tests setdefaults with nested defaults specified as dicts """

        d = {}
        inputs = {'a.b': 'bbb', 'a.c': 'ccc'}
        outputs = {'a': {'b': 'bbb', 'c': 'ccc'}}
        self.assertEqual(setdefaults(d, inputs), outputs)

        d = {'a': 'aaa'}
        self.assertEqual(setdefaults(d, inputs), d)

        d = {'a': {'b': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs)['a']['c'], outputs['a']['c'])
        self.assertEqual(setdefaults(d, inputs)['a']['b'], d['a']['b'])

        d = {'a': {'c': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs)['a']['b'], outputs['a']['b'])
        self.assertEqual(setdefaults(d, inputs)['a']['c'], d['a']['c'])

        d = {'c': 'ccc'}
        self.assertEqual(setdefaults(d, inputs)['a'], outputs['a'])
        self.assertEqual(setdefaults(d, inputs)['a']['c'], d['a']['c'])

    def test_setdefaults_dict_overlapping(self):
        """ Tests setdefaults with overlapping defaults specified as dicts """

        d = {}
        inputs = {'a.b.c': 'ccc', 'a.c.d.e': 'eee'}
        outputs = {'a': {'b': {'c': 'ccc'}, 'c': {'d': {'e': 'eee'}}}}
        self.assertEqual(setdefaults(d, inputs), outputs)

        d = {'a': 'xxx'}
        self.assertEqual(setdefaults(d, inputs), d)

        d = {'a': {'b': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs)['a']['b'], d['a']['b'])
        self.assertEqual(setdefaults(d, inputs)['a']['c'], outputs['a']['c'])

        d = {'a': {'c': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs)['a']['b'], outputs['a']['b'])
        self.assertEqual(setdefaults(d, inputs)['a']['c'], d['a']['c'])

        d = {'c': 'xxx'}
        self.assertEqual(setdefaults(d, inputs)['a'], outputs['a'])
        self.assertEqual(setdefaults(d, inputs)['c'], d['c'])

    def test_setdefaults_other(self):
        """ Tests setdefaults with defaults specified as list, set, and tuple """

        d = {}
        inputs, outputs = ['a.b', 'a.c'], {'a': {'b': None, 'c': None}}
        self.assertEqual(setdefaults(d, inputs), outputs)

        d = {'a': 'xxx'}
        self.assertEqual(setdefaults(d, inputs), d)

        d = {'a': {'b': 'xxx'}}
        self.assertEqual(setdefaults(d, inputs)['a']['b'], d['a']['b'])
        self.assertEqual(setdefaults(d, inputs)['a']['c'], outputs['a']['c'])

        d = {'c': 'ccc'}
        self.assertEqual(setdefaults(d, inputs)['a'], outputs['a'])
        self.assertEqual(setdefaults(d, inputs)['c'], d['c'])


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

        # Test when there's nothing to filter
        self.assertEqual(filter_empty(0), 0)
        self.assertEqual(filter_empty(1), 1)
        self.assertEqual(filter_empty('a'), 'a')
        self.assertEqual(filter_empty('abc'), 'abc')
        self.assertEqual(filter_empty({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual(filter_empty({'b': 'bbb', 'c': 'ccc'}), {'b': 'bbb', 'c': 'ccc'})

        # Test when there's nothing to filter, but with unused default
        self.assertEqual(filter_empty(0, None), 0)
        self.assertEqual(filter_empty(1, None), 1)
        self.assertEqual(filter_empty('a', None), 'a')
        self.assertEqual(filter_empty('abc', None), 'abc')

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

        # Test with filterable values and defaults
        self.assertEqual(filter_empty([None, EMPTY_BIN, EMPTY_STR], {}), {})
        self.assertEqual(filter_empty({EMPTY_BIN, None, EMPTY_STR}, []), [])
        self.assertEqual(filter_empty((EMPTY_BIN, EMPTY_STR, None), []), [])
        self.assertEqual(filter_empty([list(), set(), tuple(), dict()], {}), {})
        self.assertEqual(filter_empty((tuple(), dict(), list(), set()), []), [])
        self.assertEqual(filter_empty({tuple(), filter_empty(tuple(), tuple())}, []), [])

        # Test with values that should not be filtered
        self.assertEqual(filter_empty([0]), [0])
        self.assertEqual(filter_empty([1]), [1])
        self.assertEqual(filter_empty(['x']), ['x'])
        self.assertEqual(filter_empty({'y'}), {'y'})
        self.assertEqual(filter_empty(('z',)), ('z',))

        # Test with combinations of values
        self.assertEqual(filter_empty([None, 0, EMPTY_STR, 1]), [0, 1])
        self.assertEqual(filter_empty(['a', None, 'b', EMPTY_BIN, 'c']), ['a', 'b', 'c'])
        self.assertEqual(filter_empty({None, EMPTY_STR, 'a', 'b', 'c'}), {'a', 'b', 'c'})
        self.assertEqual(filter_empty(('a', 'b', None, 'c', EMPTY_BIN)), ('a', 'b', 'c'))

        # Test with non-filterable collections
        self.assertEqual(filter_empty({'a': 'aaa'}), {'a': 'aaa'})
        self.assertEqual([x for x in filter_empty(c for c in 'abc')], [c for c in 'abc'])

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


if __name__ == '__main__':
    unittest.main()
