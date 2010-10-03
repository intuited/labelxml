"""Uses the lxml package to scrape data from the .odt labels file."""
import argparse
from lxml import etree
from functools import partial

FRAME_XPATH = 'draw:frame'
PAGE_XPATH = '@text:anchor-page-number'

def draw_frames(root):
    return root.xpath('.//' + FRAME_XPATH, namespaces=root.nsmap)


STYLE_NAMES = {'name': 'P10',
               'alternate_name': 'P6',
               'price': 'P9',
               }


def style_name_xpath(style_name):
    return 'text:p[@text:style-name="{0}"]'.format(style_name)

FIELD_NAMES = ('name', 'alternate_name', 'price')
FIELD_XPATHS = dict((name, style_name_xpath(STYLE_NAMES[name]))
                    for name in FIELD_NAMES)

ALL_XPATHS = dict(FIELD_XPATHS, frame=FRAME_XPATH, page=PAGE_XPATH)


XPATH_TEXT_FMTSTRS = {'yes': '{0}[text()]',
                      'no': '{0}[not(text())]',
                      'either': '{0}'}

XPATH_TEXT_FORMATS = dict((key, fmtstr.format)
                          for key, fmtstr in XPATH_TEXT_FMTSTRS.iteritems())


def _yes_no_text(require_text, xpath,
                 formats=XPATH_TEXT_FORMATS):
    """Modify an xpath to filter or not for the presence of text."""
    return formats[require_text](xpath)

def requires_text(with_text_map, field, default):
    """Returns the yes/no/either string for ``field``, or ``default``."""
    return with_text_map.get(field, default)

def xpath_wrap_text(with_text_map, default, xpath_id, xpath,
                    formats=XPATH_TEXT_FORMATS):
    """Wrap an xpath to restrict it based on the presence/absence of inner text.

    ``with_text_map`` maps xpath-identifiers to yes/no/either strings.
    ``default`` is a yes/no/either used for xpathid's not in the map.
    ``xpath_id`` is the id of this xpath.
    ``formats`` is a dictionary of formatting functions,
                keyed with yes/no/either strings.
    """
    return _yes_no_text(requires_text(with_text_map, xpath_id, default),
                        xpath, formats=formats)


def descendant_fields(field, with_text, root):
    text_filter = partial(_yes_no_text, with_text)
    xpath = './/' + text_filter(FIELD_XPATHS[field])
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


def negate_field_condition(negations, condition, field):
    """Negates the field's predicate if it is given in ``negations``."""
    if field in negations:
        return 'not({0})'.format(condition)
    return condition


def field_predicate_xpath(with_text={'name': 'yes', 'price': 'yes'},
                          field_names=('name', 'price'),
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
                            FIELD_XPATHS[field_name])


    negate = partial(negate_field_condition, negations)

    conditions = (condition(field_name)
                  for field_name in field_names)

    descendant_conditions = ('.//' + condition for condition in conditions)

    negated_conditions = (negate(condition, field_name)
                          for condition, field_name
                              in zip(descendant_conditions, field_names))

    predicate = ' and '.join(negated_conditions)

    return predicate


def build_select_args(ns, field_names):
    """Builds parameters for ``build_frame_xpath``."""
    field_name_actions = ((field_name, getattr(ns, field_name))
                          for field_name in field_names)

    negations = []
    selected_fields = []
    # TODO: refactor to use ``xpath_wrap_text``.
    for field_name in field_names:
        action = getattr(ns, field_name)
        if action != 'either':
            selected_fields.append(field_name)
        if action == 'no':
            negations.append(field_name)

    with_text = dict((field_name, getattr(ns, field_name + '_text'))
                     for field_name in field_names)

    return with_text, selected_fields, negations

def build_frame_xpath(with_text='yes',
                      field_names=('name', 'price'),
                      negations=()):
    """Returns an xpath for draw:frame elements which match the criteria.

    The parameters are described in the docstring for
    ``field_predicate_xpath``.
    """
    # TODO: refactor to use a template
    predicate = field_predicate_xpath(with_text, field_names, negations)

    xpath = './/{0}[{1}]'.format(FRAME_XPATH, predicate)

    return xpath


