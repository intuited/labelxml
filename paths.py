import styles
from memoize import memoized

class XP(object):
    """Immutable object which caches the evaluation of an XPath on a tree.
    
    The memoization of the ``results`` method will be used
    for any future calls passing the same ``tree`` object
    for an XP object using the same xpath.
    """
    def __init__(self, name, xpath, desc=''):
        self.name = name
        self.xpath = xpath
        self.desc = desc
    def __hash__(self):
        """An XP object's identity is determined by its path.
        
        This allows meaningful memoization, with ``name`` and ``desc``
        being orthogonal to the cacheing of ``results``.
        """
        return hash(self.xpath)
    def __eq__(self, other):
        return type(self) is type(other) and self.xpath is other.xpath

    @memoized
    def results(self, tree):
        return tree.xpath(self.xpath, namespaces=tree.getroot().nsmap)

framesets = (
    XP('all_frames', '//draw:frame', 'all frames'),
    XP('names_prices',
       ('//draw:frame[(descendant::{name_1} or descendant::{name_2})'
                    ' and descendant::{price}]'
        .format(**styles.nodetests)),
       desc='Frames with name- and price-styled paragraphs.'),
    XP('names_prices_text',
       ('//draw:frame[(descendant::{name_1}[descendant-or-self::text()]'
                      ' or descendant::{name_2}[descendant-or-self::text()])'
                    ' and descendant::{price}[descendant-or-self::text()]]'
        .format(**styles.nodetests)),
       desc='Frames with name- and price-styled paragraphs'
            ' which have top-level text.'),
    XP('names_prices_tcontent',
       ('//draw:frame[(descendant::{name_1}[descendant-or-self::*[string()]]'
                      ' or descendant::{name_2}[descendant-or-self::*[string()]])'
                    ' and descendant::{price}[descendant-or-self::*[string()]]]'
        .format(**styles.nodetests)),
       desc='Frames with name- and price-styled paragraphs which contain text.'),
    XP('prices_tcontent',
       ('//draw:frame[descendant::{price}[descendant-or-self::*[string()]]]'
        .format(**styles.nodetests)),
       desc='Frames with price-styled paragraphs which contain text.'),
    XP('prices_nonzero',
       ('//draw:frame[descendant::{price}[descendant-or-self::*[string()]'
        '[not(contains(string(), "$0.00"))'
        ' and not(contains(string(), "DIV/0"))]]]'
        .format(**styles.nodetests)),
       desc='Frames with price-styled paragraphs'
            ' which contain text other than "$0.00".  '
            'Basically this will give any page'
            ' that contains a non-zero price.'),
    XP('dollars_nonzero',
       ('//draw:frame[descendant-or-self::*[contains(text(), "$")]'
        '[not(contains(text(), "$0.00"))]]'
        .format(**styles.nodetests)),
       desc="Frames containing nodes whose text contains a $ but not '$0.00'."
            "This will include even those pages"
            " which don't contain a price-styled paragraph node.  "
            "The effective difference between this and 'prices_nonzero'"
            " is that this will include one of the info pages."),
    )

all_frames = framesets[0]

frameset_dict = dict((path.name, path) for path in framesets)
