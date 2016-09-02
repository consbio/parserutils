import unittest

from parserutils.strings import EMPTY_BIN, EMPTY_STR
from parserutils.url import get_base_url, update_url_params


class URLTestCase(unittest.TestCase):

    def test_get_base_url(self):
        """ Tests get_base_url with general inputs """

        # Test empty url values
        self.assertEqual(get_base_url(None), None)
        self.assertEqual(get_base_url(EMPTY_BIN), EMPTY_BIN)
        self.assertEqual(get_base_url(EMPTY_STR), EMPTY_STR)

        # Test valid url values with no params

        base_urls = (
            'http://www.google.com',
            'http://www.google.com/',
        )
        for base_url in base_urls:
            self.assertEqual(get_base_url(base_url), base_url)

        # Test valid url values with standard params

        full_urls = (
            'http://www.google.com?a=aaa&c=ccc&b=bbb',
            'http://www.google.com/?a=aaa&c=ccc&b=bbb',
        )
        for full_url in full_urls:
            base_url = self._parse_url(full_url)[0]
            self.assertEqual(get_base_url(full_url), base_url)

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

        # Test valid values with no URL params

        base_url = 'http://www.google.com/'

        self.assertEqual(update_url_params(base_url), base_url)
        self.assertEqual(update_url_params(base_url.strip('/')), base_url.strip('/'))

        # Test valid values with valid URL params

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

        base_url, params = url.split('?', 1)
        return base_url, dict(p.split('=', 1) for p in params.split('&'))


if __name__ == '__main__':
    unittest.main()