def select_frames(root, *args, **kwargs):
    """Selects frames with a ``build_select_args``-constructed xpath."""
    return root.xpath(build_frame_xpath(*args, **kwargs),
                      namespaces=root.nsmap)


def _first_text_or_none(seq):
    return seq[0].text if len(seq) else None

def _first_or_none(seq):
    return seq[0] if seq else None


def frame_data(frame):
    return {'page': _first_or_none(frame.xpath(PAGE_XPATH,
                                   namespaces=frame.nsmap)),
            'name': _first_text_or_none(product_names(frame)),
            'price': _first_text_or_none(product_prices(frame))}


def template_xpath(template,
                   with_text_map=dict((k, 'yes') for k in STYLE_NAMES.keys()),
                   with_text_default='either',
                   axis_map=dict((k, './/') for k in STYLE_NAMES.keys()),
                   axis_default='',
                   negations=()
                   ):
    """Generate an xpath from the template.

    A ``template`` is actually a new-style format string.
    Its replacement fields are replaced with xpaths
    with values corresponding to the field names.

    ``with_text_map`` and ``with_text_default`` are used to reformat
    the xpaths to filter for/against text content.
    
    ``axis`` can be set to something like ".//" to select descendants
    for each {element}.

    For each xpath-id in ``negations``, the substituted xpath will be negated.
    """
    wrap_text = partial(xpath_wrap_text, with_text_map, with_text_default)
    negate = partial(negate_field_condition, negations)
    id_axis = lambda xpath_id: axis_map.get(xpath_id, axis_default)
    def process_xpath(field, xpath):
        xpath = wrap_text(field, xpath)
        xpath = id_axis(field) + xpath
        return negate(xpath, field)

    xpaths = dict((field, process_xpath(field, xpath))
                  for field, xpath in ALL_XPATHS.iteritems())
    return template.format(**xpaths)



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

    def add_field_args(parser, field_names):
        def optfmt(field):
            """Format an option name for the ``field``."""
            field = field.replace('_', '-')
            return '--{0}'.format(field)

        def field_args(field):
            """Generate args and kwargs for a parser --``field`` argument."""
            helpfmt = 'Control filtering on the presence of the {0} field.'.format
            return ((optfmt(field),),
                {'help': helpfmt(field),
                 'default': 'yes',
                 'choices': ('yes', 'no', 'either'),
                })

        def field_text_args(field):
            """Generate args and kwargs for a parser --``field``-text argument."""
            helpfmt = ('Determines whether the presence/absence of text'
                    ' within the {0} field is required.').format
            return ((optfmt(field) + '-text',),
                {'help': helpfmt(field),
                 'default': 'yes',
                 'choices': XPATH_TEXT_ADDITIONS.keys(),
                })

        for field in field_names:
            args, kwargs = field_args(field)
            parser.add_argument(*args, **kwargs)
            args, kwargs = field_text_args(field)
            parser.add_argument(*args, **kwargs)

    add_field_args(parser, FIELD_NAMES)

    parser.add_argument(
        '-t', '--template',
        help='Build the xpath query from a template'
             ' instead of using --name, --name-text, etc.  '
             'The xpath will be used as a predicate to select from the frames.',
        default=None,
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
    parser.add_argument(
        '-x', '--xpath',
        help='Output the generated xpath.  Only works for templates, for now.',
        action='store_true',
        )

    ns = parser.parse_args()

    root = etree.parse(ns.content_file).getroot()

    if ns.template:
        xpath = template_xpath(ns.template)
    else:
        xpath = build_frame_xpath(*build_select_args(ns, FIELD_NAMES))

    if ns.xpath:
        print xpath
    else:
        frames = root.xpath(xpath, namespaces=root.nsmap)

        frames = root.xpath(xpath, namespaces=root.nsmap)
        data = tuple(frame_data(frame) for frame in frames)
        
        print ns.format(data)


if __name__ == '__main__':
    exit(main())
