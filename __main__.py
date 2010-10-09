"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""
import paths

def print_stats(tree, options):
    from pprint import pprint
    import report
    kwargs = dict((attr, getattr(options, attr))
                  for attr in ('base_name', 'path_names')
                  if hasattr(options, attr))
    results = report.all_path_stats(tree, **kwargs)
    for result in results:
        pprint(result)


# TODO: fix this and use it
def missing(tree):
    missing_text_content = stats.PathStats(tree, paths.all_frames, paths.paths[3])
    pprint([(frame, frame.xpath('string()'))
            for frame in missing_text_content.missing_text_content_frames])


def add_comparison_args(parser, path_names):
    parser.add_argument(
        '-b', '--base',
        help="Name of the base path for comparison.  Options: [%(choices)s]; defaults to '%(default)s'.",
        default='all_frames',
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


# TODO: finish this and use it
def add_stats_command(subparsers, path_names):
    parser = subparsers.add_parser(
        'stats',
        help='Get statistics comparing the chosen path(s) with the base path.',
        )
    add_comparison_args(parser, path_names)
    parser.set_defaults(action=print_stats)


def main():
    import argparse
    from lxml import etree

    path_names = [path.name for path in paths.paths]

    parser = argparse.ArgumentParser(
        description=("Glean and analyze data"
                     " from the Grainery's label templates file."),
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

    options = parser.parse_args()

    tree = etree.parse(options.file)

    options.action(tree, options)

if __name__ == '__main__':
    main()
