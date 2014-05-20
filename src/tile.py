###################################
## Driftwood 2D Game Dev. Suite  ##
## tile.py                       ##
## Copyright 2014 PariahSoft LLC ##
###################################

## **********
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to
## deal in the Software without restriction, including without limitation the
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
## sell copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.
## **********


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
        dstrect: A four-member list containing an x,y,w,h destination rectangle for the tile's placement.
        properties: A dictionary containing tile properties.

        nowalk: If true, the tile is not walkable.
        exits: A dictionary of exit types ("exit", "exit:up", "exit:down", "exit:left", "exit:right"], with those
            present mapped to a list containing the destination [area, layer, x, y].
    """
    def __init__(self, layer, seq, tileset, gid):
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
        self.pos = [
            self.seq % self.layer.tilemap.width,
            self.seq // self.layer.tilemap.width
        ]
        self.dstrect = None
        self.properties = {}

        self.nowalk = None
        self.exits = {}

        # Real tile.
        if tileset and gid:
            self.localgid = self.gid - self.tileset.range[0]
            self.members = [self.localgid]
            self.dstrect = [
                self.pos[0] * self.tileset.tilewidth,
                self.pos[1] * self.tileset.tileheight,
                self.tileset.tilewidth,
                self.tileset.tileheight
            ]

            if self.tileset.tileproperties and self.localgid in self.tileset.tileproperties:
                self.properties = self.tileset.tileproperties[self.localgid]

            if "members" in self.properties:
                self.members = list(map(int, self.properties["members"].split(',')))
            if "afps" in self.properties:
                self.afps = float(self.properties["afps"])

            self.__cur_member = 0

            # Schedule animation.
            if self.afps:
                self.layer.tilemap.area.driftwood.tick.register(self.__next_member, delay=(1/self.afps))

    def srcrect(self):
        """Return an (x, y, w, h) srcrect for the current graphic frame of the tile.
        """
        current_member = self.members[self.__cur_member]
        return (((current_member * self.tileset.tilewidth) % self.tileset.imagewidth),
                ((current_member * self.tileset.tilewidth) // self.tileset.imagewidth) * self.tileset.tileheight,
                self.tileset.tilewidth, self.tileset.tileheight)

    def __next_member(self, seconds_past):
        self.__cur_member = (self.__cur_member + 1) % len(self.members)
        self.layer.tilemap.area.changed = True
