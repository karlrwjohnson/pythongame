import numpy
import pygame

from MobView import MobView
from UIView import UIView

class ZoneView (object):
    """Renders a zone and everything in it."""

    def __init__(self, model, ui_view, spriteSize=(32, 32)):
        self._model = None
        self._ui_view = None

        self._ui_view_event_handles = []

        self.model = model
        self.ui_view = ui_view

        # Using numpy lets us do math with vectors for cleaner syntax
        self.spriteSize = numpy.array(spriteSize)
        self.viewOffsetPx = numpy.array((0, 0))

        self._tileClickHandlers = set()

        self.mouse_pos = None
        self.tile_hover_sprite = pygame.image.load('img/hilight.png')

    @property
    def model(self):
        return self._model

    @model.setter
    def model(self, model):
        self._model = model

    @property
    def ui_view(self):
        return self._ui_view

    @ui_view.setter
    def ui_view(self, ui_view):
        # Cancel old listeners (if any)
        for handle in self._ui_view_event_handles:
            handle.cancel()

        self._ui_view = ui_view

        # Register listeners with new ui_view object
        self._ui_view_event_handles = [] \
            if self._ui_view is None \
            else [
                self.ui_view.observe(UIView.RENDER_ZONE, self._on_render),
            ]

    @property
    def center_tile(self):
        return (self.viewOffsetPx + self.ui_view.size / 2) / self.spriteSize

    @center_tile.setter
    def center_tile(self, center_tile):
        self.viewOffsetPx = center_tile * self.spriteSize - self.ui_view.size / 2

    def blit_world_sprite(self, sprite, tileCoord):
        self.ui_view.screen.blit(sprite, tileCoord * self.spriteSize - self.viewOffsetPx)

    def screen_2_tile_coord(self, screenCoord):
        return (screenCoord - self.viewOffsetPx) / self.spriteSize

    def _on_render(self):
        for tile in self.model.tiles:
            self.blit_world_sprite(tile.sprite, tile.coords)

        mob_view = MobView()
        for mob in self.model.mobs:
            mob_view.render(self, mob)

        if self.mouse_pos is not None:
            self.blit_world_sprite(self.tile_hover_sprite, self.screen_2_tile_coord(self.mouse_pos))
