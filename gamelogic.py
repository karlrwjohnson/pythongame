import abc
import itertools
import numpy

class Tile (object):
    def __init__(self, name, sprite):
        self.name = name
        self.sprite = sprite

class Map (object):
    def __init__(self, dimensions, tileFunc):
        self.dimensions = dimensions
        self.board = [[tileFunc(x, y) for x in range(dimensions[0])] for y in range(dimensions[1])]
        self.mobs = set()

class GameTime (object):
    def __init__(self, multiplier=1.0):
        self._multiplier = multiplier
        self.isPaused = False

    @property
    def multiplier(self):
        if self.isPaused:
            return 0
        else:
            return self._multiplier

    @multiplier.setter
    def multiplier(self, multiplier):
        self._multiplier = multiplier

    def toggle(self):
        self.isPaused ^= True

class GameEventScheduler (object):
    def __init__(self):
        self.events = set()

    def addEvent(self, event):
        self.events.add(event)

    def advanceBy(self, interval):
        for event in list(self.events):
            event.advance(lambda: self.events.remove(event), interval)

class GameEvent (object):
    def __init__(self, duration):
        self.duration = duration
        self.elapsed = 0.0
        self.onEndCallbacks = set()

    @property
    def remaining(self):
        return self.duration - self.elapsed

    def advance(self, remove, interval):
        self.elapsed += interval
        self.check(remove)
        if self.elapsed > self.duration:
            remove()
            for callback in self.onEndCallbacks:
                callback()
            self.onEndCallbacks.clear()

    def start(self, remove):
        pass

    @abc.abstractmethod
    def check(self, remove):
        return

class MobMovementEvent (GameEvent):
    def __init__(self, duration, mob, direction):
        super(MobMovementEvent, self).__init__(
            duration = duration
        )
        self.mob = mob
        self.direction = numpy.array(direction)

        self.mobStart = mob.position
        self.mobEnd = mob.position + direction

    def check(self, remove):
        progress = min(self.elapsed / self.duration, 1.0)
        self.mob.position = self.mobStart + self.direction * progress

class Mob (object):
    def __init__(self, position, sprite, speed=5.0):
        self.position = numpy.array(position)
        self.sprite = sprite
        self.speed = speed

class MobNavigator (object):
    def __init__(self, mob, gameEventScheduler):
        self.mob = mob
        self.gameEventScheduler = gameEventScheduler
        self.event = None

    def walk(self, direction, onEndCallback=lambda: None):
        if self.event is None:
            def onEnd():
                self.event = None
                onEndCallback()
            distance = (numpy.min(numpy.abs(direction)) * 1.5 + numpy.abs(numpy.subtract(*numpy.abs(direction))))
            self.event = MobMovementEvent(duration=distance / self.mob.speed,
                                          direction=direction,
                                          mob=self.mob)
            self.event.onEndCallbacks.add(onEnd)
            self.gameEventScheduler.addEvent(self.event)
        else:
            print RuntimeError("Already have an event")

    def walkTo(self, location, onEndCallback=lambda: None):
        def nextStep():
            if not (location == self.mob.position).all():
                direction = numpy.sign(location - self.mob.position)
                self.walk(direction, onEndCallback=nextStep)
            else:
                onEndCallback()
        nextStep()

    def patrol(self, locations):
        iterator = itertools.cycle(locations)

        def nextLeg():
            self.walkTo(iterator.next(), nextLeg)
        nextLeg()
