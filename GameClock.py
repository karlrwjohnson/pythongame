from pygame.time import Clock

from Observable import Observable, EventType

class GameClock (Observable):
    """Keeps track of how fast the game clock runs"""

    # Fires when game time advances
    # :param dt: Amount of game time that elapsed
    @EventType
    def REAL_TIME_ADVANCE(dt):
        """Game time has advanced
        :param dt: Amount of game time that elapsed, in "seconds"
        """

    @EventType
    def GAME_TIME_ADVANCE(dt):
        """Real time has passed
        :param dt: Amount of real time that elapsed, in milliseconds
        """

    def __init__(self, framerate, multiplier=1.0):
        super(GameClock, self).__init__()

        self.clock = Clock()
        self._multiplier = multiplier
        self.framerate = framerate
        self.isPaused = False

    @property
    def multiplier(self):
        """Get the real/game time ratio"""
        if self.isPaused:
            return 0
        else:
            return self._multiplier

    @multiplier.setter
    def multiplier(self, multiplier):
        """Get the real/game time ratio"""
        self._multiplier = multiplier

    def toggle(self):
        self.isPaused ^= True

    def update(self):
        # pygame.time.Clock::tick() returns milliseconds
        real_dt = self.clock.tick(self.framerate)
        #self.notify(GameClock.REAL_TIME_ADVANCE, real_dt)
        game_dt = real_dt * self.multiplier / 1000.0
        self.notify(GameClock.GAME_TIME_ADVANCE, game_dt)

    def zero(self):
        """Drain any time off the internal clock without calling any updaters"""
        real_dt = self.clock.tick(self.framerate)
        #self.notify(GameClock.REAL_TIME_ADVANCE, real_dt)
