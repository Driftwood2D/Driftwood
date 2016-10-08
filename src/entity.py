####################################
# Driftwood 2D Game Dev. Suite     #
# entity.py                        #
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

import spritesheet


class Entity:
    """This parent class represents an Entity. It is subclassed by either TileModeEntity or PixelModeEntity.

    Attributes:
        manager: Parent EntityManager instance.

        filename: Filename of the JSON entity descriptor.
        eid: The Entity ID number.
        mode: The movement mode of the entity.
        stance: The current stance of the entity.
        resting_stance: The default stance to return to when not walking.
        walk_state: Whether we are moving or not and whether we want to stop ASAP.
        collision: Whether collision should be checked for.
        spritesheet: Spritesheet instance of the spritesheet which owns this entity's graphic.
        layer: The layer of the entity.
        x: The x-coordinate of the entity.
        y: The y-coordinate of the entity.
        tile: Tile instance for the tile the entity is currently on.
        width: The width in pixels of the entity.
        height: The height in pixels of the entity.
        speed: The movement speed of the entity in pixels per second.
        members: A list of sequence positions of member graphics in the spritesheet.
        afps: Animation frames-per-second.
        gpos: A four-member list containing an x,y,w,h source rectangle for the entity's graphic.
        properties: Any custom properties of the entity.
    """

    NOT_WALKING, WALKING_WANT_CONT, WALKING_WANT_STOP = range(3)

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

        self.stance = "init"
        self.resting_stance = None
        self.walk_state = Entity.NOT_WALKING
        self.collision = None
        self.spritesheet = None
        self.layer = 0
        self.x = 0
        self.y = 0
        self.tile = None
        self.width = 0
        self.height = 0
        self.speed = 0
        self.members = []
        self.afps = 0
        self.properties = {}

        self.walking = None
        self._last_walk = None
        self._cw_teleport = False

        self.__cur_member = 0
        self._prev_xy = [0, 0]
        self._next_area = None
        self._next_tile = None
        self._next_stance = None

        self.__entity = {}
        self.__init_stance = {}

    def srcrect(self):
        """Return an (x, y, w, h) srcrect for the current graphic frame of the entity.
        """
        if self.__cur_member < len(self.members):
            current_member = self.members[self.__cur_member]
        else:
            # Guard against rare race condition.
            current_member = self.members[0]
        return (((current_member * self.width) % self.spritesheet.imagewidth),
                ((current_member * self.width) // self.spritesheet.imagewidth) * self.height,
                self.width, self.height)

    def set_stance(self, stance):
        """Set the current stance and return true if succeeded, false if failed.

        Args:
            stance: The name of the stance to set.
        """
        if not stance in self.__entity:
            # Fake!
            return False

        self.stance = stance

        # Set the stance's variables, return to init defaults for variables not present.
        if "collision" in self.__entity[stance]:
            self.collision = self.__entity[stance]["collision"]
        else:
            self.collision = self.__init_stance["collision"]

        if "image" in self.__entity[stance]:
            self.spritesheet = self.manager.spritesheet(self.__entity[stance]["image"])
            if not self.spritesheet:
                self.manager.spritesheets.append(spritesheet.Spritesheet(self.manager, self.__entity[stance]["image"]))
                self.spritesheet = self.manager.spritesheets[-1]
        else:
            self.spritesheet = self.manager.spritesheet(self.__init_stance["image"])

        if "speed" in self.__entity[stance]:
            self.speed = self.__entity[stance]["speed"]
        else:
            self.speed = self.__init_stance["speed"]

        if "members" in self.__entity[stance]:
            self.members = self.__entity[stance]["members"]
        else:
            self.members = self.__init_stance["members"]
        self.__cur_member = 0

        if "afps" in self.__entity[stance]:
            self.afps = self.__entity[stance]["afps"]
        else:
            self.afps = self.__init_stance["afps"]

        if "properties" in self.__entity[stance]:
            self.properties = self.__entity[stance]["properties"]
        else:
            self.properties = self.__init_stance["properties"]

        # Schedule animation.
        if self.afps:
            self.manager.driftwood.tick.register(self.__next_member, delay=(1 / self.afps))

        self.manager.driftwood.area.changed = True

    def _read(self, filename, data, eid):
        """Read the entity descriptor.
        """
        self.filename = filename
        self.eid = eid

        self.__entity = data
        self.__init_stance = self.__entity["init"]

        self.collision = self.__init_stance["collision"]
        self.width = self.__init_stance["width"]
        self.height = self.__init_stance["height"]
        self.speed = self.__init_stance["speed"]
        self.members = self.__init_stance["members"]
        self.afps = self.__init_stance["afps"]

        # Schedule animation.
        if self.afps:
            self.manager.driftwood.tick.register(self.__next_member, delay=(1 / self.afps))

        if "properties" in self.__init_stance:
            self.properties = self.__init_stance["properties"]

        if "resting_stance" in self.__init_stance:
            self.resting_stance = self.__init_stance["resting_stance"]
            self.set_stance(self.resting_stance)

        self.spritesheet = self.manager.spritesheet(self.__init_stance["image"])

        if not self.spritesheet:
            self.manager.spritesheets.append(spritesheet.Spritesheet(self.manager, self.__init_stance["image"]))
            self.spritesheet = self.manager.spritesheets[-1]

    def _do_exit(self):
        """Perform an exit to another area.
        """
        # Call the on_exit event if set.
        if "on_exit" in self.manager.driftwood.area.tilemap.properties:
            self.manager.driftwood.script.call(*self.manager.driftwood.area.tilemap.properties["on_exit"].split(':'))

        # Enter the next area.
        if self.manager.driftwood.area.focus(self._next_area[0]):
            self.layer = int(self._next_area[1])
            self.x = int(self._next_area[2]) * self.manager.driftwood.area.tilemap.tilewidth
            self.y = int(self._next_area[3]) * self.manager.driftwood.area.tilemap.tileheight
            self.tile = self._tile_at(self.layer, self.x, self.y)

        self._next_area = None

    def _collide(self, dsttile):
        """Report a collision.
        """
        if self.manager.collider:
            self.manager.collider(self, dsttile)

    def _tile_at(self, layer, x, y, px=0, py=0):
        """Retrieve a tile by layer and pixel coordinates.
        """
        return self.manager.driftwood.area.tilemap.layers[layer].tile(
            (x / self.manager.driftwood.area.tilemap.tilewidth) + px,
            (y / self.manager.driftwood.area.tilemap.tileheight) + py
        )

    def __next_member(self, seconds):
        """Set to change the animation frame.
        """
        self.__cur_member = (self.__cur_member + 1) % len(self.members)
        self.manager.driftwood.area.changed = True


# TODO: When PixelModeEntity is done, move common logic into functions in the superclass.
class TileModeEntity(Entity):
    """This Entity subclass represents an Entity configured for movement in by-tile mode.
    """

    def teleport(self, layer, x, y, area=None, lazy=False):
        """Teleport the entity to a new tile position.

        This is also used to change layers or to move to a new area.

        Args:
            layer: New layer, or None to skip.
            x: New x-coordinate, or None to skip.
            y: New y-coordinate, or None to skip.
            area: The area to teleport to, if any.

        Returns:
            True if succeeded, False if failed.
        """
        tilemap = self.manager.driftwood.area.tilemap

        if area:
            self._next_area = [area, layer, x, y]
            return True

        # Make sure this is a tile.
        if (((layer is not None) and (layer < 0 or len(tilemap.layers) <= layer)) or
                (x is not None and x >= tilemap.width) or
                (y is not None and y >= tilemap.height)
            ):
            self.manager.driftwood.log.msg("ERROR", "Entity", "attempted teleport to non-tile position")
            return False

        # Decide what to do with the layer.
        if layer is not None:
            temp_layer = layer
        else:
            temp_layer = self.layer

        # Decide what to do with x.
        if x is not None:  # We have an x.
            temp_x = x * tilemap.tilewidth
        elif self._cw_teleport:  # We walked here.
            temp_x = self.x - self._last_walk[0] * tilemap.tilewidth
        else:  # We scripted here.
            temp_x = self.x

        # Decide what to do with y.
        if y is not None:  # We have a y.
            temp_y = y * tilemap.tileheight
        elif self._cw_teleport:  # We walked here.
            temp_y = self.y - self._last_walk[1] * tilemap.tileheight
        else:  # We scripted here.
            temp_y = self.y

        # Set the new tile.
        self._next_tile = [temp_layer, temp_x, temp_y]

        # Call the on_tile event if set.
        self.__call_on_tile()

        # If we changed the layer, call the on_layer event if set.
        if layer is not None:
            self.__call_on_layer()

        self.manager.driftwood.area.changed = True

        return True

    def walk(self, x, y, dont_stop=False, stance=None, end_stance=None):
        """Walk the entity by one tile to a new position relative to its current
           position.

        Args:
            x: -1 for left, 1 for right, 0 for no x movement.
            y: -1 for up, 1 for down, 0 for no y movement.
            dont_stop: Walk continuously, don't stop after one tile or pixel. Only stop when self.walk_state externally
                set to Entity.WALKING_WANT_STOP.  Only has an effect if x or y is set.
            stance: Set the stance we will assume when the walk occurs.
            end_stance: Set the stance we will assume if we stop after this walk.

        Returns: True if succeeded, false if failed (due to collision or already
                 busy walking).
        """
        self._next_stance = stance
        self._end_stance = end_stance

        self._last_walk = [x, y]
        if x or y:  # We call walk with 0,0 when entering a new area.
            can_walk = self.walking is None and self.__can_walk(x, y)
            if can_walk:  # Can we walk? If so schedule the walking.
                self.__schedule_walk(x, y, dont_stop)
            elif self.walking is None:  # We can't and are not walking, but tried to. Face the entity.
                if self._end_stance:
                    self.set_stance(self._end_stance)
            return can_walk
        else:
            self.__arrive_at_tile()
            return True

    def _walk_stop(self):
        # Schedule us to stop walking.
        if self.walk_state == Entity.WALKING_WANT_CONT:
            self.walk_state = Entity.WALKING_WANT_STOP

    def _process_walk(self, seconds_past):
        # Process the walking each tick.
        if self.walk_state == Entity.NOT_WALKING:
            self.manager.driftwood.tick.unregister(self._process_walk)

        elif self.walk_state == Entity.WALKING_WANT_CONT:
            self.__inch_along(seconds_past)
            if self.__is_at_next_tile():
                self.__walk_set_tile()
                self.__arrive_at_tile()
                if not self.__can_walk(*self.walking):
                    self.__stand_still()

        elif self.walk_state == Entity.WALKING_WANT_STOP:
            self.__inch_along(seconds_past)
            if self.__is_at_next_tile():
                self.__walk_set_tile()
                self.__arrive_at_tile()
                self.__stand_still()

    def __prepare_exit_dest(self, exit_dest):
        # Prepare coordinates for teleport().

        # layer coordinate.
        if not exit_dest[1]:  # Stays the same.
            exit_dest[1] = None
        elif exit_dest[1].startswith('+'):  # Increments upward.
            exit_dest[1] = self.layer + int(exit_dest[1][1:])
        elif exit_dest[1].startswith('-'):  # Increments downward.
            exit_dest[1] = self.layer - int(exit_dest[1][1:])
        else:  # Set to a specific coordinate.
            exit_dest[1] = int(exit_dest[1])

        # x coordinate.
        if not exit_dest[2]:  # Stays the same.
            exit_dest[2] = None
        elif exit_dest[2].startswith('+'):  # Increments upward.
            exit_dest[2] = self.tile.pos[0] + int(exit_dest[2][1:])
        elif exit_dest[2].startswith('-'):  # Increments downward.
            exit_dest[2] = self.tile.pos[0] - int(exit_dest[2][1:])
        else:  # Set to a specific coordinate.
            exit_dest[2] = int(exit_dest[2])

        # y coordinate.
        if not exit_dest[3]:  # Stays the same.
            exit_dest[3] = None
        elif exit_dest[3].startswith('+'):  # Increments upward.
            exit_dest[3] = self.tile.pos[1] + int(exit_dest[3][1:])
        elif exit_dest[3].startswith('-'):  # Increments downward.
            exit_dest[3] = self.tile.pos[1] - int(exit_dest[3][1:])
        else:  # Set to a specific coordinate.
            exit_dest[3] = int(exit_dest[3])

        return exit_dest

    def __can_walk(self, x, y):
        # Check if we're allowed to walk this way.
        if x not in [-1, 0, 1]:
            x = 0

        if y not in [-1, 0, 1]:
            y = 0

        if not self.tile or self._next_tile:
            return False  # panic!

        # Perform collision detection.
        if self.collision:  # Check if the destination tile is walkable.
            dsttile = self.manager.driftwood.area.tilemap.layers[self.layer].tile(self.tile.pos[0] + x,
                                                                                  self.tile.pos[1] + y)

            # Don't walk on nowalk tiles or off the edge of the map unless there's a lazy exit.
            if self.tile:
                if dsttile:  # Does a tile exist where we're going?
                    if dsttile.nowalk or dsttile.nowalk == "":
                        # Is the tile a player or npc specific nowalk?
                        if (dsttile.nowalk == "player" and self.manager.player.eid == self.eid
                            or dsttile.nowalk == "npc" and self.manager.player.eid != self.eid):
                            self._collide(dsttile)
                            return False

                        # Any other values are an unconditional nowalk.
                        elif not dsttile.nowalk in ["player", "npc"]:
                            self._collide(dsttile)
                            return False

                    # Prepare exit from the previous tile.
                    for ex in self.tile.exits.keys():
                        if (ex == "exit:up" and y == -1) or (ex == "exit:down" and y == 1) or (
                                ex == "exit:left" and x == -1) or (ex == "exit:right" and x == 1):
                            exit_dest = self.tile.exits[ex].split(',')
                            if not exit_dest[0]:  # This area.
                                # Prepare coordinates for teleport().
                                exit_dest = self.__prepare_exit_dest(exit_dest)

                                # Do the teleport.
                                self.teleport(exit_dest[1], exit_dest[2], exit_dest[3])

                            else:  # Another area.
                                self._next_area = exit_dest

                    # Prepare exit for this tile.
                    for ex in dsttile.exits.keys():
                        if ex == "exit":
                            exit_dest = dsttile.exits[ex].split(',')
                            if not exit_dest[0]:  # This area.
                                # Prepare coordinates for teleport().
                                exit_dest = self.__prepare_exit_dest(exit_dest)

                                # Tell teleport() we got here by walking onto an exit.
                                self._cw_teleport = True
                                self.teleport(exit_dest[1], exit_dest[2], exit_dest[3])
                                self._cw_teleport = False

                            else:  # Another area.
                                self._next_area = exit_dest

                else:  # Are we allowed to walk off the edge of the area to follow a lazy exit?
                    if "exit:up" in self.tile.exits and y == -1:
                        self._next_area = self.tile.exits["exit:up"].split(',')

                    elif "exit:down" in self.tile.exits and y == 1:
                        self._next_area = self.tile.exits["exit:down"].split(',')

                    elif "exit:left" in self.tile.exits and x == -1:
                        self._next_area = self.tile.exits["exit:left"].split(',')

                    elif "exit:right" in self.tile.exits and x == 1:
                        self._next_area = self.tile.exits["exit:right"].split(',')

                    else:
                        self._collide(dsttile)
                        return False

            # Entity collision detection.
            for ent in self.manager.entities:
                # This is us.
                if ent.eid == self.eid:
                    continue

                # Collision detection.
                tilewidth = self.manager.driftwood.area.tilemap.tilewidth
                tileheight = self.manager.driftwood.area.tilemap.tileheight
                if (
                                            self.x + tilewidth < ent.x
                                or self.x > ent.x + tilewidth
                            or self.y + tileheight < ent.y
                        or self.y > ent.y + tileheight
                ):
                    self.manager.collision(self, ent)
                    return False

        return True

    def __schedule_walk(self, x, y, dont_stop):
        self.__reset_walk()
        self.walking = [x, y]
        if self._next_stance and self.stance != self._next_stance:
            self.set_stance(self._next_stance)
        if dont_stop:
            self.walk_state = Entity.WALKING_WANT_CONT
        else:
            self.walk_state = Entity.WALKING_WANT_STOP
        self.manager.driftwood.tick.register(self._process_walk)

    def __reset_walk(self):
        """Reset walking if our X,Y coordinates change."""
        self._prev_xy = [self.x, self.y]
        self._partial_xy = [self.x, self.y]

    def __inch_along(self, seconds_past):
        # Set our incremental position for rendering as we move between tiles.
        self.manager.driftwood.area.changed = True

        self._partial_xy[0] += self.walking[0] * self.speed * seconds_past
        self._partial_xy[1] += self.walking[1] * self.speed * seconds_past
        self.x = int(self._partial_xy[0])
        self.y = int(self._partial_xy[1])

    def __is_at_next_tile(self):
        """Check if we've reached or overreached our destination."""
        tilewidth = self.manager.driftwood.area.tilemap.tilewidth
        # tileheight = self.manager.driftwood.area.tilemap.tileheight

        return ((self.walking[0] == -1 and self.x <= self._prev_xy[0] - tilewidth)
                or (self.walking[0] == 1 and self.x >= self._prev_xy[0] + tilewidth)
                or (self.walking[1] == -1 and self.y <= self._prev_xy[1] - tilewidth)
                or (self.walking[1] == 1 and self.y >= self._prev_xy[1] + tilewidth))

    def __arrive_at_tile(self):
        # Perform actions for when we arrive at another tile.
        if self.tile:
            self.__call_on_tile()
            self.__do_layermod()

            # Handle teleports.
            if self._next_tile:
                tilemap = self.manager.driftwood.area.tilemap
                self.tile = self._tile_at(*self._next_tile)

                # Realign ourselves to the correct position.
                self.x = self.tile.pos[0] * tilemap.tilewidth
                self.y = self.tile.pos[1] * tilemap.tileheight
                self._partial_xy = [self.x, self.y]
                self._prev_xy = [self.x, self.y]

                self._next_tile = None
                self._walk_stop()

        # May be lazy exit, where we have no self.tile
        self.__do_take_exit()

    def __walk_set_tile(self):
        # Set the current tile.
        tilewidth = self.manager.driftwood.area.tilemap.tilewidth
        tileheight = self.manager.driftwood.area.tilemap.tileheight

        self._prev_xy[0] = self._prev_xy[0] + (tilewidth * self.walking[0])
        self._prev_xy[1] = self._prev_xy[1] + (tileheight * self.walking[1])
        self.tile = self._tile_at(self.layer, self._prev_xy[0], self._prev_xy[1])

    def __call_on_tile(self):
        # Call the on_tile event if set.
        if "on_tile" in self.tile.properties:
            args = self.tile.properties["on_tile"].split(':')
            self.manager.driftwood.script.call(*args)

    def __call_on_layer(self):
        # Call the on_layer event if set.
        if "on_layer" in self.manager.driftwood.area.tilemap.layers[self.layer].properties:
            args = self.manager.driftwood.area.tilemap.layers[self.layer].properties["on_layer"].split(':')
            self.manager.driftwood.script.call(*args)

    def __do_layermod(self):
        # Layermod macro, change the layer.
        if "layermod" in self.tile.properties:
            did_teleport = False
            xdiff, ydiff = 0, 0

            layermod = self.tile.properties["layermod"]
            # Go down so many layers.
            if layermod.startswith('-'):
                self.teleport(self.layer - int(layermod[1:]), None, None)
                did_teleport = True

            # Go up so many layers.
            elif layermod.startswith('+'):
                self.teleport(self.layer + int(layermod[1:]), None, None)
                did_teleport = True

            # Go to a specific layer.
            else:
                self.teleport(int(layermod), None, None)
                did_teleport = True

            if did_teleport:
                xdiff = self._partial_xy[0] - self.x
                ydiff = self._partial_xy[1] - self.y
            self.__call_on_tile()
            if did_teleport:
                self._partial_xy[0] = xdiff + self.x
                self._partial_xy[1] = ydiff + self.y

            return True

        return False

    def __do_take_exit(self):
        # If there is an exit, take it.
        if self._next_area:

            # If we're the player, change the area.
            if self.manager.player.eid == self.eid:
                self._do_exit()
                self.__call_on_tile()
                self.__reset_walk()

            # Exits destroy other entities.
            else:
                self.manager.kill(self.eid)

            return True

        return False

    def __stand_still(self):
        # We are entirely finished walking.
        tilemap = self.manager.driftwood.area.tilemap
        tilewidth = tilemap.tilewidth
        tileheight = tilemap.tileheight

        # Set the final position and cease walking.
        if self.tile:
            self.x = self.tile.pos[0] * tilewidth
            self.y = self.tile.pos[1] * tileheight

        self.walk_state = Entity.NOT_WALKING
        self.walking = None

        # Set the entity's final stance.
        if self._end_stance:
            self.set_stance(self._end_stance)
        elif self.resting_stance:
            self.set_stance(self.resting_stance)


# TODO: Finish pixel mode.
class PixelModeEntity(Entity):
    """This Entity subclass represents an Entity configured for movement in by-pixel mode.
    """

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

    def walk(self, x, y):
        """Move the entity by one pixel to a new position relative to its current position.

        Args:
            x: -1 for left, 1 for right, 0 for no x movement.
            y: -1 for up, 1 for down, 0 for no y movement.

        Returns: True if succeeded, false if failed (due to collision).
        """
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


# TODO: Implement turn mode.
class TurnModeEntity(Entity):
    """This Entity subclass represents an Entity configured for movement in turn-based mode.
    """
