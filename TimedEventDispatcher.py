import heapq

class TimedEventDispatcher (object):
    class TimedEvent:
        """Utility class storing event callbacks for TimedEventDispatcher"""

        def __init__(self, delay, on_complete):
            self._delay = delay
            self._on_complete = on_complete
            self._remaining = delay

        def __cmp__(self, other):
            """Compares TimedEvents by their time remaining"""
            # noinspection PyProtectedMember
            return cmp(self._remaining, other._remaining)

        def cancel(self):
            """Prevent the event from executing"""
            # We simply overwrite the callback with a no-op because mutating
            # the TimedEventDispatcher's event queue is hard, and events are
            # cleared out eventually.
            self._on_complete = lambda *args: None

        def __repr__(self):
            return "TimedEventDispatcher.TimedEvent(delay={}, _remaining={}, on_complete={})".format(
                self._delay,
                self._remaining,
                self._on_complete
            )

    def __init__(self):
        # The event queue is a minimum heap, giving O(1) access to the next
        # event, O(log(n)) removal of the next event, and O(log(n)) insertion
        # of new events
        self._event_queue = []

    def add(self, delay, callback):
        """
        :param delay: Amount of game time to wait before running the event
        :param callback: A callback to run when the timer is finished
        :return: A TimedEvent object which may be used to cancel the callback
                 from running, e.g. if the conditions for the event are no
                 longer valid.
        """
        assert delay > 0, 'Delay must be a positive number. Got {}'.format(repr(delay))
        handle = TimedEventDispatcher.TimedEvent(delay, callback)
        print "adding {}".format(repr(handle))
        heapq.heappush(self._event_queue, handle)
        print "event queue now has {} items".format(len(self._event_queue))
        return handle

    # noinspection PyProtectedMember
    def advanceBy(self, dt):
        """Advance game time by an interval of time, firing events as they become due
          and aging the rest.

        :param dt: Amount of time to advance by
        :return: None
        """

        # Pop and fire events in the order they come due
        while len(self._event_queue) > 0 and \
                self._event_queue[0]._remaining <= dt:
            next_event = heapq.heappop(self._event_queue)
            print "processing {}".format(repr(next_event))

            # Advance the game clock by the amount of time left on the next event
            dt -= next_event._remaining
            for event in self._event_queue:
                print "aging by {}: {}".format(dt, repr(event))
                event._remaining -= dt

            next_event._remaining = 0
            next_event._on_complete()

            print "event queue now has {} items".format(len(self._event_queue))
