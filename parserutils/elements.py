"""
Encapsulates all implementation specific functionality for XML parsing
Contains an API defining all operations executable against an XML tree
"""

import re
import six
import string

from six import binary_type, iteritems, string_types

from defusedxml.cElementTree import fromstring, tostring
from defusedxml.cElementTree import iterparse
from xml.etree.cElementTree import ElementTree, Element
from xml.etree.cElementTree import iselement
from parserutils.strings import DEFAULT_ENCODING, _STRING_TYPES

ElementType = type(Element(None))  # Element module doesn't have a type


XPATH_DELIM = '/'

_ABS_FILE_REGEX = {
    'lin': r'/',
    'win': r'([A-Za-z]{1}:[\/\\]{1})|([\\]{2})'
}
_FILE_LOCATION_REGEX = re.compile(r'^({win})|({lin})'.format(**_ABS_FILE_REGEX))
_NAMESPACES_FROM_DEC_REGEX = re.compile(r"""(<[^>]*)\sxmlns[^"'>]+["'][^"'>]+["']""")
_NAMESPACES_FROM_TAG_REGEX = re.compile(r'(</?)[\w\-.]+:')
_NAMESPACES_FROM_ATTR_REGEX = re.compile(r'(\s+)([\w\-.]+:)([\w\-.]+\s*=)')
_XML_DECLARATION_REGEX = re.compile(r'^\s*<\?xml[\w\s{punc}]*\?>\s*'.format(punc=string.punctuation))

_ELEM_NAME = 'name'
_ELEM_TEXT = 'text'
_ELEM_TAIL = 'tail'
_ELEM_ATTRIBS = 'attributes'
_ELEM_CHILDREN = 'children'

_OBJ_TYPE = 'type'
_OBJ_VALUE = 'value'
_OBJ_CHILDREN = 'children'
_OBJ_PROPERTIES = {_OBJ_TYPE, _OBJ_VALUE, _OBJ_CHILDREN}


def create_element_tree(elem_or_name=None, text=None, **attribute_kwargs):
    """
    Creates an ElementTree from elem_or_name, updated it with text and attributes.
    If elem_or_name is None, a permanently empty ElementTree is returned.
    :param elem_or_name: an Element or the name of the root element tag
    :param text: optional text with which to update the root element
    :param attribute_kwargs: optional attributes to add to the root element
    :return: a new ElementTree with the specified root and attributes
    """

    if elem_or_name is None:
        return ElementTree()

    is_elem = isinstance(elem_or_name, ElementType)
    element = elem_or_name if is_elem else Element(elem_or_name)

    if text is not None:
        element.text = text

    element.attrib.update(attribute_kwargs)

    return ElementTree(element)


def clear_children(parent_to_parse, element_path=None):
    """
    Clears only children (not text or attributes) from the parsed parent
    or named element.
    """

    element = get_element(parent_to_parse, element_path)

    if element is None:
        return parent_to_parse
    else:
        elem_txt = element.text
        elem_atr = element.attrib

        element.clear()

        element.text = elem_txt
        element.attrib = elem_atr

    return element


def clear_element(parent_to_parse, element_path=None):
    """
    Clears everything (text, attributes and children) from the parsed parent
    or named element.
    """

    element = get_element(parent_to_parse, element_path)

    if element is None:
        return parent_to_parse
    else:
        element.clear()

    return element


def copy_element(from_element, to_element=None, path_to_copy=None):
    """
    Copies the element at path_to_copy in from_element and uses it to create or update
    the first element found at the same location (path_to_copy) in to_element.

    If path_to_copy is not provided, from_element is copied to the root of to_element.
    """

    from_element = get_element(from_element, path_to_copy)
    dest_element = get_element(to_element, path_to_copy)

    if from_element is None:
        return None

    if dest_element is None:
        if path_to_copy is None:
            dest_element = Element(from_element.tag)
        else:
            dest_element = insert_element(Element(from_element.tag), 0, path_to_copy)

    dest_element.tag = from_element.tag
    dest_element.text = from_element.text
    dest_element.tail = from_element.tail
    dest_element.attrib = from_element.attrib

    copied_children = []

    for elem in from_element:
        copied_children.append(copy_element(elem))

    for idx, child in enumerate(copied_children):
        dest_element.insert(idx, child)

    return dest_element


