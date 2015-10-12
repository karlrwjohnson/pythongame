import numpy

from Observable import Observable, \
    EventType

class Mob (Observable):

    @EventType
    def POSITION_CHANGE(mob, old_position):
        """Mob moved
        :param mob: The mob that moved (i.e. self)
        :param old_position: The previous position
        """
        pass

    @EventType
    def WALK_DIRECTIVE_CHANGE(mob, old_position):
        """Mob's walk_directive changed
        :param mob: The mob that moved (i.e. self)
        :param old_position: The previous position
        """
        pass

    @EventType
    def WALK_ANIMATION_CHANGE(mob, old_position):
        """Mob's walk_animation changed
        :param mob: The mob that moved (i.e. self)
        :param old_position: The previous position
        """
        pass

    def __init__(self, zone, position, sprite, speed=5.0):
        super(Mob, self).__init__()

        self._position = None
        self._walk_directive = None
        self._walk_animation = None
        self.zone = zone
        self.sprite = sprite
        self.speed = speed

        zone.mobs.add(self)

        # Run setter
        self.position = position

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        # Why do I need to assert this?
        assert self._position is None or self.zone.tiles[position].occupant is None, \
            'Target tile is already occupied'

        old_position = self._position

        # Oh right, the mob claims its tile.
        # Is this definitely what I want to do though?
        if not(self._position is None):
            self.zone.tiles[self._position].occupant = None

        if position is None:
            raise RuntimeError("what the flip??")
            self._position = None
        else:
            self._position = numpy.array(position)
            self.zone.tiles[position].occupant = self

        self.notify(Mob.POSITION_CHANGE, self, old_position)

    @property
    def walk_directive(self):
        return self._walk_directive

    @walk_directive.setter
    def walk_directive(self, walk_directive):
        self._walk_directive = walk_directive
        self.notify(Mob.WALK_DIRECTIVE_CHANGE, self)

    @property
    def walk_animation(self):
        return self._walk_animation

    @walk_animation.setter
    def walk_animation(self, walk_animation):
        self._walk_animation = walk_animation
        self.notify(Mob.WALK_ANIMATION_CHANGE, self)

