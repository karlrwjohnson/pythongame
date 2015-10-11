import pygame
import pygame.locals

from GameClock import GameClock
from Observable import Observable, \
    EventType
from UIEventDispatchers import \
    KeyHoldEventDispatcher, \
    KeyPressEventDispatcher, \
    MouseEventDispatcher, \
    PygameEventDispatcher
from util import logging_passthru

class UIController (Observable):
    """
    Gets UI and Clock events from pygame and interprets them as game events
    """

    # :param coord: x/y tuple of the mouse's screen location
    PRIMARY_CLICK = EventType('UIController.PRIMARY_CLICK')

    # :param coord: x/y tuple of the mouse's screen location
    SECONDARY_CLICK = EventType('UIController.SECONDARY_CLICK')

    # :param coord: x/y tuple of the mouse's screen location
    ZONE_HOVER = EventType('UIController.ZONE_HOVER')

    # User tells character to move
    # :param direction: x/y tuple of direction
    MOVE = EventType('UIController.CHARACTER_MOVE')

    def __init__(self,
                 view,
                 framerate):
        super(UIController, self).__init__(set([
            UIController.PRIMARY_CLICK,
            UIController.SECONDARY_CLICK,
            UIController.ZONE_HOVER,
            UIController.MOVE
        ]))

        self.view = view

        self._terminate_flag = True

        # Wiring
        self.game_clock = GameClock(framerate)

        self.pygameEventDispatcher = PygameEventDispatcher()
        self.keyPressEventDispatcher = KeyPressEventDispatcher(self.pygameEventDispatcher)
        self.keyHoldEventDispatcher = KeyHoldEventDispatcher(self.pygameEventDispatcher)
        self.mouseEventDispatcher = MouseEventDispatcher(self.pygameEventDispatcher)

        self.pygameEventDispatcher.observe(pygame.locals.QUIT, self._on_quit)
        self.keyPressEventDispatcher.observe(
            (pygame.locals.KEYDOWN, pygame.locals.K_q),
            self._on_quit)
        self.mouseEventDispatcher.observe(MouseEventDispatcher.CLICK, self._on_click)

        self.keyPressEventDispatcher.observe(
            (pygame.locals.KEYDOWN, pygame.locals.K_SPACE),
            lambda *args, **kwargs: self.game_clock.toggle()
        )

        notify_walk = lambda dx, dy:\
            lambda *args, **kwargs:\
                self.notify(UIController.MOVE, logging_passthru((dx, dy), 'dx,dy = {}'))
        self.keyHoldEventDispatcher.observe(pygame.locals.K_UP, notify_walk(0, -1))
        self.keyHoldEventDispatcher.observe(pygame.locals.K_DOWN, notify_walk(0, 1))
        self.keyHoldEventDispatcher.observe(pygame.locals.K_LEFT, notify_walk(-1, 0))
        self.keyHoldEventDispatcher.observe(pygame.locals.K_RIGHT, notify_walk(1, 0))

    def run(self):
        self._terminate_flag = False

        # Drain any existing time from the clock
        self.game_clock.zero()

        while not self._terminate_flag:
            # Render
            self.view.render()

            # Time (triggers events)
            self.game_clock.update()

            # Events
            self.pygameEventDispatcher.handleEvents(pygame.event.get())
            self.keyHoldEventDispatcher.processTasks()

    def _on_quit(self, event):
        self._terminate_flag = True

    def _on_click(self, coord, button):
        #TODO distinguish between the zone and the UI (as soon as there is a UI!)
        if button == 1:
            self.notify(UIController.PRIMARY_CLICK, coord)
        elif button == 2:
            self.notify(UIController.SECONDARY_CLICK, coord)
