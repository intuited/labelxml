"""Uses the lxml package to scrape data from the .odt labels file."""
import argparse
from lxml import etree
from functools import partial

_frame_xpath = 'draw:frame'

def draw_frames(root):
    return root.xpath('.//' + _frame_xpath, namespaces=root.nsmap)


_xpath_text_additions = {'yes': '[text()]',
                         'no': '[not text()]',
                         'either': ''}

_style_names = {'name': 'P10',
                'price': 'P9'}


def _field_filter(element, value, results):
    """Filter an xpath result set for the absence or presence of a name."""


def style_name_xpath(style_name):
    return 'text:p[@text:style-name="{0}"]'.format(style_name)

_field_names = ('name', 'price')
_field_xpaths = dict((name, style_name_xpath(_style_names[name]))
                     for name in _field_names)


def _yes_no_text(require_text, xpath):
    """Modify an xpath to filter or not for the presence of text."""
    return xpath + _xpath_text_additions[require_text]



def descendant_fields(field, with_text, root):
    text_filter = partial(_yes_no_text, with_text)
    xpath = './/' + text_filter(_field_xpaths[field])
    return root.xpath(xpath, namespaces=root.nsmap)


def product_names(root, with_text='yes'):
    """Return product names under the root.

    ``text_filter`` is applied to the xpath.
    """
    return descendant_fields('name', with_text, root)

def product_prices(root, with_text='yes'):
    """Return product prices under the root.

    ``text_filter`` is applied to the xpath.
    """
    return descendant_fields('price', with_text, root)


def field_predicate_xpath(with_text={'name': 'yes', 'price': 'yes'},
                          field_names=_field_names,
                          negations=()):
    """Generates an xpath for field predicates.

    The elements of ``select_seq`` select, negate, 

    If ``with_text`` is a dict, its elements
    determine how the fields are filtered
    based on the presence of text within them.

    It will default to 'yes' for any ungiven elements.

    If it is a string, that string is used for all fields.

    `negations` is a sequence of field names;
    if a field is negated, its absence will be searched for.
    """
    (with_text,
     with_text_default) = (({}, with_text) if isinstance(with_text, basestring)
                           else (with_text, 'yes'))

    def condition(field_name):
        return _yes_no_text(with_text.get(field_name, with_text_default),
                            _field_xpaths[field_name])

    def negate(condition, field):
        if hasattr(negations, field):
            return 'not({0})'.format(condition)
        return condition

    conditions = (negate(condition(field_name), field_name)
                  for field_name in field_names)

    descendant_conditions = ('.//' + condition for condition in conditions)

    return ' and '.join(descendant_conditions)

def draw_frames_with_names_and_prices(root, with_text='yes'):
    predicate = field_predicate_xpath(with_text)

    xpath = './/{0}[{1}]'.format(_frame_xpath, predicate)

    return root.xpath(xpath, namespaces=root.nsmap)



##__  dragons

def _first_or_none(seq):
    return seq[0] if len(seq) else None

def draw_frame_data(draw_frame):
    return {'name': _first_or_none(product_names(draw_frame)),
            'prices': _first_or_none(product_prices(draw_frame))}


def main():
    parser = argparse.ArgumentParser(
        description="Scrape data from the grainery's .odt-format label database.",
        )

    parser.add_argument(
        'content_file', 
        help="The XML file to scrape.\n"
             "Normally this will be found as the top-level file ``content.xml`` "
             "after unzipping the .odt file."
        )

    parser.add_argument(
        '--name',
        help='Enable/disable filtering on the presence of a name field.',
        default='yes',
        )

    ns = parser.parse()
