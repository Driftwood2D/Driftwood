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

import spritesheet


class Entity:
    """This parent class represents an Entity. It is subclassed by either TileModeEntity or PixelModeEntity.

    Attributes:
        manager: Parent EntityManager instance.

        filename: Filename of the JSON entity descriptor.
        eid: The Entity ID number.
        mode: The movement mode of the entity.
        collision: Whether collision should be checked for.
        spritesheet: Spritesheet instance of the spritesheet which owns this entity's graphic.
        layer: The layer of the entity.
        x: The x-coordinate of the entity.
        y: The y-coordinate of the entity.
        width: The width in pixels of the entity.
        height: The height in pixels of the entity.
        speed: The movement speed of the entity in tiles per second.
        gpos: A four-member list containing an x,y,w,h source rectangle for the entity's graphic.
        properties: Any custom properties of the entity.
    """
    def __init__(self, entitymanager):
        """Entity class initializer.

        Args:
            manager: Link back to the parent EntityManager instance.
        """
        self.manager = entitymanager

        self.filename = ""
        self.eid = 0

        if isinstance(self, TileModeEntity):
            self.mode = "tile"

        elif isinstance(self, PixelModeEntity):
            self.mode = "pixel"

        else:
            self.mode = None
            print("!!! That's not supposed to happen. [1]")

        self.collision = None
        self.spritesheet = None
        self.layer = 0
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.speed = 0  #TODO
        self.gpos = [0, 0, 0, 0]
        self.properties = {}

        self.moving = None

        self.__entity = {}

    def _read(self, filename, eid):
        self.filename = filename
        self.eid = eid

        self.__entity = self.manager.driftwood.resource.request_json(filename)

        self.collision = self.__entity["collision"]
        self.gpos = self.__entity["gpos"]
        self.width, self.height = self.gpos[2], self.gpos[3]

        if "properties" in self.__entity:
            self.properties = self.__entity["properties"]

        ss = self.manager.spritesheet(self.__entity["image"])

        if ss:
            self.spritesheet = ss

        else:
            self.manager.spritesheets.append(spritesheet.Spritesheet(self.manager, self.__entity["image"]))
            self.spritesheet = self.manager.spritesheets[-1]


class TileModeEntity(Entity):
    def teleport(self, layer, x, y):
        """Teleport the entity to a new tile position.

        Args:
            layer: New layer, or None to skip.
            x: New x-coordinate, or None to skip.
            y: New y-coordinate, or None to skip.
        """
        if layer:
            self.layer = layer

        if x:
            self.x = x * self.manager.driftwood.area.tilemap.tilewidth

        if y:
            self.y = y * self.manager.driftwood.area.tilemap.tileheight

        self.manager.driftwood.area.changed = True

    def move(self, x, y):
        if not self.moving:
            if not x or not x in [-1, 0, 1]:
                x = 0

            if not y or not y in [-1, 0, 1]:
                y = 0

            # Perform collision detection.
            if self.collision:
                # Check if the destination tile is walkable.
                dsttile = self.manager.driftwood.area.tilemap.layers[self.layer].tile((self.x / self.width) + x,
                                                                                     (self.y / self.height) + y)
                if (not dsttile) or dsttile.nowalk:
                    if self.manager.collider:
                        self.manager.collider(self, dsttile)

                    return False

                # Entity collision detection.
                for ent in self.manager.entities:
                    # This is us.
                    if ent.eid == self.eid:
                        continue

                    # Collision detection, proof by contradiction.
                    if not (
                        (self.x + (x * self.manager.driftwood.area.tilemap.tilewidth)) >
                            (ent.x + (x * self.manager.driftwood.area.tilemap.tilewidth))

                        and (self.x + (x * self.manager.driftwood.area.tilemap.tilewidth) +
                                 self.manager.driftwood.area.tilemap.tilewidth) < ent.x

                        and (self.y + (y * self.manager.driftwood.area.tilemap.tileheight)) >
                                (ent.y + (x * self.manager.driftwood.area.tilemap.tileheight))

                        and (self.y + (y * self.manager.driftwood.area.tilemap.tileheight) +
                                 self.manager.driftwood.area.tilemap.tileheight) < ent.y
                    ):
                        self.manager.collision(self, ent)
                        return False

            self.manager.driftwood.tick.register(self.__move_callback)
            self.moving = [x, y]

        return True

    def __move_callback(self):
        if self.moving:
            self.x += self.moving[0]
            self.y += self.moving[1]

            if (
                    (self.moving[0] and self.x % self.manager.driftwood.area.tilemap.tilewidth) == 0
                    or (self.moving[1] and self.y % self.manager.driftwood.area.tilemap.tileheight) == 0
            ):
                self.moving = None

        else:
            self.manager.driftwood.tick.unregister(self.__move_callback)

        self.manager.driftwood.area.changed = True


class PixelModeEntity(Entity):
    def teleport(self, layer, x, y):
        """Teleport the entity to a new pixel position.

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

        self.manager.driftwood.area.changed = True

    def move(self, x, y):
        if not x or not x in [-1, 0, 1]:
            x = 0

        if not y or not y in [-1, 0, 1]:
            y = 0

        # Perform collision detection.
        if self.collision:
            # TODO: Pixel mode tile collisions.

            # Entity collision detection.
            for ent in self.manager.entities:
                # This is us.
                if ent.eid == self.eid:
                    continue

                # Collision detection, proof by contradiction.
                if not (
                    self.x + x > ent.x + ent.width

                    and self.x + self.width + x < ent.x

                    and self.y + y > ent.y + ent.height

                    and self.y + self.height + y < ent.y
                ):
                    self.manager.collision(self, ent)
                    return False

        self.x += x
        self.y += y

        self.manager.driftwood.area.changed = True

        return True
