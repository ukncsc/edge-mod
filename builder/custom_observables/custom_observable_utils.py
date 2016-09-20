from edge.tools import rgetattr


def collapse_nested_values(inputValue):
    value = inputValue
    print("input value: " + inputValue)
    if isinstance(value, basestring):
        value = rgetattr(value, ['value'])
    print("value: " + value)
    return value
