import numpy
import pygame

from util import immutableArray

class ScreenManager (object):
    def __init__(self, size=(640,480), caption='Hello World!'):
        self._size = None
        self._caption = None
        self.screen = None

        self.size = size
        self.caption = caption

        pygame.display.set_caption(caption)

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = immutableArray(size)
        self.screen = pygame.display.set_mode(size)

    @property
    def caption(self):
        return self._caption

    @caption.setter
    def caption(self, caption):
        self._caption = caption
        pygame.display.set_caption(self.caption)

    def clear(self):
        self.screen.fill((0,0,0))

    def flip(self):
        pygame.display.flip()

class MapView (object):
    def __init__(self, map, screenManager, spriteSize=(32, 32)):
        self.map = map
        self.screenManager = screenManager
        self.spriteSize = numpy.array(spriteSize)
        self.viewOffsetPx = numpy.array((0, 0))

        self._tileClickHandlers = set()

        self.mousePos = None
        self.tileHoverSprite = pygame.image.load('hilight.png')

    def blitWorldSprite(self, sprite, tileCoord):
        self.screenManager.screen.blit(sprite, tileCoord * self.spriteSize - self.viewOffsetPx)

    @property
    def centerTileCoord(self):
        return (self.viewOffsetPx + self.screenManager.size / 2) / self.spriteSize

    @centerTileCoord.setter
    def centerTileCoord(self, centerTileCoord):
        self.viewOffsetPx = centerTileCoord * self.spriteSize - self.screenManager.size / 2

    def screen2TileCoord(self, screenCoord):
        return (screenCoord - self.viewOffsetPx) / self.spriteSize

    def render(self):
        for y in range(self.map.dimensions[1]):
            for x in range(self.map.dimensions[0]):
                self.blitWorldSprite(self.map.board[y][x].sprite, (x, y))
        for mob in self.map.mobs:
            self.blitWorldSprite(mob.sprite, mob.position)

        if self.mousePos is not None:
            self.blitWorldSprite(self.tileHoverSprite, self.screen2TileCoord(self.mousePos))

    def mouseHoverCallback(self, screenCoord):
        self.mousePos = screenCoord

    def mouseClickCallback(self, screenCoord):
        for handler in self._tileClickHandlers:
            handler(self.screen2TileCoord(screenCoord))

    def addTileClickHandler(self, handler):
        self._tileClickHandlers.add(handler)

    def removeTileClickHandler(self, handler):
        self._tileClickHandlers.remove(handler)