def get_element_tree(parent_to_parse):
    """
    :return: an ElementTree initialized with the parsed element.
    :see: get_element(parent_to_parse, element_path)
    """

    if isinstance(parent_to_parse, ElementTree):
        return parent_to_parse

    element = get_element(parent_to_parse)

    return ElementTree() if element is None else ElementTree(element)


def get_element(parent_to_parse, element_path=None):
    """
    :return: an element from the parent or parsed from a Dictionary, XML string
    or file. If element_path is not provided the root element is returned.
    """

    if parent_to_parse is None:
        return None

    elif isinstance(parent_to_parse, ElementTree):
        parent_to_parse = parent_to_parse.getroot()

    elif hasattr(parent_to_parse, 'read'):
        parent_to_parse = string_to_element(parent_to_parse.read())

    elif isinstance(parent_to_parse, _STRING_TYPES):
        parent_to_parse = string_to_element(parent_to_parse)

    elif isinstance(parent_to_parse, dict):
        parent_to_parse = dict_to_element(parent_to_parse)

    if parent_to_parse is None:
        return None
    elif not isinstance(parent_to_parse, ElementType):
        element_type = type(parent_to_parse).__name__
        raise TypeError('Invalid element type: {0}'.format(element_type))

    return parent_to_parse.find(element_path) if element_path else parent_to_parse


def get_remote_element(url, element_path=None):
    """
    :return: an element initialized with the content at the specified file or URL
    :see: get_element(parent_to_parse, element_path)
    """

    content = None

    if url is None:
        return content
    elif _FILE_LOCATION_REGEX.match(url):
        with open(url, 'rb') as xml:
            content = xml.read()
    else:
        urllib = getattr(six.moves, 'urllib')
        content = urllib.request.urlopen(url).read()

    return get_element(strip_namespaces(content), element_path)


def element_exists(elem_to_parse, element_path=None):
    """ :return: true if the named element exists in the parent, false otherwise """

    return iselement(get_element(elem_to_parse, element_path))


def elements_exist(elem_to_parse, element_paths=None, all_exist=False):
    """
    :return: true if any of the named elements exist in the parent by default,
    unless all_exist is true, in which case all the named elements must exist
    """

    element = get_element(elem_to_parse)

    if element is None:
        return False

    if not element_paths or isinstance(element_paths, string_types):
        return element_exists(element, element_paths)

    exists = False

    for element_path in element_paths:
        exists = element_exists(element, element_path)

        if all_exist and not exists:
            return False

        if exists and not all_exist:
            return True

    return exists


def element_is_empty(elem_to_parse, element_path=None):
    """
    Returns true if the element is None, or has no text, tail, children or attributes.
    Whitespace in the element is stripped from text and tail before making the determination.
    """

    element = get_element(elem_to_parse, element_path)

    if element is None:
        return True

    is_empty = (
        (element.text is None or not element.text.strip()) and
        (element.tail is None or not element.tail.strip()) and
        (element.attrib is None or not len(element.attrib)) and
        (not len(element.getchildren()))
    )

    return is_empty


