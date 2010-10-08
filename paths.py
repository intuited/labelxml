import styles
from memoize import memoized

class XP(object):
    """Immutable object which caches the evaluation of an XPath on a tree.
    
    The memoization of the ``results`` method will be used
    for any future calls passing the same ``tree`` object.
    """
    def __init__(self, name, xpath):
        self.name = name
        self.xpath = xpath
    def __hash__(self):
        return hash(self.xpath)
    def __eq__(self, other):
        return type(self) is type(other) and self.xpath is other.xpath

    @memoized
    def results(self, tree):
        return tree.xpath(self.xpath, namespaces=tree.getroot().nsmap)

paths = (
    XP('all frames', '//draw:frame'),
    XP('frames with names and prices',
       ('//draw:frame[(descendant::{name_1} or descendant::{name_2})'
                    ' and descendant::{price}]'
        .format(**styles.nodetests))),
    XP('frames with names and prices with text',
       ('//draw:frame[(descendant::{name_1}[descendant-or-self::text()]'
                      ' or descendant::{name_2}[descendant-or-self::text()])'
                    ' and descendant::{price}[descendant-or-self::text()]]'
        .format(**styles.nodetests))),
    XP('frames with names and prices with text content',
       ('//draw:frame[(descendant::{name_1}[descendant-or-self::string()]'
                      ' or descendant::{name_2}[descendant-or-self::string()])'
                    ' and descendant::{price}[descendant-or-self::string()]]'
        .format(**styles.nodetests))),
    )

all_frames = paths[0]
