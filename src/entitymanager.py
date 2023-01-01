################################
# Driftwood 2D Game Dev. Suite #
# entitymanager.py             #
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

import sys
import traceback
from typing import ItemsView, List, Optional, TYPE_CHECKING

import jsonschema

from check import CHECK, CheckFailure
import entity
import spritesheet
from __schema__ import _SCHEMA

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


# Keep a reference to the entity module, which is overridden by the EntityManager.entity function later in the file.
# It is only overridden while inside type annotations.
_entity = entity


class EntityManager:
    """The Entity Manager

    This class manages entities in the current area, as well as the persistent player entity.

    Attributes:
        driftwood: Base class instance.

        player: The player entity.
        collider: The collision callback. The callback must take as arguments the two entities that collided.

        entities: The dictionary of Entity class instances for each entity. Stored by eid.
        spritesheets: The dictionary of Spritesheet class instances for each sprite sheet. Sorted by filename.
    """

    def __init__(self, driftwood: "Driftwood"):
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

    def __contains__(self, eid: int) -> bool:
        if self.entity(eid):
            return True
        return False

    def __getitem__(self, eid: int) -> Optional[entity.Entity]:
        return self.entity(eid)

    def __delitem__(self, eid: int) -> bool:
        return self.kill(eid)

    def __iter__(self) -> ItemsView:
        return self.entities.items()

    def insert(self, filename: str, layer: int, x: int, y: int, template_vars: dict = {}) -> Optional[entity.Entity]:
        """Insert an entity at a position in the area. Supports Jinja2.

        Args:
            filename: Filename of the JSON entity descriptor.
            layer: Layer of insertion.
            x: x-coordinate of insertion, by tile.
            y: y-coordinate of insertion, by tile.

        Returns: Entity ID of new entity if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(layer, int, _min=0)
            CHECK(x, int, _min=0)
            CHECK(y, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "insert", "bad argument", e)
            return None

        if not self.driftwood.area.tilemap:
            self.driftwood.log.msg("ERROR", "Entity", "insert", "no area loaded")
            return None

        data = self.driftwood.resource.request_template(filename, template_vars)
        if not data:
            self.driftwood.log.msg("ERROR", "Entity", "insert", "could not get resource", filename)
            return None
        schema = _SCHEMA["entity"]

        self.__last_eid += 1
        eid = self.__last_eid

        # Attempt to validate against the schema.
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError:
            self.driftwood.log.msg("ERROR", "Entity", "insert", "failed validation", filename)
            traceback.print_exc(1, sys.stdout)
            sys.stdout.flush()
            return None

        # Set movement mode.
        if data["init"]["mode"] == "tile":
            self.entities[eid] = entity.TileModeEntity(self)
        elif data["init"]["mode"] == "pixel":
            self.entities[eid] = entity.PixelModeEntity(self)

        # Read the entity.
        self.entities[eid]._read(filename, data, eid)

        # Set the initial position.
        self.entities[eid].x = x * self.driftwood.area.tilemap.tilewidth
        self.entities[eid].y = y * self.driftwood.area.tilemap.tileheight
        self.entities[eid].layer = layer
        self.entities[eid].tile = self.driftwood.area.tilemap.layers[layer].tile(x, y)

        # In pixel mode, record which tile(s) the entity occupies at first.
        if self.entities[eid].mode == "pixel":
            self.entities[eid]._occupies = [self.entities[eid].tile, None, None, None]

        self.driftwood.area.changed = True

        self.driftwood.log.info(
            "Entity", "inserted", "{0} on layer {1} at position {2}t, {3}t".format(filename, layer, x, y)
        )

        # Function to call when inserting the entity.
        if data["init"]["on_insert"]:
            args = data["init"]["on_insert"].split(",")
            self.driftwood.script.call(args[0], args[1], self.entities[eid])

        # Function to call before killing the entity.
        if data["init"]["on_kill"]:
            self.entities[eid]._on_kill = data["init"]["on_kill"].split(",")

        return eid

    def entity(self, eid: int) -> Optional[entity.Entity]:
        """Retrieve an entity by eid.

        Args:
            eid: The Entity ID of the entity to retrieve.

        Returns: Entity class instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(eid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "entity", "bad argument", e)
            return None

        if eid in self.entities:
            return self.entities[eid]

        return None

    def entity_at(self, x: int, y: int) -> Optional[_entity.Entity]:
        """Retrieve an entity by pixel coordinate.

        Args:
            x: The x coordinate of the tile.
            y: The y coordinate of the tile.

        Returns: Entity class instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(x, int, _min=0)
            CHECK(y, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "entity_at", "bad argument", e)
            return None

        for eid in self.entities:
            if self.entities[eid].x == x and self.entities[eid].y == y:
                return self.entities[eid]
        return None

    def layer(self, layer: int) -> List[_entity.Entity]:
        """Retrieve a list of entities on a certain layer.

        Args:
            layer: Layer to find entities on.

        Returns: List of Entity class instances.
        """
        # Input Check
        try:
            CHECK(layer, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "layer", "bad argument", e)
            return []

        ents = []

        for eid in self.entities:
            if self.entities[eid].layer == layer:
                ents.append(self.entities[eid])

        # Put them in order of eid so they don't switch around if we iterate them.
        return sorted(ents, key=lambda by_eid: by_eid.eid)

    def kill(self, eid: int) -> bool:
        """Kill an entity by eid.

        Args:
            eid: The Entity ID of the entity to kill.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(eid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "kill", "bad argument", e)
            return False

        if eid in self.entities:
            if self.entities[eid]._on_kill:  # Call a function before killing the entity.
                self.driftwood.script.call(
                    self.entities[eid]._on_kill[0], self.entities[eid]._on_kill[1], self.entities[eid]
                )
            self.entities[eid]._terminate()
            del self.entities[eid]
            self.driftwood.area.changed = True
            return True

        self.driftwood.log.msg("WARNING", "Entity", "kill", "attempt to kill nonexistent entity", eid)
        return False

    def killall(self, filename: str) -> bool:
        """Kill all entities by filename.

        Args:
            filename: Filename of the JSON entity descriptor whose insertions should be killed.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "killall", "bad argument", e)
            return False

        to_kill = []

        for eid in self.entities:
            if self.entities[eid].filename == filename:
                to_kill += eid

        for eid in to_kill:
            if self.entities[eid]._on_kill:  # Call a function before killing the entity.
                self.driftwood.script.call(
                    self.entities[eid]._on_kill[0], self.entities[eid]._on_kill[1], self.entities[eid]
                )
            self.entities[eid]._terminate()
            del self.entities[eid]

        self.driftwood.area.changed = True

        if to_kill:
            return True
        self.driftwood.log.msg("WARNING", "Entity", "killall", "attempt to kill nonexistent entities", filename)
        return False

    def spritesheet(self, filename: spritesheet.Spritesheet) -> Optional[bool]:
        """Retrieve a sprite sheet by its filename.

        Args:
            filename: Filename of the sprite sheet image.

        Returns: Spritesheet class instance if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Entity", "spritesheet", "bad argument", e)
            return None

        for ss in self.spritesheets:
            if self.spritesheets[ss].filename == filename:
                return self.spritesheets[ss]

        return False

    def collision(self, a: _entity.Entity, b: _entity.Entity) -> bool:
        """Notify the collision callback, if set, that entity "a" has collided with entity or tile "b".

        Args:
            a: First colliding entity.
            b: Second colliding entity or tile.

        Returns:
            True
        """
        if self.collider:
            self.collider(a, b)

        return True

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        for eid in self.entities:
            self.entities[eid]._terminate()
        self.entities = None
        self.spritesheets = None
