"""Contains xpaths and other data location metadata."""
import template

FRAME_XPATH = 'draw:frame'
PAGE_XPATH = '@text:anchor-page-number'

STYLE_NAMES = {'name': 'P10',
               'alternate_name': 'P6',
               'price': 'P9',
               }

def style_name_xpath(style_name):
    return 'text:p[@text:style-name="{0}"]'.format(style_name)

FIELD_NAMES = ('name', 'alternate_name', 'price')
FIELD_XPATHS = dict((name, style_name_xpath(STYLE_NAMES[name]))
                    for name in FIELD_NAMES)

ALL_XPATHS = dict(FIELD_XPATHS, frame=FRAME_XPATH, page=PAGE_XPATH)

