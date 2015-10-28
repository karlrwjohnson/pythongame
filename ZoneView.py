import numpy
import pygame

from UIView import UIView

class ZoneView (object):
    """Renders a zone and everything in it."""

    def __init__(self, zone, ui_view, spriteSize=(32, 32)):
        self._zone = None
        self._ui_view = None

        self._ui_view_event_handles = []

        self.zone = zone
        self.ui_view = ui_view

        # Using numpy lets us do math with vectors for cleaner syntax
        self.spriteSize = numpy.array(spriteSize)
        self.viewOffsetPx = numpy.array((0, 0))

        self._tileClickHandlers = set()

        self.hover_tile = None
        self.tile_hover_sprite = pygame.image.load('img/hilight.png')

    @property
    def zone(self):
        return self._zone

    @zone.setter
    def zone(self, zone):
        self._zone = zone

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

    def what_is_at(self, screen_coord):
        tile_coord = self.screen_2_tile_coord(screen_coord)

        if tile_coord in self.zone.tiles:
            return self.zone.tiles[tile_coord]
        else:
            return None

    def screen_2_tile_coord(self, screenCoord):
        return (screenCoord - self.viewOffsetPx) / self.spriteSize

    def _on_render(self):
        for tile in self.zone.tiles:
            self.blit_world_sprite(tile.sprite, tile.coords)

        for mob in self.zone.mobs:
            self.blit_world_sprite(mob.sprite, mob.position)

        if self.hover_tile is not None:
            self.blit_world_sprite(self.tile_hover_sprite, self.hover_tile.coords)
