import io
import mock
import os
import unittest

from ..elements import Element, ElementTree, ElementType
from ..elements import iselement, fromstring

from ..elements import create_element_tree, clear_children, clear_element, copy_element
from ..elements import get_element_tree, get_element, get_remote_element, get_elements
from ..elements import element_exists, elements_exist, element_is_empty
from ..elements import insert_element, remove_element, remove_elements, remove_empty_element
from ..elements import get_element_name, get_element_attribute, get_element_attributes
from ..elements import get_elements_attributes, set_element_attributes, remove_element_attributes
from ..elements import get_element_tail, get_elements_tail, get_element_text, get_elements_text
from ..elements import set_element_tail, set_elements_tail, set_element_text, set_elements_text
from ..elements import dict_to_element, element_to_dict, element_to_object
from ..elements import element_to_string, string_to_element, strip_namespaces, strip_xml_declaration
from ..elements import iter_elements, iterparse_elements, write_element

from ..strings import DEFAULT_ENCODING


ELEM_NAME = 'tag'
ELEM_TEXT = 'text'
ELEM_TAIL = 'tail'
ELEM_ATTRIBS = 'attrib'

ELEM_PROPERTIES = (ELEM_NAME, ELEM_TEXT, ELEM_TAIL, ELEM_ATTRIBS)

_EMPTY_XML_1 = '<?xml version="1.0" encoding="UTF-8"?>'
_EMPTY_XML_2 = """
    <?xml
     version="1.0"
     encoding="UTF-8"
     standalone="yes" ?>
"""


class XMLTestCase(unittest.TestCase):

    def setUp(self):
        sep = os.path.sep
        dir_name = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = sep.join((dir_name, 'data'))

        self.elem_ascii_file_path = sep.join((self.data_dir, 'elem_data_ascii.xml'))
        self.elem_data_file_path = sep.join((self.data_dir, 'elem_data_unicode.xml'))
        self.namespace_file_path = sep.join((self.data_dir, 'namespace_data.xml'))
        self.test_file_path = sep.join((self.data_dir, 'test_data.xml'))

        with open(self.elem_ascii_file_path) as data:
            self.elem_ascii_str = data.read()
        with open(self.elem_data_file_path, 'rb') as data:
            self.elem_data_str = data.read()
        with open(self.namespace_file_path, 'rb') as data:
            self.namespace_str = data.read()

        if not isinstance(self.elem_data_str, str):
            self.elem_data_str = self.elem_data_str.decode(DEFAULT_ENCODING)

        self.elem_data_bin = self.elem_data_str.encode(DEFAULT_ENCODING)
        self.elem_data_dict = element_to_dict(self.elem_data_str)
        self.elem_data_reader = io.StringIO(self.elem_data_str)

        self.elem_data_inputs = (
            fromstring(self.elem_data_str), ElementTree(fromstring(self.elem_data_str)),
            self.elem_data_bin, self.elem_data_str, self.elem_data_dict, self.elem_data_reader
        )
        self.elem_empty_inputs = (None, _EMPTY_XML_1, _EMPTY_XML_2, b'', '', io.StringIO(''), ElementTree())

        self.elem_xpath = 'c'

    def tearDown(self):
        super(XMLTestCase, self).tearDown()

        if os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)

    def _reduce_property(self, value):
        """ Ensure property values trim strings and reduce lists with single values to the value itself """

        if isinstance(value, list) and len(value) == 1:
            value = value[0]

        if isinstance(value, str):
            value = value.strip()

        return value

    def assert_element_function(self, elem_func, elem_xpath=None, **elem_kwargs):
        """
        Ensures elem_func returns None for None, and that the element returned by elem_func is equal to base_elem.
        """

        elem_func_name = elem_func.__name__

        for empty in self.elem_empty_inputs:
            self.assertIsNone(
                elem_func(empty, **elem_kwargs),
                f'Empty check failed for {elem_func_name} with "{empty}"'
            )

        base_elem = fromstring(self.elem_data_str)
        elem_name = base_elem.tag

        if elem_xpath is not None:
            elem_name = '/'.join((elem_name, self.elem_xpath))
            base_elem = base_elem.find(elem_xpath)

        for data in self.elem_data_inputs:
            self.assert_elements_are_equal(elem_func(data, **elem_kwargs), base_elem, elem_name)

    def assert_element_is_type(self, element, elem_name, elem_type=ElementType):
        """ Ensures the element is of the type specified by element_utils.ElementType """

        elem_name = elem_name or getattr(element, ELEM_NAME, 'None')

        self.assertIsInstance(
            element, elem_type,
            '{0} is not of type {1}: {2}'.format(elem_name, elem_type.__name__, type(element))
        )

    def assert_element_properties_equal(self, this_elem, that_elem, prop, elem_name=None):
        """ Ensures the element property specified matches for both elements """

        prop1 = self._reduce_property(getattr(this_elem, prop))
        prop2 = self._reduce_property(getattr(that_elem, prop))

        self.assertEqual(
            prop1, prop2,
            u'Element {0} properties are not equal at /{1}: "{2}" ({3}) != "{4}" ({5})'.format(
                prop, elem_name, prop1, type(prop1).__name__, prop2, type(prop2).__name__
            )
        )

    def assert_element_trees_are_equal(self, this_tree, that_tree, elem_name=None):
        """ Ensures both element trees are comparable, and their properties are equal """

        self.assert_element_is_type(this_tree, 'elem_tree_1', ElementTree)
        self.assert_element_is_type(that_tree, 'elem_tree_2', ElementTree)

        self.assert_elements_are_equal(this_tree.getroot(), that_tree.getroot(), elem_name)

    def assert_elements_are_equal(self, this_elem, that_elem, elem_name=None):
        """ Ensures both elements are comparable, and their properties are equal """

        if elem_name is None:
            elem_name = getattr(this_elem, ELEM_NAME, getattr(that_elem, ELEM_NAME, 'None'))

        self.assert_element_is_type(this_elem, elem_name, ElementType)
        self.assert_element_is_type(that_elem, elem_name, ElementType)

        for prop in ELEM_PROPERTIES:
            self.assert_element_properties_equal(this_elem, that_elem, prop, elem_name)

        last_tags = set()

        for next_one in this_elem:

            next_tag = getattr(next_one, ELEM_NAME)
            next_name = '/'.join((elem_name, next_tag))

            if next_tag in last_tags:
                continue

            last_tags.add(next_tag)

            these_elems = this_elem.findall(next_tag)
            those_elems = that_elem.findall(next_tag)

            len_these, len_those = len(these_elems), len(those_elems)

            self.assertEqual(
                len_these, len_those,
                f'Elements {next_name} have differing numbers of children: {len_these} != {len_those}'
            )

            for idx, child in enumerate(these_elems):
                self.assert_elements_are_equal(child, those_elems[idx], next_name)


