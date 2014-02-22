###################################
## Driftwood 2D Game Dev. Suite  ##
## entitymanager.py              ##
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

import entity


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

        self.player = None

        self.entities = []

        self.spritesheets = []

    def insert(self, filename, layer, x, y):
        """Insert an entity at a position in the area.

        Args:
            filename: Filename of the JSON entity descriptor.
            layer: Layer of insertion.
            x: x-coordinate of insertion.
            y: y-coordinate of insertion.
        """
        self.entities.append(entity.Entity(self))
        self.entities[-1]._read(filename)
        self.entities[-1].layer = layer
        self.entities[-1].x = x
        self.entities[-1].y = y

        self.driftwood.area.changed = True

        self.driftwood.log.info("Entity", "inserted", "{0} entity on layer {1} at position {2}, {3}".format(filename,
                                                                                                            layer,
                                                                                                            x, y))

    def entity(self, filename):
        """Retrieve a list of entities by filename.

        Args:
            filename: Filename of the JSON entity descriptor.

        Returns: List of Entity class instances.
        """
        ret = []

        for ent in self.entities:
            if ent.filename == filename:
                ret += ent

        return ret

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

        self.driftwood.area.changed = True

    def spritesheet(self, filename):
        """Retrieve a sprite sheet by its filename.

        Args:
            filename: Filename of the sprite sheet image.

        Returns: Spritesheet class instance.
        """
        for ss in self.spritesheets:
            if ss.filename == filename:
                return ss
