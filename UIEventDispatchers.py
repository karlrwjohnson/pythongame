import pygame.locals
import re

from Observable import Observable, EventType

PYGAME_KEY_CODES = set([
    pygame.locals.__dict__[key_name]
    for key_name in dir(pygame.locals)
    if re.match(r'^K_', key_name)
])

class PygameEventDispatcher (Observable):
    """ Processes pygame events """

    def __init__(self):
        """
            PyGame Event     Event Properties
            ------------------------------------
            QUIT             none
            ACTIVEEVENT      gain, state
            KEYDOWN          unicode, key, mod
            KEYUP            key, mod
            MOUSEMOTION      pos, rel, buttons
            MOUSEBUTTONUP    pos, button
            MOUSEBUTTONDOWN  pos, button
            JOYAXISMOTION    joy, axis, value
            JOYBALLMOTION    joy, ball, rel
            JOYHATMOTION     joy, hat, value
            JOYBUTTONUP      joy, button
            JOYBUTTONDOWN    joy, button
            VIDEORESIZE      size, w, h
            VIDEOEXPOSE      none
            USEREVENT        code
        """
        super(PygameEventDispatcher, self).__init__(set([
            pygame.locals.QUIT,
            pygame.locals.ACTIVEEVENT,
            pygame.locals.KEYDOWN,
            pygame.locals.KEYUP,
            pygame.locals.MOUSEMOTION,
            pygame.locals.MOUSEBUTTONUP,
            pygame.locals.MOUSEBUTTONDOWN,
            pygame.locals.JOYAXISMOTION,
            pygame.locals.JOYBALLMOTION,
            pygame.locals.JOYHATMOTION,
            pygame.locals.JOYBUTTONUP,
            pygame.locals.JOYBUTTONDOWN,
            pygame.locals.VIDEORESIZE,
            pygame.locals.VIDEOEXPOSE,
            pygame.locals.USEREVENT,
        ]))

    def handleEvents(self, events):
        for event in events:
            self.notify(event.type, event)

class KeyPressEventDispatcher (Observable):
    """Processes pygame keyboard events"""

    # Event types are tuples of the key direction and the key code.
    # :param event: Pygame event
    EVENT_TYPES = set([
        (pygame.locals.KEYDOWN, key_code)
        for key_code in PYGAME_KEY_CODES
    ] + [
        (pygame.locals.KEYUP, key_code)
        for key_code in PYGAME_KEY_CODES
    ])

    def __init__(self, pygame_event_dispatcher=None):
        super(KeyPressEventDispatcher, self).\
            __init__(KeyPressEventDispatcher.EVENT_TYPES)

        self._pygame_event_dispatcher = None
        self._pygame_event_dispatcher_handles = []

        self.pygame_event_dispatcher = pygame_event_dispatcher

    def _on_key_down(self, event):
        self.notify((pygame.locals.KEYDOWN, event.key), event)

    def _on_key_up(self, event):
        self.notify((pygame.locals.KEYUP, event.key), event)

    @property
    def pygame_event_dispatcher(self):
        return self._pygame_event_dispatcher

    @pygame_event_dispatcher.setter
    def pygame_event_dispatcher(self, pygame_event_dispatcher):
        for handle in self._pygame_event_dispatcher_handles:
            handle.cancel()

        self._pygame_event_dispatcher = pygame_event_dispatcher

        self._pygame_event_dispatcher_handles = [] \
            if self._pygame_event_dispatcher is None \
            else [
                self._pygame_event_dispatcher.observe(pygame.locals.KEYDOWN, self._on_key_down),
                self._pygame_event_dispatcher.observe(pygame.locals.KEYUP, self._on_key_up),
            ]

class KeyHoldEventDispatcher (Observable):
    """Fires events for keys which are being held down"""

    def __init__(self, pygame_event_dispatcher=None):
        super(KeyHoldEventDispatcher, self).__init__(PYGAME_KEY_CODES)

        self._heldKeys = set()
        self._pygame_event_dispatcher = None
        self._pygame_event_dispatcher_handles = []

        self.pygame_event_dispatcher = pygame_event_dispatcher

    def _on_key_down(self, event):
        self._heldKeys.add(event.key)

    def _on_key_up(self, event):
        self._heldKeys.discard(event.key)

    @property
    def pygame_event_dispatcher(self):
        return self._pygame_event_dispatcher

    @pygame_event_dispatcher.setter
    def pygame_event_dispatcher(self, pygame_event_dispatcher):
        for handle in self._pygame_event_dispatcher_handles:
            handle.cancel()

        self._pygame_event_dispatcher = pygame_event_dispatcher

        self._pygame_event_dispatcher_handles = [] \
            if self._pygame_event_dispatcher is None \
            else [
                self._pygame_event_dispatcher.observe(pygame.locals.KEYDOWN, self._on_key_down),
                self._pygame_event_dispatcher.observe(pygame.locals.KEYUP, self._on_key_up),
            ]

    def processTasks(self):
        for key in self._heldKeys:
            self.notify(key, key)

class MouseEventDispatcher(Observable):
    """Processes pygame mouse events"""

    # Fired when the mouse is clicked
    # :param pos:    A tuple of the (x,y) location of the mouse
    # :param button: Integer corresponding to the button clicked.
    #                Primary = 1, Secondary = 2, Middle = 3, etc.
    CLICK = EventType('MouseEventDispatcher.CLICK')

    # Fired when the mouse is clicked
    # :param pos:     A tuple of the (x,y) location of the mouse
    # :param rel:     A tuple of the (x,y) location of the mouse relative to the previous update
    # :param buttons: A 3-tuple of which button is being pressed.
    MOVE = EventType('MouseEventDispatcher.MOVE')

    def __init__(self, pygame_event_dispatcher=None):
        super(MouseEventDispatcher, self).__init__(set([
            MouseEventDispatcher.CLICK,
            MouseEventDispatcher.MOVE,
        ]))

        self._pygame_event_dispatcher = None
        self._pygame_event_dispatcher_handles = []

        self.pygame_event_dispatcher = pygame_event_dispatcher

    @property
    def pygame_event_dispatcher(self):
        return self._pygame_event_dispatcher

    @pygame_event_dispatcher.setter
    def pygame_event_dispatcher(self, pygame_event_dispatcher):
        for handle in self._pygame_event_dispatcher_handles:
            handle.cancel()

        self._pygame_event_dispatcher = pygame_event_dispatcher

        self._pygame_event_dispatcher_handles = [] \
            if self._pygame_event_dispatcher is None \
            else [
                self._pygame_event_dispatcher.observe(pygame.locals.MOUSEMOTION, self._on_mouse_motion),
                self._pygame_event_dispatcher.observe(pygame.locals.MOUSEBUTTONDOWN, self._on_button_down),
                self._pygame_event_dispatcher.observe(pygame.locals.MOUSEBUTTONUP, self._on_button_up),
            ]

    def _on_button_up(self, evt):
        self.notify(MouseEventDispatcher.CLICK, evt.pos, evt.button)

    def _on_button_down(self, evt):
        pass

    def _on_mouse_motion(self, evt):
        self.notify(MouseEventDispatcher.MOVE, evt.pos, evt.rel, evt.buttons)