class XMLTests(XMLTestCase):

    def test_create_element_tree(self):
        """ Tests create_element_tree with None, and for equality with different params """

        self.assertIsNone(create_element_tree().getroot(), 'None check failed for create_element_tree')

        self.assert_element_trees_are_equal(
            create_element_tree('root', ELEM_TEXT, a='aaa', b='bbb'),
            create_element_tree(fromstring(b'<root a="aaa" b="bbb">text</root>'))
        )

        self.assert_element_trees_are_equal(
            create_element_tree('root', ELEM_TEXT, a='aaa', b='bbb'),
            create_element_tree(fromstring(u'<root a="aaa" b="bbb">text</root>'))
        )

    def test_clear_children(self):
        """ Tests clear_children with different element data, including None """

        self.assertIsNone(clear_children(None), 'None check failed for clear_children')

        for data in self.elem_data_inputs:
            data = clear_children(data)
            self.assertEqual(
                list(data), [], 'Clear children failed for input type {0}'.format(type(data).__name__)
            )

    def test_clear_children_xpath(self):
        """ Tests clear_children at an XPATH location with different element data """

        for data in self.elem_data_inputs:
            data = clear_children(data, self.elem_xpath)
            self.assertEqual(
                list(data), [], 'Clear children XPATH failed for input type {0}'.format(type(data).__name__)
            )

    def assert_element_cleared(self, elem, elem_type, msg='Clear element'):
        """ Ensures an element has been cleared by testing text, tail, attributes and children """

        self.assertFalse(bool(elem.text), f'{msg} failed for {elem_type}: text == "{elem.text}"')
        self.assertFalse(bool(elem.tail), f'{msg} failed for {elem_type}: tail == "{elem.tail}"')
        self.assertFalse(bool(elem.attrib), f'{msg} failed for {elem_type}: attrib == "{elem.attrib}"')
        self.assertFalse(
            bool(list(elem)),
            '{0} failed for {1}: children == "{2}"'.format(msg, elem_type, list(elem))
        )

    def test_clear_element(self):
        """ Tests clear_element with different element data, including None """

        self.assertIsNone(clear_element(None), 'None check failed for clear_element')

        for data in self.elem_data_inputs:
            self.assert_element_cleared(clear_element(data), type(data).__name__)

    def test_clear_element_xpath(self):
        """ Tests clear_element at an XPATH location with different element data """

        for data in self.elem_data_inputs:
            self.assert_element_cleared(
                clear_element(data, self.elem_xpath), type(data).__name__, 'Clear element XPATH'
            )

    def test_copy_element(self):
        """ Tests copy_element with different element data, including None """
        self.assert_element_function(copy_element)

    def test_copy_element_to(self):
        """ Tests copy_element to a destination element with different element data """
        self.assert_element_function(copy_element, to_element='<a />')

    def test_copy_element_xpath(self):
        """ Tests copy_element at an XPATH location to a destination element with different element data """

        self.assert_element_function(
            copy_element, self.elem_xpath, to_element='<a />', path_to_copy=self.elem_xpath
        )

    def test_get_element_tree(self):
        """ Tests get_element_tree with None, and for equality with different params """

        self.assertIsNone(get_element_tree(None).getroot(), 'None check failed for get_element_tree')

        base_elem = get_element(self.elem_data_str)
        base_tree = ElementTree(base_elem)

        for data in self.elem_data_inputs:
            self.assert_element_trees_are_equal(get_element_tree(data), base_tree, base_elem.tag)

    def test_get_element(self):
        """ Tests get_element with None, and for equality with different params """

        self.assert_element_function(get_element)

        for bad_xml in ({'a': 'aaa'}, 'NOT XML', io.StringIO('NOT XML')):
            # Assert that invalid XML values result in SyntaxError
            with self.assertRaises(SyntaxError):
                get_element(bad_xml)

        for bad_xml in (self, list(), set(), tuple(), ['a'], {'b'}, ('c',)):
            # Assert that non-XML values result in TypeError
            with self.assertRaises(TypeError):
                get_element(bad_xml)

    def test_get_element_xpath(self):
        """ Tests get_element at an XPATH location with different element data """
        self.assert_element_function(get_element, self.elem_xpath, element_path=self.elem_xpath)

    @mock.patch('parserutils.elements.urlopen')
    def test_get_remote_element(self, mock_urlopen):
        """ Tests get_remote_element with None and a well-known URL with and without an XPATH location """

        self.assertIsNone(get_remote_element(None), 'None check failed for get_remote_element')

        file_path = self.elem_ascii_file_path
        self.assertIsNotNone(
            get_remote_element(file_path), 'Remote element returns None for ascii file'
        )
        self.assertIsNotNone(
            get_remote_element(file_path, 'b'), 'Remote element returns None for ascii file at "b"'
        )

        file_path = self.elem_data_file_path
        self.assertIsNotNone(
            get_remote_element(file_path), 'Remote element returns None for unicode file'
        )
        self.assertIsNotNone(
            get_remote_element(file_path, 'b'), 'Remote element returns None for unicode file at "b"'
        )

        file_path = self.namespace_file_path
        self.assertIsNotNone(
            get_remote_element(file_path), 'Remote element returns None for namespaces file'
        )
        self.assertIsNotNone(
            get_remote_element(file_path, 'c'), 'Remote element returns None for namespaces at "c"'
        )

        remote_url = 'https://www.w3schools.com/xml/note.xml'
        return_val = (
            "<note>"
            "<to>recipient</to>"
            "<from>sender</from>"
            "<heading>Reminder</heading>"
            "<body>Don't forgetweekend!</body>"
            "</note>"
        )

        mock_urlopen.return_value = io.StringIO(return_val)
        self.assertIsNotNone(
            get_remote_element(remote_url), 'Remote element returns None for url'
        )
        mock_urlopen.return_value = io.StringIO(return_val)
        self.assertIsNotNone(
            get_remote_element(remote_url, 'body'), 'Remote element returns None for "body"'
        )

    def test_get_elements(self):
        """ Tests get_elements for single and multiple XPATHs parsed from different data sources """

        self.assertEqual(get_elements(None, None), [], 'None check failed for get_elements')
        self.assertEqual(get_elements(u'<a />', u''), [], 'Empty check failed for get_elements')

        xml_content = (
            u'<b/>', u'<b></b>', u'<b b="bbb">btext<c />ctail</b>',
            u'<b/><b></b>', u'<b/><b></b><b b="bbb">btext<c />ctail</b>'
        )

        for xml in xml_content:
            elements = get_elements(f'<a>{xml}</a>', 'b')
            targeted = fromstring(f'<x>{xml}</x>').findall('b')

            for idx, elem in enumerate(elements):
                self.assert_elements_are_equal(elem, targeted[idx], 'a/b')

        xpath = 'c/d'
        targeted = fromstring(self.elem_data_str).findall(xpath)

        for data in self.elem_data_inputs:
            for idx, elem in enumerate(get_elements(data, xpath)):
                self.assert_elements_are_equal(elem, targeted[idx], 'a/' + xpath)

    def test_dict_to_element(self):
        """ Tests dictionary to element conversion on elements converted from different data sources """

        self.assertIsNone(dict_to_element(None), 'None check failed for dict_to_element')
        self.assertIsNone(dict_to_element({}), 'Empty dict check failed for dict_to_element')
        self.assertIsNone(dict_to_element(ElementTree()), 'ElementTree check failed for dict_to_element')

        base_elem = fromstring(self.elem_data_str)
        dict_elem = dict_to_element(self.elem_data_dict)
        empty_elem = Element(u'')

        self.assert_elements_are_equal(base_elem, dict_elem)

        self.assertIsInstance(dict_to_element(base_elem), ElementType)
        self.assertIsInstance(dict_to_element(dict_elem), ElementType)
        self.assertIsInstance(dict_to_element(empty_elem), ElementType)

        # Test that invalid dict values result in syntax error
        with self.assertRaises(SyntaxError):
            dict_to_element({'a': 'aaa'})

        for bad_xml in (self, list(), set(), tuple(), ['a'], {'b'}, ('c',)):
            # Assert that non-XML values result in TypeError
            with self.assertRaises(TypeError):
                dict_to_element(bad_xml)

        # Test that invalid file or string IO objects are handled the cElementTree way
        with self.assertRaises(TypeError):
            dict_to_element(io.StringIO('NOT XML'))

    def test_element_to_dict(self):
        """ Tests element to dictionary conversion on elements converted from different data sources """

        self.assertEqual(element_to_dict(None), {}, 'None check failed for element_to_dict')

        base_dict = element_to_dict(self.elem_data_str)
        base_elem = get_element(self.elem_data_str)

        for data in self.elem_data_inputs:
            test_dict = element_to_dict(data)

            # Test conversion to and from for each data input
            self.assertEqual(
                base_dict, test_dict, 'Converted dictionary equality check failed for {0}'.format(type(data).__name__)
            )
            self.assert_elements_are_equal(base_elem, dict_to_element(test_dict))

            # Test conversion to and from for each data input with element path
            for elem in base_elem:
                test_child = [c for c in test_dict['children'] if c['name'] == elem.tag][0]
                self.assertEqual(element_to_dict(base_elem, elem.tag), test_child)
                self.assert_elements_are_equal(elem, dict_to_element(test_child))

        # Test conversion with element path for each sub-element
        for elem in base_elem:
            self.assertEqual(
                element_to_dict(base_elem, elem.tag),
                element_to_dict(get_element(base_elem, elem.tag))
            )

    def test_element_to_object(self):
        """ Tests element to object conversion on elements converted from different data sources """

        self.assertEqual(element_to_object(None), (u'', {u'': {}}), 'None check failed for element_to_object')

        base_elem = get_element(self.elem_data_str)
        base_obj = element_to_object(self.elem_data_str)

        # Test conversion to object for each data input
        for data in self.elem_data_inputs:
            test_obj = element_to_object(data)
            self.assertEqual(
                base_obj, test_obj, 'Converted object equality check failed for {0}'.format(type(data).__name__)
            )

        # Test conversion with element path for each sub-element
        for elem in base_elem:
            self.assertEqual(
                element_to_object(base_elem, elem.tag),
                element_to_object(get_element(base_elem, elem.tag))
            )

    def test_element_to_string(self):
        """ Tests element conversion from different data sources to XML, with and without a declaration line """

        self.assertEqual('', element_to_string(None), 'None check failed for element_to_string')
        self.assertEqual('', element_to_string(b''), 'Binary check failed for element_to_string')
        self.assertEqual('', element_to_string(''), 'Unicode check failed for element_to_string')
        self.assertEqual('', element_to_string(io.StringIO('')), 'StringIO check failed for element_to_string')

        self.assertEqual(
            self.elem_data_bin.decode(DEFAULT_ENCODING).replace(os.linesep, '\n').strip(),
            element_to_string(fromstring(self.elem_data_str), include_declaration=False),
            'Raw string check failed for element_to_string'
        )

    def test_element_to_string_with_dec(self):
        """ Tests element conversion from different data sources to XML, with and without a declaration line """

        as_string = element_to_string(fromstring(self.elem_data_str))

        for data in self.elem_data_inputs:
            data_type = type(data).__name__
            self.assertEqual(
                element_to_string(data), as_string,
                f'With declaration check failed for element_to_string for {data_type}'
            )

    def test_element_to_string_wout_dec(self):
        """ Tests conversion from different data sources to XML, with and without a declaration line """

        as_string = element_to_string(fromstring(self.elem_data_str), include_declaration=False)

        for data in self.elem_data_inputs:
            data_type = type(data).__name__
            self.assertEqual(
                element_to_string(data, include_declaration=False), as_string,
                f'Without declaration check failed for element_to_string for {data_type}'
            )

    def test_string_to_element(self):
        """ Tests element conversion from different data sources to XML, with and without a declaration line """

        for empty in self.elem_empty_inputs:
            self.assertIsNone(string_to_element(empty), 'Empty check failed for string_to_element')

        parsed = fromstring(self.elem_data_str)

        # Ensure elements and element trees are passed back unchanged

        self.assertIs(string_to_element(parsed), parsed, 'Hard equality test failed for string_to_element')
        self.assertIs(
            string_to_element(ElementTree(parsed)), parsed, 'Tree equality test failed for string_to_element'
        )

        # Ensure binary and string reader objects are processed

        self.assert_elements_are_equal(
            string_to_element(self.elem_data_bin), parsed,
            'Binary equality test failed for string_to_element'
        )
        self.assert_elements_are_equal(
            string_to_element(self.elem_data_reader), parsed,
            'StringIO equality test failed for string_to_element'
        )

        # Test that invalid string values are handled the cElementTree way
        with self.assertRaises(SyntaxError):
            string_to_element('NOT XML')

        # Test that invalid file or string IO objects are handled the cElementTree way
        with self.assertRaises(SyntaxError):
            string_to_element(io.StringIO('NOT XML'))

        for bad_xml in (self, list(), set(), tuple(), ['a'], {'b'}, ('c',)):
            # Assert that non-XML values result in TypeError
            with self.assertRaises(TypeError):
                string_to_element(bad_xml)

        # Test include_namespaces: parsing of name-spaced and stripped string data

        with open(self.namespace_file_path, 'rb') as data:
            namespaced = data.read()

            unstripped = string_to_element(namespaced, include_namespaces=True)
            self.assert_elements_are_equal(unstripped, fromstring(namespaced))

            stripped = string_to_element(namespaced, include_namespaces=False)
            self.assert_elements_are_equal(stripped, fromstring(strip_namespaces(namespaced)))

            with self.assertRaises(AssertionError):
                self.assert_elements_are_equal(unstripped, stripped)

    def test_iter_elements(self):
        """ Tests iter_elements with a custom function on elements from different data sourcs """

        self.assertIsNone(iter_elements(None, None), 'None check failed for iter_elements')
        self.assert_elements_are_equal(fromstring(b'<a/>'), iter_elements(set_element_attributes, '<a/>'))
        self.assert_elements_are_equal(fromstring(u'<a/>'), iter_elements(set_element_attributes, b'<a/>'))

        base_elem = fromstring(u'<a><b /><c /></a>').find(self.elem_xpath)
        base_elem.attrib = {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}

        def iter_elements_func(elem, **attrib_kwargs):
            """ Test function for iter_elements test """
            set_element_attributes(clear_element(elem), **attrib_kwargs)

        for data in self.elem_data_inputs:
            test_elem = iter_elements(iter_elements_func, data, **base_elem.attrib)
            self.assert_elements_are_equal(test_elem.find(self.elem_xpath), base_elem)

    def test_iterparse_elements(self):

        # Test with some basic invalid inputs
        self.assertIsNone(iterparse_elements(None, None), 'None check failed for iter_elements')
        self.assertIsNone(iterparse_elements('', None), 'Empty check failed for iter_elements')

        # Test with file path and file object
        self._test_iterparse_elements_op(io.StringIO(self.elem_ascii_str), self.elem_ascii_str)
        self._test_iterparse_elements_op(self.elem_ascii_file_path, self.elem_ascii_str)

        # Test with file path and file object
        self._test_iterparse_elements_op(self.elem_data_reader, self.elem_data_str)
        self._test_iterparse_elements_op(self.elem_data_file_path, self.elem_data_str)

    def _test_iterparse_elements_op(self, elem_to_parse, target_string):

        base_attribs = {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}
        base_elem = fromstring(u'<a />')

        def iterparse_func(elem, **attrib_kwargs):
            """
            Test function for iterparse_elements test. This function is run once for every element
            in the file being parsed. The original file is not changed, but a local variable can be.
            """
            if elem.tag == self.elem_xpath:
                elem.attrib = attrib_kwargs
                self.assert_elements_are_equal(
                    elem, copy_element(elem, insert_element(base_elem, 0, self.elem_xpath))
                )

        iterparse_elements(iterparse_func, elem_to_parse, **base_attribs)

        existing_elem = fromstring(target_string).find(self.elem_xpath)
        existing_elem.attrib = base_attribs

        self.assert_elements_are_equal(base_elem.find(self.elem_xpath), existing_elem)

    def test_strip_namespaces(self):
        """ Tests namespace stripping by comparing equivalent XML from different data sources """

        self.assertEqual(strip_namespaces(None), None, 'None check failed for strip_namespaces')
        self.assertEqual(strip_namespaces(b''), u'', 'Bin check failed for strip_namespaces')
        self.assertEqual(strip_namespaces(''), u'', 'Str check failed for strip_namespaces')
        self.assertEqual(strip_namespaces(io.StringIO('')), u'', 'IO check failed for strip_namespaces')
        self.assertEqual(strip_namespaces([]), [], 'List check failed for strip_namespaces')

        with open(self.namespace_file_path, 'rb') as namespace_file:
            self._test_strip_namespaces(namespace_file)

    def test_strip_namespaces_with_binary(self):
        """ Tests namespace stripping by comparing equivalent XML from different data sources """

        with open(self.namespace_file_path, 'rb') as data:
            xml_content = data.read()

        self._test_strip_namespaces(xml_content)

    def test_strip_namespaces_with_string(self):
        """ Tests namespace stripping by comparing equivalent XML from different data sources """

        with open(self.namespace_file_path, 'rb') as data:
            self._test_strip_namespaces(data.read())

    def _test_strip_namespaces(self, to_strip):
        """ Tests namespace stripping by comparing equivalent XML from different data sources """

        stripped = fromstring(strip_namespaces(to_strip))

        for data in self.elem_data_inputs:
            self.assert_elements_are_equal(get_element(data), stripped)

    def test_strip_xml_declaration(self):
        """ Tests namespace stripping by comparing equivalent XML from different data sources """

        self.assertEqual(strip_xml_declaration(None), None, 'None check failed for strip_xml_declaration')
        self.assertEqual(strip_xml_declaration(b''), u'', 'Bin check failed for strip_xml_declaration')
        self.assertEqual(strip_xml_declaration(''), u'', 'Str check failed for strip_xml_declaration')
        self.assertEqual(strip_xml_declaration(io.StringIO('')), u'', 'IO check failed for strip_xml_declaration')
        self.assertEqual(strip_xml_declaration([]), [], 'List check failed for strip_xml_declaration')

        target = u'<root a="aaa" b="bbb">text</root>'
        test_unicode = _EMPTY_XML_1 + target
        test_binary = test_unicode.encode(DEFAULT_ENCODING)

        self.assertEqual(strip_xml_declaration(test_unicode), target, 'Unicode check failed for strip_xml_declaration')
        self.assertEqual(strip_xml_declaration(test_binary), target, 'Binary check failed for strip_xml_declaration')

    def test_write_element_to_path(self):
        """ Tests writing an element to a file path, reading it in, and testing the content for equality """

        for data in self.elem_data_inputs:

            if os.path.exists(self.test_file_path):
                os.remove(self.test_file_path)

            write_element(data, self.test_file_path)

            with open(self.test_file_path, 'rb') as test:
                self.assert_elements_are_equal(get_element(test), fromstring(self.elem_data_str))

    def test_write_element_to_file(self):
        """ Tests writing an element to a file object, reading it in, and testing the content for equality """

        for data in self.elem_data_inputs:

            if os.path.exists(self.test_file_path):
                os.remove(self.test_file_path)

            with open(self.test_file_path, 'wb') as test:
                write_element(data, test)

            with open(self.test_file_path, 'rb') as test:
                self.assert_elements_are_equal(get_element(test), fromstring(self.elem_data_str))


