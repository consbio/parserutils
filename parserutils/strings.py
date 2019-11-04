import re
import six
import string
import unicodedata


binary_type = getattr(six, 'binary_type')
six_moves = getattr(six, 'moves')
string_types = getattr(six, 'string_types')
text_type = getattr(six, 'text_type')
xrange = getattr(six_moves, 'xrange')


ALPHANUMERIC = set(string.ascii_letters + string.digits)
PUNCTUATION = set(string.punctuation)

DEFAULT_ENCODING = 'UTF-8'

EMPTY_BIN = binary_type()
EMPTY_STR = text_type()

# Reduce types to minimum possible (in Python 2 there are duplicates)
STRING_TYPE = string_types[0]
STRING_TYPES = tuple(t for t in {binary_type, STRING_TYPE})

_TO_SNAKE_REGEX_1 = re.compile(r'(.)([A-Z][a-z]+)')
_TO_SNAKE_REGEX_2 = re.compile(r'([a-z0-9])([A-Z])')
_TO_SNAKE_REGEX_3 = re.compile(r'[_]{2,}')
_TO_SNAKE_PATTERN = r'\1_\2'

_TO_CAMEL_REGEX = re.compile(r'_+([a-zA-Z0-9])')


def camel_to_constant(s):
    """ :return: s with camel segments upper cased and separated by underscores """
    return _camel_to_underscored(s, True)


def camel_to_snake(s):
    """ :return: s with camel segments lower cased and separated by underscores """
    return _camel_to_underscored(s, False)


def _camel_to_underscored(s, to_constant):
    if s is None or len(s) == 0:
        return s

    converted = _TO_SNAKE_REGEX_1.sub(_TO_SNAKE_PATTERN, s)
    converted = _TO_SNAKE_REGEX_2.sub(_TO_SNAKE_PATTERN, converted)
    converted = _TO_SNAKE_REGEX_3.sub('_', converted)

    return converted.upper() if to_constant else converted.lower()


def constant_to_camel(s):
    """ :return: the snake cased s without underscores, and each segment but the first capitalized """
    return _underscored_to_camel(s)


def snake_to_camel(s):
    """ :return: the snake cased s without underscores, and each segment but the first capitalized """
    return _underscored_to_camel(s)


def _underscored_to_camel(s):
    if s is None or len(s) == 0:
        return s

    return _TO_CAMEL_REGEX.sub(lambda match: match.group(1).upper(), s.strip('_').lower())


def find_all(s, sub, start=0, end=0, limit=-1, reverse=False):
    """
    Find all indexes of sub in s.

    :param s: the string to search
    :param sub: the string to search for
    :param start: the index in s at which to begin the search (same as in ''.find)
    :param end: the index in s at which to stop searching (same as in ''.find)
    :param limit: the maximum number of matches to find
    :param reverse: if False search s forwards; otherwise search backwards

    :return: all occurrences of substring sub in string s
    """

    indexes = []

    if not bool(s and sub):
        return indexes

    lstr = len(s)
    if lstr <= start:
        return indexes

    lsub = len(sub)
    if lstr < lsub:
        return indexes

    if limit == 0:
        return indexes
    elif limit < 0:
        limit = lstr

    end = min(end, lstr) or lstr
    idx = s.rfind(sub, start, end) if reverse else s.find(sub, start, end)

    while idx != -1:
        indexes.append(idx)
        if reverse:
            idx = s.rfind(sub, start, idx - lstr)
        else:
            idx = s.find(sub, idx + lsub, end)

        if len(indexes) >= limit:
            break

    return indexes