def insert_element(elem_to_parse, elem_idx, elem_path, elem_txt=u'', **kwargs):
    """
    Creates an element named after elem_path, containing elem_txt, with kwargs
    as attributes, inserts it into elem_to_parse at elem_idx and returns it.

    If elem_path is an XPATH pointing to a non-existent element, elements not
    in the path are inserted and the text and index are applied to the last one.

    If elem_path is an XPATH pointing to an existing element, the new element is
    inserted as a sibling of the last one in the path at the index specified.
    """

    element = get_element(elem_to_parse)

    if element is None:
        return element

    if not elem_path:
        return None

    if not elem_idx:
        elem_idx = 0

    if elem_path and XPATH_DELIM in elem_path:
        tags = elem_path.split(XPATH_DELIM)

        if element_exists(element, elem_path):

            # Get the next to last element in the XPATH
            parent = get_element(element, XPATH_DELIM.join(tags[:-1]))

            # Insert the new element as sibling to the last one
            return insert_element(parent, elem_idx, tags[-1], elem_txt, **kwargs)

        else:
            this_elem = element
            last_idx = len(tags) - 1

            # Iterate over tags from root to leaf
            for idx, tag in enumerate(tags):
                next_elem = get_element(this_elem, tag)

                # Insert missing elements in the path or continue
                if next_elem is None:

                    # Apply text and index to last element only
                    if idx == last_idx:
                        next_elem = insert_element(this_elem, elem_idx, tag, elem_txt, **kwargs)
                    else:
                        next_elem = insert_element(this_elem, 0, tag, u'', **kwargs)

                this_elem = next_elem

            return this_elem

    subelem = Element(elem_path, kwargs)
    subelem.text = elem_txt

    element.insert(elem_idx, subelem)

    return subelem


def remove_element(parent_to_parse, element_path, clear_empty=False):
    """
    Searches for a sub-element named after element_name in the parsed element,
    and if it exists, removes them all and returns them as a list.
    If clear_empty is True, removes empty parents if all children are removed.
    :see: remove_empty_element(parent_to_parse, element_path, target_element=None)
    :see: get_element(parent_to_parse, element_path)
    """

    element = get_element(parent_to_parse)

    if element is None:
        return element

    removed = []

    if element_exists(element, element_path):
        if XPATH_DELIM not in element_path:
            for subelem in get_elements(element, element_path):
                removed.append(subelem)
                element.remove(subelem)
        else:
            xpath_segments = element_path.split(XPATH_DELIM)
            parent_segment = XPATH_DELIM.join(xpath_segments[:-1])
            last_segment = xpath_segments[-1]

            for parent in get_elements(element, parent_segment):
                rem = remove_element(parent, last_segment)
                removed.extend(rem if isinstance(rem, list) else [rem])

            if clear_empty:
                removed.extend(remove_empty_element(element, parent_segment))

    return removed[0] if len(removed) == 1 else removed


def remove_elements(parent_to_parse, element_paths, clear_empty=False):
    """
    Removes all elements named after each elements_or_paths. If clear_empty is True,
    for each XPATH, empty parents are removed if all their children are removed.
    :see: remove_element(parent_to_parse, element_path)
    """

    element = get_element(parent_to_parse)
    if element is None:
        return element

    removed = []
    if not element_paths:
        return removed

    if isinstance(element_paths, string_types):
        rem = remove_element(element, element_paths, clear_empty)
        removed.extend(rem if isinstance(rem, list) else [rem])
    else:
        for xpath in element_paths:
            rem = remove_element(element, xpath, clear_empty)
            removed.extend(rem if isinstance(rem, list) else [rem])

    return removed


def remove_empty_element(parent_to_parse, element_path, target_element=None):
    """
    Searches for all empty sub-elements named after element_name in the parsed element,
    and if it exists, removes them all and returns them as a list.
    """

    element = get_element(parent_to_parse)

    removed = []

    if element is None or not element_path:
        return removed

    if target_element:

        # Always deal with just the element path
        if not element_path.endswith(target_element):
            element_path = XPATH_DELIM.join([element_path, target_element])
        target_element = None

    if XPATH_DELIM not in element_path:

        # Loop over and remove empty sub-elements directly
        for subelem in get_elements(element, element_path):
            if element_is_empty(subelem):
                removed.append(subelem)
                element.remove(subelem)
    else:
        # Parse target element from last node in element path
        xpath_segments = element_path.split(XPATH_DELIM)
        element_path = XPATH_DELIM.join(xpath_segments[:-1])
        target_element = xpath_segments[-1]

        # Loop over children and remove empty ones directly
        for parent in get_elements(element, element_path):
            for child in get_elements(parent, target_element):
                if element_is_empty(child):
                    removed.append(child)
                    parent.remove(child)

            # Parent may be empty now: recursively remove empty elements in XPATH
            if element_is_empty(parent):
                if len(xpath_segments) == 2:
                    removed.extend(remove_empty_element(element, xpath_segments[0]))
                else:
                    next_element_path = XPATH_DELIM.join(xpath_segments[:-2])
                    next_target_element = parent.tag

                    removed.extend(remove_empty_element(element, next_element_path, next_target_element))

    return removed


