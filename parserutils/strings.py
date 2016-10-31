import re
import unicodedata

from string import ascii_letters, digits, punctuation
from six import binary_type, text_type, string_types


_STRING_TYPES = (binary_type, string_types)

ALPHANUMERIC = set(ascii_letters + digits)
PUNCTUATION = set(punctuation)

DEFAULT_ENCODING = 'UTF-8'

EMPTY_BIN = binary_type()
EMPTY_STR = text_type()

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
