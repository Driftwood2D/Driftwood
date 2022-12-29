################################
# Driftwood 2D Game Dev. Suite #
# tile.py                      #
# Copyright 2014-2017          #
# Sei Satzparad & Paul Merrill #
################################

# **********
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
# **********

from typing import List, Optional

from check import CHECK, CheckFailure
import layer
import tileset


class Tile:
    """This class represents a tile.

    Attributes:
        layer: Parent Layer instance.

        seq: Tile's sequence in the layer.
        tileset: Tileset instance of the tileset which owns this tile's graphic.
        gid: Global Graphic-ID of the tile.
        localgid: Graphic-ID of the tile in relation to its own tileset.
        members: A list of sequence positions of member graphics in the tile's tileset.
        afps: Animation frames-per-second.
        pos: A two-member list containing the x and y coordinates of the tile's position in the map.
        properties: A dictionary containing tile properties.

        nowalk: If true, the tile is not walkable.
        exits: A dictionary of exit types ("exit", "exit:up", "exit:down", "exit:left", "exit:right"], with those
            present mapped to a list containing the destination [area, layer, x, y].
    """

    __slots__ = [
        "layer",
        "seq",
        "tileset",
        "gid",
        "localgid",
        "members",
        "afps",
        "pos",
        "properties",
        "nowalk",
        "exits",
        "__dstrect",
        "__cur_member",
    ]

    def __init__(self, layer: layer.Layer, seq: int, tileset: Optional[tileset.Tileset], gid: Optional[int]):
        """Tile class initializer.

        Args:
            layer: Link back to the parent Layer instance.
            seq: Tile's sequence in the map.
            tileset: Tileset instance of the tileset which owns this tile's graphic.
            gid: Global Graphic-ID of the tile.
        """
        self.layer = layer

        self.seq = seq
        self.tileset = tileset
        self.gid = gid
        self.localgid = None
        self.members = []
        self.afps = 0.0
        self.pos = [self.seq % self.layer.tilemap.width, self.seq // self.layer.tilemap.width]
        self.properties = {}

        self.nowalk = None
        self.exits = {}

        self.__dstrect = None

        # Real tile.
        if tileset and gid:
            self.localgid = self.gid - self.tileset.range[0]
            self.members = [self.localgid]
            self.__dstrect = [
                self.pos[0] * self.tileset.tilewidth,
                self.pos[1] * self.tileset.tileheight,
                self.tileset.tilewidth,
                self.tileset.tileheight,
            ]

            if self.tileset.tileproperties and self.localgid in self.tileset.tileproperties:
                self.properties = self.tileset.tileproperties[self.localgid]

            if "members" in self.properties:
                temp_members = list(map(int, self.properties["members"].split(",")))
                self.members = []
                for m in temp_members:
                    # Make things prettier for the end user by lining up member IDs with GIDs.
                    self.members.append(m - 1)
            if "afps" in self.properties:
                self.afps = float(self.properties["afps"])

            self.__cur_member = 0

            # Schedule animation.
            if self.afps:
                self.layer.tilemap.area.driftwood.tick.register(self.__next_member, delay=(1 / self.afps))

    def srcrect(self) -> List[int]:
        """Return an (x, y, w, h) srcrect for the current graphic frame of the tile."""
        if self.members:
            current_member = self.members[self.__cur_member]
            if current_member != -1:
                return [
                    (current_member * self.tileset.tilewidth) % self.tileset.imagewidth,
                    current_member * self.tileset.tilewidth // self.tileset.imagewidth * self.tileset.tileheight,
                    self.tileset.tilewidth,
                    self.tileset.tileheight,
                ]
        return [0, 0, 0, 0]

    def dstrect(self) -> List[int]:
        """Return a copy of our (x, y, w, h) dstrect so that external operations don't change our local variable."""
        return list(self.__dstrect)

    def offset(self, x, y) -> Optional["Tile"]:
        """Return the tile at this offset."""
        # Input Check
        try:
            CHECK(x, int)
            CHECK(y, int)
        except CheckFailure as e:
            self.tileset.driftwood.log.msg("ERROR", "Tile", [self.layer, self.pos], "offset", "bad argument", e)
            return None

        return self.layer.tile(self.pos[0] + x, self.pos[1] + y)

    def setgid(self, gid: int, members: List[int] = None, afps: int = None) -> Optional[bool]:
        """Helper function to change the tile graphic or animation.

        gid: The primary graphic ID to set.
        members: List of graphic IDs of the animation members if set.
        afps: Animation frames per second if set. Will not animate otherwise.

        Returns:
            True
        """
        # TODO: Make sure the GID exists.

        # Input Check
        try:
            CHECK(gid, int, _min=0)
            if members is not None:
                CHECK(members, list)
            if afps is not None:
                CHECK(afps, int, _min=0)
        except CheckFailure as e:
            self.tileset.driftwood.log.msg("ERROR", "Tile", [self.layer, self.pos], "setgid", "bad argument", e)
            return None

        self.gid = gid
        self.localgid = self.gid - self.tileset.range[0]

        if members:
            for m in range(len(members)):
                # Make things prettier for the end user by lining up member IDs with GIDs.
                members[m] -= 1
            self.members = members
        else:
            self.members = [self.localgid]

        if afps:
            self.afps = afps
            self.layer.tilemap.area.driftwood.tick.register(self.__next_member, delay=(1 / self.afps))

        return True

    def __next_member(self, seconds_past: float) -> None:
        if self.members:
            self.__cur_member = (self.__cur_member + 1) % len(self.members)
            self.layer.tilemap.area.changed = True

    def unregister(self) -> None:
        driftwood = self.layer.tilemap.area.driftwood
        if driftwood.tick.registered(self.__next_member):
            driftwood.tick.unregister(self.__next_member)

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        self.unregister()
