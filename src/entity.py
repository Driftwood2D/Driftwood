###################################
## Driftwood 2D Game Dev. Suite  ##
## entity.py                     ##
## Copyright 2014 PariahSoft LLC ##
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

import spritesheet


class EntityManager:
    """The Entity Manager

    This class manages entities in the current area, as well as the persistent player entity.

    Attributes:
        driftwood: Base class instance.

        player: The player entity.

        entities: The list of Entity class instances for each entity.
        spritesheets: The list of Spritesheet class instances for each sprite sheet.
    """
    def __init__(self, driftwood):
        """EntityManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.player = None  # TODO

        self.entities = []

        self.spritesheets = []

        self.__resource = self.driftwood.resource

    def insert(self, filename, layer, x, y):
        """Insert an entity at a position in the area.

        Args:
            filename: Filename of the JSON entity descriptor.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.
        """
        self.entities.append(Entity(self))
        self.entities[-1]._read(filename)
        self.entities[-1].layer = layer
        self.entities[-1].x = x
        self.entities[-1].y = y
        self.entities[-1].bound.append([layer, x, y])

        self.driftwood.area.changed = True

    def entity(self, filename):
        """Retrieve an entity by its filename.

        Args:
            filename: Filename of the JSON entity descriptor.

        Returns: Entity class instance.
        """
        for ent in self.entities:
            if ent.filename == filename:
                return ent

    def layer(self, layer):
        """Retrieve a list of entities on a certain layer.

        Args:
            layer: Layer to find entities on.

        Returns: List of Entity class instances.
        """
        ents = []

        for ent in self.entities:
            if ent.layer == layer:
                ents.append(ent)

        return ents

    def killall(self, filename):
        """Kill all entities by filename.

        Args:
            filename: Filename of the JSON entity descriptor whose insertions should be killed.
        """
        for ent in range(len(self.entities)):
            if self.entities[ent].filename == filename:
                del self.entities[ent]

    def spritesheet(self, filename):
        """Retrieve a sprite sheet by its filename.

        Args:
            filename: Filename of the sprite sheet image.

        Returns: Spritesheet class instance.
        """
        for ss in self.spritesheets:
            if ss.filename == filename:
                return ss


class Entity:
    """This class represents an Entity.

    Attributes:
        manager: Parent EntityManager instance.

        filename: Filename of the JSON entity descriptor.
        spritesheet: Spritesheet instance of the spritesheet which owns this entity's graphic.
        layer: The layer of the entity.
        x: The x-coordinate of the entity.
        y: The y-coordinate of the entity.
        gpos: A four-member list containing an x,y,w,h source rectangle for the entity's graphic.
        bound: A list of [layer, x, y] positions for tiles the entity is bound to.
        properties: Any custom properties of the entity.
    """
    def __init__(self, entitymanager):
        """Entity class initializer.

        Args:
            manager: Link back to the parent EntityManager instance.
        """
        self.manager = entitymanager

        self.filename = ""
        self.spritesheet = None
        self.layer = 0
        self.x = 0
        self.y = 0
        self.gpos = [0, 0, 0, 0]
        self.bound = []
        self.properties = {}

        self.__entity = {}

        self.__resource = self.manager.driftwood.resource

    def _read(self, filename):
        self.filename = filename

        self.__entity = json.loads(self.__resource[filename])

        self.gpos = self.__entity["gpos"]

        if "properties" in self.__entity:
            self.properties = self.__entity["properties"]

        ss = self.manager.spritesheet(self.__entity["image"])

        if ss:
            self.spritesheet = ss

        else:
            self.manager.spritesheets.append(spritesheet.Spritesheet(self.manager, self.__entity["image"]))
            self.spritesheet = self.manager.spritesheets[-1]

    def bind(self, layer, x, y):
        """Bind the entity to a tile by its coordinates.

        Args:
            layer: Layer of the tile.
            x: x-coordinate of the tile.
            y: y-coordinate of the tile.
        """
        if not [layer, x, y] in self.bound:
            self.bound.append([layer, x, y])

            # Ouch.
            self.manager.driftwood.area.tilemap.layers[layer].tile(x, y).entities.append(self)

    def unbind(self, layer, x, y):
        """Unbind the entity from a tile by its coordinates.

        Args:
            layer: Layer of the tile.
            x: x-coordinate of the tile.
            y: y-coordinate of the tile.
        """
        if [layer, x, y] in self.bound:
            self.bound.remove([layer, x, y])

            # Ouch.
            self.manager.driftwood.area.tilemap.layers[layer].tile(x, y).entities.remove(self)

    def move(self, layer, x, y):
        """Move the entity to a new graphical position.

        Args:
            layer: New layer, or None to skip.
            x: New x-coordinate, or None to skip.
            y: New y-coordinate, or None to skip.
        """
        if layer:
            self.layer = layer

        if x:
            self.x = x

        if y:
            self.y = y
