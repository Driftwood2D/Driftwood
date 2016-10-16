####################################
# Driftwood 2D Game Dev. Suite     #
# lightmanager.py                  #
# Copyright 2016 Michael D. Reiley #
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

import jsonschema
import sys
import traceback

import filetype
import light


class LightManager:
    """The Light Manager

    This class manages lights in the current area.

    Attributes:
        driftwood: Base class instance.

        lights: The list of Light class instances for each light. Stored by lid.
        area_lighting: Whole-area lighting effects. {intensity, color}
    """

    def __init__(self, driftwood):
        """LightManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.lights = {}

        self.area_lighting = None

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

    def insert(self, filename, layer, x, y, entity=None):
        """Insert a light at a position in the area.

        Args:
            filename: Filename of the JSON light descriptor.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.

        Returns: New light if succeeded, None if failed.
        """
        data = self.driftwood.resource.request_json(filename)
        schema = self.driftwood.resource.request_json("schema/light.json")

        self.__last_lid += 1
        lid = self.__last_lid

        # Attempt to validate against the schema.
        try:
            jsonschema.validate(data, schema)
        except (jsonschema.ValidationError):
            self.driftwood.log.msg("ERROR", "Light", filename, "failed validation")
            traceback.print_exc(1, sys.stdout)
            sys.stdout.flush()
            return None

        lightmap = self.driftwood.resource.request_image(filename)

        self.lights[lid] = light.Light(self, lid, lightmap, layer, x, y, data["width"], data["height"],
                                       data["intensity"], data["color"], data["soft"], entity)

        self.driftwood.area.changed = True

        return self.lights[lid]

    def new(self, lightmap, layer, x, y, w, h, intensity, color="FFFFFF", soft=True, entity=None):
        """Create and place a new light manually.

        Args:
            lightmap: ImageFile instance of the lightmap.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.
            w: Width of the light.
            h: Height of the light.
            intensity: Brightness of the light, in percentage.
            color: Hexadeximal color value of the light.
            soft: Whether to soften on zoom. Otherwise pixelates.
            entity: If set, eid of entity to track the light to. Disabled if None.

        Returns: New light if succeeded, None if failed.
        """
        self.__last_lid += 1
        lid = self.__last_lid

        self.lights[lid] = light.Light(self, lid, lightmap, layer, x, y, w, h, intensity, color, soft, entity)

        self.driftwood.area.changed = True

        return self.lights[lid]

    def area(self, intensity, color="FFFFFF"):
        """Set the area lighting.

        Args:
            intensity: Brightness of the light, in percentage.
            color: Hexadeximal color value of the light.

        Returns:
            True if succeeded, False if invalid.
        """
        if not type(intensity) is float and type(color) is str:
            self.driftwood.log.msg("ERROR", "Light", "invalid area lighting")
            return False
        self.area_lighting = {"intensity": intensity, "color": color}
        self.driftwood.area.changed = True
        return True

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

    def kill(self, lid):
        """Kill a light by lid.

        Args:
            lid: The Light ID of the light to kill.

        Returns:
            True if succeeded, False if failed.
        """
        if lid in self.lights:
            del self.lights[lid]
            self.driftwood.area.changed = True
            return True

        self.driftwood.log.msg("WARNING", "Light", "attempt to kill nonexistent light", lid)
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
            del self.lights[lid]

        self.driftwood.area.changed = True

        if to_kill:
            return True
        self.driftwood.log.msg("WARNING", "Entity", "attempt to kill nonexistent lights", file)
        return False

    def reset(self):
        """Reset the lights.

        Returns: True
        """
        self.lights = {}
        self.area_lighting = None
        self.driftwood.area.changed = True
        return True