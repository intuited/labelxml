"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""
import paths

def print_stats(tree, path_names=None, base_name=None):
    from pprint import pprint
    import report
    kwargs = dict((n, v) for n, v in (('base_name', base_name),
                                      ('path_names', path_names))
                         if v is not None)
    results = report.all_path_stats(tree, **kwargs)
    for result in results:
        pprint(result)

# TODO: fix this and use it
def missing(tree):
    missing_text_content = stats.PathStats(tree, paths.all_frames, paths.paths[3])
    pprint([(frame, frame.xpath('string()'))
            for frame in missing_text_content.missing_text_content_frames])

# TODO: finish this and use it
def add_stats_command(subparser):
    parser = subparser.add_parser(
        'stats',
        help='Get statistics comparing the chosen path(s) with the base path.',
        )


def main():
    import argparse
    from lxml import etree

    path_names = [path.name for path in paths.paths]

    parser = argparse.ArgumentParser(
        description=("Glean and analyze data"
                     "from the Grainery's label templates file."),
        )
    parser.add_argument(
        'file',
        type=argparse.FileType('r'),
        help=('The XML content file. '
              'This can be found in the root directory'
              ' of an unzipped labels .odt file.')
        )
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

    options = parser.parse_args()

    tree = etree.parse(options.file)

    print_stats(tree, path_names=options.path_names, base_name=options.base)

if __name__ == '__main__':
    main()
