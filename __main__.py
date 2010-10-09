"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""

def print_stats(tree):
    from pprint import pprint
    import report
    results = report.all_path_stats(tree)
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
    # TODO: make this take effect
    import paths
    parser.add_argument(
        '-b', '--base',
        help="Identifier of the base path for comparison.",
        default='all_frames',
        choices=(path.name for path in paths.paths),
        )

    options = parser.parse_args()

    tree = etree.parse(options.file)

    print_stats(tree)

if __name__ == '__main__':
    main()
