import re

from string import ascii_letters, digits
from six import binary_type, text_type


ALPHANUMERIC = set(ascii_letters + digits)

EMPTY_BIN = binary_type()
EMPTY_STR = text_type()

TO_SNAKE_REGEX_1 = re.compile(r'(.)([A-Z][a-z]+)')
TO_SNAKE_REGEX_2 = re.compile(r'([a-z0-9])([A-Z])')
TO_SNAKE_REGEX_3 = re.compile(r'[_]{2,}')
TO_SNAKE_PATTERN = r'\1_\2'

TO_CAMEL_REGEX = re.compile(r'_+([a-zA-Z0-9])')

XML_OBJECT_KEYS = {'type', 'value'}


def camel_to_constant(s):
    """ :return: s with camel segments upper cased and separated by underscores """
    return _camel_to_underscored(s, True)


def camel_to_snake(s):
    """ :return: s with camel segments lower cased and separated by underscores """
    return _camel_to_underscored(s, False)


def _camel_to_underscored(s, to_constant):
    if s is None or len(s) == 0:
        return s

    converted = TO_SNAKE_REGEX_1.sub(TO_SNAKE_PATTERN, s)
    converted = TO_SNAKE_REGEX_2.sub(TO_SNAKE_PATTERN, converted)
    converted = TO_SNAKE_REGEX_3.sub('_', converted)

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

    return TO_CAMEL_REGEX.sub(lambda match: match.group(1).upper(), s.strip('_').lower())
