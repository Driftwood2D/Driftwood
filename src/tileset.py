####################################
# Driftwood 2D Game Dev. Suite     #
# tileset.py                       #
# Copyright 2014 PariahSoft LLC    #
# Copyright 2017 Michael D. Reiley #
# & Paul Merrill                   #
####################################

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

from sdl2 import *


class Tileset:
    """This class abstracts a tileset.

    Attributes:
        tilemap: Parent Tilemap instance.

        filename: Filename of the tileset image.
        name: Name of the tileset, if any.
        image: The filetype.ImageFile instance for the tileset image.
        texture: The SDL_Texture for the tileset image.
        width: Width of the tileset in tiles.
        height: Height of the tileset in tiles.
        imagewidth: Width of the tileset in pixels.
        imageheight: Height of the tileset in pixels.
        tilewidth: Width in pixels of tiles in the tileset.
        tileheight: Height in pixels of tiles in the tileset.
        size: Number of tiles in the tileset.
        spacing: Spacing in pixels between tiles in the tileset.
        range: A two-member list containing the first and last tile GIDs coverered by this tileset.
        properties: A dictionary containing the tileset properties.
        tileproperties: A dictionary containing mappings of tile GIDs to properties that apply to that GID.
    """

    def __init__(self, tilemap, tilesetdata):
        """Tileset class initializer.

        Args:
            tilemap: Link back to the parent Tilemap instance.
            tilesetdata: JSON tileset segment.
        """
        self.tilemap = tilemap

        self.filename = ""
        self.name = ""
        self.image = None
        self.texture = None
        self.width = 0
        self.height = 0
        self.imagewidth = 0
        self.imageheight = 0
        self.tilewidth = 0
        self.tileheight = 0
        self.size = 0
        self.spacing = 0
        self.range = [0, 0]
        self.properties = {}
        self.tileproperties = {}

        # This contains the JSON of the tileset.
        self.__tileset = tilesetdata

        # Prepare the tileset abstractions.
        self.__prepare_tileset()

    def __prepare_tileset(self):
        self.filename = self.__tileset["image"]
        self.name = self.__tileset["name"]
        self.image = self.tilemap.area.driftwood.resource.request_image(self.filename)  # Ouch
        self.texture = self.image.texture
        self.imagewidth = self.__tileset["imagewidth"]
        self.imageheight = self.__tileset["imageheight"]
        self.tilewidth = self.__tileset["tilewidth"]
        self.tileheight = self.__tileset["tileheight"]
        self.width = self.imagewidth // self.tilewidth
        self.height = self.imageheight // self.tileheight
        self.size = int(self.width * self.height)
        self.spacing = self.__tileset["spacing"]
        self.range = [self.__tileset["firstgid"], self.__tileset["firstgid"] - 1 + self.size]
        if "properties" in self.__tileset:
            self.properties = self.__tileset["properties"]
        if "tileproperties" in self.__tileset:
            for key in self.__tileset["tileproperties"].keys():
                self.tileproperties[int(key)] = self.__tileset["tileproperties"][key]

    def _terminate(self):
        """Cleanup before deletion.
        """
        if self.image:
            self.image._terminate()
            self.image = None
        if self.texture:
            SDL_DestroyTexture(self.texture)
            self.texture = None
