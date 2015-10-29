# -*- coding: utf-8 -*-

import itertools

from Observable import Observable, \
    EventType
from Tile import Tile
from util import *

class ActionState(object):
    def __init__(self, name, permitted_transitions=set()):
        self.name = name
        self.permitted_transitions = permitted_transitions
    def __repr__(self):
        return 'ActionState.{}'.format(self.name)
    @property
    def is_cancelable(self):
        return ActionState.CANCEL in self.permitted_transitions

ActionState.COMPLETE = ActionState('COMPLETE')
ActionState.CANCEL = ActionState('CANCEL')
ActionState.COOL_DOWN = ActionState('COOL_DOWN', { ActionState.COMPLETE })
ActionState.WARM_UP = ActionState('WARM_UP', { ActionState.COOL_DOWN, ActionState.CANCEL })
ActionState.WARM_UP = ActionState('PRECOND_WAIT', { ActionState.WARM_UP, ActionState.CANCEL })
ActionState.NOT_STARTED = ActionState('NOT_STARTED', { ActionState.PRECOND_WAIT, ActionState.WARM_UP, ActionState.CANCEL })

class Action (Observable):
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

    def __init__(self):
        super(self, Action).__init__({
            ActionState.NOT_STARTED,
            ActionState.WARM_UP,
            ActionState.COOL_DOWN,
            ActionState.CANCEL,
            ActionState.COMPLETE
        })
        self._state = ActionState.NOT_STARTED

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        if state in self.state.permitted_transitions:
            self._state = state
            self.notify(state, self)
        else:
            raise TypeError('Cannot transition from state {!r} to state {!r}'.format(self.state, state))

class WalkToAdjacentTileAction (Observable):

    def __init__(self,
                 mob,
                 dest_tile,
                 timed_event_dispatcher):
        """
        :param mob:                  The mob who is moving
        :param dest_tile:     The Tile the mob is moving to
        :param timed_event_dispatcher: To register the callbacks
        :return:
        """
        super(WalkToAdjacentTileAction, self).__init__()

        self.mob = mob
        self.dest_tile = dest_tile
        self.source_tile = mob.tile
        self.timed_event_dispatcher = timed_event_dispatcher

        self.warmup_time = \
        self.cooldown_time = \
            distance(self.source_tile.coords, self.dest_tile.coords) / (2.0 * self.mob.speed)

        # Event references
        self._timer_event = None
        self._tile_event = None

        self.observe(ActionState.WARM_UP, self._on_warm_up)
        self.observe(ActionState.COOL_DOWN, self._on_cool_down)
        self.observe(ActionState.CANCEL, self._on_cancel)
        self.observe(ActionState.COMPLETE, self._on_complet)

        if self.dest_tile.occupant is None:
            self._on_tile_vacate()
        else:
            self.tile_event = self.dest_tile.observe(Tile.VACATE, self._on_tile_vacate, limit=1)
            self.state = ActionState.PRECOND_WAIT

    def cancel(self):
        """Abort the current walk action"""
        if self.state == ActionState.CANCEL:
            # Cancellation is idempotent
            pass
        elif self.state.is_cancelable:
            self._cancel()
        else:
            raise RuntimeError('Too late to cancel the action')

    _progress_by_state = {
        ActionState.NOT_STARTED: lambda self: 0.0,
        ActionState.PRECOND_WAIT: lambda self: 0.0,
        ActionState.CANCEL: lambda self: 0.0,
        ActionState.WARM_UP: lambda self: self.timer_event.progress / 2.0,
        ActionState.COOL_DOWN: lambda self: self.timer_event.progress / 2.0 + 0.5,
        ActionState.COMPLETE: lambda self: 1.0,
    }

    @property
    def progress(self):
        """How close the action is to completion as a number increasing from 0 to 1.0"""
        return WalkToAdjacentTileAction._progress_by_state[self.state](self)

    @property
    def current_position(self):
        return vec_interpolate(self.source_tile.coords, self.dest_tile.coords, self.progress)

    @property
    def timer_event(self):
        return self._timer_event

    @timer_event.setter
    def timer_event(self, timer_event):
        if self._timer_event is not None:
            self._timer_event.cancel()

        self._timer_event = timer_event

    @property
    def tile_event(self):
        return self._tile_event

    @tile_event.setter
    def tile_event(self, tile_event):
        if self._tile_event is not None:
            self._tile_event.cancel()

        self._tile_event = tile_event

    #def _on_mob_speed_change(self, mob):
        # I need to change the completion time of an in-progress event!
        # I should probably just cancel the current one and re-issue it.

    def _on_tile_vacate(self, *args):
        self.state = ActionState.WARM_UP

    def _on_warm_up(self, *args):
        self.tile_event = self.dest_tile.observe(Tile.OCCUPY, self._on_tile_stolen, limit=1)
        self.timer_event = self.timed_event_dispatcher.add(self.warmup_time, self._on_warmup_done)
        #self._mobSpeedEvent = self.mob.observe(Mob.SPEED_CHANGE, self._on_mob_speed_change)

    def _on_tile_stolen(self, *args):
        """Callback for the destination tile becoming occupied before the mob can reach it"""
        self.state = ActionState.CANCEL

    def _on_cancel(self):
        self.timer_event = None
        self.tile_event = None
        #self.mobSpeedEvent = None

    def _on_warmup_done(self):
        """Callback for the warmup event's completion"""
        assert self.dest_tile.occupant is None, \
            "Target tile is occupied, but I didn't get a Tile.OCCUPY event"

        # No longer watching for the tile to be occupied
        self.tile_event = None

        # Mob jumps to next tile
        self.mob.tile = self.dest_tile

        self.state = ActionState.COOL_DOWN

    def _on_cool_down(self, *args):
        self.timer_event = self.timed_event_dispatcher.add(self.cooldown_time, self._on_cooldown_done)

    def _on_cooldown_done(self, *args):
        self.state = ActionState.COMPLETE

    def _on_complete(self):
        self.timer_event = None
        self.tile_event = None
        #self.mobSpeedEvent = None

        self.state = ActionState.COMPLETE

