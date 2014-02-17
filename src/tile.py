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

import math


class Tile:
    """This class represents a tile.

    Attributes:
        layer: Parent Layer instance.

        seq: Tile's sequence in the layer.
        tileset: Tileset instance of the tileset which owns this tile's graphic.
        gid: Global Graphic-ID of the tile.
        localgid: Graphic-ID of the tile in relation to its own tileset.
        gpos: A two-member list containing the x and y coordinates of the tile's graphic in its tileset.
        tpos: A two-member list containing the x and y coordinates of the tile's position in the map.
        srcrect: A four-member list containing an x,y,w,h source rectangle for the tile's graphic.
        srcrect: A four-member list containing an x,y,w,h destination rectangle for the tile's placement.
        entities: A list of entities bound to this tile.
        properties: A dictionary containing tile properties.
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
        self.localgid = self.gid - self.tileset.range[0]
        self.gpos = [
            (self.gid - self.tileset.range[0]) % self.tileset.width,
            math.floor((self.gid - self.tileset.range[0]) / self.tileset.width)
        ]
        self.tpos = [
            self.seq % self.layer.tilemap.width,
            math.floor(self.seq / self.layer.tilemap.width)
        ]
        self.srcrect = [
            (self.gpos[0] * self.tileset.tilewidth) + (self.gpos[0] * self.tileset.spacing),
            (self.gpos[1] * self.tileset.tileheight) + (self.gpos[1] * self.tileset.spacing),
            self.tileset.tilewidth,
            self.tileset.tileheight
        ]
        self.dstrect = [
            self.tpos[0] * self.tileset.tilewidth,
            self.tpos[1] * self.tileset.tileheight,
            self.tileset.tilewidth,
            self.tileset.tileheight
        ]
        self.entities = []
        if self.tileset.tileproperties and self.localgid in self.tileset.tileproperties:
            self.properties = self.tileset.tileproperties[self.localgid]
