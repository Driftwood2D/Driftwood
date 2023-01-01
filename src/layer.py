################################
# Driftwood 2D Game Dev. Suite #
# layer.py                     #
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

from typing import Dict, Optional, TYPE_CHECKING

from check import CHECK, CheckFailure
import tile
import tilemap

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class Layer:
    """This class abstracts a layer.

    Attributes:
        tilemap: Parent Tilemap instance.

        properties: A dictionary containing layer properties.

        tiles: The list of Tile class instances for each tile.
    """

    def __init__(self, driftwood: "Driftwood", tilemap: "tilemap.Tilemap", layerdata: dict, zpos: int):
        """Layer class initializer.

        Args:
            driftwood: Base class instance.
            tilemap: Link back to the parent Tilemap instance.
            layerdata: JSON layer segment.
            zpos: Layer's z-position.
        """
        self.driftwood = driftwood
        self.tilemap = tilemap

        self.zpos = zpos
        self.properties = {}

        self.tiles = _TileLoader(driftwood, self)

        # This contains the JSON of the layer.
        self._layer = layerdata

        self.__prepare_layer()

    def __getitem__(self, item: int) -> "_AbstractColumn":
        return _AbstractColumn(self, item)

    def clear(self) -> None:
        for tile in self.tiles:
            self.tiles[tile].unregister()

    def tile(self, x: int, y: int) -> Optional["tile.Tile"]:
        """Retrieve a tile from the layer by its coordinates.

        Args:
            x: x-coordinate
            y: y-coordinate

        Returns: Tile instance or None if out of bounds.
        """
        # Input Check
        try:
            CHECK(x, int)
            CHECK(y, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Layer", self.zpos, "tile", "bad argument", e)
            return None

        if x < 0 or y < 0 or x >= self.tilemap.width or y >= self.tilemap.height:
            return None

        if int((y * self.tilemap.width) + x) < len(self.tiles):
            return self.tiles[int((y * self.tilemap.width) + x)]

        else:
            self.driftwood.log.msg(
                "WARNING", "Layer", self.zpos, "tile", "tried to lookup nonexistent tile at", "{0}x{1}".format(x, y)
            )
            return None

    def tile_index(self, x: int, y: int) -> Optional[int]:
        """Retrieve the index of a tile in the tiles list so you can modify it.

        Args:
            x: x-coordinate
            y: y-coordinate

        Returns: index of tile in tiles list if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(x, int)
            CHECK(y, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Layer", self.zpos, "tile_index", "bad argument", e)
            return None

        if int((y * self.tilemap.width) + x) < len(self.tiles):
            return int((y * self.tilemap.width) + x)

        else:
            self.driftwood.log.msg(
                "WARNING",
                "Layer",
                self.zpos,
                "tile_index",
                "tried to lookup nonexistent tile at",
                "{0}x{1}".format(x, y),
            )
            return None

    def _process_objects(self, objdata: dict) -> None:
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
            if (
                obj["x"] % self.tilemap.tilewidth
                or obj["y"] % self.tilemap.tileheight
                or obj["width"] % self.tilemap.tilewidth
                or obj["height"] % self.tilemap.tileheight
            ):
                self.driftwood.log.msg(
                    "ERROR", "Layer", self.zpos, "_process_objects", "invalid object size or placement"
                )
                continue

            # Map object properties onto their tiles.
            for x in range(0, obj["width"] // self.tilemap.tilewidth):
                for y in range(0, obj["height"] // self.tilemap.tileheight):
                    tx = obj["x"] // self.tilemap.tilewidth + x
                    ty = obj["y"] // self.tilemap.tileheight + y

                    # Insert the object properties.
                    if "properties" in obj:
                        self.__expand_properties(obj["properties"])
                        self.tile(tx, ty).properties.update(obj["properties"])

                    # Set nowalk if present.
                    if "nowalk" in self.tile(tx, ty).properties:
                        self.tile(tx, ty).nowalk = self.tile(tx, ty).properties["nowalk"]

                    # Set exit if present.
                    for exittype in ["exit", "exit:up", "exit:down", "exit:left", "exit:right"]:
                        if exittype in self.tile(tx, ty).properties:

                            # First check for and handle wide exits.
                            exit_coords = self.tile(tx, ty).properties[exittype].split(",")
                            if len(exit_coords) != 4:
                                self.driftwood.log.msg(
                                    "ERROR",
                                    "Layer",
                                    self.zpos,
                                    "_process_objects",
                                    "invalid exit trigger",
                                    self.tile(tx, ty).properties[exittype],
                                )
                                continue

                            if (exit_coords[2] and exit_coords[2][-1] == "+") and (
                                exit_coords[3] and exit_coords[3][-1] == "+"
                            ):  # Invalid wide exit.
                                self.driftwood.log.msg(
                                    "ERROR", "Layer", "_process_objects", "cannot have multi-directional wide exits"
                                )

                            # Check for and handle horizontal wide exit.
                            elif exit_coords[2] and exit_coords[2][-1] == "+":
                                base_coord = int(exit_coords[2][:1])  # Chop off the plus sign.
                                if tx % self.tilemap.width == base_coord:  # This is the first position.
                                    for wx in range(0, (obj["width"] // self.tilemap.tilewidth)):  # Set exits.
                                        final_coords = exit_coords
                                        final_coords[2] = str(base_coord + wx)
                                        self.tile(tx + wx, ty).exits[exittype] = ",".join(final_coords)
                                else:  # This is not the first position, skip.
                                    continue

                            # Check for and handle vertical wide exit.
                            elif exit_coords[3] and exit_coords[3][-1] == "+":
                                base_coord = int(exit_coords[3][:1])  # Chop off the plus sign.
                                if ty == base_coord:  # This is the first position.
                                    for wy in range(0, (obj["height"] // self.tilemap.tileheight)):  # Set exits.
                                        final_coords = exit_coords
                                        final_coords[3] = str(base_coord + wy)
                                        self.tile(tx, ty + wy).exits[exittype] = ",".join(final_coords)
                                else:  # This is not the first position, skip.
                                    continue

                            else:  # Just a regular exit.
                                self.tile(tx, ty).exits[exittype] = self.tile(tx, ty).properties[exittype]

                    # Handle entity auto-spawn triggers.
                    if "entity" in self.tile(tx, ty).properties:
                        self.driftwood.area._autospawns.append(
                            [self.tile(tx, ty).properties["entity"], self.zpos, tx, ty]
                        )

    def __expand_properties(self, properties: Dict[str, str]) -> None:
        new_props = {}
        old_props = []

        # Expand user-defined trigger shortcuts
        for property_name in properties:
            if self.driftwood.script.is_custom_trigger(property_name):
                property = properties[property_name]
                event, trigger = self.driftwood.script.lookup(property_name, property)
                new_props[event] = trigger
                old_props.append(property_name)

        for event in new_props:
            properties[event] = new_props[event]
        for prop in old_props:
            del properties[prop]

    def __prepare_layer(self) -> None:
        # Set layer properties if present.
        if "properties" in self._layer:
            self.properties = self._layer["properties"]

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        for tile in self.tiles:
            self.tiles[tile]._terminate()
        self.tiles = []


class _AbstractColumn:
    def __init__(self, layer: Layer, x: int):
        self._layer = layer
        self.__x = x

    def __getitem__(self, item: int) -> Optional["tile.Tile"]:
        return self._layer.tile(self.__x, item)


class _TileLoader:
    """Tile Loader

    Implements lazy map loading by reading and caching each individual tile as needed. This class pretends to be a
    list.
    """

    def __init__(self, driftwood, layer):
        self.driftwood = driftwood
        self.__tiles = {}
        self.__layer = layer

    def __getitem__(self, item: int) -> Optional["tile.Tile"]:
        # Returns a tile by its sequence number.
        return self.__get(item)

    def __len__(self) -> int:
        # Returns the total size in tiles of the tilemap.
        return self.__layer.tilemap.width * self.__layer.tilemap.height

    def __iter__(self):
        # Allow us to be iterated like a list. This will necessarily load all tiles and is not recommended.
        for seq in range(self.__len__()):
            return self.__get(seq)

    def __get(self, seq: int) -> Optional["tile.Tile"]:
        # Get a tile by its sequence number, loading if not loaded.
        if seq in self.__tiles:
            # Already loaded. Return the cached tile.
            return self.__tiles[seq]

        else:
            # Iterate through the tile graphic IDs.
            layer = self.__layer
            gid = layer._layer["data"][seq]
            range_inclusive = lambda start, end: range(start, end + 1)

            # Does this tile actually exist?
            if gid:
                # Find which tileset the tile's graphic is in.
                for ts in layer.tilemap.tilesets:
                    if gid in range_inclusive(*ts.range):
                        # Create the Tile instance for this tile.
                        self.__tiles[seq] = tile.Tile(layer, seq, ts, gid)
                        break  # Stop searching.

                if not seq in self.__tiles:
                    # We found nothing. Set nothing.
                    self.driftwood.log.msg(
                        "WARNING", "Layer", layer.zpos, "_TileLoader", "Orphan gid", gid, "for tile", seq
                    )
                    self.__tiles[seq] = tile.Tile(layer, seq, None, None)

            # No tile, here create a dummy tile.
            else:
                self.__tiles[seq] = tile.Tile(layer, seq, None, None)

            return self.__tiles[seq]
