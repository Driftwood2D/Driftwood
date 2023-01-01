################################
# Driftwood 2D Game Dev. Suite #
# areamanager.py               #
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

import math
from typing import TYPE_CHECKING

from sdl2 import *

from check import CHECK, CheckFailure
import tilemap

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


def int_greater_than_or_equal_to(x: float) -> int:
    return int(math.ceil(x))


def int_smaller_than(x: float) -> int:
    return int(math.floor(x - 0.001))


class AreaManager:
    """The Area Manager

    This class manages the currently focused area.

    Attributes:
        driftwood: Base class instance.
        filename: Filename of the current area.
        tilemap: Tilemap instance for the area's tilemap.
        changed: Whether the area should be rebuilt. This is true if the area changed since last checked.
        offset: Offset at which to draw the area inside the viewport.
        refocused: Whether we have gone to a new area since last checked.
    """

    def __init__(self, driftwood: "Driftwood"):
        """AreaManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.filename = ""
        self.tilemap = None
        self.changed = False
        self.offset = [0, 0]
        self.refocused = False
        self._autospawns = []

        self.driftwood.tick.register(self._tick)

    def register(self) -> None:
        """Register our tick callback."""
        self.driftwood.tick.register(self._tick)

    def focus(self, filename: str) -> bool:
        """Load and make active a new area.

        Args:
            filename: Filename of the area's Tiled map file.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Area", "focus", "bad argument", e)
            return False

        # Ask the resource manager for the JSON map file.
        map_json = self.driftwood.resource.request_json(filename)

        if map_json:  # Did we successfully retrieve the map?
            self.tilemap = tilemap.Tilemap(self.driftwood, self)
            self.filename = filename  # Set out current filename.
            if not self.tilemap._read(filename, map_json):  # Read the tilemap.
                self.driftwood.log.msg("ERROR", "Area", "focus", "could not load tilemap", filename)
                self.tilemap = None
                return False
            self.driftwood.log.info("Area", "loaded", filename)

            # We have moved areas.
            self.refocused = True

            # Call world's global on_focus handlers.
            self.driftwood.script._call_global_triggers("on_focus")

            # If there is an on_focus function defined for this map, call it.
            if "on_focus" in self.tilemap.properties:
                args = self.tilemap.properties["on_focus"].split(",")
                if len(args) < 2:
                    self.driftwood.log.msg(
                        "ERROR", "Area", "Focus", "invalid on_focus event", self.tilemap.properties["on_focus"]
                    )
                    return True
                self.driftwood.script.call(*args)

            # Are we autospawning any entities?
            for ent in self._autospawns:
                print(ent)
                self.driftwood.entity.insert(*ent)
            self._autospawns = []

            return True

        else:
            self.driftwood.log.msg("ERROR", "Area", "focus", "could not load area", filename)
            return False

    def _blur(self) -> None:
        """Call the global on_blur functions, and call the map's on_blur, if it has one. This is called when we leave
        an area.
        """
        # Call the world's global on_blur handlers.
        self.driftwood.script._call_global_triggers("on_blur")

        if "on_blur" in self.tilemap.properties:
            args = self.tilemap.properties["on_blur"].split(",")
            if len(args) < 2:
                self.driftwood.log.msg(
                    "ERROR", "Area", "blur", "invalid on_blur event", self.tilemap.properties["on_blur"]
                )
                return
            self.driftwood.script.call(*args)
        self.tilemap = None

    def _tick(self, seconds_past: float) -> None:
        """Tick callback."""
        if self.changed:  # TODO: Only redraw portions that have changed.
            if self.refocused:
                self.driftwood.frame.prepare(
                    self.tilemap.width * self.tilemap.tilewidth, self.tilemap.height * self.tilemap.tileheight
                )
                self.refocused = False
            else:
                self.driftwood.frame.clear()
            self.driftwood.frame.calc_rects()
            self.__build_frame()
            self.driftwood.frame.finish_frame()
            self.changed = False

    def __build_frame(self) -> None:
        """Build the frame and pass to WindowManager.

        For every tile and entity in each layer, copy its graphic onto the frame, then give the frame to WindowManager
        for display.
        """
        tilemap = self.tilemap
        tilewidth = tilemap.tilewidth
        tileheight = tilemap.tileheight
        offset = self.offset

        # Find the tiles that will show up if we draw them.
        x_begin, x_end, y_begin, y_end = self.calculate_visible_tile_bounds()

        # Start with the bottom layer and work up.
        for l in range(len(tilemap.layers)):
            layer = tilemap.layers[l]

            srcrect = [-1, -1, tilewidth, tileheight]
            dstrect = [-1, -1, tilewidth, tileheight]

            # Draw each tile in the layer into its position.
            for y in range(y_begin, y_end + 1):
                for x in range(x_begin, x_end + 1):
                    # Retrieve data about the tile.
                    tile = layer.tiles[y * tilemap.width + x]
                    tileset = tile.tileset

                    if not tileset and not tile.gid:
                        # This is a dummy tile, don't draw it.
                        continue

                    member = tile.members[tile._Tile__cur_member]

                    if member == -1:
                        # This tile is invisible at this point in its animation, don't draw it.
                        continue

                    # Get the source and destination rectangles needed by SDL_RenderCopy.
                    srcrect[0] = member % tileset.width * tilewidth
                    srcrect[1] = member // tileset.width * tileheight

                    dstrect[0] = x * tilewidth + offset[0]
                    dstrect[1] = y * tileheight + offset[1]

                    # Copy the tile onto our frame.
                    r = self.driftwood.frame.copy(tileset.texture, srcrect, dstrect)
                    if r < 0:
                        self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

            # Draw the lights onto the layer.
            for light in self.driftwood.light.layer(l):
                srcrect = 0, 0, light.lightmap.width, light.lightmap.height
                dstrect = [light.x - light.w // 2, light.y - light.h // 2, light.w, light.h]
                dstrect[0] += self.offset[0]
                dstrect[1] += self.offset[1]

                r = self.driftwood.frame.copy(
                    light.lightmap.texture,
                    srcrect,
                    dstrect,
                    alpha=light.alpha,
                    blendmode=light.blendmode,
                    colormod=light.colormod,
                )
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

            arearect = (
                0,
                0,
                self.tilemap.width * self.tilemap.tilewidth,
                self.tilemap.height * self.tilemap.tileheight,
            )

            tall_parts = []

            # Draw each entity on the layer into its position.
            for entity in self.driftwood.entity.layer(l):
                tall_amount = entity.height - self.tilemap.tileheight

                # Get the destination rectangle needed by SDL_RenderCopy.
                dstrect = [entity.x, entity.y - tall_amount, entity.width, entity.height]

                # Draw the layers of the entity.
                for srcrect in entity.srcrect():
                    srcrect = list(srcrect)
                    # Clip entities so they don't appear outside the area.
                    clip_left = 0 if arearect[0] <= dstrect[0] else arearect[0] - dstrect[0]
                    clip_top = 0 if arearect[1] <= dstrect[1] else arearect[1] - dstrect[1]
                    clip_right = (
                        0 if dstrect[0] + dstrect[2] <= arearect[2] else (dstrect[0] + dstrect[2]) - arearect[2]
                    )
                    clip_bot = 0 if dstrect[1] + dstrect[3] <= arearect[3] else (dstrect[1] + dstrect[3]) - arearect[3]

                    srcrect[0] += clip_left
                    dstrect[0] += clip_left
                    srcrect[1] += clip_top
                    dstrect[1] += clip_top
                    srcrect[2] -= clip_left + clip_right
                    dstrect[2] -= clip_left + clip_right
                    srcrect[3] -= clip_top + clip_bot
                    dstrect[3] -= clip_top + clip_bot

                    # Area rumble et al.
                    dstrect[0] += self.offset[0]
                    dstrect[1] += self.offset[1]

                    # Copy the entity onto our frame.
                    r = self.driftwood.frame.copy(entity.spritesheet.texture, srcrect, dstrect)
                    if r < 0:
                        self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

                    if tall_amount:  # It's taller than the tile. Figure out where to put the tall part.
                        dstrect = [
                            entity.x,
                            entity.y - tall_amount,
                            entity.width,
                            entity.height - (entity.height - tall_amount),
                        ]

                        srcrect[3] = dstrect[3]

                        # Clip entities so they don't appear outside the area.
                        clip_left = 0 if arearect[0] <= dstrect[0] else arearect[0] - dstrect[0]
                        clip_top = 0 if arearect[1] <= dstrect[1] else arearect[1] - dstrect[1]
                        clip_right = (
                            0 if dstrect[0] + dstrect[2] <= arearect[2] else (dstrect[0] + dstrect[2]) - arearect[2]
                        )
                        clip_bot = (
                            0 if dstrect[1] + dstrect[3] <= arearect[3] else (dstrect[1] + dstrect[3]) - arearect[3]
                        )

                        srcrect[0] += clip_left
                        dstrect[0] += clip_left
                        srcrect[1] += clip_top
                        dstrect[1] += clip_top
                        srcrect[2] -= clip_left + clip_right
                        dstrect[2] -= clip_left + clip_right
                        srcrect[3] -= clip_top + clip_bot
                        dstrect[3] -= clip_top + clip_bot

                        # Area rumble et al.
                        dstrect[0] += self.offset[0]
                        dstrect[1] += self.offset[1]

                        tall_parts.append([entity.spritesheet.texture, srcrect, dstrect])

                # Draw the tall bits here.
                for tall in tall_parts:
                    r = self.driftwood.frame.copy(*tall)
                    if r < 0:
                        self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

    def calculate_visible_tile_bounds(self) -> [int]:
        tilemap = self.tilemap
        tilewidth = tilemap.tilewidth
        tileheight = tilemap.tileheight
        offset = self.offset

        viewport_width, viewport_height = self.driftwood.window.resolution()

        viewport_left_bound = -self.driftwood.frame._frame[2].x
        viewport_top_bound = -self.driftwood.frame._frame[2].y
        viewport_right_bound = viewport_left_bound + viewport_width
        viewport_bottom_bound = viewport_top_bound + viewport_height

        # A tile will show up onscreen when it intersects the viewport rectangle. We can express the state of this
        # intersection with a set of four inequalities, all of which must be true for the intersection to occur.
        # --------------------------------------------------------------------------------------------------------
        # viewport_left_bound <= tile_right_bound
        # viewport_top_bound <= tile_bottom_bound
        # tile_left_bound < viewport_right_bound
        # tile_top_bound < viewport_bottom_bound

        # The following equations hold. (Unit of measurement is pixels.)
        # --------------------------------------------------------------
        # tile_left_bound   =  tile_x_pos      * tilewidth  + offset[0]
        # tile_top_bound    =  tile_y_pos      * tileheight + offset[1]
        # tile_right_bound  = (tile_x_pos + 1) * tilewidth  + offset[0] - 1
        # tile_bottom_bound = (tile_y_pos + 1) * tileheight + offset[1] - 1

        # Substitute the equations into the inequalities.
        # -----------------------------------------------
        # viewport_left_bound <= (tile_x_pos + 1) * tilewidth  + offset[0] - 1
        # viewport_top_bound  <= (tile_y_pos + 1) * tileheight + offset[1] - 1
        # tile_x_pos * tilewidth  + offset[0] < viewport_right_bound
        # tile_y_pos * tileheight + offset[1] < viewport_bottom_bound

        # Solve for tile_x_pos and tile_y_pos.
        # ------------------------------------
        # (viewport_left_bound - offset[0] + 1) / tilewidth  - 1 <= tile_x_pos
        # (viewport_top_bound  - offset[1] + 1) / tileheight - 1 <= tile_y_pos
        # tile_x_pos < (viewport_right_bound  - offset[0]) / tilewidth
        # tile_y_pos < (viewport_bottom_bound - offset[1]) / tileheight

        # We can now compute the minimum and maximum X and Y coordinates for visible tiles.

        x_begin = int_greater_than_or_equal_to((viewport_left_bound - offset[0] + 1) / tilewidth - 1)
        y_begin = int_greater_than_or_equal_to((viewport_top_bound - offset[1] + 1) / tileheight - 1)
        x_end = int_smaller_than((viewport_right_bound - offset[0]) / tilewidth)
        y_end = int_smaller_than((viewport_bottom_bound - offset[1]) / tileheight)

        x_begin = max(0, x_begin)
        y_begin = max(0, y_begin)
        x_end = min(x_end, tilemap.width - 1)
        y_end = min(y_end, tilemap.height - 1)

        return x_begin, x_end, y_begin, y_end
