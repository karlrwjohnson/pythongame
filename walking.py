import itertools
import numpy

from Observable import Observable, \
    EventType
from Tile import Tile
from util import removeAdjacentDuplicates

class WalkToAdjacentTileAction (Observable):
    """

    An action is a discrete operation taken by a mob, such as walking or firing a weapon.
    Action are characterized by three phases:
    1. A warm-up period of time
    2. An instant during which the action occurs
    3. A cool-down time

    In the case of walking to an adjacent tile, the warm-up represents the character leaving the current tile,
    the cool-down is the mob entering the next tile, and between them is the quantum jump in which the mob releases
    ownership of the old tile and takes ownership of the new.
    """

    @EventType
    def DONE(success):
        """The action has completed
        :param success: Whether the character now occupies the new tile
        """

    def __init__(self,
                 mob,
                 destination_tile,
                 timedEventDispatcher,
                 warmup_time,
                 cooldown_time):
        """
        :param mob:                  The mob who is moving
        :param destination_tile:     The Tile the mob is moving to
        :param timedEventDispatcher: To register the callbacks
        :param warmup_time:          An amount of game time
        :param cooldown_time:        An amount of game time
        :return:
        """
        super(WalkToAdjacentTileAction, self).__init__()

        self.mob = mob
        self.destination_tile = destination_tile
        self.timedEventDispatcher = timedEventDispatcher

        # Event references
        self._timerEvent = None
        self._tileEvent = None

        self.warmup_time = warmup_time
        self.cooldown_time = cooldown_time

    def start(self, *args):
        """Initiate the action as soon as the destination tile becomes vacant."""
        if self.destination_tile.occupant:
            # Wake me up when September ends -- I mean, when the tile is empty
            self._tileEvent = self.destination_tile.observe(Tile.VACATE, self.start, limit=1)
        else:
            self._timerEvent = self.timedEventDispatcher.add(self.warmup_time, self._on_warmup_done)
            self._tileEvent = self.destination_tile.observe(Tile.OCCUPY, self._on_tile_stolen, limit=1)

    def _on_warmup_done(self):
        """Callback for the warmup event's completion"""
        assert self.destination_tile.occupant is None, \
            "Target tile is occupied, but I didn't get a Tile.OCCUPY event"

        # No longer watching for the tile to be occupied
        self._tileEvent.cancel()
        self._tileEvent = None

        # Mob jumps to next tile
        self.mob.position = self.destination_tile.coords

        # Set timer for cooldown
        self._timerEvent = self.timedEventDispatcher.add(self.cooldown_time, self._on_complete)

    def _on_tile_stolen(self, *args):
        """Callback for the destination tile becoming occupied before the mob can reach it"""
        self._on_cancel()

    def _on_cancel(self):
        if self._timerEvent is not None:
            self._timerEvent.cancel()
        if self._tileEvent is not None:
            self._tileEvent.cancel()

        self.notify(WalkToAdjacentTileAction.DONE, False)

    def _on_complete(self):
        self.notify(WalkToAdjacentTileAction.DONE, True)

class WalkDirective (Observable):
    """Base class for WalkToDestinationDirective and PatrolDirective.

    A directive is a higher-level command to a mob. In this case, a WalkDirective
    causes a mob to make a series of `WalkToAdjacentTileAction`s to achieve the
    goal of reaching a destination tile (as in the case of WalkToDestinationDirective)
    or walking a set path (as in the case of PatrolDirective)
    """

    @EventType
    def DONE(success):
        """The directive has completed
        :param success: Whether the mob reached its destination
        """

    def __init__(self, mob, timed_event_dispatcher):
        super(WalkDirective, self).__init__(set([
            WalkDirective.DONE
        ]))

        self.mob = mob
        self.timed_event_dispatcher = timed_event_dispatcher

        # Claim the mob for the duration of the directive
        self.mob.walk_directive = self
        self.observe(WalkDirective.DONE, self._on_done, limit=1)

    def walk(self, direction, on_walk_done):
        assert (direction[0] == 0 and (direction[1] == 1 or direction[1] == -1)) or \
               (direction[1] == 0 and (direction[0] == 1 or direction[0] == -1)), \
            'Mobs can only walk to adjacent tiles'

        distance = 1 if direction[0] == 0 or direction[1] == 0 \
            else 1.5
        warmup_time = distance / (2.0 * self.mob.speed)
        cooldown_time = distance / (2.0 * self.mob.speed)
        destination = self.mob.zone.tiles[self.mob.position + direction]

        action = WalkToAdjacentTileAction(
            mob=self.mob,
            destination_tile=destination,
            timedEventDispatcher=self.timed_event_dispatcher,
            warmup_time=warmup_time,
            cooldown_time=cooldown_time)
        action.observe(WalkToAdjacentTileAction.DONE, on_walk_done, limit=1)
        action.start()

    def _on_done(self, success):
        if self.mob.walk_directive == self:
            self.mob.walk_directive = None

class WalkToDestinationDirective (WalkDirective):
    """Navigates a mob to the destination tile in the straightest line"""

    def __init__(self, mob, timed_event_dispatcher, destination):
        super(WalkToDestinationDirective, self).\
            __init__(mob, timed_event_dispatcher)

        self.destination = destination

    def start(self):
        self._on_walk_action_done()

    def _on_walk_action_done(self, success=None):
        if (self.mob.position == self.destination).all():
            self.notify(WalkDirective.DONE, True)
        else:
            #TODO: enable when diagonal movement is supported
            #direction = numpy.sign(self.destination - self.mob.position)
            direction = (numpy.sign(self.destination[0] - self.mob.position[0]), 0) \
                        if self.destination[0] != self.mob.position[0] else \
                        (0, numpy.sign(self.destination[1] - self.mob.position[1]))
            self.walk(direction, self._on_walk_action_done)

class PatrolDirective (WalkDirective):
    """Navigates a mob between a list of points indefinitely"""

    def __init__(self, mob, timed_event_dispatcher, destination_list):
        super(PatrolDirective, self).\
            __init__(mob, timed_event_dispatcher)

        assert len(removeAdjacentDuplicates(destination_list)) > 0, \
            'More than one unique destination is required'

        self.destination_list = destination_list
        self.destination_iter = itertools.cycle(destination_list)
        self.current_destination = self.destination_iter.next()

    def start(self):
        self._on_walk_action_done()

    def _on_walk_action_done(self, success=None):
        while (self.mob.position == self.current_destination).all():
            self.current_destination = self.destination_iter.next()

        #TODO: enable when diagonal movement is supported
        #direction = numpy.sign(self.destination - self.mob.position)
        direction = (numpy.sign(self.current_destination[0] - self.mob.position[0]), 0) \
                    if self.current_destination[0] != self.mob.position[0] else \
                    (0, numpy.sign(self.current_destination[1] - self.mob.position[1]))
        self.walk(direction, self._on_walk_action_done)
