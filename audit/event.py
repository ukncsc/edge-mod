
from setup import log_error


class Event(object):
    def __init__(self):
        self._handlers = {}

    def set_handler(self, handler_name, callback):
        if not handler_name:
            raise ValueError('A handler name must be supplied.')

        if not hasattr(callback, '__call__'):
            raise TypeError('The handler callback must be a function.')

        self._handlers[handler_name] = callback

    def unset_handler(self, handler_name):
        self._handlers[handler_name] = None

    def raise_event(self, source, **event_args):
        for handler in self._handlers:
            try:
                self._handlers[handler](source, **event_args)
            except Exception, e:
                log_error(e)
