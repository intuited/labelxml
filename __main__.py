"""CLI for the labelxml module.

Provides a command-line interface to the label data extractor.
"""

def print_stats(tree):
    from pprint import pprint
    import stats, paths
    results = tuple(stats.all_path_stats(tree))
    for result in results:
        pprint(result)
    missing_text_content = stats.PathStats(tree, paths.all_frames, paths.paths[3])
    pprint([(frame, frame.xpath('string()'))
            for frame in missing_text_content.missing_text_content_frames])

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
    options = parser.parse_args()

    tree = etree.parse(options.file)

    print_stats(tree)

if __name__ == '__main__':
    main()
