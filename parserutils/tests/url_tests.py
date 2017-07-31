import six
import unittest

from parserutils.collections import reduce_value, wrap_value
from parserutils.strings import EMPTY_BIN, EMPTY_STR
from parserutils.urls import _urllib_parse
from parserutils.urls import clear_cache, get_base_url, update_url_params
from parserutils.urls import url_to_parts, parts_to_url


iteritems = getattr(six, 'iteritems')


try:
    from urllib.parse import _parse_cache
except ImportError:
    from urlparse import _parse_cache


class URLTestCase(unittest.TestCase):

    def test_get_base_url(self):
        """ Tests get_base_url with general inputs """

        # Test empty url values
        self.assertEqual(get_base_url(None), None)
        self.assertEqual(get_base_url(EMPTY_BIN), None)
        self.assertEqual(get_base_url(EMPTY_STR), None)
        self.assertEqual(get_base_url([]), None)

        in_urls = (
            'http://www.get_base_url.com',
            'http://www.get_base_url.com/',
            'http://www.get_base_url.com/test/path',
            'http://www.get_base_url.com/test/path/',
            'http://www.get_base_url.com?a=aaa&c=ccc&b=bbb',
            'http://www.get_base_url.com/?a=aaa&c=ccc&b=bbb'
        )

        # Test valid url values when include_path=False
        out_url = 'http://www.get_base_url.com/'
        for url in in_urls:
            self.assertEqual(get_base_url(url), out_url)

        # Test valid url values when include_path=True
        for url in in_urls:
            self.assertEqual(get_base_url(url, True), self._parse_url(url)[0])

        self.assertTrue(len(_parse_cache))
        clear_cache()
        self.assertFalse(len(_parse_cache))

    def test_update_url_params(self):
        """ Tests update_url_params with general inputs """

        # Test empty values with no URL params
        self.assertEqual(update_url_params(None), None)
        self.assertEqual(update_url_params(EMPTY_BIN), None)
        self.assertEqual(update_url_params(EMPTY_STR), None)
        self.assertEqual(update_url_params([]), None)

        # Test empty values with valid URL params
        self.assertEqual(update_url_params(None, t='test'), None)
        self.assertEqual(update_url_params(EMPTY_BIN, t='test'), None)
        self.assertEqual(update_url_params(EMPTY_STR, t='test'), None)

        # Test valid values with no URL params (ignore trailing slash)

        base_urls = (
            'http://www.update_url_params.com',
            'http://www.update_url_params.com/',
            'http://www.update_url_params.com/test/path',
            'http://www.update_url_params.com/test/path/'
        )
        for base_url in base_urls:
            self.assertEqual(update_url_params(base_url), base_url)

        # Test valid values with single value URL params

        full_urls = (
            'http://www.update_url_params.com?a=aaa&c=ccc&b=bbb',
            'http://www.update_url_params.com/?a=aaa&c=ccc&b=bbb',
        )
        for full_url in full_urls:
            in_url, in_params = self._parse_url(full_url)

            params = [
                ('same', {'a': 'aaa', 'b': 'bbb', 'c': 'ccc'}),  # Test sending the same parameters
                ('diff', {'a': 'xxx', 'b': 'yyy', 'c': 'zzz'}),  # Test updating the same parameters
                ('add', {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}),   # Test adding new parameters
                ('rep', {'replace_all': 0}),                     # Test with "replace_all" when not "False"
                ('rep', {'replace_all': 1}),                     # Test with "replace_all" when not "True"
                ('opt', {'replace_all': False}),                 # Test with "replace_all" option disabled
                ('opt', {'x': 'xxx', 'y': 'yyy', 'z': 'zzz', 'replace_all': True})  # Test with "replace_all" option
            ]

            for comp, new_params in params:
                out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

                if comp == 'add':
                    new_params.update(in_params)
                elif comp == 'rep':
                    new_params.update(in_params)
                    new_params['replace_all'] = str(new_params['replace_all'])
                elif comp == 'opt':
                    if not new_params.pop('replace_all'):
                        new_params.update(in_params)

                self.assertEqual(out_url, in_url)
                self.assertEqual(out_params, in_params if comp == 'same' else new_params)

        # Test valid values with multiple value URL params

        full_urls = (
            'http://www.update_url_params.com?abc=a&abc=b&abc=c',
            'http://www.update_url_params.com/?abc=a&abc=b&abc=c',
        )
        for full_url in full_urls:
            in_url, in_params = self._parse_url(full_url)

            params = [
                ('same', {'abc': {'a', 'b', 'c'}}),  # Test sending the same parameters
                ('diff', {'abc': {'x', 'y', 'z'}}),  # Test updating the same parameters
                ('add', {'xyz': {'x', 'y', 'z'}}),   # Test adding new parameters
                ('rep', {'replace_all': {0, 1}}),    # Test with "replace_all" when neither "True" nor "False"
                ('opt', {'replace_all': False}),     # Test with "replace_all" option disabled
                ('opt', {'xyz': {'x', 'y', 'z'}, 'replace_all': True})    # Test with "replace_all" option
            ]

            for comp, new_params in params:
                out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

                if comp == 'add':
                    new_params.update(in_params)
                elif comp == 'rep':
                    new_params.update(in_params)
                    new_params['replace_all'] = set(str(v) for v in new_params['replace_all'])
                elif comp == 'opt':
                    if not new_params.pop('replace_all'):
                        new_params.update(in_params)

                self.assertEqual(out_url, in_url)
                self.assertEqual(out_params, in_params if comp == 'same' else new_params)

        self.assertTrue(len(_parse_cache))
        clear_cache()
        self.assertFalse(len(_parse_cache))

    def test_update_base_url_params(self):
        """ Tests update_url_params after calling get_base_url """

        full_urls = (
            'http://www.update_url_params.com?a=aaa&c=ccc&b=bbb',
            'http://www.update_url_params.com/?a=aaa&c=ccc&b=bbb',
        )
        for full_url in full_urls:
            base_url = get_base_url(full_url)

            # Test both adding and updating parameters

            new_params = {'a': 'xxx', 'b': 'yyy', 'c': 'zzz', 'x': 'aaa', 'y': 'bbb', 'z': 'zzz'}
            out_url, out_params = self._parse_url(update_url_params(base_url, **new_params))

            self.assertEqual(out_url, base_url)
            self.assertEqual(out_params, new_params)

    def _parse_url(self, url):
        """ Simple helper for splitting URL's for comparison """

        # Use url_lib functions to get first the base URL and then the query
        base_url = _urllib_parse.urlunsplit(_urllib_parse.urlsplit(url)[:3] + ('', ''))
        url_params = _urllib_parse.parse_qs(_urllib_parse.urlsplit(url)[3])

        # Ensure base URL ends with '/', and that query will be a set for reliable comparisons
        base_url = base_url if base_url.endswith('/') else base_url + '/'
        url_params = {k: reduce_value(set(wrap_value(v))) for k, v in iteritems(url_params)}

        return base_url, url_params

    def test_url_to_parts(self):
        """ Tests url_to_parts with general inputs """

        urlsplit = _urllib_parse.urlsplit

        # Test empty values
        self.assertEqual(url_to_parts(None), None)
        self.assertEqual(url_to_parts(EMPTY_BIN), None)
        self.assertEqual(url_to_parts(EMPTY_STR), None)
        self.assertEqual(url_to_parts([]), None)
        self.assertEqual(url_to_parts({}), None)

        simple_urls = (
            'http://www.url_to_parts.com',
            'http://www.url_to_parts.com/',
            'http://www.url_to_parts.com:8080/',
            'http://www.url_to_parts.com#a=aaa&c=ccc&b=bbb',
            'http://www.url_to_parts.com/#a=aaa&c=ccc&b=bbb#'
        )

        for url in simple_urls:
            parts = url_to_parts(url)
            split = urlsplit(url)

            self.assertEqual(parts.path, [])
            self.assertEqual(parts.query, {})

            self.assertEqual(parts.scheme, split.scheme)
            self.assertEqual(parts.netloc, split.netloc)
            self.assertEqual(parts.fragment, split.fragment)

        complex_urls = (
            'http://www.url_to_parts.com/test/path',
            'http://www.url_to_parts.com/test/path/',
            'http://www.url_to_parts.com?a=aaa&c=ccc&b=bbb',
            'http://www.url_to_parts.com/?a=aaa&c=ccc&b=bbb',
            'http://www.url_to_parts.com?a=aaa&c=ccc&b=bbb#x=xxx&y=yyy&z=zzz',
            'http://www.url_to_parts.com/test/path?a=aaa&c=ccc&b=bbb#x=xxx&y=yyy&z=zzz'
        )

        for url in complex_urls:
            parts = url_to_parts(url)
            split = urlsplit(url)

            # Test string values from complex urls
            self.assertEqual(parts.scheme, split.scheme)
            self.assertEqual(parts.netloc, split.netloc)
            self.assertEqual(parts.fragment, split.fragment)

            # Test path and query values from complex urls

            self.assertTrue(parts.path or parts.query)

            if parts.path:
                self.assertEqual(parts.path, ['test', 'path'])
            else:
                self.assertEqual(parts.path, [])

            if parts.query:
                self.assertEqual(parts.query, {'a': ['aaa'], 'b': ['bbb'], 'c': ['ccc']})
            else:
                self.assertEqual(parts.query, {})

        url = 'http://www.url_to_parts.com/test/path/again?a=aaa&c=ccc&b=bbb&a=xxx&c=yyy&b=zzz#x=aaa&y=bbb&z=ccc'
        parts = url_to_parts(url)
        split = urlsplit(url)

        # Test all values from especially complex url
        self.assertEqual(parts.scheme, split.scheme)
        self.assertEqual(parts.netloc, split.netloc)
        self.assertEqual(parts.path, ['test', 'path', 'again'])
        self.assertEqual(parts.query, {'a': ['aaa', 'xxx'], 'b': ['bbb', 'zzz'], 'c': ['ccc', 'yyy']})
        self.assertEqual(parts.fragment, split.fragment)

    def test_parts_to_url(self):
        """ Tests parts_to_url with general inputs """

        SplitResult = _urllib_parse.SplitResult
        urlsplit = _urllib_parse.urlsplit

        # Test empty values
        self.assertEqual(parts_to_url(), None)
        self.assertEqual(parts_to_url(None), None)
        self.assertEqual(parts_to_url(EMPTY_BIN), None)
        self.assertEqual(parts_to_url(EMPTY_STR), None)
        self.assertEqual(parts_to_url([]), None)
        self.assertEqual(parts_to_url({}), None)

        # Test with parts coming from urlsplit

        url = 'http://netloc/path?query=true#frag'

        self.assertEqual(parts_to_url(urlsplit(url)), url)                    # as SplitResult
        self.assertEqual(parts_to_url(None, *urlsplit(url)), url)             # as ordered args
        self.assertEqual(parts_to_url(urlsplit(url)._asdict()), url)          # as dict
        self.assertEqual(parts_to_url(None, **urlsplit(url)._asdict()), url)  # as keyword args

        # Test urls with different parameter configurations

        url_data = {
            'http://one.parts_to_url.com/': {'netloc': 'one.parts_to_url.com'},
            'http://two.parts_to_url.com/': {'scheme': 'http', 'netloc': 'two.parts_to_url.com'},
            'http://www.parts_to_url.com/': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com', 'path': [], 'query': {}, 'fragment': ''
            },
            'http://www.parts_to_url.com:8080/': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com:8080', 'path': [], 'query': {}, 'fragment': ''
            },
            'http://www.parts_to_url.com:8080/?a=aaa': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com:8080',
                'path': [], 'query': {'a': 'aaa'}, 'fragment': ''
            },
            'http://www.parts_to_url.com/#x=xxx&y=yyy&z=zzz': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': [], 'query': {}, 'fragment': 'x=xxx&y=yyy&z=zzz'
            },
            'http://www.parts_to_url.com/#x=xxx&y=yyy&z=zzz#': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': [], 'query': {}, 'fragment': 'x=xxx&y=yyy&z=zzz#'
            },
            'http://www.parts_to_url.com/test/path': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path'], 'query': {}, 'fragment': ''
            },
            'http://www.parts_to_url.com/test/path': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path'], 'query': {}, 'fragment': ''
            },
            'http://www.parts_to_url.com/test/path?b=bbb': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path'], 'query': {'b': 'bbb'}, 'fragment': ''
            },
            'http://www.parts_to_url.com/test/path?c=ccc#x=xxx&y=yyy&z=zzz': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path'], 'query': {'c': 'ccc'}, 'fragment': 'x=xxx&y=yyy&z=zzz'
            },
            'http://www.parts_to_url.com/?c=ccc&b=bbb&a=aaa': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': [], 'query': (('c', ['ccc']), ('b', ['bbb']), ('a', ['aaa'])), 'fragment': ''
            },
            'http://www.parts_to_url.com/?c=ccc&b=bbb&a=aaa#x=xxx&y=yyy&z=zzz': {
                'scheme': 'http', 'netloc': 'www.parts_to_url.com',
                'path': [], 'query': (('c', ['ccc']), ('b', ['bbb']), ('a', ['aaa'])), 'fragment': 'x=xxx&y=yyy&z=zzz'
            },
            'http://www.parts_to_url.com/test/path?c=ccc&b=bbb&a=aaa#x=xxx&y=yyy&z=zzz': {
                'scheme': 'http',
                'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path'],
                'query': (('c', ['ccc']), ('b', ['bbb']), ('a', ['aaa'])),
                'fragment': 'x=xxx&y=yyy&z=zzz'
            },
            'http://www.parts_to_url.com/test/path/again?c=ccc&c=yyy&a=aaa&a=xxx&b=zzz&b=bbb#x=aaa&y=bbb&z=ccc': {
                'scheme': 'http',
                'netloc': 'www.parts_to_url.com',
                'path': ['test', 'path', 'again'],
                'query': (('c', ['ccc', 'yyy']), ('a', ['aaa', 'xxx']), ('b', ['zzz', 'bbb'])),
                'fragment': 'x=aaa&y=bbb&z=ccc'
            }
        }

        for url, data in iteritems(url_data):
            valid = [
                data.get('scheme', 'http'),
                data.get('netloc', ''),
                data.get('path', '/'),
                data.get('query', ''),
                data.get('fragment', '')
            ]
            parts = SplitResult(*valid)

            # Test with parts=dict
            self.assertEqual(parts_to_url(data), url)

            # Test with parts=SplitResult
            self.assertEqual(parts_to_url(parts), url)

            if len(data) == 5:
                # Test with individual parameterized args
                self.assertEqual(parts_to_url(**data), url)

            # Test with a valid list of ordered args
            self.assertEqual(parts_to_url(None, *valid), url)

            # Test with an invalid list of ordered args

            # Corrupt lists and strings by doubling them, and dicts by reordering them
            invalid = [dict(d) if isinstance(d, (dict, tuple)) else d * 2 for d in valid]

            # Ensure invalid are corrupt, then that they are ignored
            self.assertNotEqual(parts_to_url(None, *invalid), url)
            self.assertEqual(parts_to_url(parts, *invalid), url)
