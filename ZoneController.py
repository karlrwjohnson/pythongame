import pygame

from GameClock import GameClock
from Mob import Mob
from Observable import Observable, \
    EventType
from Tile import Tile
from UIController import UIController

class ZoneController (Observable):

    @EventType
    def CLICK_TILE(tile):
        """A tile was clicked
        :param tile: The tile that was clicked
        """

    @EventType
    def CLICK_ENTITY(tile):
        """An entity was clicked
        :param tile: The tile that was clicked
        """

    @EventType
    def HOVER_TILE(tile):
        """The mouse is hovering over a tile
        :param tile: The tile is being hovered over
        """

    @EventType
    def TIME_ADVANCE(dt):
        """Game time has advanced
        :param dt: Amount of time to advance by
        """

    def __init__(self, ui_controller, zone, view, pc):
        super(ZoneController, self).__init__()

        # Private variables
        self._ui_controller = None
        self._ui_controller_event_handles = []

        # Public variables
        self.zone = zone
        self.view = view
        self.pc = pc

        # Public setters
        self.ui_controller = ui_controller

    @property
    def ui_controller(self):
        return self._ui_controller

    @ui_controller.setter
    def ui_controller(self, ui_controller):
        # Cancel old listeners (if any)
        for handle in self._ui_controller_event_handles:
            handle.cancel()

        self._ui_controller = ui_controller

        # Register listeners with new ui_controller object
        self._ui_controller_event_handles = [] \
            if self._ui_controller is None \
            else [
                self.ui_controller.observe(UIController.PRIMARY_CLICK, self._on_primary_click),
                self.ui_controller.observe(UIController.SECONDARY_CLICK, self._on_secondary_click),
                self.ui_controller.observe(UIController.ZONE_HOVER, self._on_zone_hover),
                self.ui_controller.observe(UIController.MOVE, self._on_move),
                self.ui_controller.game_clock.observe(GameClock.GAME_TIME_ADVANCE, self._on_game_time_advance),
            ]

    def _on_game_time_advance(self, dt):
        self.zone.timed_event_dispatcher.advanceBy(dt)

    def _on_primary_click(self, coord):
        thing = self.view.what_is_at(coord)
        if isinstance(thing, Tile):
            self.notify(event_type=ZoneController.CLICK_TILE, coord=coord)

    def _on_zone_hover(self, coord):
        thing = self.view.what_is_at(coord)
        if isinstance(thing, Tile):
            self.notify(event_type=ZoneController.HOVER_TILE, coord=coord)

    def _on_secondary_click(self, coord, button):
        #TODO this is how we click on characters and entities
        pass

    def _on_move(self, direction):
        self.pc.walk(direction)

    def _on_click_tile(self, coord):
        dest_tile = self.zone.tiles[coord]
        self.pc.walk_to(dest_tile)
