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


def select_frames(root, with_text='yes',
                        field_names=_field_names,
                        negations=()):
    """Returns draw:frame elements which match the criteria.

    The parameters are described in the docstring for
    ``field_predicate_xpath``.
    """
    predicate = field_predicate_xpath(with_text, field_names, negations)

    xpath = './/{0}[{1}]'.format(_frame_xpath, predicate)

    return root.xpath(xpath, namespaces=root.nsmap)


def build_select_args(ns, field_names):
    """Builds parameters for ``select_frames``."""
    field_name_actions = ((field_name, getattr(ns, field_name))
                          for field_name in field_names)

    negations = []
    selected_fields = []
    for field_name in field_names:
        action = getattr(ns, field_name)
        if action != 'either':
            selected_fields.append(field_name)
        if action == 'no':
            negations.append(field_name)

    with_text = dict((field_name, getattr(ns, field_name + '_text'))
                     for field_name in field_names)

    return with_text, selected_fields, negations


##__  dragons

def _first_text_or_none(seq):
    return seq[0].text if len(seq) else None

def frame_data(frame):
    return {'name': _first_text_or_none(product_names(frame)),
            'price': _first_text_or_none(product_prices(frame))}


def main():
    from pprint import PrettyPrinter
    import json
    parser = argparse.ArgumentParser(
        description="Scrape data from the grainery's .odt-format label database.",
        )

    parser.set_defaults(
        format=PrettyPrinter(indent=2).pformat
        )

    parser.add_argument(
        'content_file', 
        help="The XML file to scrape.\n"
             "Normally this will be found as the top-level file ``content.xml`` "
             "after unzipping the .odt file."
        )
    parser.add_argument(
        '--name',
        help='Control filtering on the presence of a name field.',
        default='yes',
        choices=('yes', 'no', 'either'),
        )
    parser.add_argument(
        '--name-text',
        help='Determines whether the presence/absence of text'
             ' within a name field is required.',
        default='yes',
        choices=_xpath_text_additions.keys(),
        )
    parser.add_argument(
        '--price',
        help='Control filtering on the presence of a price field.',
        default='yes',
        choices=('yes', 'no', 'either'),
        )
    parser.add_argument(
        '--price-text',
        help='Determines whether the presence/absence of text'
             ' within a price field is required.',
        default='yes',
        choices=_xpath_text_additions.keys(),
        )

    parser.add_argument(
        '-j', '--json',
        help='Output in JSON format.',
        action='store_const',
        const=partial(json.dumps, indent=2),
        dest='format',
        )
    parser.add_argument(
        '-c', '--count',
        help='Output the element count instead of their content.',
        action='store_const',
        const=len,
        dest='format',
        )

    ns = parser.parse_args()

    root = etree.parse(ns.content_file).getroot()

    frames = select_frames(root, *build_select_args(ns, _field_names))

    data = tuple(frame_data(frame) for frame in frames)
    
    print ns.format(data)


if __name__ == '__main__':
    exit(main())
