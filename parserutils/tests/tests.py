from parserutils.tests.collection_tests import DictsTestCase, ListTupleSetTestCase
from parserutils.tests.date_tests import DateTestCase
from parserutils.tests.element_tests import XMLCheckTests, XMLInsertRemoveTests, XMLPropertyTests, XMLTests
from parserutils.tests.number_tests import NumberTestCase
from parserutils.tests.string_tests import StringCasingTestCase, StringConversionTestCase
from parserutils.tests.url_tests import URLTestCase


class CollectionsTestCase(DictsTestCase, ListTupleSetTestCase):
    """ Consolidates all collection_tests for ease of execution """


class DatesTestCase(DateTestCase):
    """ Consolidates all date_tests for ease of execution """


class ElementsTestCase(XMLCheckTests, XMLInsertRemoveTests, XMLPropertyTests, XMLTests):
    """ Consolidates all element_tests for ease of execution """


class NumbersTestCase(NumberTestCase):
    """ Consolidates all number_tests for ease of execution """


class StringsTestCase(StringCasingTestCase, StringConversionTestCase):
    """ Consolidates all string_tests for ease of execution """


class URLParsingTestCase(URLTestCase):
    """ Consolidates all url_tests for ease of execution """
