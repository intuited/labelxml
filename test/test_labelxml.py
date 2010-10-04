"""Test suite for the labelxml script."""
import unittest
import labelxml as ls

def data_file(scriptfile):
    from os.path import join, abspath, dirname
    return join(dirname(abspath(scriptfile)),
                'data', 'labels_@2010-10-01T16:42:08.content.xml')

DATA_FILE = data_file(__file__)

class TextXPathGeneration(unittest.TestCase):
    def test_field_predicate(self):
        """Test the default constructed field predicate."""
        self.assertEqual(ls.field_predicate_xpath(),
                         './/text:p[@text:style-name="P10"]'
                            '[child::text()]'
                         ' and .//text:p[@text:style-name="P9"]'
                            '[child::text()]')

    def test_negated_predicates(self):
        self.assertEqual(ls.field_predicate_xpath(negations=('price')),
                         './/text:p[@text:style-name="P10"]'
                            '[child::text()] '
                         'and not(.//text:p[@text:style-name="P9"]'
                            '[child::text()])')

    def test_template_predicate(self):
        self.assertEqual(ls.template_xpath('{name} and {price}'),
                         './/text:p[@text:style-name="P10"]'
                            '[descendant::text()]'
                         ' and .//text:p[@text:style-name="P9"]'
                            '[descendant::text()]')

    def test_negated_template_predicate(self):
        """Test negation of xpaths using the default text settings.
        
        Note that unlike the field_predicate_xpath function,
        the template system uses the 'descendant' axis by default.
        """
        self.assertEqual(ls.template_xpath('{name} and {price}',
                                           negations=('name',)),
                         'not(.//text:p[@text:style-name="P10"]'
                            '[descendant::text()])'
                         ' and .//text:p[@text:style-name="P9"]'
                            '[descendant::text()]')

    def test_template_text_control(self):
        """Test yes/no/either text filters."""
        with_text_map = {'name': 'yes', 'price': 'no',
                         'alternate_name': 'either'}
        template = '({name} or {alternate_name}) and {price}'
        self.assertEqual(ls.template_xpath(template,
                                           with_text_map=with_text_map),
                         '(.//text:p[@text:style-name="P10"]'
                            '[descendant::text()]'
                          ' or .//text:p[@text:style-name="P6"]'
                         ') and .//text:p[@text:style-name="P9"]'
                            '[not(descendant::text())]' )

class LXMLBaseTestClass(unittest.TestCase):
    def setUp(self):
        from lxml import etree
        self.tree = etree.parse(DATA_FILE)
        self.root = self.tree.getroot()

class TestXPathValidity(LXMLBaseTestClass):
    def test_some_draw_frames_found(self):
        self.assertTrue(len(ls.draw_frames(self.root)))
    def test_some_product_names_found(self):
        self.assertTrue(len(ls.product_names(self.root)))
    def test_some_product_prices_found(self):
        self.assertTrue(len(ls.product_prices(self.root)))

class TestXPathFirstElement(LXMLBaseTestClass):
    def test_product_name_of_first_draw_frame(self):
        df = ls.draw_frames(self.root)[0]
        self.assertEqual(ls.product_names(df)[0].text,
                         'Updated from Speerville price list, Fery 19th, 2009 ')
    def test_first_product_name(self):
        self.assertEqual(ls.product_names(self.root)[0].text,
                         'Updated from Speerville price list, Fery 19th, 2009 ')
    def test_first_price(self):
        self.assertEqual(ls.product_prices(self.root)[0].text,
                         'community price rounded up to nearest nickel ')

class TestXPathLastElement(LXMLBaseTestClass):
    def test_product_name_of_last_draw_frame(self):
        """The last draw frame doesn't have a product name.  Gotcha!"""
        df = ls.draw_frames(self.root)[-1]
        self.assertEqual(ls.product_names(df), [])
    def test_last_product_name(self):
        self.assertEqual(ls.product_names(self.root)[-1].text,
                         'Red Quinoa')
    def test_last_price(self):
        self.assertEqual(ls.product_prices(self.root)[-1].text,
                         '$8.00')

class TestElementCounts(LXMLBaseTestClass):
    def test_draw_frame_count(self):
        """Test that lxml's count agrees with that of tidy | grep | wc.

        This is mostly just a sanity check on the xpath,
        since obviously lxml is reliable.
        """
        self.assertEqual(len(ls.draw_frames(self.root)),
                         169)
    def test_product_name_count(self):
        """Check the count of the number of product name fields containing text.

        The expected counts for this and the other product/price count tests
        are just regression tests,
        i.e. the expected counts were gleaned from the test data.
        """
        self.assertEqual(len(ls.product_names(self.root)),
                         115)
    def test_product_price_count(self):
        self.assertEqual(len(ls.product_prices(self.root)),
                         163)
    def test_all_product_name_count(self):
        """Include product name fields devoid of text in the count."""
        self.assertEqual(len(ls.product_names(self.root, with_text='either')),
                         143)
    def test_all_product_price_count(self):
        """Include product price fields devoid of text in the count."""
        self.assertEqual(len(ls.product_prices(self.root, with_text='either')),
                         172)

    def test_drawframes_with_products_and_prices(self):
        """All draw frame elements which have textual prices and products."""
        dfs = ls.select_frames(self.root)
        self.assertEqual(len(tuple(dfs)),
                         104)

    def test_frames_with_names_and_no_prices(self):
        frames = ls.select_frames(self.root, negations=('price'))
        self.assertEqual(len(tuple(frames)),
                         3)

class TestPage297(LXMLBaseTestClass):
    def setUp(self):
        super(TestPage297, self).setUp()
        self.page = self.root.xpath(
            ls.template_xpath('//draw:frame[@text:anchor-page-number="297"]'),
            namespaces=self.root.nsmap)

    def test_page_count(self):
        """There can be only one page 297."""
        self.assertEqual(len(self.page), 1)

    def test_descendant(self):
        """Labels which consist of two parts have a different style attribute.

        The P6 ("alternative_name") style is one alternate style.

        In such cases, the node with that style does not directly contain text;
        its contained elements do.

        Page 297 contains one such element.

        This test tests reading of its name with the 'descendant' axis
        being used to locate text nodes within the label node.
        """
        descentext = ls.xpath_text_formats('descendant')
        self.assertEqual(
            ls.frame_data(self.page[0],
                          text_formats=descentext)['name'],
            "Spelt Bran Bread")

    def test_descendant_or_self(self):
        """Try to read the name on page 297 with the descendant-or-self axis."""
        descentext = ls.xpath_text_formats('descendant-or-self')
        self.assertEqual(
            ls.frame_data(self.page[0],
                          text_formats=descentext)['name'],
            "Spelt Bran Bread")

    def test_child(self):
        """This one shouldn't work."""
        tf = ls.xpath_text_formats('child')
        self.assertEqual(
            ls.frame_data(self.page[0],
                          text_formats=tf)['name'],
            None)


def suite():
    from unittest import defaultTestLoader, TestCase, TestSuite
    load = defaultTestLoader.loadTestsFromTestCase
    cases = (g for g in globals().values()
               if type(g) == type and issubclass(g, TestCase))
    return TestSuite(load(c) for c in cases)

if __name__ == '__main__':
    unittest.main()
