################################
# Driftwood 2D Game Dev. Suite #
# tileset.py                   #
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

import os
from typing import Optional, TYPE_CHECKING

from check import CHECK, CheckFailure
import tilemap

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


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

    def __init__(self, driftwood: "Driftwood", tilemap: "tilemap.Tilemap"):
        """Tileset class initializer.

        Args:
            driftwood: Base class instance.
            tilemap: Link back to the parent Tilemap instance.
            source_filename: Filename of the Tiled map file this tileset is from.
        """
        self.driftwood = driftwood
        self.tilemap = tilemap

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

    def load(self, tilemap_filename: str, tileset_json: dict) -> Optional[bool]:
        """Populate a Tileset with data from a Tiled map's tileset object.

        Args:
            tilemap_filename: Filename to say is our filename.
            tileset_json: Tiled tileset JSON object.

        Returns:
            True if everything was successful, False otherwise
        """
        # Input Check
        try:
            CHECK(tilemap_filename, str)
            CHECK(tileset_json, object)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Tileset", "load", "bad argument", e)
            return None

        # Regardless of whether this will be an internal or external tileset, the firstgid is always found here.
        firstgid = tileset_json["firstgid"]

        if "image" in tileset_json:
            # Internal tileset... everything we need is here
            return self.__prepare(tilemap_filename, tileset_json, firstgid)
        else:
            # External tileset... there's a filename with another JSON
            tileset_filename = self.__resolve_path(tilemap_filename, tileset_json["source"])
            external_json = self.driftwood.resource.request_json(tileset_filename)
            if not external_json or not self.__prepare(tileset_filename, external_json, firstgid):
                self.driftwood.log.msg("ERROR", "Tileset", "load_tileset", "could not load tileset", tileset_filename)
                return False
            return True

    def __prepare(self, image_base_path: str, tileset_json: dict, firstgid: int) -> bool:
        """Load values into our tileset."""
        self.name = tileset_json["name"]
        self.imagewidth = tileset_json["imagewidth"]
        self.imageheight = tileset_json["imageheight"]
        self.tilewidth = tileset_json["tilewidth"]
        self.tileheight = tileset_json["tileheight"]
        self.width = self.imagewidth // self.tilewidth
        self.height = self.imageheight // self.tileheight
        self.size = int(self.width * self.height)
        self.spacing = tileset_json["spacing"]
        self.range = [firstgid, firstgid - 1 + self.size]
        if "properties" in tileset_json:
            self.properties = tileset_json["properties"]
        if "tileproperties" in tileset_json:
            for key in tileset_json["tileproperties"].keys():
                self.tileproperties[int(key)] = tileset_json["tileproperties"][key]

        # The image's path is relative to another file. Which file it is depends on if this is an internal or external
        # tileset.
        image_filename = self.__resolve_path(image_base_path, tileset_json["image"])

        self.image = self.driftwood.resource.request_image(image_filename)  # Ouch

        if self.image:
            self.texture = self.image.texture
            return True
        else:
            return False

    @staticmethod
    def __resolve_path(base_filename: str, filename: str) -> str:
        """Determine the location of a file that was defined relative to another"""
        if os.path.dirname(base_filename):
            return os.path.normpath(os.path.dirname(base_filename) + os.path.sep + filename)
        else:
            return filename
