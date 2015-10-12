import pygame

from Observable import Observable, EventType
from util import immutableArray

class UIView (Observable):

    @EventType
    def RENDER_ZONE():
        """The ZoneView should render the Zone"""

    def __init__(self, size, caption):
        super(UIView, self).__init__()

        pygame.init()

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
        """Turns the screen black"""
        self.screen.fill((0,0,0))

    def render(self):
        self.clear()
        self.notify(UIView.RENDER_ZONE)
        pygame.display.flip()
