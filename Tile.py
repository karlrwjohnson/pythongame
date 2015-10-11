from Observable import Observable, EventType

class Tile (Observable):
    """A square region of map which can hold one occupant."""

    # Fired when the tile becomes occupied.
    # Callback signature: lambda tile: Tile = self, occupant: Mob
    OCCUPY = EventType('Tile.OCCUPY')

    # Fired when the tile becomes unoccupied.
    # Callback signature: lambda tile: Tile = self, occupant: Mob
    VACATE = EventType('Tile.VACATE')

    class OwnershipException (Exception):
        pass

    def __init__(self, zone, coords, sprite=None):
        super(Tile, self).__init__(set([
            Tile.OCCUPY,
            Tile.VACATE,
        ]))

        self.zone = zone
        self._coords = tuple(coords)
        self.sprite = sprite
        self._occupant = None

    @property
    def occupant(self):
        return self._occupant

    @occupant.setter
    def occupant(self, occupant):
        """Change the occupant of the tile
        :param occupant: New occupant
        :raises Tile.OwnershipException: To prevent mobs "stealing" tiles, this
           must first be explicitly cleared by setting to None before being set
           to another occupant.
        :return:
        """
        if self._occupant:
            if occupant:
                raise Tile.OwnershipException(self._occupant, occupant)
            else:
                self._occupant = occupant
                self.notify(Tile.VACATE, self, self._occupant)
        else:
            if occupant:
                self._occupant = occupant
                self.notify(Tile.OCCUPY, self, occupant)
            else:
                pass

    @property
    def coords(self):
        return self._coords

    def __repr__(self):
        return 'Tile(coords={}, occupant={}, ...)'.format(self.coords, self.occupant)
