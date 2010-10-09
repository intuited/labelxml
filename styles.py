"""Encapsulates metadata about the label XML schema."""
names = {'name_1': 'P10',
         'name_2': 'P6',
         'origin': 'P5',
         'price': 'P9',
         'member_price': 'P15',
         }

def expr(style):
    return '@text:style-name="{0}"'.format(names[style])

def nodetest(style):
    return 'text:p[{expr}]'.format(expr=expr(style))

nodetests = dict((style, nodetest(style))
                 for style in names.keys())

class PageRelpaths(object):
    """xpaths relative to a page frame node for that page's data."""
    page_number = '@text:anchor-page-number'
    name = ('string(descendant::{name_1} | descendant::{name_2})'
            .format(**nodetests))
    price = 'string(descendant::{price})'.format(**nodetests)
    member_price = 'string(descendant::{member_price})'.format(**nodetests)
    full_text = 'string()'
