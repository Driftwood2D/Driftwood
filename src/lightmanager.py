####################################
# Driftwood 2D Game Dev. Suite     #
# lightmanager.py                  #
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

import filetype
import light


class LightManager:
    """The Light Manager

    This class manages lights in the current area.

    Attributes:
        driftwood: Base class instance.

        lights: The list of Light class instances for each light. Stored by lid.
    """

    def __init__(self, driftwood):
        """LightManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.lights = {}

        self.__last_lid = -1

    def __contains__(self, lid):
        if self.light(lid):
            return True
        return False

    def __getitem__(self, lid):
        return self.light(lid)

    def __delitem__(self, lid):
        return self.kill(lid)

    def __iter__(self):
        return self.lights.items()

    def insert(self, filename, layer, x, y, w, h, color="FFFFFFFF", blend=False, entity=None, layermod=0):
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

        Returns: New light if succeeded, None if failed.
        """

        lightmap = self.driftwood.resource.request_image(filename, False)
        if not lightmap:
            self.driftwood.log.msg("ERROR", "Light", "insert", "could not load lightmap", lightmap)
            return None

        try:
            int(color, 16)
        except ValueError:
            self.driftwood.log.msg("ERROR", "Light", "insert", "invalid color", color)
            return None

        if entity is not None:
            if not self.driftwood.entity.entity(entity):
                self.driftwood.log.msg("ERROR", "Light", "insert", "cannot bind to nonexistent entity", entity)
                return None

        self.__last_lid += 1
        lid = self.__last_lid

        self.lights[lid] = light.Light(self, lid, lightmap, layer, x, y, w, h, color, blend, entity, layermod)

        if blend:
            r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_BLEND)
        else:
            r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_ADD)
        if r < 0:
            self.driftwood.log.msg("ERROR", "Light", "insert", "SDL", SDL_GetError())

        r = SDL_SetTextureColorMod(self.lights[lid].lightmap.texture, int(color[0:2], 16), int(color[2:4], 16),
                                   int(color[4:6], 16))
        if r < 0:
            self.driftwood.log.msg("ERROR", "Light", "insert", "SDL", SDL_GetError())

        r = SDL_SetTextureAlphaMod(self.lights[lid].lightmap.texture, int(color[6:8], 16))
        if r < 0:
            self.driftwood.log.msg("ERROR", "Light", "insert", "SDL", SDL_GetError())

        self.driftwood.log.info("Light", "inserted", "{0} on layer {1} at position {2}, {3}".format(filename, layer,
                                                                                                    x, y))

        self.driftwood.area.changed = True

        return self.lights[lid]

    def light(self, lid):
        """Retrieve a light by lid.

        Args:
            lid: The Light ID of the light to retrieve.

        Returns: Light class instance if succeeded, None if failed.
        """
        if lid in self.lights:
            return self.lights[lid]
        return None

    def light_at(self, x, y):
        """Retrieve a light by pixel coordinate.

        Args:
            x: The x coordinate of the light.
            y: The y coordinate of the light.

        Returns: Light class instance if succeeded, None if failed.
        """
        for lid in self.lights:
            if self.lights[lid].x == x and self.lights[lid].y == y:
                return self.lights[lid]
        return None

    def layer(self, l):
        """Retrieve a list of lights on the specified layer.

        Args:
            l: The layer from which to list lights.

        Returns: Tuple of Light class instances.
        """
        lights = []

        for lid in self.lights:
            if self.lights[lid].layer == l:
                lights.append(self.lights[lid])

        return lights

    def entity(self, eid):
        """Retrieve a light by the entity it is bound to.

        Args:
            eid: The Entity ID of the entity to check for bound light.

        Returns: Light class instance if succeeded, None if failed.
        """
        for lid in self.lights:
            if self.lights[lid].entity == eid:
                return self.lights[lid]
        return None

    def set_color(self, lid, color, blend=None):
        """Update the color, alpha, and blending of an existing light.

        Args:
            lid: The Light ID of the light to update.
            color: Hexadecimal color and alpha value of the light. "RRGGBBAA"
            blend: If set, whether to blend light instead of adding it. Otherwise keep old value.

        Returns: True if succeeded, False if failed.
        """
        try:
            int(color, 16)
        except ValueError:
            self.driftwood.log.msg("ERROR", "Light", "set_color", "invalid color", color)
            return False

        if lid in self.lights:
            success = True

            r = SDL_SetTextureColorMod(self.lights[lid].lightmap.texture, int(color[0:2], 16), int(color[2:4], 16),
                                       int(color[4:6], 16))
            if r < 0:
                self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                success = False

            r = SDL_SetTextureAlphaMod(self.lights[lid].lightmap.texture, int(color[6:8], 16))
            if r < 0:
                self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                success = False

            if blend is not None:
                if blend:
                    r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_BLEND)
                else:
                    r = SDL_SetTextureBlendMode(self.lights[lid].lightmap.texture, SDL_BLENDMODE_ADD)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Light", "set_color", "SDL", SDL_GetError())
                    success = False

            self.driftwood.area.changed = True

            if success:
                return True

        return False

    def kill(self, lid):
        """Kill a light by lid.

        Args:
            lid: The Light ID of the light to kill.

        Returns:
            True if succeeded, False if failed.
        """
        if lid in self.lights:
            self.lights[lid]._terminate()
            del self.lights[lid]
            self.driftwood.area.changed = True
            return True

        self.driftwood.log.msg("WARNING", "Light", "kill", "attempt to kill nonexistent light", lid)
        return False

    def killall(self, file):
        """Kill all lights by filename or lightmap.

        Args:
            file: Filename of the JSON light descriptor whose insertions should be killed, or ImageFile of the lightmap.

        Returns:
            True if succeeded, False if failed.
        """
        to_kill = []

        if isinstance(file, filetype.ImageFile):
            for lid in self.lights:
                if self.lights[lid].lightmap == file:
                    to_kill += lid

        else:
            for lid in self.lights:
                if self.lights[lid].filename == file:
                    to_kill += lid

        for lid in to_kill:
            self.lights[lid]._terminate()
            del self.lights[lid]

        self.driftwood.area.changed = True

        if to_kill:
            return True
        self.driftwood.log.msg("WARNING", "Entity", "killall", "attempt to kill nonexistent lights", file)
        return False

    def reset(self):
        """Reset the lights.

        Returns: True
        """
        for light in self.lights:
            self.lights[light]._terminate()
        self.lights = {}
        self.driftwood.area.changed = True
        self.driftwood.log.info("Light", "reset")
        return True

    def _terminate(self):
        """Cleanup before deletion.
        """
        for light in self.lights:
            self.lights[light]._terminate()
        self.lights = {}
