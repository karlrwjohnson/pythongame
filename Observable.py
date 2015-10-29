from __future__ import print_function

import types

debug_events = False

class EventType (object):
    """
    Usage::
        class MyClass (Observable):
            @EventType
            def MY_EVENT(param1, param2):
                pass

            def __init__(self, arg1, arg2):
                super(MyClass, self).__init__()

            def something_that_fires_an_event():
                param1, param2 = something()
                self.notify(MyClass.MY_EVENT, param1, param2)

    It is not recommended that the prototype function uses default parameters.
    There's no way to support them on Pythons other than CPython.
    """
    def __init__(self, prototype_function):
        self.prototype_function = prototype_function

    def __str__(self):
        return self.prototype_function.func_name

    def __repr__(self):
        return 'EventType({})'.format(self.prototype_function.func_name)

    @property
    def prototype_argcount(self):
        return self.prototype_function.func_code.co_argcount

    @property
    def prototype_has_args(self):
        return bool(self.prototype_function.func_code.co_flags & 0b100)

    @property
    def prototype_has_kwargs(self):
        return bool(self.prototype_function.func_code.co_flags & 0b1000)

    def matches_signature(self, function):
        # Compare argument lengths for now

        argcount = function.func_code.co_argcount - (1 if isinstance(function, types.MethodType) else 0)
        has_args = bool(function.func_code.co_flags & 0b100)
        has_kwargs = bool(function.func_code.co_flags & 0b1000)

        # Conditions where `function` could not be callable in `prototype_function`'s place:
        # 1. `function` has fewer arguments than `prototype_function` and lacks an *args parameter
        # 2. `function` has more arguments than `prototype_function`, not counting `function`'s default parameters
        # 3. `prototype_function` has an *args parameter but `function` doesn't
        # 4. `prototype_function` has a **kwargs parameter, but `function` doesn't
        #     - In theory, you might be safe if `function` always implements the arguments that are passed through
        #       **kwargs, but that's not type safety. Don't define kwargs on the interface if you can't use them in
        #       the implementation!

        # Without using the inspect module (which only works on CPython, not PyPy or other verions), I cannot determine:
        # a. Any of `prototype_function`'s default parameters, which could be used on `function`
        # b. Whether any of `function`'s parameters have defaults, which would allow it to safely have more parameters than `prototype_function`
        #     - This makes check #2 impossible

        return (has_args or (not self.prototype_has_args and self.prototype_argcount <= argcount)) \
            and (has_kwargs or not self.prototype_has_kwargs)

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

    def __init__(self, supported_event_types=set(), scan_for_event_types=True):
        """
        :param supported_event_types: Optional list of permitted `EventType`s
        :param scan_for_event_types: Search through the class's attributes for
                                     EventType objects
        :return:
        """
        self._observer_handles = {}

        self._supported_event_types = supported_event_types \
            if type(supported_event_types) == set \
            else set(supported_event_types)

        if scan_for_event_types:
            self._supported_event_types |= _find_event_types(type(self)) 

    @staticmethod
    def _find_event_types(clazz):
        return {
            attr_value
            for attr_name in dir(clazz)
            for attr_value in [getattr(clazz, attr_name)]
            if isinstance(attr_value, EventType)
        }

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
        if event_type not in self._supported_event_types:
            raise KeyError('Event type {} is not supported by this Observable'.format(repr(event_type)))
        elif 'matches_signature' in dir(event_type) and not event_type.matches_signature(callback):
            raise TypeError('Callback {} ({} args) cannot be called by event type {} ({} args)'.format(
                repr(callback), callback.func_code.co_argcount,
                repr(event_type), event_type.prototype_argcount,
            ))
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
