from edge.tools import rgetattr


def collapse_nested_values(value):
    return rgetattr(value, ['value'], value)
