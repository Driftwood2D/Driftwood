###################################
## Driftwood 2D Game Dev. Suite  ##
## layer.py                      ##
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

import tile


class Layer:
    """This class abstracts a layer.

    Attributes:
        tilemap: Parent Tilemap instance.

        properties: A dictionary containing layer properties.

        tiles: The list of Tile class instances for each tile.
    """
    def __init__(self, tilemap, layerdata, zpos):
        """Layer class initializer.

        Args:
            tilemap: Link back to the parent Tilemap instance.
            layerdata: JSON layer segment.
            zpos: Layer's z-position.
        """
        self.tilemap = tilemap

        self.zpos = zpos
        self.properties = {}

        self.tiles = []

        # This contains the JSON of the layer.
        self.__layer = layerdata

        self.__prepare_layer()

    def __prepare_layer(self):
        # Set layer properties if present.
        if "properties" in self.__layer:
            self.properties = self.__layer["properties"]

        # Iterate through the tile graphic IDs.
        for seq, gid in enumerate(self.__layer["data"]):
            # Does this tile actually exist?
            if gid:
                # Find which tileset the tile's graphic is in.
                for ts in self.tilemap.tilesets:
                    if gid in range(*ts.range):
                        # Create the Tile instance for this tile.
                        self.tiles.append(tile.Tile(self, seq, ts, gid))

            else:
                self.tiles.append(None)

    def _process_objects(self, objdata):
        """Process and merge an object layer into the tile layer below.

        This method is marked private even though it's called from Tilemap, because it should not be called outside the
        engine code.

        Args:
            objdata: JSON object layer segment.
        """
        if "properties" in objdata:
            self.properties.update(objdata["properties"])

        for obj in objdata["objects"]:
            # Is the object properly sized?
            if (obj["x"] % self.tilemap.tilewidth or obj["y"] % self.tilemap.tileheight or
                    obj["width"] % self.tilemap.tilewidth or obj["height"] % self.tilemap.tileheight):
                self.tilemap.area.driftwood.log.msg("ERROR", "Map", "invalid object size or placement")
                continue

            # Map object properties onto their tiles.
            for x in range(1, int(obj["width"] / self.tilemap.tilewidth)+1):
                for y in range(1, int(obj["height"] / self.tilemap.tileheight)+1):
                    tx = (x * obj["x"]) / self.tilemap.tilewidth
                    ty = (y * obj["y"]) / self.tilemap.tileheight

                    # Insert the object properties.
                    self.tiles[int((ty * self.tilemap.width) + tx)].properties.update(obj["properties"])

    def tile(self, x, y):
        """Retrieve a tile from the layer by its coordinates.

        Args:
            x: x-coordinate
            y: y-coordinate
        """
        return self.tiles[int((y * self.tilemap.width) + x)]
