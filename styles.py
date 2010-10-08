"""Encapsulates metadata about the label XML schema."""
names = {'name_1': 'P10',
         'name_2': 'P6',
         'price': 'P9',
         }

def expr(style):
    return '@text:style-name="{0}"'.format(names[style])

def nodetest(style):
    return 'text:p[{expr}]'.format(expr=expr(style))

nodetests = dict((style, nodetest(style))
                    for style in names.keys())
