import six

parse = getattr(six.moves, 'urllib_parse')

parse_qsl = parse.parse_qsl
urlencode = parse.urlencode
urlsplit = parse.urlsplit
urlunsplit = parse.urlunsplit


def get_base_url(url):
    """ :return: the url without the query or fragment segments """

    if url is None or len(url) == 0:
        return url

    split_url = urlsplit(url)
    return urlunsplit((split_url.scheme, split_url.netloc, split_url.path, None, None))


def update_url_params(url, **url_params):
    """ :return: url with its query updated from url_params (non-matching params are retained) """

    if url is None or len(url) == 0 or len(url_params) == 0:
        return url

    split_url = urlsplit(url)
    url_query = dict(parse_qsl(split_url[3]))
    url_query.update(url_params)
    return urlunsplit((split_url.scheme, split_url.netloc, split_url.path, urlencode(url_query), None))
