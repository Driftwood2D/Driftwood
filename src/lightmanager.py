################################
# Driftwood 2D Game Dev. Suite #
# lightmanager.py              #
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

from typing import ItemsView, List, Optional, TYPE_CHECKING

from sdl2 import *

from check import CHECK, CheckFailure
import entity
import filetype
import light

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


# Keep a reference to the light module, which is overridden by the LightManager.light function later in the file.
# It is only overridden while inside type annotations.
_light = light


class LightManager:
    """The Light Manager

    This class manages lights in the current area.

    Attributes:
        driftwood: Base class instance.

        lights: The dictionary of Light class instances for each light. Stored by lid.
    """

    def __init__(self, driftwood: "Driftwood"):
        """LightManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.lights = {}

        self.__last_lid = -1

        self.__area_light_layer = [None, None]

    def __contains__(self, lid: int) -> bool:
        if self.light(lid):
            return True
        return False

    def __getitem__(self, lid) -> Optional[light.Light]:
        return self.light(lid)

    def __delitem__(self, lid) -> bool:
        return self.kill(lid)

    def __iter__(self) -> ItemsView:
        return self.lights.items()

    def insert(
        self,
        filename: str,
        layer: int,
        x: int,
        y: int,
        w: int,
        h: int,
        color: str = "FFFFFFFF",
        blend: bool = False,
        entity: entity.Entity = None,
        layermod=0,
    ) -> Optional[int]:
        """Create and insert a new light into the area.

        Args:
            filename: Filename of the lightmap.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.
            w: Width of the light.
            h: Height of the light.
            color: Hexadeximal color and alpha value of the light. "RRGGBBAA"
            blend: Whether to blend light instead of adding it. Useful for dark lights.
            entity: If set, eid of entity to track the light to. Disabled if None.
            layermod: Integer to add to the layer the light is drawn on when tracking an entity.

        Returns: Light ID of new light if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(layer, int, _min=0)
            CHECK(x, int)
            CHECK(y, int)
            CHECK(color, str, _equals=8)
            CHECK(blend, bool)
            if entity is not None:
                CHECK(entity, int, _min=0)
            CHECK(layermod, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "insert", "bad argument", e)
            return None

        # Try to request the lightmap image from the resource manager.
        lightmap = self.driftwood.resource.request_image(filename)
        if not lightmap:
            self.driftwood.log.msg("ERROR", "Light", "insert", "could not load lightmap", lightmap)
            return None

        # Is the color a real color?
        try:
            int(color, 16)
        except ValueError:
            self.driftwood.log.msg("ERROR", "Light", "insert", "invalid color", color)
            return None

        # Does the entity exist if we passed one to track?
        if entity is not None:
            if not self.driftwood.entity.entity(entity):
                self.driftwood.log.msg("ERROR", "Light", "insert", "cannot bind to nonexistent entity", entity)
                return None

        # Add our light to the dictionary and increment the light id count.
        self.__last_lid += 1
        lid = self.__last_lid

        # Give the light transparency.
        alpha = int(color[6:8], 16)

        # Are we blending the light?
        blendmode = SDL_BLENDMODE_ADD
        if blend:
            blendmode = SDL_BLENDMODE_BLEND

        # Give the light color.
        colormod = (int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))

        # Assign the light to its light id in the dictionary.
        self.lights[lid] = light.Light(
            self, lid, lightmap, layer, x, y, w, h, alpha, blendmode, colormod, entity, layermod
        )

        # We are done.
        self.driftwood.log.info(
            "Light", "inserted", "{0} on layer {1} at position {2}px, {3}px".format(filename, layer, x, y)
        )
        # The area has changed because we added a light.
        self.driftwood.area.changed = True

        return lid

    def light(self, lid: int) -> Optional[light.Light]:
        """Retrieve a light by lid.

        Args:
            lid: The Light ID of the light to retrieve.

        Returns: Light class instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(lid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "light", "bad argument", e)
            return None

        if lid in self.lights:
            return self.lights[lid]
        return None

    def light_at(self, x: int, y: int) -> Optional[_light.Light]:
        """Retrieve a light by pixel coordinate.

        Args:
            x: The x coordinate of the light.
            y: The y coordinate of the light.

        Returns: Light class instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(x, int)
            CHECK(y, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "light_at", "bad argument", e)
            return None

        for lid in self.lights:
            if self.lights[lid].x == x and self.lights[lid].y == y:
                return self.lights[lid]
        return None

    def layer(self, l: int) -> Optional[List[_light.Light]]:
        """Retrieve a list of lights on the specified layer.

        Args:
            l: The layer from which to list lights.

        Returns: Tuple of Light class instances if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(l, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "layer", "bad argument", e)
            return None

        lights = []

        for lid in self.lights:
            if self.lights[lid].layer == l:
                lights.append(self.lights[lid])

        return lights

    def entity(self, eid: int) -> Optional[_light.Light]:
        """Retrieve a light by the entity it is bound to.

        Args:
            eid: The Entity ID of the entity to check for bound light.

        Returns: Light class instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(eid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "entity", "bad argument", e)
            return None

        for lid in self.lights:
            if self.lights[lid].entity == eid:
                return self.lights[lid]
        return None

    def set_color(self, lid: int, color: str, blend: bool = None) -> bool:
        """Update the color, alpha, and blending of an existing light.

        Args:
            lid: The Light ID of the light to update.
            color: Hexadecimal color and alpha value of the light. "RRGGBBAA"
            blend: If set, whether to blend light instead of adding it. Otherwise keep old value.

        Returns: True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(lid, int, _min=0)
            CHECK(color, str, _equals=8)
            if blend is not None:
                CHECK(blend, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "set_color", "bad argument", e)
            return False

        # Is it a real color?
        try:
            int(color, 16)
        except ValueError:
            self.driftwood.log.msg("ERROR", "Light", "set_color", "invalid color", color)
            return False

        # If the light exists, work on it.
        if lid in self.lights:
            success = True

            # Set the color.
            r = SDL_SetTextureColorMod(
                self.lights[lid].lightmap.texture, int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            )
            if r < 0:
                self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                success = False

            # Set the alpha.
            r = SDL_SetTextureAlphaMod(self.lights[lid].lightmap.texture, int(color[6:8], 16))
            if r < 0:
                self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                success = False

            # Are we going to blend the light?
            if blend is not None:
                if blend:
                    r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_BLEND)
                else:
                    r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_ADD)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                    success = False

            # The area has changed because we changed the light.
            self.driftwood.area.changed = True

            if success:
                return True

        return False

    def area(self, filename, color="FFFFFFFF", blend=False):
        """Convenience function to apply a lightmap over an entire area.

        Be aware that this will create a new layer the first time it's run on an area.
        It will do so again if the area has been unfocused and refocused and its number of layers has changed back.

        Args:
            filename: Filename of the lightmap.
            color: Hexadeximal color and alpha value of the light. "RRGGBBAA"
            blend: Whether to blend light instead of adding it. Useful for dark lights.

        Returns:
            New light if succeeded, None if failed.
        """
        layer = len(self.driftwood.area.tilemap.layers) - 1
        if self.__area_light_layer[0] != self.driftwood.area.filename or self.__area_light_layer[1] != layer:
            self.driftwood.area.tilemap.new_layer()
            layer = len(self.driftwood.area.tilemap.layers) - 1
            self.__area_light_layer = [self.driftwood.area.filename, layer]

        areasize = [
            self.driftwood.area.tilemap.width * self.driftwood.area.tilemap.tilewidth,
            self.driftwood.area.tilemap.height * self.driftwood.area.tilemap.tileheight,
        ]
        insertpos = [areasize[0] // 2, areasize[1] // 2]

        return self.driftwood.light.insert(
            filename, layer, insertpos[0], insertpos[1], areasize[0], areasize[1], color=color, blend=blend
        )

    def kill(self, lid: int) -> bool:
        """Kill a light by lid.

        Args:
            lid: The Light ID of the light to kill.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(lid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "kill", "bad argument", e)
            return False

        if lid in self.lights:
            del self.lights[lid]
            self.driftwood.area.changed = True
            return True

        self.driftwood.log.msg("WARNING", "Light", "kill", "attempt to kill nonexistent light", lid)
        return False

    def killall(self, file: str) -> bool:
        """Kill all lights by filename or lightmap.

        Args:
            file: Filename of the JSON light descriptor whose insertions should be killed, or ImageFile of the lightmap.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(file, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Light", "killall", "bad argument", e)
            return False

        to_kill = []

        # Collect a list of lights to kill, searching by lightmap ImageFile.
        if isinstance(file, filetype.ImageFile):
            for lid in self.lights:
                if self.lights[lid].lightmap == file:
                    to_kill += lid

        # Collect a list of lights to kill, searching by lightmap filename.
        else:
            for lid in self.lights:
                if self.lights[lid].filename == file:
                    to_kill += lid

        # Kill the lights in the list.
        for lid in to_kill:
            del self.lights[lid]

        self.driftwood.area.changed = True

        # Did we succeed?
        if to_kill:
            return True
        self.driftwood.log.msg("WARNING", "Light", "killall", "attempt to kill nonexistent lights", file)
        return False

    def reset(self) -> bool:
        """Reset the lights.

        Returns: True
        """
        self.lights = {}
        self.driftwood.area.changed = True
        self.driftwood.log.info("Light", "reset")
        return True
