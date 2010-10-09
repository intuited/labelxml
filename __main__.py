"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""
import paths

# Various data dumpers

def print_stats(tree, options):
    from pprint import pprint
    import report
    kwargs = {}
    if hasattr(options, 'path_names'):
        kwargs.update(path_names=options.path_names)
    if hasattr(options, 'base'):
        kwargs.update(base_name=options.base)
    results = report.all_path_stats(tree, **kwargs)
    for result in results:
        pprint(result)

def print_diff(tree, options):
    import stats, report
    from pprint import pprint
    base_path = paths.frameset_dict[options.base]
    for path_name in options.path_names:
        path = paths.frameset_dict[path_name]
        missing_text_content = stats.PathStats(tree, base_path, path)
        pprint([report.diff_report(tree, frame)
                for frame in missing_text_content.missing_text_content_frames])

def print_xpaths(tree, options):
    import paths
    from pprint import pprint
    data = ((('name', path.name), ('xpath', path.xpath), ('description', path.desc))
            for path in paths.framesets)
    for xpath in data:
        pprint(xpath)

def print_dump(tree, options):
    import report, paths, dump
    xp = paths.frameset_dict[options.path_name]
    pages = report.frameset_content(tree, xp.results(tree))
    dump = dump.dumpers[options.output_format]
    print dump(pages, options)

# Argument parser components

def add_comparison_args(parser, path_names):
    """Add common arguments for comparison actions to their parsers."""
    parser.add_argument(
        '-b', '--base',
        help="Name of the base path for comparison.  Options: [%(choices)s]; defaults to '%(default)s'.",
        default='prices_nonzero',
        choices=path_names,
        metavar='PATH_NAME',
        )
    parser.add_argument(
        '-n', '--path-names',
        help="Names of the xpath or xpaths to be used.  Defaults to %(default)s.",
        nargs='+',
        default=('names_prices_tcontent',),
        choices=path_names,
        metavar='PATH_NAME',
        )


# Commands

def add_stats_command(subparsers, path_names):
    parser = subparsers.add_parser(
        'stats',
        help='Get statistics comparing the frames selected by the chosen path(s) with those selected by the base path.',
        )
    add_comparison_args(parser, path_names)
    parser.set_defaults(action=print_stats)

def add_diff_command(subparsers, path_names):
    parser = subparsers.add_parser(
        'diff',
        help=('Show frames found in the base frameset'
              ' but not in the comparison frameset(s).  '
              'This option outputs (xpath, page-number, text-content) tuples'
              ' for each differing frame.'),
        )
    add_comparison_args(parser, path_names)
    parser.set_defaults(action=print_diff)

def add_xpaths_command(subparsers):
    parser = subparsers.add_parser(
        'xpaths',
        help=('Display the available xpaths and their descriptions.  '
              'This is just in the form of a raw data dump.  '
              'For practical purposes the default xpath should work fine.'),
        )
    parser.set_defaults(action=print_xpaths)

def add_dump_command(subparsers, path_names):
    import dump
    parser = subparsers.add_parser(
        'dump',
        help=('Dump the dataset for the named xpath.'),
        )
    parser.add_argument(
        '-n', '--path-name',
        help=('The name of the xpath whose data will be dumped.  '
              "Defaults to '%(default)s';"
              ' use the `xpaths` command for info on the options.'),
        default='prices_nonzero',
        choices=path_names,
        metavar='PATH_NAME',
        )
    parser.add_argument(
        '-o', '--output-format',
        help=('The format of the dumped data.  '
              'Output CSV data will be in Excel tab-delimited format'
              ' with a header row.'
              "Defaults to '%(default)s'."),
        default='json',
        choices=dump.dumpers.keys(),
        )
    parser.set_defaults(action=print_dump)


# Main

def main():
    import argparse
    from lxml import etree

    path_names = [path.name for path in paths.framesets]

    parser = argparse.ArgumentParser(
        description=(
            "Glean and analyze data"
            " from the Grainery's label templates file."
            ),
        epilog=(
            "The `content.xml` file in the labels .odt archive"
            " contains a number of 'frame sets',"
            " all or some of which represent a page containing a label.  "
            "The goal of this utility is to provide a convenient interface"
            " to selecting from a number of xpath queries"
            " in order to determine the correct query"
            " with which to retrieve price data from the `content.xml` file.  "
            "This utility can also be used to retrieve the data."),
        )
    parser.add_argument(
        'file',
        type=argparse.FileType('r'),
        help=('The XML content file. '
              'This can be found in the root directory'
              ' of an unzipped labels .odt file.')
        )

    subparsers = parser.add_subparsers()

    add_stats_command(subparsers, path_names)
    add_diff_command(subparsers, path_names)
    add_xpaths_command(subparsers)
    add_dump_command(subparsers, path_names)

    options = parser.parse_args()

    tree = etree.parse(options.file)

    options.action(tree, options)

if __name__ == '__main__':
    main()
