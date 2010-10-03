"""Test suite for the labelscrape script."""
import unittest
import labelscrape as ls

def data_file(scriptfile):
    from os.path import join, abspath, dirname
    return join(dirname(abspath(scriptfile)),
                'data', 'labels_@2010-10-01T16:42:08.content.xml')

DATA_FILE = data_file(__file__)

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

class TestElementCounts(LXMLBaseTestClass):
    def test_draw_frame_count(self):
        self.assertEqual(len(ls.draw_frames(self.root)),
                         169)
    def test_product_name_count(self):
        self.assertEqual(len(ls.product_names(self.root)),
                         115)
    def test_product_price_count(self):
        self.assertEqual(len(ls.product_prices(self.root)),
                         163)
    def test_all_product_name_count(self):
        """Include product name fields devoid of text in the count."""
        self.assertEqual(len(ls.product_names(self.root, with_text=False)),
                         143)
    def test_all_product_price_count(self):
        """Include product price fields devoid of text in the count."""
        self.assertEqual(len(ls.product_prices(self.root, with_text=False)),
                         172)

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


if __name__ == '__main__':
    unittest.main()
