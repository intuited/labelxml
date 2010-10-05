"""Provides a templating system to generate xpaths using string formatters.

The idea is to be able to readily plug in queries such as

    >>> food = Expression(
    >>> expand

"""

def expand(template, 


def template_xpath(template,
                   with_text_map=dict((k, 'yes') for k in STYLE_NAMES.keys()),
                   with_text_default='either',
                   text_axis='descendant',
                   axis_map=dict((k, './/') for k in STYLE_NAMES.keys()),
                   axis_default='',
                   negations=(),
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
    wrap_text = partial(xpath_wrap_text, with_text_map, with_text_default,
                        formats=xpath_text_formats(text_axis))
    negate = partial(negate_field_condition, negations)
    id_axis = lambda xpath_id: axis_map.get(xpath_id, axis_default)
    def process_xpath(field, xpath):
        xpath = wrap_text(field, xpath)
        xpath = id_axis(field) + xpath
        return negate(xpath, field)

    xpaths = dict((field, process_xpath(field, xpath))
                  for field, xpath in ALL_XPATHS.iteritems())
    return template.format(**xpaths)
