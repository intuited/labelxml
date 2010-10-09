"""Various routines to dump the price data.

These use an 'options' object
as constructed by the main argument parser.
"""
class DataValidationError(Exception):
    pass


def process_page(page):
    """Validates and processes a page in dictionary format."""
    page_numbers = page['Page Number in .odt Source']
    if len(page_numbers) > 1:
        raise DataValidationError("Found more than 1 page number for page {0}."
                                    .format(page))
    if not page_numbers:
        raise DataValidationError("Did not find page number for page {0}"
                                    .format(page))
    page['Page Number in .odt Source'] = int(page_numbers[0])
    return page

def dump_json(pages, options):
    from json import dumps
    dicts = (dict(page) for page in pages)
    processed_pages = [process_page(page) for page in dicts]
    return dumps(processed_pages, indent=True)

def dump_yaml(pages, options):
    from yaml import dump_all
    return dump_all(pages)

def dump_csv(pages, options):
    """Dump in CSV format.

    ``pages`` is an iterable of (field, value) tuples.

    It's assumed that the same fields are used in each tuple.
    """
    from itertools import chain
    from csv import DictWriter
    from sys import stdout
    pages = iter(pages)
    try:
        first_row = pages.next()
    except StopIteration:
        return
    fields = [item[0] for item in first_row]
    rows = chain((first_row,), pages)
    dicts = (dict(page) for page in rows)
    dicts = (process_page(row) for row in dicts)

    def validate_row_length(row_dict):
        if len(row_dict) != len(fields):
            raise DataValidationError(
                'Inconsistent number of fields in row {0}.\n'
                'Fields: {1}'.format(row_dict, fields))
        return row_dict
    dicts = (validate_row_length(row) for row in dicts)

    from deboogie import iterdebug
    ##~~  dicts = iterdebug('csv dicts', dicts)

    writer = DictWriter(stdout, fields)
    writer.writerow(dict((v, v) for v in fields))
    writer.writerows(dicts)

dumpers = {'json': dump_json, 'yaml': dump_yaml, 'csv': dump_csv}
