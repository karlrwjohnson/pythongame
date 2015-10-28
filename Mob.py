# -*- coding: utf-8 -*-

from Observable import Observable, \
    EventType
from walking import \
    WalkToAdjacentTileAction, \
    WalkToAdjacentTileDirective, \
    WalkToDestinationDirective, \
    PatrolDestinationsDirective

class Mob (Observable):
    """
    A Movable entity that occupies tiles
    """

    @EventType
    def POSITION_CHANGE(mob, old_tile):
        """Mob moved
        :param mob: The mob that moved (i.e. self)
        :param old_tile: The previous tile
        """

    @EventType
    def SPEED_CHANGE(mob):
        """Mob's speed changed"""

    @EventType
    def STOP_MOVING(mob):
        """Mob is not moving"""

    def __init__(self, tile, sprite, speed=5.0):
        super(Mob, self).__init__()

        # Private properties
        self._speed = None
        self._tile = None
        self._walk_action = None
        self._walk_directive = None

        # Static/public properties
        self.sprite = sprite

        # Setters
        self.speed = speed
        self.tile = tile

    @property
    def tile(self):
        return self._tile

    @tile.setter
    def tile(self, tile):
        """Directly set which tile a mob occupies.
        :param tile: obvious
        :raises Tile.OwnershipException: If the new tile is already occupied
        """

        if tile is not None:
            # This might throw a Tile.OwnershipException
            tile.occupant = self

        old_tile = self._tile
        self._tile = tile

        if old_tile is not None:
            old_tile.occupant = None

        self.notify(Mob.POSITION_CHANGE, self, old_tile)

    @property
    def position(self):
        return self.tile.coords \
            if self._walk_action is None \
            else self._walk_action.current_position

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, speed):
        self._speed = speed
        self.notify(Mob.SPEED_CHANGE, self)

    @property
    def walk_directive(self):
        return self._walk_directive

    @walk_directive.setter
    def walk_directive(self, walk_directive):
        """
        :param walk_directive: Should be an iterator
        """
        self._walk_directive = walk_directive

        if self.walk_directive is not None:
            try:
                next_tile = self.walk_directive.next()
            except StopIteration as e:
                # New directive says we're already there
                if self._walk_action.state.is_cancelable:
                    self._walk_action.cancel()
            else:
                if self._walk_action is None:
                    self._on_walk_action_done()
                elif next_tile is self._walk_action.dest_tile:
                    # Let it happen
                    pass
                else:
                    # If possible, abort the current walk, automatically starting the next one
                    if self._walk_action.state.is_cancelable:
                        self._walk_action.cancel()

    # Verbs

    def walk(self, direction):
        """Move to an adjacent or diagonal tile
        :param direction: A (x,y) tuple where x,y ∈ {-1,0,1}
        """
        self.walk_directive = WalkToAdjacentTileDirective(mob=self, direction=direction)

    def walk_to(self, tile):
        """Navigate to an arbitrary tile on the map
        :param tile: Tile to move to
        """
        self.walk_directive = WalkToDestinationDirective(mob=self, tile=tile)
    
    def patrol(self, tile_list):
        """Patrol a circuit of tiles ad infinitum
        :param tile_list: List of tiles to patrol
        """
        self.walk_directive = PatrolDestinationsDirective(mob=self, tile_list=tile_list)

    # Handlers

    def _on_walk_action_done(self, success=None):
        """Callback for when the current walk action has completed"""
        self._walk_action = None

        if self.walk_directive is not None:
            try:
                next_tile = self.walk_directive.next()
            except StopIteration as e:
                # No more tiles to walk to
                self.walk_directive = None
                self.notify(Mob.STOP_MOVING, self)
            else:
                self._walk_action = WalkToAdjacentTileAction(
                    mob=self,
                    dest_tile=next_tile,
                    timed_event_dispatcher=self.tile.zone.timed_event_dispatcher)
                self._walk_action.observe(WalkToAdjacentTileAction.DONE,
                                          self._on_walk_action_done,
                                          limit=1)


