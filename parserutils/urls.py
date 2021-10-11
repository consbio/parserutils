from urllib.parse import SplitResult, parse_qs, unquote, urlencode, urlsplit, urlunsplit


def get_base_url(url, include_path=False):
    """ :return: the url without the query or fragment segments, but always with trailing slash """

    if not url:
        return None

    parts = urlsplit(url)
    base_url = urlunsplit((
        parts.scheme, parts.netloc, (parts.path if include_path else ''), None, None
    ))

    return base_url.strip('/')


def has_trailing_slash(url):
    """ :return: true if the part of the url before parameters ends with a slash, false otherwise """

    return False if not url else url.split('?', 1)[0].split('#', 1)[0].endswith('/')


def update_url_params(url, replace_all=False, **url_params):
    """ :return: url with its query updated from url_query (non-matching params are retained) """

    # Ensure 'replace_all' can be sent as a url param
    if not (replace_all is True or replace_all is False):
        url_params['replace_all'] = replace_all

    if not url or not url_params:
        return url or None

    scheme, netloc, url_path, url_query, fragment = urlsplit(url)

    if replace_all is True:
        url_query = url_params
    else:
        url_query = parse_qs(url_query)
        url_query.update(url_params)

    return urlunsplit((scheme, netloc, url_path, unquote(urlencode(url_query, doseq=True)), fragment))


def url_to_parts(url):
    """ Split url urlsplit style, but return path as a list and query as a dict """

    if not url:
        return None

    scheme, netloc, path, query, fragment = urlsplit(url)

    if not path or path == '/':
        path = []
    else:
        path = path.strip('/').split('/')

    if not query:
        query = {}
    else:
        query = parse_qs(query)

    return SplitResult(scheme, netloc, path, query, fragment)


def parts_to_url(parts=None, scheme=None, netloc=None, path=None, query=None, fragment=None, trailing_slash=None):
    """
    Build url urlunsplit style, but optionally handle path as a list and/or query as a dict
    :param parts: a SplitResult of urlsplit, or a dict with keys corresponding to the same
    :param scheme..fragment: the individual values contained in a urlsplit SplitResult
    :param trailing_slash: if True, add a slash after path; if False, remove it; otherwise, leave it as is
    """

    if isinstance(parts, SplitResult):
        scheme, netloc, path, query, fragment = parts
    elif parts and isinstance(parts, dict):
        scheme = parts.get('scheme', 'http')
        netloc = parts.get('netloc', '')
        path = parts.get('path', [])
        query = parts.get('query', {})
        fragment = parts.get('fragment', '')

    if isinstance(path, (list, tuple)):
        path = '/'.join(path)

    if trailing_slash is not None:
        path = path or '/'
        if trailing_slash and not path.endswith('/'):
            path += '/'
        if not trailing_slash and path.endswith('/'):
            path = path.rstrip('/')

    if isinstance(query, (dict, tuple)):
        query = unquote(urlencode(query, doseq=True))

    return urlunsplit((scheme, netloc, path, query, fragment)) or None
