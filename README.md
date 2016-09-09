# parserutils

[![Build Status](https://travis-ci.org/consbio/parserutils.png?branch=master)](https://travis-ci.org/consbio/parserutils) [![Coverage Status](https://coveralls.io/repos/github/consbio/parserutils/badge.svg?branch=master)](https://coveralls.io/github/consbio/parserutils?branch=master)

This is a library of utility functions designed to make a developer's life easier.

The functions in this library are written to be both performant and Pythonic, as well as compatible with Python 2.7 and 3.5.
They are both documented and covered thoroughly by unit tests that fully describe and prove their behavior.

In general, my philosophy is that utility functions should be fast and handle edge cases so the caller doesn't have to take all kinds of precautions or do type checking on results.
Thus, in this library, if None will break a function it is simply returned as is; if there's nothing to do for a value, the result is returned without processing; Etc.

Still, this is just a starting point. I welcome feedback and requests for additional functionality.


#Installation#
Install with `pip install parserutils`.

#Usage#

Here's what you can do with `dict` objects and other collections.
```
from parserutils import collections

collections.accumulate([('key', 'val1'), ('key', 'val2'), ('key', 'val3')])   # {'key': ['val1', 'val2', 'val3']}
collections.accumulate(
    [('key1', 'val1'), ('key2', 'val2'), ('key3', 'val3')], reduce_each=True  # {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
)

collections.setdefaults({}, 'a.b')                         # {'a': {'b': None}}
collections.setdefaults({}, ['a.b', 'a.c'])                # {'a': {'b': None, 'c': None}}
collections.setdefaults({}, {'a.b': 'bbb', 'a.c': 'ccc'})  # {'a': {'b': 'bbb', 'c': 'ccc'}}

# Also see: collections.filter_empty, collections.reduce_value, collections.wrap_value
```

Here's a little bit about dates and numbers.
```
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
```
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
```

Finally, XML parsing is also supported, using the cElementTree and defusedxml libraries for performance and security
```
from parserutils import elements

xml_string = '<root><parent><child>one</child><child>two</child><uglyChild>yuck</uglyChild></parent></root>'
xml_element =  elements.get_element(xml_string)


# Update an XML string and print it back out
elements.set_element_text(xml_element, 'parent/child', 'child text')
elements.set_element_attributes(xml_element, childHas='child attribute')
elements.remove_element(xml_element, 'parent/uglyChild')
elements.element_to_string(xml_element)


# Conversion to element from dict, and from dict back to string
converted = elements.element_to_dict(xml_string, recurse=True)
reverted = elements.dict_to_element(converted)
reverted = elements.get_element(converted)
xml_string == elements.element_to_string(converted)


# Conversion to flattened object
root, obj = elements.element_to_object(converted)
obj == {'root': {'parent': {'child': ['one', 'two'], 'uglyChild': 'yuck'}}}


# Read in an XML file and write it elswhere
with open('/path/to/file.xml', 'wb') as xml:
    xml_from_file = elements.get_element(xml)
    elements.write_element(xml_from_file, '/path/to/updated/file.xml')


# Write a local file from a remote location
xml_from_web = elements.get_remote_element('http://en.wikipedia.org/wiki/XML')
elements.write_element(xml_from_web, '/path/to/new/file.xml')


# Read content at a local filepath to a string
xml_from_path = elements.get_remote_element('/path/to/file.xml')
elements.element_to_string(xml_from_path)
```

