import re
import six
import string
import unicodedata

from six import binary_type, text_type

xrange = getattr(six.moves, 'xrange')


ALPHANUMERIC = set(string.ascii_letters + string.digits)
PUNCTUATION = set(string.punctuation)

DEFAULT_ENCODING = 'UTF-8'

EMPTY_BIN = six.binary_type()
EMPTY_STR = six.text_type()

# Reduce types to minimum possible (in Python 2 there are duplicates)
STRING_TYPES = tuple(t for t in {six.binary_type, six.string_types[0]})


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


def splitany(s, sep, maxsplit=-1):

    if s is None:
        return []
    elif not isinstance(s, STRING_TYPES):
        raise TypeError('Cannot split a {t}: {s}'.format(s=s, t=type(s).__name__))
    elif not isinstance(sep, STRING_TYPES):
        raise TypeError('Cannot split on a {t}: {s}'.format(s=sep, t=type(sep).__name__))

    if not isinstance(s, type(sep)):
        # Python 3 compliance: ensure "s" and "sep" are either both unicode or both binary
        transform = sep.decode if isinstance(sep, binary_type) else sep.encode
        sep = transform(DEFAULT_ENCODING)

    if len(s) == 0 or len(sep) == 0 or maxsplit == 0:
        return [s]
    elif len(sep) == 1:
        return s.split(sep, maxsplit)

    parts = []
    start = 0
    rest = None

    try:
        while maxsplit < 0 or maxsplit >= len(parts):
            rest = s if start == 0 else rest[start:]
            stop = min(rest.index(sub) for sub in sep if sub in rest)

            parts.append(rest if maxsplit == len(parts) else rest[:stop])
            start = stop + 1  # Skip index of last delim

    except ValueError:
        parts.append(rest)

    return parts

_split_sep_types = STRING_TYPES


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
    u'\u2010': u'-', u'\u2011': u'-',                   # Hyphens
    u'\u2012': u'-', u'\u2013': u'-', u'\u2014': u'-',  # Dashes
    u'\u02b9': u"'", u'\u02bb': u"'", u'\u02bc': u"'",  # Single Quotes
    u'\u02bd': u"'", u'\u2018': u"'", u'\u2019': u"'",  # Single Quotes
    u'\u02ba': u'"', u'\u201d': u'"', u'\u201c': u'"',  # Double Quotes
    u'\u3001': u',',                                    # Commas
    u'\u2e32': u',', u'\u2e34': u',', u'\u2e41': u',',  # Commas
    u'\ufe11': u',', u'\ufe10': u',', u'\ufe50': u',',  # Commas
    u'\ufe51': u',', u'\uff64': u',', u'\uff0c': u',',  # Commas
}