def get_elements(parent_to_parse, element_path):
    """
    :return: all elements by name from the parsed parent element.
    :see: get_element(parent_to_parse, element_path)
    """

    element = get_element(parent_to_parse)

    if element is None or not element_path:
        return []

    return element.findall(element_path)


def get_element_attribute(elem_to_parse, attrib_name, default_value=u''):
    """
    :return: an attribute from the parsed element if it has the attribute,
    otherwise the default value
    """

    element = get_element(elem_to_parse)

    if element is None:
        return default_value

    return element.attrib.get(attrib_name, default_value)


def get_element_attributes(parent_to_parse, element_path=None):
    """
    :return: all the attributes for the parsed element if it has any, or an empty dict
    """

    element = get_element(parent_to_parse, element_path)

    return {} if element is None else element.attrib


def set_element_attributes(elem_to_parse, **attrib_kwargs):
    """
    Adds the specified key/value pairs to the element's attributes, and
    returns the updated set of attributes.

    If the element already contains any of the attributes specified in
    attrib_kwargs, they are updated accordingly.
    """

    element = get_element(elem_to_parse)

    if element is None:
        return element

    if len(attrib_kwargs):
        element.attrib.update(attrib_kwargs)

    return element.attrib


def remove_element_attributes(elem_to_parse, *args):
    """
    Removes the specified keys from the element's attributes, and
    returns a dict containing the attributes that have been removed.
    """

    element = get_element(elem_to_parse)

    if element is None:
        return element

    if len(args):
        attribs = element.attrib
        return {key: attribs.pop(key) for key in args if key in attribs}

    return {}


def get_element_name(parent_to_parse):
    """
    :return: the name of the parsed element.
    :see: get_element(parent_to_parse, element_path)
    """

    element = get_element(parent_to_parse)

    return None if element is None else element.tag


def get_element_tail(parent_to_parse, element_path=None, default_value=u''):
    """
    :return: text following the parsed parent element if it exists,
    otherwise the default value.
    :see: get_element(parent_to_parse, element_path)
    """

    parent_element = get_element(parent_to_parse, element_path)

    if parent_element is None:
        return default_value

    if parent_element.tail:
        return parent_element.tail.strip() or default_value

    return default_value


def get_element_text(parent_to_parse, element_path=None, default_value=u''):
    """
    :return: text from the parsed parent element if it has a text value,
    otherwise the default value.
    :see: get_element(parent_to_parse, element_path)
    """

    parent_element = get_element(parent_to_parse, element_path)

    if parent_element is None:
        return default_value

    if parent_element.text:
        return parent_element.text.strip() or default_value

    return default_value


def get_elements_tail(parent_to_parse, element_path=None):
    """
    :return: list of text following the parsed parent element, or the default
    :see: get_element(parent_to_parse, element_path)
    """

    return _get_elements_property(parent_to_parse, element_path, 'tail')


def get_elements_text(parent_to_parse, element_path=None):
    """
    :return: list of text extracted from the parsed parent element, or the default
    :see: get_element(parent_to_parse, element_path)
    """

    return _get_elements_property(parent_to_parse, element_path, 'text')


def _get_elements_property(parent_to_parse, element_path, prop_name):
    """
    Assigns an array of string values to each of the elements parsed from the parent.
    The values must be strings, and they are assigned in the same order they are provided.
    The operation stops when values run out, and excess values are ignored.
    :see: get_element(parent_to_parse, element_path)
    """

    parent_element = get_element(parent_to_parse)

    if parent_element is None:
        return []

    if element_path and not element_exists(parent_element, element_path):
        return []

    if not element_path:
        texts = getattr(parent_element, prop_name)
        texts = texts.strip() if texts else None
        texts = [texts] if texts else []
    else:
        texts = [t for t in (
            prop.strip() if isinstance(prop, string_types) else prop
            for prop in (getattr(node, prop_name) for node in parent_element.findall(element_path)) if prop
        ) if t]

    return texts


