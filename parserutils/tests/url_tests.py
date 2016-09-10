import collections
import six
import unittest

from parserutils.collections import reduce_value
from parserutils.strings import EMPTY_BIN, EMPTY_STR
from parserutils.urls import get_base_url, update_url_params


class URLTestCase(unittest.TestCase):

    def test_get_base_url(self):
        """ Tests get_base_url with general inputs """

        # Test empty url values
        self.assertEqual(get_base_url(None), None)
        self.assertEqual(get_base_url(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(get_base_url(EMPTY_STR), EMPTY_STR)

        in_urls = (
            'http://www.google.com',
            'http://www.google.com/',
            'http://www.google.com/test/path',
            'http://www.google.com/test/path/',
            'http://www.google.com?a=aaa&c=ccc&b=bbb',
            'http://www.google.com/?a=aaa&c=ccc&b=bbb'
        )

        # Test valid url values when include_path=False
        out_url = 'http://www.google.com/'
        for url in in_urls:
            self.assertEqual(get_base_url(url), out_url)

        # Test valid url values when include_path=True
        for url in in_urls:
            self.assertEqual(get_base_url(url, True), self._parse_url(url)[0])

    def test_update_url_params(self):
        """ Tests update_url_params with general inputs """

        # Test empty values with no URL params
        self.assertEqual(update_url_params(None), None)
        self.assertEqual(update_url_params(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(update_url_params(EMPTY_STR), EMPTY_STR)

        # Test empty values with valid URL params
        self.assertEqual(update_url_params(None, t='test'), None)
        self.assertEqual(update_url_params(EMPTY_BIN, t='test'), EMPTY_BIN)
        self.assertEqual(update_url_params(EMPTY_STR, t='test'), EMPTY_STR)

        # Test valid values with no URL params (ignore trailing slash)

        base_urls = (
            'http://www.google.com',
            'http://www.google.com/',
            'http://www.google.com/test/path',
            'http://www.google.com/test/path/'
        )
        for base_url in base_urls:
            self.assertEqual(update_url_params(base_url), base_url)

        # Test valid values with single value URL params

        full_urls = (
            'http://www.google.com?a=aaa&c=ccc&b=bbb',
            'http://www.google.com/?a=aaa&c=ccc&b=bbb',
        )
        for full_url in full_urls:
            in_url, in_params = self._parse_url(full_url)

            # Test sending the same parameters

            out_url, out_params = self._parse_url(update_url_params(full_url, a='aaa', b='bbb', c='ccc'))
            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, in_params)

            out_url, out_params = self._parse_url(update_url_params(full_url, **{'a': 'aaa', 'b': 'bbb', 'c': 'ccc'}))
            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, in_params)

            # Test updating the same parameters

            new_params = {'a': 'xxx', 'b': 'yyy', 'c': 'zzz'}
            out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, new_params)

            # Test adding new parameters

            new_params = {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}
            out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

            new_params.update(in_params)

            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, new_params)

        # Test valid values with multiple value URL params

        full_urls = (
            'http://www.google.com?abc=a&abc=b&abc=c',
            'http://www.google.com/?abc=a&abc=b&abc=c',
        )
        for full_url in full_urls:
            in_url, in_params = self._parse_url(full_url)

            # Test sending the same parameters

            out_url, out_params = self._parse_url(update_url_params(full_url, abc={'a', 'b', 'c'}))
            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, in_params)

            out_url, out_params = self._parse_url(update_url_params(full_url, **{'abc': {'a', 'b', 'c'}}))
            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, in_params)

            # Test updating the same parameters

            new_params = {'abc': {'x', 'y', 'z'}}
            out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, new_params)

            # Test adding new parameters

            new_params = {'xyz': {'x', 'y', 'z'}}
            out_url, out_params = self._parse_url(update_url_params(full_url, **new_params))

            new_params.update(in_params)

            self.assertEqual(out_url, in_url)
            self.assertEqual(out_params, new_params)

    def test_update_base_url_params(self):
        """ Tests update_url_params after calling get_base_url """

        full_urls = (
            'http://www.google.com?a=aaa&c=ccc&b=bbb',
            'http://www.google.com/?a=aaa&c=ccc&b=bbb',
        )
        for full_url in full_urls:
            base_url = get_base_url(full_url)

            # Test both adding and updating parameters

            new_params = {'a': 'xxx', 'b': 'yyy', 'c': 'zzz', 'x': 'aaa', 'y': 'bbb', 'z': 'zzz'}
            out_url, out_params = self._parse_url(update_url_params(base_url, **new_params))

            self.assertEqual(out_url, base_url)
            self.assertEqual(out_params, new_params)

    def _parse_url(self, url):
        """ Simple helper for splitting basic URL's for comparison """

        if '?' in url:
            base, query = url.split('?', 1)
        else:
            base, query = url, None

        base_url = base if base.endswith('/') else base + '/'
        if not query:
            params = {}
        else:
            # Append multiple parameters under single keys as in urllib.parse_qs
            params = collections.defaultdict(set)
            for key, val in (p.split('=', 1) for p in query.split('&')):
                params[key].add(val)

        # Convert defaultdict to dict, unwrapping single parameter values as well
        return base_url, {k: reduce_value(v) for k, v in six.iteritems(params)}
