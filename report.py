import paths
import stats
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
                         path_names=paths.path_dict.keys()):
    """Builds an iterator of reports for all paths or just those passed in.

    Each path is compared to ``paths.path_dict[base]``.

    ``paths`` is an iterable of keys from ``paths.path_dict``.

    Yields a stats report on the base frame set,
    followed by stats reports
    on each of the frame sets given in ``path_names``.
    """
    from functools import partial
    from itertools import chain

    base = paths.path_dict[base_name]
    paths_ = (paths.path_dict[key] for key in path_names
                                   if key is not base_name)

    get_data = partial(get_report_data, tree, base=base)
    make_report = lambda report, path: report(path, get_data(path))

    return (('base frame set', make_report(base_report, base)),
            ('compared frame sets', tuple(make_report(report, path) for path in paths_)))