def set_element_tail(parent_to_parse, element_path=None, element_tail=u''):
    """
    Assigns the text following the parsed parent element and then returns it.
    If element_path is provided and doesn't exist, it is inserted with element_tail.
    :see: get_element(parent_to_parse, element_path)
    """

    return _set_element_property(parent_to_parse, element_path, _ELEM_TAIL, element_tail)


def set_element_text(parent_to_parse, element_path=None, element_text=u''):
    """
    Assigns a string value to the parsed parent element and then returns it.
    If element_path is provided and doesn't exist, it is inserted with element_text.
    :see: get_element(parent_to_parse, element_path)
    """

    return _set_element_property(parent_to_parse, element_path, _ELEM_TEXT, element_text)


def _set_element_property(parent_to_parse, element_path, prop_name, value):
    """ Assigns the value to the parsed parent element and then returns it """

    element = get_element(parent_to_parse)

    if element is None:
        return None

    if element_path and not element_exists(element, element_path):
        element = insert_element(element, 0, element_path)

    if not isinstance(value, string_types):
        value = u''

    setattr(element, prop_name, value)

    return element


def set_elements_tail(parent_to_parse, element_path=None, tail_values=None):
    """
    Assigns an array of tail values to each of the elements parsed from the parent. The
    tail values are assigned in the same order they are provided.
    If there are less values then elements, the remaining elements are skipped; but if
    there are more, new elements will be inserted for each with the remaining tail values.
    """

    if tail_values is None:
        tail_values = []

    return _set_elements_property(parent_to_parse, element_path, _ELEM_TAIL, tail_values)


def set_elements_text(parent_to_parse, element_path=None, text_values=None):
    """
    Assigns an array of text values to each of the elements parsed from the parent. The
    text values are assigned in the same order they are provided.
    If there are less values then elements, the remaining elements are skipped; but if
    there are more, new elements will be inserted for each with the remaining text values.
    """

    if text_values is None:
        text_values = []

    return _set_elements_property(parent_to_parse, element_path, _ELEM_TEXT, text_values)


def _set_elements_property(parent_to_parse, element_path, prop_name, values):
    """
    Assigns an array of string values to each of the elements parsed from the parent.
    The values must be strings, and they are assigned in the same order they are provided.
    The operation stops when values run out; extra values will be inserted as new elements.
    :see: get_element(parent_to_parse, element_path)
    """

    element = get_element(parent_to_parse)

    if element is None or not values:
        return []

    if isinstance(values, string_types):
        values = [values]

    if not element_path:
        return [_set_element_property(element, None, prop_name, values[0])]

    elements = get_elements(element, element_path)
    affected = []

    for idx, val in enumerate(values):
        if idx < len(elements):
            next_elem = elements[idx]
        else:
            next_elem = insert_element(element, idx, element_path)

        affected.append(
            _set_element_property(next_elem, None, prop_name, val)
        )

    return affected


def dict_to_element(element_as_dict):
    """
    Converts a Dictionary object to an element. The Dictionary can
    include any of the following tags, only name is required:
        - name (required): the name of the element tag
        - text: the text contained by element
        - tail: text immediately following the element
        - attributes: a Dictionary containing element attributes
        - children: a List of converted child elements
    """

    if element_as_dict is None:
        return None
    elif isinstance(element_as_dict, ElementTree):
        return element_as_dict.getroot()
    elif isinstance(element_as_dict, ElementType):
        return element_as_dict
    elif not isinstance(element_as_dict, dict):
        raise TypeError('Invalid element dict: {0}'.format(element_as_dict))

    if len(element_as_dict) == 0:
        return None

    try:
        converted = Element(
            element_as_dict[_ELEM_NAME],
            element_as_dict.get(_ELEM_ATTRIBS, {})
        )

        converted.tail = element_as_dict.get(_ELEM_TAIL, u'')
        converted.text = element_as_dict.get(_ELEM_TEXT, u'')

        for child in element_as_dict.get(_ELEM_CHILDREN, []):
            converted.append(dict_to_element(child))

    except KeyError:
        raise SyntaxError('Invalid element dict: {0}'.format(element_as_dict))

    return converted


