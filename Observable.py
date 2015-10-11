from __future__ import print_function

debug_events = False

class EventType (object):
    """Wrapper class to make event_type singletons, which wouldn't be confused """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

class Observable (object):
    """Data structure useful for implementing the Observable pattern"""

    class Handle (object):
        """Utility class for Observable objects"""
        def __init__(self, callback, event_type, limit, manager):
            #TODO might need to use weak references
            self._callback = callback
            self._event_type = event_type
            self._limit = limit
            self._manager = manager

        def cancel(self):
            """Removes the callback from its original Observable"""
            self._manager.unobserve(self._event_type, self)

    def __init__(self, supported_event_types=None):
        """
        :param supported_event_types: Optional list of permitted `event_type`s
        :return:
        """
        self._observer_handles = {}
        self._supported_event_types = supported_event_types

    def observe(self, event_type, callback, limit=float('inf')):
        """Registers a callback
        :param callback: Function to call on notify() for corresponding
                         event_type
        :param event_type: Key designating the event's type.
        :param limit: Optional maximum number of times to execute callback.
                      By default, callbacks are immortal.
        :return: A Handle which may be used to cancel()'ed to remove
                 it from the Observable
        """
        if self._supported_event_types and not(event_type in self._supported_event_types):
            raise KeyError('Event type {} is not supported by this Observable'.format(repr(event_type)))
        else:
            if not(event_type in self._observer_handles):
                self._observer_handles[event_type] = []

            handle = Observable.Handle(callback, event_type, limit, self)
            self._observer_handles[event_type].append(handle)
            return handle

    def unobserve(self, event_type, handle):
        """Stop calling the Handle's callback for event_type
        :param handle:
        :param event_type:
        :return:
        """
        self._observer_handles[event_type].remove(handle)

    # noinspection PyProtectedMember
    def notify(self, event_type, *args, **kwargs):
        """ Calls all observers with a corresponding event_type in the order they were registered
        :param event_type: Matches add():event_type
        :param args: Ordered arguments to pass to the callbacks
        :param kwargs: Named arguments to pass to the callbacks
        :return: None
        """

        if debug_events:
            print('[Event] {}: args={} kwargs={}'.format(event_type, repr(args), repr(kwargs)))

        if self._supported_event_types and not(event_type in self._supported_event_types):
            raise KeyError('Event type {} is not supported by this Observable'.format(repr(event_type)))

        elif event_type in self._observer_handles:
            observers = self._observer_handles[event_type]

            # Call each listener and decay it
            for listener in list(observers):
                listener._callback(*args, **kwargs)
                listener._limit -= 1

            # Cull expired callbacks
            observers[:] = [
                listener
                for listener in observers
                if listener._limit != 0
            ]

            # Cull childless event_types
            if len(observers) == 0:
                del self._observer_handles[event_type]
