import paths
import stats

def report(xp, report_data):
    """Builds a report on an XP object given its report data."""
    return (('id', xp.name),
            ('desc', xp.desc),
            ('xpath', xp.xpath),
            ('stats', report_data))

def get_report_data(tree, path, base=paths.all_frames):
    """Returns report data comparing the paths ``path`` and ``base``.

    Uses the etree ``tree``.
    """
    path_stats = stats.PathStats(tree, base, path)
    return path_stats.report_data()

def all_path_stats(tree, base=paths.all_frames):
    """Builds an iterator of reports for all paths.

    Each path is compared to ``base``.
    """
    from functools import partial
    get_data = partial(get_report_data, tree, base=base)
    return (report(path, get_data(path)) for path in paths.paths)
