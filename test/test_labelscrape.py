"""Test suite for the labelscrape script."""
import unittest
import labelscrape

def data_file(scriptfile):
    from os.path import join, abspath, dirname
    return join(dirname(abspath(scriptfile)),
                'data', 'labels_@2010-10-01T16:42:08.content.xml')

DATA_FILE = data_file(__file__)

class TestXPathValidity(unittest.TestCase):
    def setUp(self):
        from lxml import etree
        self.tree = etree.parse(DATA_FILE)
        self.root = self.tree.getroot()

    def test_some_draw_frames_found(self):
        self.assertTrue(len(labelscrape.draw_frames(self.root)))
    def test_some_product_names_found(self):
        self.assertTrue(len(labelscrape.product_names(self.root)))
    def test_some_product_prices_found(self):
        self.assertTrue(len(labelscrape.product_prices(self.root)))


if __name__ == '__main__':
    unittest.main()
