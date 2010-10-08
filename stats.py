from memoize import memoized
import paths

class PathStats(object):
    def __init__(self, tree, base_xp, xp):
        """Initialize the stats given comparison and base paths.XP objects."""
        self.tree = tree
        self.base_xp = base_xp
        self.xp = xp
    def __hash__(self):
        return hash((self.xp, self.base_xp, self.tree))
    def __eq__(self, other):
        return (type(self) is type(other)
                and self.xp is other.xp and self.base_xp is other.base_xp
                and self.tree is other.tree)

    @property
    def count(self):
        """The number of elements found by this xpath."""
        return len(self.xp.results(self.tree))

    @property
    @memoized
    def missing_frames(self):
        """The frames which are present in the base and not the main xp."""
        return (set(self.xp.results(self.tree))
                - set(self.base_xp.results(self.tree)))
    @property
    def missing_frame_count(self):
        """The number of frames present in the base and not the main xp."""
        return len(self.missing_frames)

    @property
    @memoized
    def missing_text_content_frames(self):
        """The missing frames which contain textual content."""
        return [frame for frame in self.missing_frames
                      if frame.text_content()]
    @property
    def missing_text_content_frame_count(self):
        """
        The number of text-containing frames
        present in the base and not the main xp.
        """
        return len(self.missing_text_content_frames)

    def report_data(self, elements=('count',
                                    'missing_frame_count',
                                    'missing_text_content_frame_count')):
        """Returns (name, docs, value) for each of the ``elements``."""
        return tuple(tuple((e,
                            getattr(type(self), e).__doc__,
                            getattr(self, e)))
                     for e in elements)

def all_path_stats(tree):
    from functools import partial
    stats = partial(PathStats, tree, paths.all_frames)
    def report(path):
        return (('name', path.name),
                ('xpath', path.xpath),
                ('stats', stats(path).report_data()))
    return (report(path) for path in paths.paths)
