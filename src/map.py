###################################
## Project Driftwood             ##
## map.py                        ##
## Copyright 2013 PariahSoft LLC ##
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

import json
import math


class MapManager:
    """The Map Manager

    This class reads the Tiled map file for the currently focused area, and presents an abstraction.

    Attributes:
        config: ConfigManager instance.

        width: Width of the map in tiles.
        height: Height of the map in tiles.
        tilewidth: Width of tiles in the map.
        tileheight: Height of tiles in the map.
        num_layers: Number of layers in the map.
        num_tilesets: Number of tilesets in the map.
    """

    def __init__(self, config):
        self.config = config

        self.width = 0
        self.height = 0
        self.tilewidth = 0
        self.tileheight = 0
        self.num_layers = 0
        self.num_tilesets = 0

        # A list of lists of dictionaries, wherein each list represents a layer starting at layer 0, and each layer is a
        # list of dictionaries representing individual tiles.
        #
        # Dict Keys:
        #     tileset: The number of the tileset containing the tile's graphic.
        #     tx: The x-coordinate of the graphic.
        #     ty: The y-coordinate of the graphic.
        #     properties: TODO: A dict containing any object properties covering the tile.
        self.__tiles = []

        # A list of dicts wherein each member represents a tileset.
        #
        # Dict Keys:
        #     filename: The filename of the tileset image.
        #     name: The name of the tileset.
        #     image: filetype.ImageFile instance of the tileset image.
        #     texture: Texture of the tileset image.
        #     width: Width of the tileset in tiles.
        #     height: Height of the tileset in tiles.
        #     imagewidth: Width of the tileset in pixels.
        #     imageheight: Height of the tileset in pixels.
        #     tilewidth: Width of tiles in the tileset.
        #     tileheight: Height of tiles in the tileset.
        #     size: Number of tiles in the tileset.
        #     spacing: TODO: Spacing in pixels between tiles in the tileset.
        #     range: Range of tile graphic IDs covered by this tileset.
        #     properties: A dict containing any custom properties of the tileset.
        self.__tilesets = []

        # This contains the JSON of the Tiled map.
        self.__map = {}

        self.__log = self.config.baseclass.log
        self.__filetype = self.config.baseclass.filetype
        self.__resource = self.config.baseclass.resource

    def _read(self, data):
        """Read and abstract a Tiled map.

        Reads the JSON Tiled map and processes its information into useful abstractions. This method is private even
        though it's called from AreaManager, because it should never be called from anywhere else.

        Args:
            data: JSON contents of the Tiled map.
        """
        self.__map = json.loads(data)

        # Set class attributes representing information about the map.
        self.width = self.__map["width"]
        self.height = self.__map["height"]
        self.tilewidth = self.__map["tilewidth"]
        self.tileheight = self.__map["tileheight"]
        self.num_layers = len(self.__map["layers"])
        self.num_tilesets = len(self.__map["tilesets"])

        # Build the tileset abstractions.
        for ts, tileset in enumerate(self.__map["tilesets"]):
            self.__tilesets.append({})
            self.__tilesets[ts]["filename"] = tileset["image"]
            self.__tilesets[ts]["name"] = tileset["name"]
            self.__tilesets[ts]["image"] = self.__filetype.ImageFile(
                self.__resource.request(self.__tilesets[ts]["filename"], True)
            )
            self.__tilesets[ts]["texture"] = self.__tilesets[ts]["image"].texture
            self.__tilesets[ts]["imagewidth"] = tileset["imagewidth"]
            self.__tilesets[ts]["imageheight"] = tileset["imageheight"]
            self.__tilesets[ts]["tilewidth"] = tileset["tilewidth"]
            self.__tilesets[ts]["tileheight"] = tileset["tileheight"]
            self.__tilesets[ts]["width"] = int(self.__tilesets[ts]["imagewidth"] / self.__tilesets[ts]["tilewidth"])
            self.__tilesets[ts]["height"] = int(self.__tilesets[ts]["imageheight"] / self.__tilesets[ts]["tileheight"])
            self.__tilesets[ts]["size"] = int(self.__tilesets[ts]["width"] * self.__tilesets[ts]["height"])
            self.__tilesets[ts]["spacing"] = tileset["spacing"]
            self.__tilesets[ts]["range"] = [tileset["firstgid"], tileset["firstgid"]-1 + self.__tilesets[ts]["size"]]
            self.__tilesets[ts]["properties"] = {}
            for prop in tileset["properties"]:
                self.__tilesets[ts]["properties"][prop] = tileset["properties"][prop]

        # Build the tile abstractions.
        for layer in self.__map["layers"]:
            self.__tiles.append([])

            # Iterate through the tile graphic IDs.
            for d in layer["data"]:
                self.__tiles[-1].append({})

                # Does this tile actually exist?
                if d:
                    # Find which tileset the tile's graphic is in.
                    for ts, tileset in enumerate(self.__tilesets):
                        if d in range(*tileset["range"]):
                            # Set the tile's tileset.
                            self.__tiles[-1][-1]["tileset"] = ts
                            break

                    # Set the tile's x and y graphic coordinates.
                    self.__tiles[-1][-1]["tx"] = ((d - tileset["range"][0]) %
                                                  self.__tilesets[self.__tiles[-1][-1]["tileset"]]["width"])
                    self.__tiles[-1][-1]["ty"] = math.floor((d - tileset["range"][0]) /
                                                            self.__tilesets[self.__tiles[-1][-1]["tileset"]]["width"])

    def get_tile(self, layer, x, y):
        """Get a tile by its layer and x y coordinates.

        Args:
            layer: The layer (z) coordinate.
            x: The x-coordinate.
            y: The y-coordinate.

        Returns:
            Member of self.__tiles.
        """
        if layer >= len(self.__tiles) or x > self.width or y > self.height:
            return None

        return self.__tiles[layer][(y * self.width) + x]

    def get_tile_coords(self, layer, num):
        """Figure out the coordinates of a tile by its number in the sequence.

        Args:
            layer: The layer (z) coordinate.
            num: The tile's number in the map's layer data sequence.

        Returns:
            List containing the x and y coordinates of the tile.
        """
        if layer >= len(self.__tiles) or num >= len(self.__tiles[layer]):
            return None

        return [num % self.width, math.floor(num / self.width)]

    def get_tileset(self, num):
        """Get a tileset by its ID number.

        Args:
            num: The tileset's ID number.

        Returns:
            Member of self.__tilesets.
        """
        if num >= len(self.__tilesets):
            return None

        return self.__tilesets[num]

    def get_tile_srcrect(self, layer, x, y):
        """Get a source SDL_Rect for the tile's graphic in the tileset.

        For the tile at the given coordinates, produce an x,y,w,h source rectangle describing the position of the tile's
        graphic in its tileset. This rectangle is used by SDL_RenderCopy.

        Args:
            layer: The layer (z) coordinate.
            x: The x-coordinate.
            y: The y-coordinate.
        """
        tile = self.get_tile(layer, x, y)
        if not tile:
            return None

        srcrect = [0, 0, 0, 0]

        srcrect[0] = tile["tx"] * self.get_tileset(tile["tileset"])["tilewidth"]
        srcrect[1] = tile["ty"] * self.get_tileset(tile["tileset"])["tileheight"]
        srcrect[2] = self.get_tileset(tile["tileset"])["tilewidth"]
        srcrect[3] = self.get_tileset(tile["tileset"])["tileheight"]

        return srcrect

    def get_tile_dstrect(self, layer, x, y):
        """Get a destination SDL_Rect for the tile graphic's position on the display.

        For the tile at the given coordinates, produce an x,y,w,h destination rectangle describing the position of the
        tile graphic's appearance on the display. This rectangle is used by SDL_RenderCopy.

        Args:
            layer: The layer (z) coordinate.
            x: The x-coordinate.
            y: The y-coordinate.
        """
        tile = self.get_tile(layer, x, y)
        if not tile:
            return None

        dstrect = [0, 0, 0, 0]

        dstrect[0] = x * self.get_tileset(tile["tileset"])["tilewidth"]
        dstrect[1] = y * self.get_tileset(tile["tileset"])["tileheight"]
        dstrect[2] = self.get_tileset(tile["tileset"])["tilewidth"]
        dstrect[3] = self.get_tileset(tile["tileset"])["tileheight"]

        return dstrect
