from Tile import Tile
from TimedEventDispatcher import TimedEventDispatcher

class Zone (object):
    """
    A zone is a region of space and everything inside it.
    It (tentatively) contains:
    - Tile data
    - Dimensions (extents of mob/entity locations and tile data)
    - Mobs
    - Entities (unimplemented)
    - Initial directives
    """

    class TilesDelegate (object):
        """Gives access to a Zone's tiles"""
        def __init__(self, zone):
            self._zone = zone

        def __getitem__(self, coords):
            """Retrieves a tile at the given coordinate

            :param coords: A tuple (or similar) containing the x and y
                           coordinates of the tile
            """
            (x, y) = coords
            # noinspection PyProtectedMember
            return self._zone._tiles[y][x]

        def __contains__(self, coords_or_tile):
            """Checks whether a tile belongs to this model or a coordinate is in bounds

            Yes, this function is overloaded to do two different things.
            So sue me.

            :param coords_or_tile: A tuple-like x/y coordinate or a Tile object
            :return: A boolean
            """
            if isinstance(coords_or_tile, Tile):
                # Is a Tile
                if coords_or_tile.coords in self:
                    for tile in self:
                        if tile is coords_or_tile:
                            return True
                    else:
                        return False
                else:
                    return False
            else:
                # Is a coordinate
                (x, y) = coords_or_tile
                return 0 <= x < self._zone.dimensions[0] \
                    and 0 <= y < self._zone.dimensions[1]

        def __iter__(self):
            """Iterates over every tile in the zone"""
            # noinspection PyProtectedMember
            for row in self._zone._tiles:
                for tile in row:
                    yield tile

    def __init__(self, dimensions):

        self._dimensions = dimensions
        self._tileDelegate = Zone.TilesDelegate(self)
        self._mob_tiles = dict()

        self._tiles = [
            [Tile(zone=self, coords=(x,y)) for x in range(dimensions[0])]
            for y in range(dimensions[1])
        ]

        self.timed_event_dispatcher = TimedEventDispatcher()

        for tile in self.tiles:
            tile.observe(Tile.OCCUPY, self._on_tile_occupy)
            tile.observe(Tile.VACATE, self._on_tile_vacate)

    @property
    def tiles(self):
        return self._tileDelegate

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def mobs(self):
        return self._mob_tiles.keys()

    def _on_tile_occupy(self, tile):
        mob = tile.occupant
        if mob in self._mob_tiles:
            self._mob_tiles[mob].add(tile)
        else:
            self._mob_tiles[mob] = set([tile])

    def _on_tile_vacate(self, tile, mob):
        self._mob_tiles[mob].remove(tile)
        if len(self._mob_tiles[mob]) == 0:
            del self._mob_tiles[mob]

    # @property
    # def mobs(self):
    #     return self._mobsDelegate