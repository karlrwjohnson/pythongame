import pygame.locals
import time

class Timer (object):
    def __init__(self):
        self._then = time.time()

    def elapsed(self):
        now = time.time()
        dt = now - self._then
        self._then = now
        return dt

class PygameEventDispatcher (object):
    """ Processes pygame events """

    def __init__(self):
        """
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
        self._handlers = {
            pygame.locals.QUIT:            set(),
            pygame.locals.ACTIVEEVENT:     set(),
            pygame.locals.KEYDOWN:         set(),
            pygame.locals.KEYUP:           set(),
            pygame.locals.MOUSEMOTION:     set(),
            pygame.locals.MOUSEBUTTONUP:   set(),
            pygame.locals.MOUSEBUTTONDOWN: set(),
            pygame.locals.JOYAXISMOTION:   set(),
            pygame.locals.JOYBALLMOTION:   set(),
            pygame.locals.JOYHATMOTION:    set(),
            pygame.locals.JOYBUTTONUP:     set(),
            pygame.locals.JOYBUTTONDOWN:   set(),
            pygame.locals.VIDEORESIZE:     set(),
            pygame.locals.VIDEOEXPOSE:     set(),
            pygame.locals.USEREVENT:       set(),
        }
    def addQuitHandler(self, handler):
        self._handlers[pygame.locals.QUIT].add(handler)
    def removeQuitHandler(self, handler):
        self._handlers[pygame.locals.QUIT].discard(handler)
    def addActiveEventHandler(self, handler):
        self._handlers[pygame.locals.ACTIVEEVENT].add(handler)
    def removeActiveEventHandler(self, handler):
        self._handlers[pygame.locals.ACTIVEEVENT].discard(handler)
    def addKeyDownHandler(self, handler):
        self._handlers[pygame.locals.KEYDOWN].add(handler)
    def removeKeyDownHandler(self, handler):
        self._handlers[pygame.locals.KEYDOWN].discard(handler)
    def addKeyUpHandler(self, handler):
        self._handlers[pygame.locals.KEYUP].add(handler)
    def removeKeyUpHandler(self, handler):
        self._handlers[pygame.locals.KEYUP].discard(handler)
    def addMouseMotionHandler(self, handler):
        self._handlers[pygame.locals.MOUSEMOTION].add(handler)
    def removeMouseMotionHandler(self, handler):
        self._handlers[pygame.locals.MOUSEMOTION].discard(handler)
    def addMouseButtonUpHandler(self, handler):
        self._handlers[pygame.locals.MOUSEBUTTONUP].add(handler)
    def removeMouseButtonUpHandler(self, handler):
        self._handlers[pygame.locals.MOUSEBUTTONUP].discard(handler)
    def addMouseButtonDownHandler(self, handler):
        self._handlers[pygame.locals.MOUSEBUTTONDOWN].add(handler)
    def removeMouseButtonDownHandler(self, handler):
        self._handlers[pygame.locals.MOUSEBUTTONDOWN].discard(handler)
    def addJoyAxisMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYAXISMOTION].add(handler)
    def removeJoyAxisMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYAXISMOTION].discard(handler)
    def addJoyBallMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYBALLMOTION].add(handler)
    def removeJoyBallMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYBALLMOTION].discard(handler)
    def addJoyHatMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYHATMOTION].add(handler)
    def removeJoyHatMotionHandler(self, handler):
        self._handlers[pygame.locals.JOYHATMOTION].discard(handler)
    def addJoyButtonUpHandler(self, handler):
        self._handlers[pygame.locals.JOYBUTTONUP].add(handler)
    def removeJoyButtonUpHandler(self, handler):
        self._handlers[pygame.locals.JOYBUTTONUP].discard(handler)
    def addJoyButtonDownHandler(self, handler):
        self._handlers[pygame.locals.JOYBUTTONDOWN].add(handler)
    def removeJoyButtonDownHandler(self, handler):
        self._handlers[pygame.locals.JOYBUTTONDOWN].discard(handler)
    def addVideoResizeHandler(self, handler):
        self._handlers[pygame.locals.VIDEORESIZE].add(handler)
    def removeVideoResizeHandler(self, handler):
        self._handlers[pygame.locals.VIDEORESIZE].discard(handler)
    def addVideoExposeHandler(self, handler):
        self._handlers[pygame.locals.VIDEOEXPOSE].add(handler)
    def removeVideoExposeHandler(self, handler):
        self._handlers[pygame.locals.VIDEOEXPOSE].discard(handler)
    def addUserEventHandler(self, handler):
        self._handlers[pygame.locals.USEREVENT].add(handler)
    def removeUserEventHandler(self, handler):
        self._handlers[pygame.locals.USEREVENT].discard(handler)
    def handleEvents(self, events):
        for event in events:
            for handler in self._handlers[event.type]:
                handler(event)

class KeyboardEventDispatcher (object):
    """ Processes pygame keyboard events """

    def __init__(self):
        self._handlers = dict()
        self._tasks = dict()
        self._keysDown = set()

    def keyDownCallback(self, event):
        self._keysDown.add(event.key)
        if (event.key in self._handlers):
            for handler in self._handlers[event.key]:
                handler(event)

    def keyUpCallback(self, event):
        self._keysDown.discard(event.key)

    def addKeyDownHandler(self, key, handler):
        if not(key in self._handlers):
            self._handlers[key] = set()
        self._handlers[key].add(handler)

    def removeKeyDownHandler(self, key, handler):
        self._handlers[key].discard(handler)
        if len(self._handlers[key]) == 0:
            del self._handlers[key]

    def addKeyPressTask(self, key, handler):
        if not(key in self._tasks):
            self._tasks[key] = set()
        self._tasks[key].add(handler)

    def removeKeyPressTask(self, key, handler):
        self._tasks[key].discard(handler)
        if len(self._tasks[key]) == 0:
            del self._tasks[key]

    def processTasks(self):
        for key in self._keysDown:
            if key in self._tasks:
                for task in self._tasks[key]:
                    task()

class MouseEventDispatcher(object):
    """ Processes pygame mouse events """

    def __init__(self):
        self._clickHandlers = set()
        self._moveHandlers = set()

    def mouseMotionHandler(self, evt):
        for handler in self._moveHandlers:
            handler(evt.pos)
    def mouseButtonUpHandler(self, evt):
        for handler in self._clickHandlers:
            handler(evt.pos)
    def mouseButtonDownHandler(self, evt):
        pass

    def addClickHandler(self, handler):
        self._clickHandlers.add(handler)
    def removeClickHandler(self, handler):
        self._clickHandlers.remove(handler)
    def addMoveHandler(self, handler):
        self._moveHandlers.add(handler)
    def removeMoveHandler(self, handler):
        self._moveHandlers.remove(handler)

