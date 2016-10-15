####################################
# Driftwood 2D Game Dev. Suite     #
# entitymanager.py                 #
# Copyright 2014 PariahSoft LLC    #
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

import entity
from inputmanager import InputManager


class EntityManager:
    """The Entity Manager

    This class manages entities in the current area, as well as the persistent player entity.

    Attributes:
        driftwood: Base class instance.

        player: The player entity.
        collider: The collision callback. The callback must take as arguments the two entities that collided.

        entities: The list of Entity class instances for each entity.
        spritesheets: The list of Spritesheet class instances for each sprite sheet.
    """

    def __init__(self, driftwood):
        """EntityManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.player = None
        self.collider = None

        self.entities = {}

        self.spritesheets = {}

        self.__last_eid = -1

    def insert(self, filename, layer, x, y):
        """Insert an entity at a position in the area.

        Args:
            filename: Filename of the JSON entity descriptor.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.

        Returns: New entity if succeeded, None if failed.
        """
        data = self.driftwood.resource.request_json(filename)
        schema = self.driftwood.resource.request_json("schema/entity.json")

        self.__last_eid += 1
        eid = self.__last_eid

        # Attempt to validate against the schema.
        try:
            jsonschema.validate(data, schema)
        except (jsonschema.ValidationError):
            self.driftwood.log.msg("ERROR", "Entity", filename, "failed validation")
            traceback.print_exc(1, sys.stdout)
            sys.stdout.flush()
            return None

        # Set movement mode.
        if data["init"]["mode"] == "tile":
            self.entities[eid] = entity.TileModeEntity(self)
        elif data["init"]["mode"] == "pixel":
            self.entities[eid] += entity.PixelModeEntity(self)

        # Read the entity.
        self.entities[eid]._read(filename, data, eid)

        # Set the initial position.
        self.entities[eid].x = x
        self.entities[eid].y = y
        self.entities[eid].layer = layer

        # Are we on a tile?
        if (x % self.driftwood.area.tilemap.tilewidth == 0) and (y % self.driftwood.area.tilemap.tileheight == 0):
            self.entities[eid].tile = self.driftwood.area.tilemap.layers[layer].tile(
                x / self.driftwood.area.tilemap.tilewidth,
                y / self.driftwood.area.tilemap.tileheight
            )
        else:
            self.driftwood.log.msg("ERROR", "Entity", filename, "must start on a tile")
            return None

        self.driftwood.area.changed = True

        self.driftwood.log.info("Entity", "inserted", "{0} on layer {1} at position {2}, {3}".format(filename,
                                                                                                            layer,
                                                                                                            x, y))

        # Function to call when inserting the entity.
        if data["init"]["on_insert"]:
            args = data["init"]["on_insert"].split(',')
            self.driftwood.script.call(args[0], args[1], self.entities[eid])

        # Function to call before killing the entity.
        if data["init"]["on_kill"]:
            self.entities[eid]._on_kill = data["init"]["on_kill"].split(',')

        return self.entities[eid]

    def entity(self, eid):
        """Retrieve an entity by eid.

        Args:
            eid: The Entity ID of the entity to retrieve.

        Returns: Entity class instance if succeeded, None if failed.
        """
        for ent in self.entities:
            if ent.eid == eid:
                return ent

        return None

    def entity_at(self, x, y):
        """Retrieve an entity by pixel coordinate.

        Args:
            x: The x coordinate of the tile.
            y: The y coordinate of the tile.

        Returns: Entity class instance if succeeded, None if failed.
        """
        for eid in self.entities:
            if self.entities[eid].x == x and self.entities[eid].y == y:
                return self.entities[eid]
        return None

    def layer(self, layer):
        """Retrieve a list of entities on a certain layer.

        Args:
            layer: Layer to find entities on.

        Returns: Tuple of Entity class instances.
        """
        ents = []

        for eid in self.entities:
            if self.entities[eid].layer == layer:
                ents.append(self.entities[eid])

        return tuple(ents)

    def kill(self, eid):
        """Kill an entity by eid.

        Args:
            eid: The Entity ID of the entity to kill.

        Returns:
            True if succeeded, False if failed.
        """
        if eid in self.entities:
            if self.entities[eid]._on_kill: # Call a function before killing the entity.
                self.driftwood.script.call(self.entities[eid]._on_kill[0], self.entities[eid]._on_kill[1],
                                           self.entities[eid])
            del self.entities[eid]
            self.driftwood.area.changed = True
            return True

        self.driftwood.log.msg("WARNING", "Entity", "attempt to kill nonexistent entity", eid)
        return False

    def killall(self, filename):
        """Kill all entities by filename.

        Args:
            filename: Filename of the JSON entity descriptor whose insertions should be killed.

        Returns:
            True if succeeded, False if failed.
        """
        to_kill = []

        for eid in self.entities:
            if self.entities[eid].filename == filename:
                to_kill += eid

        for eid in to_kill:
            if self.entities[eid]._on_kill: # Call a function before killing the entity.
                self.driftwood.script.call(self.entities[eid]._on_kill[0], self.entities[eid]._on_kill[1],
                                           self.entities[eid])
            del self.entities[eid]

        self.driftwood.area.changed = True

        if to_kill:
            return True
        self.driftwood.log.msg("WARNING", "Entity", "attempt to kill nonexistent entities", filename)
        return False

    def spritesheet(self, filename):
        """Retrieve a sprite sheet by its filename.

        Args:
            filename: Filename of the sprite sheet image.

        Returns: Spritesheet class instance if succeeded, False if failed.
        """
        for ss in self.spritesheets:
            if self.spritesheets[ss].filename == filename:
                return self.spritesheets[ss]

        return False

    def collision(self, a, b):
        """Notify the collision callback, if set, that entity "a" has collided with entity or tile "b".

        Args:
            a: First colliding entity.
            b: Second colliding entity or tile.


        """
        if self.collider:
            self.collider(a, b)

        return True