def element_to_dict(elem_to_parse, element_path=None, recurse=True):
    """
    :return: an element losslessly as a dictionary. If recurse is True,
    the element's children are included, otherwise they are omitted.

    The resulting Dictionary will have the following attributes:
        - name: the name of the element tag
        - text: the text contained by element
        - tail: text immediately following the element
        - attributes: a Dictionary containing element attributes
        - children: a List of converted child elements
    """

    element = get_element(elem_to_parse, element_path)

    if element is not None:
        converted = {
            _ELEM_NAME: element.tag,
            _ELEM_TEXT: element.text,
            _ELEM_TAIL: element.tail,
            _ELEM_ATTRIBS: element.attrib,
            _ELEM_CHILDREN: []
        }

        if recurse is True:
            for child in element:
                converted[_ELEM_CHILDREN].append(element_to_dict(child, recurse=recurse))

        return converted

    return {}


def element_to_object(elem_to_parse, element_path=None):
    """
    :return: the root key, and a dict with all the XML data, but without preserving structure, for instance:

    <elem val="attribute"><val>nested text</val><val prop="attr">nested dict text</val>nested dict tail</elem>
    {'elem': {
        'val': [
            u'nested text',
            {'prop': u'attr', 'value': [u'nested dict text', u'nested dict tail']},
            u'attribute'
        ]
    }}
    """

    if isinstance(elem_to_parse, _STRING_TYPES) or hasattr(elem_to_parse, 'read'):
        # Always strip namespaces if not already parsed
        elem_to_parse = strip_namespaces(elem_to_parse)

    if element_path is not None:
        elem_to_parse = get_element(elem_to_parse, element_path)

    element_tree = get_element_tree(elem_to_parse)
    element_root = element_tree.getroot()
    root_tag = u'' if element_root is None else element_root.tag

    return root_tag, {root_tag: _element_to_object(element_root)}


def _element_to_object(element):

    def accumulate_items(obj, items, tag=None):
        """ Add or append non-None key/val pairs in items under each key in obj """

        for key, val in items:
            # Ensure XML tags don't override or get overridden by object properties
            obj_key = '_'.join((tag, key)) if tag and key in _OBJ_PROPERTIES else key
            obj_val = val.strip() if isinstance(val, string_types) else val

            if obj_key not in obj:
                obj[obj_key] = obj_val
            elif isinstance(obj[obj_key], list):
                obj[obj_key].append(obj_val)
            else:
                obj[obj_key] = [obj[obj_key]]
                obj[obj_key].append(obj_val)

    obj = {}
    if not isinstance(element, ElementType):
        return obj

    # Populate leaf elements first to reduce cost of recursion stack

    children = ((e.tag, _element_to_object(e)) for e in element)
    accumulate_items(obj, children)

    # Now that all children have been populated, fill out the parent object

    attributes = ((k, v) for k, v in iteritems(element.attrib) if v and v.strip())
    accumulate_items(obj, attributes, element.tag)

    # Add as value a list containing text and tail if both are present, or just the text for one
    text_values = ((text or u'').strip() for text in (element.text, element.tail))
    text_values = [text for text in text_values if text]  # Filter on stripped values
    text_values = (text_values[0] if len(text_values) == 1 else text_values) or u''

    # Reduce obj to text only if no other keys are present
    if not obj:
        obj = text_values
    elif text_values:
        obj[_OBJ_VALUE] = text_values

    return obj


def element_to_string(element, encoding=DEFAULT_ENCODING, method='xml'):
    """ :return: the string value of the element or element tree """

    # No Parsing of Element here, since String is the destination
    if isinstance(element, ElementTree):
        element = element.getroot()
    elif not isinstance(element, ElementType):
        element = get_element(element)

    # Elements have 'iter' as opposed to '__iter__'
    if hasattr(element, 'iter'):
        return tostring(element, encoding, method).decode(encoding=DEFAULT_ENCODING)

    return u''


