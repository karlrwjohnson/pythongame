from Observable import Observable, EventType
from util import *

class Tile (Observable):
    """A square region of map which can hold one occupant."""

    @EventType
    def OCCUPY(tile):
        """The tile became occupied
        :param tile: The tile in question, i.e. Self
        """

    @EventType
    def VACATE(tile, mob):
        """The tile became unoccupied
        :param tile: The tile in question, i.e. Self
        :param mob: The mob that vacated the tile
        """

    class OwnershipException (Exception):
        pass

    def __init__(self, zone, coords, sprite=None):
        super(Tile, self).__init__()

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

        # No change (None -> None or Mob -> same Mob)
        if self._occupant is occupant:
            pass
        # Tile previously occupied
        elif self._occupant:
            # Attempting to invade tile (Mob -> different Mob)
            if occupant:
                raise Tile.OwnershipException(self._occupant, occupant)
            # Vacating tile (Mob -> None)
            else:
                previous, self._occupant = self._occupant, None
                self.notify(Tile.VACATE, self, previous)
        # Claiming tile (None -> Mob)
        else:
            self._occupant = occupant
            self.notify(Tile.OCCUPY, self)

    @property
    def coords(self):
        return self._coords

    def get_relative_tile(self, rel_coords):
        abs_coords = vec_add(self.coords, rel_coords)
        if abs_coords in self.zone.tiles:
            return self.zone.tiles[abs_coords]
        else:
            return None

    def __repr__(self):
        return 'Tile(coords={}, occupant={}, ...)'.format(self.coords, self.occupant)
