from edge.tools import rgetattr


def collapse_nested_values(value):
    if isinstance(value, basestring):
        return value
    if isinstance(value, int):
        return str(value)
    else:
        return rgetattr(value, ['value'])

