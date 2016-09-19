from edge.tools import rgetattr


def collapse_nested_values(value):
    if isinstance(value, basestring):
        value = rgetattr(value, ['value'])

    return value
