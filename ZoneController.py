import pygame

from GameClock import GameClock
from Mob import Mob
from Observable import Observable, \
    EventType
from TimedEventDispatcher import TimedEventDispatcher
from UIController import UIController
from walking import \
    PatrolDirective, \
    WalkToDestinationDirective

class ZoneController (Observable):

    @EventType
    def CLICK_TILE(tile):
        """A tile was clicked
        :param tile: The tile that was clicked
        """
        pass

    @EventType
    def CLICK_ENTITY(tile):
        """An entity was clicked
        :param tile: The tile that was clicked
        """
        pass

    @EventType
    def HOVER_TILE(tile):
        """The mouse is hovering over a tile
        :param tile: The tile is being hovered over
        """
        pass

    @EventType
    def TIME_ADVANCE(dt):
        """Game time has advanced
        :param dt: Amount of time to advance by
        """
        pass

    def __init__(self, ui_controller, model, view):
        super(ZoneController, self).__init__()

        self._ui_controller = None
        self.model = model
        self.view = view

        self._ui_controller_event_handles = []

        self.ui_controller = ui_controller

        self.timed_event_dispatcher = TimedEventDispatcher()

        ################################################
        # Should this stuff really be here?
        grass_sprite = pygame.image.load('img/tile.png')
        for tile in model.tiles:
            tile.sprite = grass_sprite

        stick_fig_sprite = pygame.image.load('img/stickfig.png')
        self.pc = Mob(zone=self.model, position=(4, 2), sprite=stick_fig_sprite)

        guard = Mob(zone=self.model, position=(5, 2), sprite=stick_fig_sprite)
        PatrolDirective(
            mob=guard,
            destination_list=[(5,5), (15,5), (10,10), (5,10)],
            timed_event_dispatcher=self.timed_event_dispatcher
        ).start()

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
        self.timed_event_dispatcher.advanceBy(dt)

    def _notify_tile_mouse_event(self, coord, event_type):
        tile_coord = self.view.screen_2_tile_coord(coord)

        if tile_coord in self.model.tiles:
            tile = self.model.tiles[tile_coord]
            self.notify(event_type, tile)

    def _on_primary_click(self, coord):
        self._notify_tile_mouse_event(event_type=ZoneController.CLICK_TILE,
                                      coord=coord)

    def _on_zone_hover(self, coord):
        self._notify_tile_mouse_event(event_type=ZoneController.HOVER_TILE,
                                      coord=coord)

    def _on_secondary_click(self, coord, button):
        #TODO this is how we click on characters and entities
        pass

    def _on_move(self, direction):
        if self.pc.walk_directive is None:
            destination = map(lambda (a, b): a + b, zip(self.pc.position, direction))
            WalkToDestinationDirective(
                mob=self.pc,
                destination=destination,
                timed_event_dispatcher=self.timed_event_dispatcher
            ).start()

    def _on_click_tile(self, coord):
        if self.pc.walk_directive is None:
            WalkToDestinationDirective(
                mob=self.pc,
                destination=coord,
                timed_event_dispatcher=self.timed_event_dispatcher
            ).start()

