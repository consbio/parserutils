# parserutils

[![Build Status](https://travis-ci.org/consbio/parserutils.png?branch=master)](https://travis-ci.org/consbio/parserutils)[![Coverage Status](https://coveralls.io/repos/github/consbio/parserutils/badge.svg?branch=master)](https://coveralls.io/github/consbio/parserutils?branch=master)

This is a library of utility functions designed to make a developer's life easier.

The functions in this library are written to be both performant and Pythonic, as well as compatible with Python 2.7 through 3.6.
They are both documented and covered thoroughly by unit tests that fully describe and prove their behavior.

In general, my philosophy is that utility functions should be fast and handle edge cases so the caller doesn't have to take all kinds of precautions or do type checking on results.
Thus, in this library, if None will break a function it is simply returned as is; if there's nothing to do for a value, the result is returned without processing; otherwise, values are either processed successfully or a standard exception is returned.

But this is just a starting point. I welcome feedback and requests for additional functionality.


## Installation
Install with `pip install parserutils`.

## Usage

Here's what you can do with `dict` objects and other collections.
```python
from parserutils import collections

collections.accumulate_items([('key', 'val1'), ('key', 'val2'), ('key', 'val3')])   # {'key': ['val1', 'val2', 'val3']}
collections.accumulate_items(
    [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')], reduce_each=True  # {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
)

collections.setdefaults({}, 'a.b')                         # {'a': {'b': None}}
collections.setdefaults({}, ['a.b', 'a.c'])                # {'a': {'b': None, 'c': None}}
collections.setdefaults({}, {'a.b': 'bbb', 'a.c': 'ccc'})  # {'a': {'b': 'bbb', 'c': 'ccc'}}

collections.filter_empty(x for x in (None, [], ['a'], '', {'b'}, 'c'))      # [['a'], {'b'}, 'c']
collections.flatten_items(x for x in ('abc', ['a', 'b', 'c'], ('d', 'e')))  # ['abc', 'a', 'b', 'c', 'd', 'e']

collections.remove_duplicates('abcdefabc')                                 # 'abcdef'
collections.remove_duplicates('abcdefabc', in_reverse=True)                # 'defabc'
collections.remove_duplicates(['a', 'b', 'c', 'a'])                        # ['a', 'b', 'c']
collections.remove_duplicates(('a', 'b', 'c', 'a'), in_reverse=True)       # ('b', 'c', 'a')
collections.remove_duplicates(x for x in 'abca')                           # ['a', 'b', 'c']
collections.remove_duplicates((x for x in 'abca'), in_reverse=True)        # ['b', 'c', 'a']
collections.remove_duplicates((set(x) for x in 'abca'), is_hashable=True)  # [{'a'}, {'b'}, {'c'}]

collections.rindex('aba', 'a')               # 2
collections.rindex(['a', 'b', 'a'], 'a')     # 2
collections.rindex(('a', 'b', 'a'), 'a')     # 2
collections.rindex('xyz', 'a')               # ValueError
collections.rindex([x for x in 'xyz'], 'a')  # ValueError

collections.rfind('aba', 'a')                # 2
collections.rfind(['a', 'b', 'a'], 'a')      # 2
collections.rfind(('a', 'b', 'a'), 'a')      # 2
collections.rindex('xyz', 'a')               # -1
collections.rfind([x for x in 'xyz'], 'a')   # -1

collections.reduce_value(['abc'])          # 'abc'
collections.reduce_value(('abc',))         # 'abc'
collections.reduce_value({'abc'})          # 'abc'
collections.reduce_value('abc')            # 'abc'
collections.reduce_value({'a': 'aaa'})     # {'a': 'aaa'}
collections.reduce_value([{'a': 'aaa'}])   # {'a': 'aaa'}
collections.reduce_value(['a', 'b', 'c'])  # ['a', 'b', 'c']

collections.wrap_value(['abc'])           # ['abc']
collections.wrap_value(('abc',))          # ('abc',)
collections.wrap_value('abc')             # ['abc']
collections.wrap_value(x for x in 'abc')  # ['a', 'b', 'c']
collections.wrap_value({'a': 'aaa'})      # [{'a': 'aaa'}]
collections.wrap_value(['a', 'b', 'c'])   # ['a', 'b', 'c']
```

Here's a little bit about dates and numbers.
```python
from parserutils import dates
from parserutils import numbers

# Leverages dateutil in general, but also handles milliseconds and provides defaults

dates.parse_dates(None, default='today')  # Today (default behavior)
dates.parse_dates(None, default=None)     # Returns None
dates.parse_dates('nope', default=None)   # Returns None
dates.parse_dates(0)                      # 1970
dates.parse_dates('<date_format>')        # Behaves as described in dateutil library

# Reliably handles all the usual cases

numbers.is_number(0)                    # Integer: True
numbers.is_number(1.1)                  # Float: True
numbers.is_number('2.2')                # String: True
numbers.is_number(False)                # Boolean: False by default
numbers.is_number(False, if_bool=True)  # Boolean: True if you need it to
numbers.is_number(float('inf'))         # Infinite: False
numbers.is_number(float('nan'))         # NaN: False
```

Here's something about string and URL parsing helpers.
```python
from parserutils import strings
from parserutils import urls

# These string conversions are written to be fast and reliable

strings.camel_to_constant('toConstant')        # TO_CONSTANT
strings.camel_to_constant('XMLConstant')       # XML_CONSTANT
strings.camel_to_constant('withNumbers1And2')  # WITH_NUMBERS1_AND2

strings.camel_to_snake('toSnake')              # to_snake
strings.camel_to_snake('withXMLAbbreviation')  # with_xml_abbreviation
strings.camel_to_snake('withNumbers3And4')     # with_numbers3_and4

strings.snake_to_camel('from_snake')              # fromSnake
strings.snake_to_camel('_leading_and_trailing_')  # leadingAndTrailing
strings.snake_to_camel('extra___underscores')     # extraUnderscores

strings.find_all('ab??ca??bc??', '??')                         # [2, 6, 10]
strings.find_all('ab??ca??bc??', '??', reverse=True)           # [10, 6, 2]
strings.find_all('ab??ca??bc??', '??', limit=2, reverse=True)  # [10, 6]
strings.find_all('ab??ca??bc??', '??', start=4)                # [6, 10]
strings.find_all('ab??ca??bc??', '??', end=8)                  # [2, 6]
strings.find_all('ab??ca??bc??', '??', start=4, end=8)         # [6]

strings.splitany('ab:ca:bc', ',')           # Same as 'ab:ca:bc'.split(':')
strings.splitany('ab:ca:bc', ',', 1)        # Same as 'ab:ca:bc'.split(':', 1)
strings.splitany('ab|ca:bc', '|:')          # ['ab', 'ca', 'bc']
strings.splitany('ab|ca:bc', ':|', 1)       # ['ab', 'ca:bc']
strings.splitany('0<=3<5', ['<', '<='])     # ['0', '3', '5']
strings.splitany('0<=3<5', ['<', '<='], 1)  # ['0', '3<5']

strings.to_ascii_equivalent('smart quotes, etc.')  # Replaces with ascii quotes, etc.

# URL manipulation leverages urllib, but spares you the extra code

urls.get_base_url('http://www.params.com?a=aaa')                  # 'http://www.params.com/'
urls.get_base_url('http://www.path.com/test')                     # 'http://www.path.com/'
urls.get_base_url('http://www.path.com/test', include_path=True)  # 'http://www.path.com/test/'
urls.get_base_url('http://www.params.com/test?a=aaa', True)       # 'http://www.params.com/test/'

urls.update_url_params('http://www.params.com?a=aaa', a='aaa')  # 'http://www.params.com?a=aaa'
urls.update_url_params('http://www.params.com?a=aaa', a='xxx')  # 'http://www.params.com?a=xxx'
urls.update_url_params('http://www.params.com', b='bbb')        # 'http://www.params.com?b=bbb'
urls.update_url_params('http://www.params.com', c=['c', 'cc'])  # 'http://www.params.com?c=c&c=cc'

# Helpers to parse urls to and from parts: parses path as list and params as dict
urls.url_to_parts('http://www.params.com/test/path?a=aaa')      # SplitResult(..., path=['test', 'path'], query={'a': 'aaa'})
urls.parts_to_url(
    {'netloc': 'www.params.com', 'query': {'a': 'aaa'}          # 'http://www.params.com?a=aaa'
)
urls.parts_to_url(
    urls.url_to_parts('http://www.params.com/test/path?a=aaa')  # 'http://www.params.com/test/path?a=aaa'
)
```

Finally, XML parsing is also supported, using the cElementTree and defusedxml libraries for performance and security
```python
from parserutils import elements

# First convert an XML string to an Element object
xml_string = '<root><parent><child>one</child><child>two</child><uglyChild>yuck</uglyChild></parent></root>'
xml_element = elements.get_element(xml_string)


# Update the XML string and print it back out
elements.set_element_text(xml_element, 'parent/child', 'child text')
elements.set_element_attributes(xml_element, childHas='child attribute')
elements.remove_element(xml_element, 'parent/uglyChild')
elements.element_to_string(xml_element)


# Conversion from string to Element, to dict, and then back to string
converted = elements.element_to_dict(xml_string, recurse=True)
reverted = elements.dict_to_element(converted)
reverted = elements.get_element(converted)
xml_string == elements.element_to_string(converted)


# Conversion to flattened dict object
root, obj = elements.element_to_object(converted)
obj == {'root': {'parent': {'child': ['one', 'two'], 'uglyChild': 'yuck'}}}


# Read in an XML file and write it elsewhere
with open('/path/to/file.xml', 'wb') as xml:
    xml_from_file = elements.get_element(xml)
    elements.write_element(xml_from_file, '/path/to/updated/file.xml')


# Write a local file from a remote location (via URL)
xml_from_web = elements.get_remote_element('http://en.wikipedia.org/wiki/XML')
elements.write_element(xml_from_web, '/path/to/new/file.xml')


# Read content at a local file path to a string
xml_from_path = elements.get_remote_element('/path/to/file.xml')
elements.element_to_string(xml_from_path)
```