def string_to_element(element_as_string, include_namespaces=False):
    """ :return: an element parsed from a string value, or the element as is if already parsed """

    if element_as_string is None:
        return None
    elif isinstance(element_as_string, ElementTree):
        return element_as_string.getroot()
    elif isinstance(element_as_string, ElementType):
        return element_as_string

    if isinstance(element_as_string, string_types):
        # For Python 2 compliance: FIRST check basestring before str
        element_as_string = element_as_string.strip()
    elif isinstance(element_as_string, binary_type):
        # For Python 3 compliance: NOW decode binary arrays (not Python 2 str)
        element_as_string = element_as_string.decode(encoding=DEFAULT_ENCODING).strip()
    elif hasattr(element_as_string, 'read'):
        # Handles files, but more importantly StringIO
        element_as_string = element_as_string.read().strip()

    if not isinstance(element_as_string, string_types):
        # Let cElementTree handle the error
        return fromstring(element_as_string)

    # For Python 2 compliance: replacement string must not specify unicode u''
    element_as_string = _XML_DECLARATION_REGEX.sub('', element_as_string, 1)

    if not element_as_string:
        return None  # Same as ElementTree().getroot()
    elif include_namespaces:
        return fromstring(element_as_string)
    else:
        return fromstring(strip_namespaces(element_as_string))


def iter_elements(element_function, parent_to_parse, **kwargs):
    """
    Applies element_function to each of the sub-elements in parent_to_parse.
    The passed in function must take at least one element, and an optional
    list of kwargs which are relevant to each of the elements in the list:
        def elem_func(each_elem, **kwargs)
    """

    parent = get_element(parent_to_parse)

    if not hasattr(element_function, '__call__'):
        return parent

    for child in ([] if parent is None else parent):
        element_function(child, **kwargs)

    return parent


def iterparse_elements(element_function, file_or_path, **kwargs):
    """
    Applies element_function to each of the sub-elements in the XML file.
    The passed in function must take at least one element, and an optional
    list of **kwarg which are relevant to each of the elements in the list:
        def elem_func(each_elem, **kwargs)

    Implements the recommended cElementTree iterparse pattern, which is
    efficient for reading in a file, making changes and writing it again.
    """

    if not hasattr(element_function, '__call__'):
        return

    file_path = getattr(file_or_path, 'name', file_or_path)
    context = iter(iterparse(file_path, events=('start', 'end')))
    root = None  # Capture root for Memory management

    # Start event loads child; by the End event it's ready for processing

    for event, child in context:
        if root is None:
            root = child
        if event == 'end':  # Ensures the element has been fully read
            element_function(child, **kwargs)
            root.clear()  # Descendants will not be accessed again


def strip_namespaces(file_or_xml):
    """
    Removes all namespaces from the XML file or string passed in.
    If file_or_xml is not a file or string, it is returned as is.
    """

    if isinstance(file_or_xml, string_types):
        xml_content = file_or_xml
    elif isinstance(file_or_xml, binary_type):
        xml_content = file_or_xml.decode(encoding=DEFAULT_ENCODING)
    elif hasattr(file_or_xml, 'read'):
        xml_content = file_or_xml.read()
    else:
        return file_or_xml

    # This pattern can have overlapping matches, necessitating the loop
    while _NAMESPACES_FROM_DEC_REGEX.search(xml_content) is not None:
        xml_content = _NAMESPACES_FROM_DEC_REGEX.sub('\\1', xml_content)

    # Remove namespaces at the tag level
    xml_content = _NAMESPACES_FROM_TAG_REGEX.sub(r'\1', xml_content)

    # Remove namespaces at the attribute level
    xml_content = _NAMESPACES_FROM_ATTR_REGEX.sub(r'\1\3', xml_content)

    return xml_content


def write_element(elem_to_parse, file_or_path, encoding=DEFAULT_ENCODING):
    """
    Writes the contents of the parsed element to file_or_path
    :see: get_element(parent_to_parse, element_path)
    """

    xml_header = '<?xml version="1.0" encoding="{0}"?>'.format(encoding)

    get_element_tree(elem_to_parse).write(file_or_path, encoding, xml_header)
