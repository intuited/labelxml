import paths
import stats
import styles
def identity(x): return x

def base_report_data(report_data):
    """Trims report data down to that applicable to base paths."""
    return tuple(item for item in report_data
                      if item[0] == 'count')

def report(xp, report_data, filter_report_data=identity):
    """Builds a report on an XP object given its report data."""
    return (('frame set', xp.name),
            ('desc', xp.desc),
            ('xpath', xp.xpath),
            ('stats', filter_report_data(report_data)))

def base_report(xp, report_data):
    return report(xp, report_data, filter_report_data=base_report_data)


def get_report_data(tree, path, base=paths.all_frames):
    """Returns report data comparing the paths ``path`` and ``base``.

    Uses the etree ``tree``.
    """
    path_stats = stats.PathStats(tree, base, path)
    return path_stats.report_data()

def all_path_stats(tree, base_name='all_frames',
                         path_names=paths.frameset_dict.keys()):
    """Builds an iterator of reports for all paths or just those passed in.

    Each path is compared to ``paths.frameset_dict[base]``.

    ``paths`` is an iterable of keys from ``paths.frameset_dict``.

    Yields a stats report on the base frame set,
    followed by stats reports
    on each of the frame sets given in ``path_names``.
    """
    from functools import partial
    from itertools import chain

    base = paths.frameset_dict[base_name]
    paths_ = (paths.frameset_dict[key] for key in path_names
                                   if key is not base_name)

    get_data = partial(get_report_data, tree, base=base)
    make_report = lambda report, path: report(path, get_data(path))

    return (('base frame set', make_report(base_report, base)),
            ('compared frame sets', tuple(make_report(report, path) for path in paths_)))

def diff_report(tree, frame):
    """Returns diff report data for the frame."""
    return (tree.getpath(frame),
            frame.xpath(styles.PageRelpaths.page_number, namespaces=frame.nsmap),
            frame.xpath('string()', namespaces=frame.nsmap))


def frame_content(tree, frame):
    """Returns discernable data for the frame."""
    data = (('name', 'Item Name'),
            ('page_number', 'Page Number in .odt Source'),
            ('price', 'Item Price'),
            ('member_price', 'Member Price'),
            ('full_text', 'Full Text of .odt Page'))
    xpaths = ((label, getattr(styles.PageRelpaths, datum))
              for datum, label in data)
    return ((label, frame.xpath(path, namespaces=frame.nsmap))
            for label, path in xpaths)

def frameset_content(tree, frameset, frame_content=frame_content):
    return (tuple(frame_content(tree, frame)) for frame in frameset)