class XMLPropertyTests(XMLTestCase):

    def assert_element_values_equal(self, prop, value1, value2):
        """ Ensures the two trimmed values are equal, and fails with an informative message """

        val1, val2 = self._reduce_property(value1), self._reduce_property(value2)

        self.assertEqual(
            val1, val2,
            'Element {0} properties are not equal: "{1}" ({2}) != "{3}" ({4})'.format(
                prop, val1, type(val1).__name__, val2, type(val2).__name__
            )
        )

    def assert_element_property_getter(self, prop, elem_func, elem_xpath=None, default_target=None, **elem_kwargs):
        """ Ensures the properties returned by the function are as expected for all data sources """

        self.assert_element_values_equal(prop, elem_func(None, **elem_kwargs), default_target)
        self.assert_element_values_equal(
            prop, elem_func('<a/>', **elem_kwargs), 'a' if prop == ELEM_NAME else default_target
        )

        base_elem = fromstring(self.elem_data_str)
        if elem_xpath:
            base_elem = base_elem.find(elem_xpath)

        base_prop = getattr(base_elem, prop) or default_target

        for data in self.elem_data_inputs:
            self.assert_element_values_equal(prop, elem_func(data, **elem_kwargs), base_prop)

    def test_get_element_attribute(self):
        """
        Tests get_element_attribute for null, empty, and non-existent attributes; also
        tests that an attribute returned from different data sources matches the expected
        """
        default_val = 'x'

        self.assertEqual(
            default_val, get_element_attribute(None, None, default_val),
            'Value check for get null element attribute failed.'
        )
        self.assertEqual(
            default_val, get_element_attribute('<a/>', None, default_val),
            'Value check for get empty element attribute failed.'
        )
        self.assertEqual(
            default_val, get_element_attribute('<a/>', 'a', default_val),
            'Value check for get non-existent element attribute failed.'
        )

        base_elem = fromstring(self.elem_data_str)
        base_key = list(base_elem.attrib.keys())[0]
        base_val = base_elem.attrib[base_key]

        for data in self.elem_data_inputs:
            self.assert_element_values_equal(
                f'attributes.{base_key}', get_element_attribute(data, base_key), base_val
            )

    def test_get_element_attributes(self):
        """
        Tests get_element_attributes for null and empty attributes; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_ATTRIBS, get_element_attributes, default_target={})

    def test_get_element_attributes_xpath(self):
        """
        Tests get_element_attributes with an XPATH for null and empty attributes; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_ATTRIBS, get_element_attributes, self.elem_xpath, element_path=self.elem_xpath, default_target={}
        )

    def test_add_element_attributes(self):
        """
        Tests set_element_attributes for null, empty, and new attributes; also
        tests that attributes are added to elements parsed from different data sources
        """
        new_attrs = {'x': 'xxx', 'y': 'yyy', 'z': 'zzz'}

        self.assertIsNone(set_element_attributes(None), 'None check for adding element attributes failed.')
        self.assertEqual(
            {}, set_element_attributes('<a/>'),
            'Value check for adding empty element attributes failed.'
        )
        self.assertEqual(
            new_attrs, set_element_attributes('<a/>', x='xxx', y='yyy', z='zzz'),
            'Value check for adding all new element attributes failed.'
        )

        base_elem = fromstring(self.elem_data_str)
        base_attrs = base_elem.attrib
        base_attrs.update(new_attrs)

        for data in self.elem_data_inputs:
            self.assert_element_values_equal(
                'attributes', set_element_attributes(data, **new_attrs), base_attrs
            )

        set_element_attributes(base_elem, **new_attrs)

        self.assert_element_values_equal('attributes', base_elem.attrib, base_attrs)

    def test_remove_element_attributes(self):
        """
        Tests remove_element_attributes for null, empty, and non-existent attributes; also
        tests that attributes are removed successfully from elements parsed from different data sources
        """
        self.assertIsNone(
            remove_element_attributes(None),
            'None check for removing element attributes failed.'
        )
        self.assertEqual(
            {}, remove_element_attributes('<a/>'),
            'Value check for removing empty element attributes failed.'
        )
        self.assertEqual(
            {}, remove_element_attributes('<a/>', 'x', 'y', 'z'),
            'Value check for removing non-existent element attributes failed.'
        )

        base_elem = fromstring(self.elem_data_str)
        base_attrs = base_elem.attrib
        base_keys = base_attrs.keys()

        for data in self.elem_data_inputs:
            self.assert_element_values_equal(
                'attributes', remove_element_attributes(data, *base_keys), base_attrs
            )

        remove_element_attributes(base_elem, *base_keys)

        self.assert_element_values_equal('attributes', base_elem.attrib, {})

    def test_get_element_name(self):
        """
        Tests get_element_name with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_NAME, get_element_name)

    def test_get_element_tail(self):
        """
        Tests test_get_element_tail with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_TAIL, get_element_tail, default_target='x', default_value='x')

    def test_get_element_tail_xpath(self):
        """
        Tests test_get_element_tail with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_TAIL, get_element_tail,
            self.elem_xpath, default_target='x', default_value='x', element_path=self.elem_xpath
        )

    def test_get_element_text(self):
        """
        Tests get_element_text with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_TEXT, get_element_text, default_target='x', default_value='x')

    def test_get_element_text_xpath(self):
        """
        Tests get_element_text with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_TEXT, get_element_text,
            self.elem_xpath, default_target='x', default_value='x', element_path=self.elem_xpath
        )

    def test_get_elements_attributes(self):
        """
        Tests get_elements_attributes with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_ATTRIBS, get_elements_attributes, default_target=[])

    def test_get_elements_attributes_xpath(self):
        """
        Tests get_elements_attributes with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_ATTRIBS, get_elements_attributes, self.elem_xpath,
            default_target=[], element_path=self.elem_xpath
        )

    def test_get_elements_attributes_xpath_attrs(self):
        """
        Tests get_elements_attributes with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        base_elem = fromstring(self.elem_data_str).find(self.elem_xpath)
        base_prop = getattr(base_elem, ELEM_ATTRIBS)

        # Test all attributes at path "c" for all but self.elem_data_reader, which can only be read once
        for data in self.elem_data_inputs[:-1]:
            for attr in base_prop:
                parsed = get_elements_attributes(data, element_path=self.elem_xpath, attrib_name=attr)
                self.assert_element_values_equal(ELEM_ATTRIBS, parsed[0], base_prop[attr])

    def test_get_elements_tail(self):
        """
        Tests get_elements_tail with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_TAIL, get_elements_tail, default_target=[])

    def test_get_elements_text(self):
        """
        Tests get_elements_text with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(ELEM_TEXT, get_elements_text, default_target=[])

    def test_get_elements_text_xpath(self):
        """
        Tests get_elements_text with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_TEXT, get_elements_text,
            self.elem_xpath, default_target=[], element_path=self.elem_xpath
        )

    def test_get_elements_tail_xpath(self):
        """
        Tests get_elements_tail with an XPATH with null and empty elements; also
        tests that attributes returned from different data sources match those expected
        """
        self.assert_element_property_getter(
            ELEM_TAIL, get_elements_tail,
            self.elem_xpath, default_target=[], element_path=self.elem_xpath
        )

    def assert_element_property_setter(self, prop, elem_func, default=None, target=None, **elem_kwargs):
        """ Ensures the properties returned by the function are as expected for all data sources """

        def wrap_property(value):
            return value if isinstance(value, list) else [value]

        self.assert_element_values_equal(prop, elem_func(None, **elem_kwargs), default)

        target = wrap_property(target)

        self.elem_data_inputs += ('<a/>',)  # Test with empty element too

        for data in self.elem_data_inputs:
            elems = wrap_property(elem_func(data, **elem_kwargs))

            for idx, val in enumerate((getattr(elem, prop) for elem in elems)):
                self.assert_element_values_equal(prop, val, target[idx] if target else u'')

    def test_set_element_tail_none(self):
        self.assert_element_property_setter(ELEM_TAIL, set_element_tail, target=[], element_tail=None)

    def test_set_element_tail_one(self):
        self.assert_element_property_setter(ELEM_TAIL, set_element_tail, target='x', element_tail='x')

    def test_set_element_tail_xpath(self):
        """ Tests set_element_tail with an XPATH with null and empty values, and data from different sources """

        self.assert_element_property_setter(
            ELEM_TAIL, set_element_tail, target='x', element_path=self.elem_xpath, element_tail='x'
        )

    def test_set_element_text_none(self):
        self.assert_element_property_setter(ELEM_TEXT, set_element_text, target=[], element_text=None)

    def test_set_element_text_one(self):
        self.assert_element_property_setter(ELEM_TEXT, set_element_text, target='x', element_text='x')

    def test_set_element_text_xpath(self):
        """ Tests set_element_text with an XPATH with null and empty values, and data from different sources """

        self.assert_element_property_setter(
            ELEM_TEXT, set_element_text, target='x', element_path=self.elem_xpath, element_text='x'
        )

    def test_set_elements_text_none(self):
        self.assert_element_property_setter(ELEM_TEXT, set_elements_text, default=[], target=[], text_values=None)

    def test_set_elements_text_str(self):
        self.assert_element_property_setter(ELEM_TEXT, set_elements_text, default=[], target=['x'], text_values='x')

    def test_set_elements_text_list(self):
        self.assert_element_property_setter(ELEM_TEXT, set_elements_text, default=[], target=['x'], text_values=['x'])

    def test_set_elements_texts(self):
        """ Tests set_elements_text with null, empty and multiple valid values, with data from different sources """

        target = ['x', 'y', 'z']
        self.assert_element_property_setter(
            ELEM_TEXT, set_elements_text, default=[], target=target[0], text_values=target
        )

    def test_set_elements_text_xpath(self):
        """ Tests set_elements_text with an XPATH with null and empty values, and with data from different sources """

        elem_xpath = self.elem_xpath
        self.assert_element_property_setter(
            ELEM_TEXT, set_elements_text, default=[], target=['x'], element_path=elem_xpath, text_values=['x']
        )

    def test_set_elements_texts_xpath(self):
        """
        Tests set_elements_text with an XPATH with both invalid and valid values, and with data from different sources
        """
        target = ['x', 'y', 'z']
        elem_xpath = self.elem_xpath

        self.assert_element_property_setter(
            ELEM_TEXT, set_elements_text, default=[], target=target, element_path=elem_xpath, text_values=target
        )

    def test_set_elements_tail_none(self):
        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=[], tail_values=None
        )

    def test_set_elements_tail_str(self):
        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=['x'], tail_values='x'
        )

    def test_set_elements_tail_list(self):
        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=['x'], tail_values=['x']
        )

    def test_set_elements_tails(self):
        """ Tests set_elements_tail with null, empty and multiple valid values, with data from different sources """

        target = ['x', 'y', 'z']
        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=target[0], tail_values=target
        )

    def test_set_elements_tail_xpath(self):
        """ Tests set_elements_tail with an XPATH with null and empty values, and with data from different sources """

        elem_xpath = self.elem_xpath
        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=['x'], element_path=elem_xpath, tail_values=['x']
        )

    def test_set_elements_tails_xpath(self):
        """
        Tests set_elements_tail with an XPATH with null, empty and multiple valid values,
        and with data from different sources
        """
        target = ['x', 'y', 'z']
        elem_xpath = self.elem_xpath

        self.assert_element_property_setter(
            ELEM_TAIL, set_elements_tail, default=[], target=target, element_path=elem_xpath, tail_values=target
        )


class XMLCheckTests(XMLTestCase):

    def test_element_exists(self):
        """ Tests element_exists with different params including None """

        self.assertFalse(element_exists(None), 'None check failed for element_exists')

        for data in self.elem_data_inputs:
            self.assertTrue(element_exists(data), 'element_exists returned False for {0}'.format(type(data).__name__))

    def test_element_exists_xpath(self):
        """ Tests element_exists at an XPATH location with different element data """

        self.assertFalse(
            element_exists(None, self.elem_xpath),
            f'None check failed for element_exists at XPATH "{self.elem_xpath}"'
        )
        for data in self.elem_data_inputs:
            self.assertTrue(
                element_exists(data, self.elem_xpath),
                'element_exists returned False for {0} at XPATH "{1}"'.format(type(data).__name__, self.elem_xpath)
            )

    def assert_elements_exist(self, test_func, elem_xpaths=[], all_exist=False, target=True):
        """ Ensures element existence agrees with target for each data source """

        self.assertFalse(elements_exist(None, elem_xpaths, all_exist), f'None check failed for {test_func}')

        for data in self.elem_data_inputs:
            exists = elements_exist(data, elem_xpaths, all_exist)

            self.assertEqual(
                exists, target,
                '{0}: elements_exist returned {1} for {2}'.format(test_func, exists, type(data).__name__)
            )

    def assert_element_is_empty(self, test_func, elem_xpath=None, target=True):
        """ Ensures element emptiness agrees with target for each data source """

        for data in self.elem_data_inputs:
            is_empty = element_is_empty(data, elem_xpath)

            self.assertEqual(
                is_empty, target,
                '{0}: element_is_empty returned {1} for {2}'.format(test_func, is_empty, type(data).__name__)
            )

    def test_elements_exist(self):
        """ Tests elements_exist with defaults with different element data """
        self.assert_elements_exist('test_elements_exist')

    def test_elements_exist_all_xpaths(self):
        """ Tests elements_exist at all specified XPATH locations with different element data """
        self.assert_elements_exist('test_elements_exist_all_xpaths', ('b', 'c'), True)

    def test_elements_exist_any_xpaths(self):
        """ Tests elements_exist at any of several XPATH locations with different element data """
        self.assert_elements_exist('test_elements_exist_any_xpaths', ('a', 'b', 'c'))

    def test_elements_exist_no_xpaths(self):
        """ Tests elements_exist at none of several XPATH locations with different element data """
        self.assert_elements_exist('test_elements_exist_no_xpaths', ('x', 'y', 'z'), target=False)

    def test_elements_exist_not_all_xpaths(self):
        """ Tests elements_exist at only some of several XPATH locations with different element data """
        self.assert_elements_exist('test_elements_exist_not_all_xpaths', ('a', 'b', 'c'), True, False)

    def test_element_is_empty(self):
        """ Tests element_is_empty with empty and non-empty values, and different data sources """

        for empty in (None, '<a />', '<a></a>'):
            self.assertTrue(element_is_empty(empty), f'Empty check failed for {empty}: False')

        for not_empty in ('<a>aaa</a>', '<a x="xxx"></a>', '<a><b /></a>', '<a><b></b></a>'):
            self.assertFalse(element_is_empty(not_empty), f'Empty check failed for {not_empty}: True')

        self.assert_element_is_empty('test_element_is_empty', target=False)

    def test_element_is_empty_xpath(self):
        """ Tests element_is_empty at an XPATH location with different non-empty element data sources """

        empties = ('<a />', '<a></a>', '<a><b /></a>', '<a><b></b></a>')
        for empty in empties:
            self.assertTrue(element_is_empty(empty, 'b'), f'Empty check failed for {empty}: False')

        not_empties = (
            '<a><b>bbb</b></a>', '<a><b></b>bbb</a>', '<a><b x="xxx"></b></a>',
            '<a><b><c /></b></a>', '<a><b><c></c></b></a>'
        )
        for not_empty in not_empties:
            self.assertFalse(element_is_empty(not_empty, 'b'), f'Empty check failed for {not_empty}: True')

        self.assert_element_is_empty('test_element_is_empty_xpath', self.elem_xpath, False)

    def test_element_is_not_empty_xpath(self):
        """ Tests element_is_empty at an XPATH location with different empty element data sources """
        self.assert_element_is_empty('test_element_is_not_empty_xpath', 'c/f')


class XMLInsertRemoveTests(XMLTestCase):

    def assert_element_inserted(self, **elem_kwargs):
        """ Ensures element inserts are done correctly at various indexes and for each data source  """

        insert_kwargs = {'elem_path': elem_kwargs[ELEM_NAME]}
        insert_kwargs.update(elem_kwargs[ELEM_ATTRIBS])

        # Test that an element has been inserted at different indices

        base_elem = fromstring(self.elem_data_str)

        inserted = insert_element(base_elem, 0, elem_txt='middle', **insert_kwargs)
        self.assert_elements_are_equal(base_elem.find(insert_kwargs['elem_path']), inserted)

        inserted = insert_element(base_elem, 0, elem_txt='first', **insert_kwargs)
        self.assert_elements_are_equal(base_elem.findall(insert_kwargs['elem_path'])[0], inserted)

        inserted = insert_element(base_elem, 2, elem_txt='last', **insert_kwargs)
        self.assert_elements_are_equal(base_elem.findall(insert_kwargs['elem_path'])[2], inserted)

        # Test that elements inserted into different data sources are valid

        insert_kwargs['elem_txt'] = elem_kwargs[ELEM_TEXT]

        for data in self.elem_data_inputs:
            inserted = insert_element(data, 0, **insert_kwargs)
            self.assertIsNotNone(inserted, 'Insert failed for {0}'.format(type(data).__name__))

            # All of the original values should be accessible through inserted
            for key, val in elem_kwargs.items():
                elem_val = getattr(inserted, key)

                if '/' in val:
                    val = val.split('/')[-1]

                self.assertEqual(val, elem_val, '{0} was not inserted correctly for {1}: {2} != {3}'.format(
                    key, type(data).__name__, elem_val, val
                ))

    def assert_elements_removed(self, test_func, elem_xpaths, clear_empty=False):
        """ Ensures elements for all elem_xpaths in different data sources have been removed and cleared """

        self.assertEqual(
            remove_elements(None, elem_xpaths, clear_empty), [], f'None check failed for {test_func}'
        )
        self.assertEqual(
            remove_elements(self.elem_data_str, [], clear_empty), [], f'Empty XPATH check failed for {test_func}'
        )

        base_elem = fromstring(self.elem_data_str)
        is_xpath = isinstance(elem_xpaths, str)

        for data in self.elem_data_inputs:

            data = get_element(data) if clear_empty else data
            removed = remove_elements(data, elem_xpaths, clear_empty)

            if is_xpath:
                self.assert_element_removed(test_func, data, elem_xpaths, removed, base_elem, clear_empty)
            else:
                for xpath in elem_xpaths:
                    filtered = [rem for rem in removed if rem.tag in xpath]
                    self.assert_element_removed(test_func, data, xpath, filtered, base_elem, clear_empty)

    def assert_element_removed(self, test_func, data, elem_xpath, removed_elems, base_elem, clear_empty):
        """ Ensures removed_elems have been removed and cleared """

        if clear_empty:
            self.assert_removed_element_cleared(test_func, elem_xpath, data, removed_elems, base_elem)
        else:
            found = base_elem.findall(elem_xpath)

            ecount, rcount = len(found), len(removed_elems)
            self.assertEqual(
                ecount, rcount, f'Only {rcount} of {ecount} elements were cleared for {test_func}'
            )

            for idx, elem in enumerate(removed_elems):
                self.assert_elements_are_equal(found[idx], elem, elem_xpath)

    def assert_removed_element_cleared(self, test_func, elem_xpath, cleared_elem, removed_elems, base_elem):
        """ Ensures removed_elems are removed from cleared_elem, and present in the return value """

        elem_xroot = elem_xpath.split('/')[0]
        elem_xtags = elem_xpath.split('/')[1:]

        removed_tags = [rem.tag for rem in removed_elems]

        xpath = elem_xroot

        for xtag in elem_xtags:

            xpath += '/' + xtag
            ecount = len(base_elem.findall(xpath))
            rcount = removed_tags.count(xtag)

            self.assertEqual(
                ecount, rcount, f'Only {rcount} of {ecount} elements were cleared for {test_func}'
            )
            self.assertFalse(
                iselement(cleared_elem.find(xpath)), f'Element {cleared_elem.tag} was not cleared for {test_func}'
            )

    def test_insert_element(self):
        """ Tests insert_element with valid/invalid values, and with different data sources at various indices """

        self.assertIsNone(insert_element(None, None, None), 'Insert with all None check failed for insert_element')
        self.assertIsNone(
            insert_element(self.elem_data_str, None, None), 'Insert with empty path check failed for insert_element'
        )
        self.assertIsNone(
            insert_element(None, None, 'none'), 'Insert with empty data check failed for insert_element'
        )
        self.assert_element_inserted(tag='p', text='ppp', attrib={'q': 'qqq', 'r': 'rrr', 's': 'sss'})

    def test_insert_element_xpath(self):
        """ Tests insert_element at an XPATH location with different valid/invalid data sources at various indices """
        self.assert_element_inserted(tag='t/u/v', text='www', attrib={'x': 'xxx', 'y': 'yyy', 'z': 'zzz'})

    def test_remove_element(self):
        """ Tests remove_element with None, and for equality given different data sources """
        self.assert_element_function(remove_element, self.elem_xpath, element_path=self.elem_xpath)

    def test_remove_element_clear(self):
        """ Tests remove_element with clearing of empty elements from different data sources  """

        elem_xpath = 'c/g/h/i'
        base_elem = fromstring(self.elem_data_str)

        for data in self.elem_data_inputs:
            element = get_element(data)
            removed = remove_element(element, elem_xpath, True)

            self.assert_removed_element_cleared('test_remove_element_clear', elem_xpath, element, removed, base_elem)

    def test_remove_elements_single(self):
        """ Tests remove_elements with a single XPATH but different data sources """
        self.assert_elements_removed('test_remove_elements_single', self.elem_xpath)

    def test_remove_elements_single_clear(self):
        """ Tests remove_elements with a single XPATH, clearing empty elements from different data sources """
        self.assert_elements_removed('test_remove_elements_single_clear', 'c/g/h/i', clear_empty=True)

    def test_remove_elements_multiple(self):
        """ Tests remove_elements with multiple XPATHs and different data sources """
        self.assert_elements_removed('test_remove_elements_multiple', ('c/d', 'c/e', 'c/f', 'c/g/h/i'))

    def test_remove_elements_multiple_clear(self):
        """ Tests remove_elements with multiple XPATHs, clearing empty elements from different data sources """

        elem_xpaths = ('c/d', 'c/e', 'c/f', 'c/g/h/i')
        self.assert_elements_removed('test_remove_elements_multiple_clear', elem_xpaths, clear_empty=True)

    def test_remove_empty_element(self):

        # Ensure nothing is done when there are no children
        self.assertEqual(remove_empty_element(parent_to_parse='<a/>', element_path=''), [])

        # Ensure nothing is done when there are children, but no xpath
        self.assertEqual(remove_empty_element(parent_to_parse='<a><b/></a>', element_path=''), [])

        # Ensure a single element is removed and returned
        one_child = remove_empty_element(parent_to_parse='<a><b/></a>', element_path='b')
        self.assertEqual(len(one_child), 1)
        self.assertEqual(one_child[0].tag, 'b')

        # Ensure nothing is done when there are attributes
        self.assertEqual(remove_empty_element(parent_to_parse='<a><b x="xxx" /></a>', element_path='b'), [])
        # Ensure nothing is done when there is text
        self.assertEqual(remove_empty_element(parent_to_parse='<a><b>bbb</b></a>', element_path='b'), [])
        # Ensure nothing is done when there is a tail
        self.assertEqual(remove_empty_element(parent_to_parse='<a><b/>bbb</a>', element_path='b'), [])
        # Ensure nothing is done when there are children
        self.assertEqual(remove_empty_element(parent_to_parse='<a><b><c/><d/></b></a>', element_path='b'), [])

        # Ensure all elements are removed when stacked
        stacked_children = remove_empty_element(parent_to_parse='<a><b><c><d/></c></b></a>', element_path='b/c/d')
        self.assertEqual(len(stacked_children), 3)
        self.assertEqual({d.tag for d in stacked_children}, {'b', 'c', 'd'})

        # Ensure only the (first) child specified is removed
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><d/></b></a>', element_path='b/c')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'c')

        # Ensure only the (second) child specified is removed
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><d/></b></a>', element_path='b/d')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'd')

        # Ensure only the (first) empty child is removed when it precedes another
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><c>ccc</c><d/></b></a>', element_path='b/c')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'c')

        # Ensure only the (first) empty child is removed when it follows another
        nested_child = remove_empty_element(parent_to_parse='<a><b><c>ccc</c><c/><d/></b></a>', element_path='b/c')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'c')

        # Ensure both (first) empty children are removed
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><c/><d/></b></a>', element_path='b/c')
        self.assertEqual(len(nested_child), 2)
        self.assertEqual(u''.join(c.tag for c in nested_child), 'c' * 2)

        # Ensure only the (second) empty child is removed when it precedes another
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><d/><d>ddd</d></b></a>', element_path='b/d')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'd')

        # Ensure only the (second) empty child is removed when it follows another
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><d>ddd</d><d/></b></a>', element_path='b/d')
        self.assertEqual(len(nested_child), 1)
        self.assertEqual(nested_child[0].tag, 'd')

        # Ensure all three (second) empty children are removed
        nested_child = remove_empty_element(parent_to_parse='<a><b><c/><d/><d/><d/></b></a>', element_path='b/d')
        self.assertEqual(len(nested_child), 3)
        self.assertEqual(u''.join(d.tag for d in nested_child), 'd' * 3)