def find_path(from_tile, to_tile):
    """Braindead pathfinder which picks the most direct route

    :param from_tile: The starting tile
    :param to_tile: The goal tile
    :return: An adjacent or diagonal tile to navigate to first
    """
    assert from_tile.zone is to_tile.zone, \
        'Tiles are in different zones'

    from_coord = from_tile.coords
    to_coord = to_tile.coords

    #direction = sign(vec_subtract(to_coord, from_coord))
    direction = (sign(to_coord[0] - from_coord[0]), 0) \
                if to_coord[0] != from_coord[0] else \
                (0, sign(to_coord[1] - from_coord[1]))

    return from_tile.get_relative_tile(direction)

class WalkToAdjacentTileDirective(object):
    """Trivial iterator navigating a mob one tile in any direction"""
    def __init__(self, mob, direction):
        assert is_adjacent_vector(direction)

        # May be None if @ edge of zone
        self.mob = mob
        self.destination = mob.tile.get_relative_tile(direction)
    def __iter__(self):
        return self
    def next(self):
        if self.mob.tile is self.destination or self.destination is None:
            raise StopIteration()
        else:
            return self.destination

class WalkToDestinationDirective(object):
    """Iterator which navigates a mob to a given point"""
    def __init__(self, mob, tile):
        assert mob.tile.zone is tile.zone, \
            'Can only walk between tiles on the same map'

        self.mob = mob
        self.tile = tile
    def __iter__(self):
        return self
    def next(self):
        if self.mob.tile is self.tile:
            raise StopIteration()
        else:
            return find_path(self.mob.tile, self.tile)

class PatrolDestinationsDirective(object):
    """Iterator which navigates a mob between a cycle of points ad infinitum"""
    def __init__(self, mob, tile_list):
        assert all_true([
                mob.tile.zone is tile.zone
                for tile in tile_list
            ]), \
            'Can only walk between tiles on the same map'
        assert len(removeAdjacentDuplicates(tile_list)) > 0, \
            'More than one unique destination is required'

        self.mob = mob
        self.tile_list = tile_list
        self.destination_iter = itertools.cycle(self.tile_list)
        self.current_destination = self.mob.tile
    def __iter__(self):
        return self
    def next(self):
        if self.mob.tile is self.current_destination:
            self.current_destination = self.destination_iter.next()
        return find_path(self.mob.tile, self.current_destination)