def splitany(s, sep=None, maxsplit=-1):
    """
    Splits "s" into substrings using "sep" as the delimiter string. Behaves like str.split, except that:

    1. Single strings are parsed into characters, any of which may be used as a delimiter
    2. Lists or tuples of multiple character strings may be provided, and thus used as delimiters

    If "sep" is None, a single character, or a list with one string, str.split is called directly.
    Otherwise, "s" is parsed iteratively until all delimiters have been found, or maxsplit has been reached.

    :param s: the unicode or binary string to split
    :param sep: a string or list of strings to use as delimiter in the split (defaults to whitespace):
        if a string, split on any char; if a list or tuple, split on any of its values
    :param maxsplit: if provided, the maximum number of splits to perform

    :return: the list of substrings in "s" between occurrences of "sep"
    """

    if s is None:
        return []
    elif not isinstance(s, STRING_TYPES):
        raise TypeError('Cannot split a {t}: {s}'.format(s=s, t=type(s).__name__))
    elif sep is None:
        return s.split(sep, maxsplit)
    elif not isinstance(sep, _split_sep_types):
        raise TypeError('Cannot split on a {t}: {s}'.format(s=sep, t=type(sep).__name__))
    else:
        split_on_any_char = isinstance(sep, STRING_TYPES)

        if split_on_any_char:
            # Python 3 compliance: sync and wrap to prevent issues with Binary: b'a'[0] == 97
            seps = [_sync_string_to(s, sep)]
        elif all(isinstance(sub, STRING_TYPES) for sub in sep):
            # Python 3 compliance: sync, but also sort keys by length to do largest matches first
            seps = [_sync_string_to(s, sub) for sub in sep]
        else:
            invalid_seps = [sub for sub in sep if not isinstance(sep, STRING_TYPES)]
            raise TypeError('Cannot split on the following: {s}'.format(s=invalid_seps))

    if len(s) == 0 or len(seps) == 0 or maxsplit == 0:
        return [s]
    elif len(seps) == 1:
        # Reduce to single char or list item
        # Call split if sep like: 'a', ['a'], ['ab']
        # Otherwise, split on any if sep like: 'ab'

        seps = seps[0]
        if not split_on_any_char or len(seps) == 1:
            return s.split(seps, maxsplit)

    as_text = isinstance(seps, _split_txt_types)
    parts = []
    start = 0
    rest = None

    try:
        while maxsplit < 0 or maxsplit >= len(parts):
            rest = s if start == 0 else rest[start:]

            # Sort based on (index_in_sep, negative_len_of_sep) to do largest matches first
            if as_text:
                stop = min((rest.index(sub), 0 - len(sub)) for sub in seps if sub in rest)
            else:
                # Python 3 compliance: iterating over bytes results in ints
                stop = min((rest.index(sub), 0 - len(bytes([sub]))) for sub in seps if sub in rest)

            parts.append(rest if maxsplit == len(parts) else rest[:stop[0]])
            start = stop[0] - stop[1]  # Skip full index of last delim

    except ValueError:
        parts.append(rest)

    return parts

_split_sep_types = STRING_TYPES + (list, tuple)
_split_txt_types = (STRING_TYPE, list, tuple)


def _sync_string_to(bin_or_str, string):
    """ Python 3 compliance: ensure two strings are the same type (unicode or binary) """

    if isinstance(string, type(bin_or_str)):
        return string
    elif isinstance(string, binary_type):
        return string.decode(DEFAULT_ENCODING)
    else:
        return string.encode(DEFAULT_ENCODING)


def to_ascii_equivalent(text):
    """ Converts any non-ASCII characters (accents, etc.) to their best-fit ASCII equivalents """

    if text is None:
        return None
    elif isinstance(text, binary_type):
        text = text.decode(DEFAULT_ENCODING)
    elif not isinstance(text, text_type):
        text = text_type(text)

    text = EMPTY_STR.join(_ASCII_PUNCTUATION_MAP.get(c, c) for c in text)
    return EMPTY_STR.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')


_ASCII_PUNCTUATION_MAP = {
    # Hyphens and dashes
    u'\u2010': u'-', u'\u2011': u'-', u'\u2012': u'-', u'\u2013': u'-', u'\u2014': u'-', u'\u2015': u'-',
    u'\uff0d': u'-', u'\uff63': u'-',
    # Single quotes
    u'\u02b9': u"'", u'\u02bb': u"'", u'\u02bc': u"'", u'\u02bd': u"'", u'\u02be': u"'", u'\u02bf': u"'",
    u'\u2018': u"'", u'\u2019': u"'", u'\u201a': u"'", u'\u201b': u"'",
    # Double quotes
    u'\u02ba': u'"', u'\u201c': u'"', u'\u201d': u'"', u'\u201e': u'"', u'\u201f': u'"', u'\u2e42': u'"',
    # Commas
    u'\u2e32': u',', u'\u2e34': u',', u'\u2e41': u',', u'\u3001': u',',
    u'\ufe10': u',', u'\ufe11': u',', u'\ufe50': u',', u'\ufe51': u',', u'\uff0c': u',', u'\uff64': u',',
}
