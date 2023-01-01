################################
# Driftwood 2D Game Dev. Suite #
# tilemap.py                   #
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

from typing import TYPE_CHECKING

import areamanager
import layer
import tileset

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class Tilemap:
    """This class reads the Tiled map file for the currently focused area, and presents an abstraction.

    Attributes:
        area: Parent AreaManager instance.

        width: Width of the map in tiles.
        height: Height of the map in tiles.
        tilewidth: Width of tiles in the map.
        tileheight: Height of tiles in the map.
        properties: A dictionary containing map properties.

        layers: The list of Layer class instances for each layer.
        tilesets: The list of Tileset class instances for each tileset.
    """

    def __init__(self, driftwood: "Driftwood", area: "areamanager.AreaManager"):
        """Tilemap class initializer.

        Args:
            driftwood: Base class instance.
            area: Link back to the parent AreaManager instance.
        """
        self.driftwood = driftwood
        self.area = area

        # Attributes which will be updated with information about the map.
        self.width = 0
        self.height = 0
        self.tilewidth = 0
        self.tileheight = 0
        self.properties = {}

        self.layers = []
        self.tilesets = []

        # This contains the JSON of the Tiled map.
        self.__tilemap = {}

    def __contains__(self, item) -> bool:
        if len(self.layers) > item:
            return True
        return False

    def __getitem__(self, item) -> "layer.Layer":
        if len(self.layers) > item:
            return self.layers[item]

    def new_layer(self) -> int:
        """Create a new virtual tile layer.

        Returns:
            Layer z position.
        """
        fakedata = {"data": [0] * (self.width * self.height)}
        self.layers.append(layer.Layer(self.driftwood, self, fakedata, len(self.layers)))
        return self.layers[-1].zpos

    def _read(self, filename: str, data: dict) -> bool:
        """Read and abstract a Tiled map.

        Reads the JSON Tiled map and processes its information into useful abstractions. This method is marked private
        even though it's called from AreaManager, because it must only be called once per area focus.

        Args:
            filename: Filename of the Tiled map file.
            data: JSON contents of the Tiled map.

        Returns:
            True if succeeded, False if failed.
        """
        # Reset variables left over from the last map.
        if self.layers:
            for l in self.layers:
                l.clear()
            self.layers = []
        if self.tilesets:
            self.tilesets = []
        self.driftwood.light.reset()

        # Load the JSON data.
        self.__tilemap = data

        # Set class attributes representing information about the map.
        self.width = self.__tilemap["width"]
        self.height = self.__tilemap["height"]
        self.tilewidth = self.__tilemap["tilewidth"]
        self.tileheight = self.__tilemap["tileheight"]
        if "properties" in self.__tilemap:
            self.properties = self.__tilemap["properties"]
        else:
            self.properties = {}

        self.__expand_properties()

        # Call world's global on_enter handlers.
        self.driftwood.script._call_global_triggers("on_enter")

        # Call the on_enter event if set.
        if "on_enter" in self.properties:
            self.driftwood.script.call(*self.properties["on_enter"].split(","))

        # Set the window title.
        if "title" in self.properties:
            self.driftwood.window.title(self.properties["title"])

        # Build the tileset abstractions.
        for tileset_json in self.__tilemap["tilesets"]:
            if tileset_json["tilewidth"] != self.tilewidth or tileset_json["tileheight"] != self.tileheight:
                # Tilemaps and tilesets must have the equal tile widths and heights.
                return False

            ts = tileset.Tileset(self.driftwood, self)
            if not ts.load(filename, tileset_json):
                return False  # There is no way we can continue without our tilesets.
            self.tilesets.append(ts)

        # Global object layer.
        gobjlayer = {}

        # Build the tile and layer abstractions.
        for zpos, l in enumerate(self.__tilemap["layers"]):
            # This layer is marked invisible, skip it.
            if not l["visible"]:
                continue

            # This is a tile layer.
            if l["type"] == "tilelayer":
                self.layers.append(layer.Layer(self.driftwood, self, l, zpos))

            # This is an object layer.
            elif l["type"] == "objectgroup":
                # If this is the very first layer, it's the global object layer.
                if not self.layers:
                    gobjlayer = l
                else:
                    self.layers[-1]._process_objects(l)

        # Merge the global object layer into all tile layers.
        if gobjlayer:
            for l in self.layers:
                l._process_objects(gobjlayer)

        return True

    def __expand_properties(self) -> None:
        new_props = {}
        old_props = []

        # Expand user-defined trigger shortcuts
        for property_name in self.properties:
            if self.driftwood.script.is_custom_trigger(property_name):
                property = self.properties[property_name]
                event, trigger = self.driftwood.script.lookup(property_name, property)
                new_props[event] = trigger
                old_props.append(property_name)

        for event in new_props:
            self.properties[event] = new_props[event]
        for prop in old_props:
            del self.properties[prop]

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        for t in range(len(self.tilesets)):
            self.tilesets[t]._terminate()
        self.tilesets = []
