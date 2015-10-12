import heapq

class TimedEventDispatcher (object):
    class TimedEvent:
        """Utility class storing event callbacks for TimedEventDispatcher"""

        def __init__(self, period, on_complete):
            self._period = period
            self._time_remaining = period
            self.on_complete = on_complete

        def __cmp__(self, other):
            """Compares TimedEvents by their time remaining"""
            return cmp(self.time_remaining, other.time_remaining)

        def __repr__(self):
            return "TimedEventDispatcher.TimedEvent(period={}, _time_remaining={}, on_complete={})".format(
                self._period,
                self._time_remaining,
                self.on_complete
            )

        def cancel(self):
            """Prevent the event from executing"""
            # We simply overwrite the callback with a no-op because mutating
            # the TimedEventDispatcher's event queue is hard, and events are
            # cleared out eventually.
            self.on_complete = lambda *args: None

        def age(self, time):
            assert time <= self._time_remaining, \
                'Tried to age a TimedEvent by {}, but it only had {} remaining'.format(
                    time, self._time_remaining
                )
            self._time_remaining -= time

        @property
        def time_remaining(self):
            return self._time_remaining

        @property
        def period(self):
            return self._period

        @property
        def progress(self):
            return 1.0 - float(self.time_remaining) / self.period

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
        heapq.heappush(self._event_queue, handle)
        return handle

    def advanceBy(self, interval):
        """Advance game time by an interval of time, firing events as they become due
          and aging the rest.

        :param interval: Amount of time to advance by
        :return: None
        """

        # Pop and fire events in the order they come due
        while len(self._event_queue) > 0 and \
                self._event_queue[0].time_remaining <= interval:
            next_event = heapq.heappop(self._event_queue)

            # Advance the game clock by the amount of time left on the next event
            interval -= next_event.time_remaining
            for event in self._event_queue:
                event.age(next_event.time_remaining)

            next_event.age(next_event.time_remaining)
            next_event.on_complete()

        # Age everything left by the remaining time
        for event in self._event_queue:
            event.age(interval)
