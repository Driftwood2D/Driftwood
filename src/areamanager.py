####################################
# Driftwood 2D Game Dev. Suite     #
# areamanager.py                   #
# Copyright 2014 PariahSoft LLC    #
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

import tilemap


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

    def __init__(self, driftwood):
        """AreaManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.filename = ""
        self.tilemap = tilemap.Tilemap(driftwood, self)
        self.changed = False
        self.offset = [0, 0]
        self.refocused = False

        self.driftwood.tick.register(self._tick)

    def register(self):
        """Register our tick callback."""
        self.driftwood.tick.register(self._tick)

    def focus(self, filename):
        """Load and make active a new area.

        Args:
            filename: Filename of the area's Tiled map file.

        Returns:
            True if succeeded, False if failed.
        """
        # Ask the resource manager for the JSON map file.
        map_json = self.driftwood.resource.request_json(filename)

        if map_json: # Did we successfully retrieve the map?
            self.filename = filename  # Set out current filename.
            self.tilemap._read(filename, map_json)  # Read the tilemap. This should only be called from here.
            self.driftwood.log.info("Area", "loaded", filename)

            # We have moved areas.
            self.refocused = True

            # If there is an on_focus function defined for this map, call it.
            if "on_focus" in self.tilemap.properties:
                args = self.tilemap.properties["on_focus"].split(',')
                if len(args) < 2:
                    self.driftwood.log.msg("ERROR", "Area", "Focus", "invalid on_focus event",
                                           self.tilemap.properties["on_focus"])
                    return True
                self.driftwood.script.call(*args)

            return True

        else:
            self.driftwood.log.msg("ERROR", "Area", "focus", "no such area", filename)
            return False

    def _blur(self):
        """If there is an on_blur function defined for this map, call it. This is called when we leave an area.
        """
        if "on_blur" in self.tilemap.properties:
            args = self.tilemap.properties["on_blur"].split(',')
            if len(args) < 2:
                self.driftwood.log.msg("ERROR", "Area", "blur", "invalid on_blur event",
                                       self.tilemap.properties["on_blur"])
                return
            self.driftwood.script.call(*args)

    def _tick(self, seconds_past):
        """Tick callback.
        """
        if self.changed:  # TODO: Only redraw portions that have changed.
            if self.refocused:
                self.driftwood.frame.prepare(self.tilemap.width * self.tilemap.tilewidth,
                                             self.tilemap.height * self.tilemap.tileheight)
                self.refocused = False
            else:
                self.driftwood.frame.clear()
            self.__build_frame()
            self.changed = False

    def __build_frame(self):
        """Build the frame and pass to WindowManager.

        For every tile and entity in each layer, copy its graphic onto the frame, then give the frame to WindowManager
        for display.
        """
        # Start with the bottom layer and work up.
        for l in range(len(self.tilemap.layers)):
            # Draw each tile in the layer into its position.
            for t in range(self.tilemap.width * self.tilemap.height):
                # Retrieve data about the tile.
                tile = self.tilemap.layers[l].tiles[t]

                # This is a dummy tile, don't draw it.
                if not tile.tileset and not tile.gid:
                    continue

                # Get the source and destination rectangles needed by SDL_RenderCopy.
                srcrect = tile.srcrect()
                dstrect = tile.dstrect()
                dstrect[0] += self.offset[0]
                dstrect[1] += self.offset[1]
                # Copy the tile onto our frame.
                r = self.driftwood.frame.copy(tile.tileset.texture, srcrect, dstrect)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

            # Draw the lights onto the layer.
            for light in self.driftwood.light.layer(l):
                srcrect = 0, 0, light.lightmap.width, light.lightmap.height
                dstrect = [light.x - light.w // 2, light.y - light.h // 2, light.w, light.h]
                dstrect[0] += self.offset[0]
                dstrect[1] += self.offset[1]

                r = self.driftwood.frame.copy(light.lightmap.texture, srcrect, dstrect, alpha=light.alpha,
                                              blendmode=light.blendmode, colormod=light.colormod)
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
                    clip_right = 0 if dstrect[0] + dstrect[2] <= arearect[2] else (dstrect[0] + dstrect[2]) - arearect[2]
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
                        dstrect = [entity.x, entity.y - tall_amount, entity.width,
                                   entity.height - (entity.height - tall_amount)]

                        srcrect[3] = dstrect[3]

                        # Clip entities so they don't appear outside the area.
                        clip_left = 0 if arearect[0] <= dstrect[0] else arearect[0] - dstrect[0]
                        clip_top = 0 if arearect[1] <= dstrect[1] else arearect[1] - dstrect[1]
                        clip_right = 0 if dstrect[0] + dstrect[2] <= arearect[2] else (dstrect[0] + dstrect[2]) - arearect[2]
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

                        tall_parts.append([entity.spritesheet.texture, srcrect, dstrect])

                # Draw the tall bits here.
                for tall in tall_parts:
                    r = self.driftwood.frame.copy(*tall)
                    if r < 0:
                        self.driftwood.log.msg("ERROR", "Area", "__build_frame", "SDL", SDL_GetError())

        # Tell FrameManager to publish the finished frame.
        self.driftwood.frame.frame(None)
