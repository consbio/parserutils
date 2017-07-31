import six

try:
    from urllib.parse import clear_cache as _clear_cache
except ImportError:
    from urlparse import clear_cache as _clear_cache


_six_moves = getattr(six, 'moves')
_urllib_parse = getattr(_six_moves, 'urllib_parse')

_parse_qs = _urllib_parse.parse_qs
_unquote = _urllib_parse.unquote
_urlencode = _urllib_parse.urlencode
_urlsplit = _urllib_parse.urlsplit
_urlunsplit = _urllib_parse.urlunsplit


def clear_cache():
    """ Clear the urllib parse cache """
    _clear_cache()


def get_base_url(url, include_path=False):
    """ :return: the url without the query or fragment segments """

    if not url:
        return None

    parts = _urlsplit(url)
    base_url = _urlunsplit((
        parts.scheme, parts.netloc, (parts.path if include_path else ''), None, None
    ))

    return base_url if base_url.endswith('/') else base_url + '/'


def update_url_params(url, replace_all=False, **url_params):
    """ :return: url with its query updated from url_query (non-matching params are retained) """

    # Ensure 'replace_all' can be sent as a url param
    if not (replace_all is True or replace_all is False):
        url_params['replace_all'] = replace_all

    if not url or not url_params:
        return url or None

    scheme, netloc, url_path, url_query, fragment = _urlsplit(url)

    if replace_all is True:
        url_query = url_params
    else:
        url_query = _parse_qs(url_query)
        url_query.update(url_params)

    return _urlunsplit((scheme, netloc, url_path, _unquote(_urlencode(url_query, doseq=True)), fragment))


def url_to_parts(url):
    """ Split url urlsplit style, but return path as a list and query as a dict """

    if not url:
        return None

    scheme, netloc, path, query, fragment = _urlsplit(url)

    if not path or path == '/':
        path = []
    else:
        path = path.strip('/').split('/')

    if not query:
        query = {}
    else:
        query = _parse_qs(query)

    return _urllib_parse.SplitResult(scheme, netloc, path, query, fragment)


def parts_to_url(parts=None, scheme=None, netloc=None, path=None, query=None, fragment=None):
    """ Build url urlunsplit style, but optionally handle path as a list and/or query as a dict """

    if isinstance(parts, _urllib_parse.SplitResult):
        scheme, netloc, path, query, fragment = parts
    elif parts and isinstance(parts, dict):
        scheme = parts.get('scheme', 'http')
        netloc = parts.get('netloc', '')
        path = parts.get('path', [])
        query = parts.get('query', {})
        fragment = parts.get('fragment', '')

    if isinstance(path, (list, tuple)):
        path = '/' + '/'.join(path).strip('/')
    if isinstance(query, (dict, tuple)):
        query = _unquote(_urlencode(query, doseq=True))

    return _urlunsplit((scheme, netloc, path, query, fragment)) or None
