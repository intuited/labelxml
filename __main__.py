"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""
import labelxml

def add_output_args(parser):
    group = parser.add_argument_group('Mutually-exclusive OUTPUT OPTIONS')
    group.add_argument(
        '-j', '--json',
        help='Output in JSON format.',
        action='store_const',
        const=partial(json.dumps, indent=2),
        dest='format',
        )
    group.add_argument(
        '-c', '--count',
        help='Output the number of elements instead of their content.',
        action='store_const',
        const=len,
        dest='format',
        )
    group.add_argument(
        '-x', '--output-xpath',
        help='Output the generated xpath.',
        action='store_true',
        )
def add_field_args(parser, field_names):
    group = parser.add_argument_group('FIELD OPTIONS')

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
            'choices': ('yes', 'no', 'either'),
            })

    for field in field_names:
        args, kwargs = field_args(field)
        group.add_argument(*args, **kwargs)
        args, kwargs = field_text_args(field)
        group.add_argument(*args, **kwargs)

def main():
    from pprint import PrettyPrinter
    import argparse
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

    add_field_args(parser, FIELD_NAMES)

    parser.add_argument(
        '-t', '--template',
        # TODO: add a list of template replacement fields.
        help='Build the xpath query from a template'
             ' instead of using --name, --name-text, etc.  '
             'The xpath will be used as a predicate to select from the frames.'
             '\n\n'
             'If this option is given, the FIELD OPTIONS will be ignored.',
        default=None,
        # The ``template`` attrib is a function that takes the text axis.
        # Here we curry the template_xpath function
        #   so that it can accept the parse-time argument separately.
        type=lambda fmtstr: partial(template_xpath, fmtstr)
        )
    parser.add_argument(
        '-f', '--frame-template',
        help='Use the template to generate an xpath predicate'
             ' which is applied to the set of all frames.'
             'This is equivalent to passing `{0}` as the --template.'
             .format(frame_predicate_fmtstr),
        default=None,
        dest='template',
        # This one is a bit more complex
        #   because we need to inject the args into the inner function.
        type=(lambda fmtstr:
                     (lambda *args, **kwargs:
                             format_frame_xpath(template_xpath(fmtstr, *args,
                                                               **kwargs))))
        )

    parser.add_argument(
        '-a', '--text-axis',
        help='The xpath axis to use when checking for text content.',
        default='child',
        choices=('child', 'descendant'),
        )

    add_output_args(parser)

    ns = parser.parse_args()

    root = etree.parse(ns.content_file).getroot()

    if ns.template:
        xpath = ns.template(text_axis=ns.text_axis)
    else:
        xpath = build_frame_xpath(*build_select_args(ns, FIELD_NAMES))

    if ns.output_xpath:
        print xpath
    else:
        frames = root.xpath(xpath, namespaces=root.nsmap)

        frames = root.xpath(xpath, namespaces=root.nsmap)
        # TODO: deal with empty result sets
        text_formats = xpath_text_formats(ns.text_axis)
        data = tuple(frame_data(frame, text_formats=text_formats)
                     for frame in frames)
        
        print ns.format(data)


if __name__ == '__main__':
    exit(main())
