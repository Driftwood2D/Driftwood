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
        tilemap: Tilemap instance for the area's tilemap.
        changed: Whether the area should be rebuilt.
        offset: Offset at which to draw the area inside the viewport.
    """

    def __init__(self, driftwood):
        """AreaManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.filename = ""

        self.tilemap = tilemap.Tilemap(self)

        self.changed = False

        self.offset = [0, 0]

        # The current rendered frame.
        self.__frame = None

        self.refocused = False

    def register(self):
        # Register the tick callback.
        self.driftwood.tick.register(self._tick)

    def focus(self, filename):
        """Load and make active a new area.

        Args:
            filename: Filename of the area's Tiled map file.

        Returns:
            True if succeeded, False if failed.
        """
        map_json = self.driftwood.resource.request_json(filename)
        if map_json:
            self.filename = filename
            self.tilemap._read(map_json)  # This should only be called from here.
            self.driftwood.log.info("Area", "loaded", filename)

            self.refocused = True

            # If there is an on_focus function defined for this map, call it.
            if "on_focus" in self.tilemap.properties:
                args = self.tilemap.properties["on_focus"].split(',')
                if len(args) < 2:
                    self.driftwood.log.msg("ERROR", "Map", "invalid on_focus event",
                                           self.tilemap.properties["on_focus"])
                    return True
                self.driftwood.script.call(*args)

            return True

        else:
            self.driftwood.log.msg("ERROR", "Area", "no such area", filename)
            return False

    def blur(self):
        # If there is an on_blur function defined for this map, call it.
        if "on_blur" in self.tilemap.properties:
            args = self.tilemap.properties["on_blur"].split(',')
            if len(args) < 2:
                self.driftwood.log.msg("ERROR", "Map", "invalid on_blur event",
                                       self.tilemap.properties["on_blur"])
                return
            self.driftwood.script.call(*args)

    def _tick(self, seconds_past):
        """Tick callback.
        """
        if self.changed:  # TODO: Only redraw portions that have changed.
            if self.refocused:
                self.__prepare_frame()
                self.refocused = False
            self.__build_frame()
            self.changed = False

    def __prepare_frame(self):
        """Prepare the local frame.

        Prepare self.__frame as a new SDL_Texture in the size of the area.
        """
        #if self.__frame:
        #    SDL_DestroyTexture(self.__frame) # TODO: Find out why this causes __build_frame to fail.

        self.__frame = SDL_CreateTexture(self.driftwood.window.renderer,
                                         SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_TARGET,
                                         self.tilemap.width * self.tilemap.tilewidth,
                                         self.tilemap.height * self.tilemap.tileheight)

        if type(self.__frame) == int and self.__frame < 0:
            self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

    def __build_frame(self):
        """Build the frame and pass to WindowManager.

        For every tile and entity in each layer, copy its graphic onto the frame, then give the frame to WindowManager
        for display.
        """
        # Tell SDL to render to our frame instead of the window's frame.
        r = SDL_SetRenderTarget(self.driftwood.window.renderer, self.__frame)
        if r < 0:
            self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

        srcrect = SDL_Rect()
        dstrect = SDL_Rect()

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
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = tile.srcrect()
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = tile.dstrect
                dstrect.x += self.offset[0]
                dstrect.y += self.offset[1]
                # Copy the tile onto our frame.
                r = SDL_RenderCopy(self.driftwood.window.renderer, tile.tileset.texture, srcrect,
                                   dstrect)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

            # Draw the lights onto the layer.
            for light in self.driftwood.light.layer(l):
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = 0, 0, light.lightmap.width, light.lightmap.height
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = light.x - light.w // 2, \
                                                             light.y - light.h // 2, \
                                                             light.w, light.h
                dstrect.x += self.offset[0]
                dstrect.y += self.offset[1]

                r = SDL_RenderCopy(self.driftwood.window.renderer, light.lightmap.texture, srcrect, dstrect)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

            tall_parts = []

            # Draw each entity on the layer into its position.
            for entity in self.driftwood.entity.layer(l):
                tall_amount = entity.height - self.tilemap.tileheight

                # Get the source and destination rectangles needed by SDL_RenderCopy.
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = entity.srcrect()
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = entity.x, entity.y - tall_amount, entity.width, \
                                                             entity.height
                dstrect.x += self.offset[0]
                dstrect.y += self.offset[1]

                # Copy the entity onto our frame.
                r = SDL_RenderCopy(self.driftwood.window.renderer, entity.spritesheet.texture, srcrect, dstrect)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

                tall_srcrect = SDL_Rect()
                tall_dstrect = SDL_Rect()

                if tall_amount:  # It's taller than the tile. Figure out where to put the tall part.
                    tall_srcrect.x, tall_srcrect.y, tall_srcrect.w, tall_srcrect.h = entity.srcrect()
                    tall_dstrect.x, tall_dstrect.y, tall_dstrect.w, tall_dstrect.h = \
                        entity.x, entity.y - tall_amount, entity.width, entity.height - (entity.height - tall_amount)
                    tall_dstrect.x += self.offset[0]
                    tall_dstrect.y += self.offset[1]
                    tall_srcrect.h = tall_dstrect.h
                    tall_parts.append([entity.spritesheet.texture, tall_srcrect, tall_dstrect])

            # Draw the tall bits here.
            for tall in tall_parts:
                r = SDL_RenderCopy(self.driftwood.window.renderer, *tall)
                if r < 0:
                    self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

        # Draw the widgets above everything.
        for widget in sorted(self.driftwood.widget.widgets.keys()):
            if self.driftwood.widget.widgets[widget].active and \
                    self.driftwood.widget.widgets[widget].srcrect():  # It's visible, draw it.
                # But ignore inactive containers.
                if (not self.driftwood.widget.widgets[widget].container) or \
                        self.driftwood.widget.widgets[self.driftwood.widget.widgets[widget].container].active:
                    srcrect.x, srcrect.y, srcrect.w, srcrect.h = self.driftwood.widget.widgets[widget].srcrect()
                    dstrect.x, dstrect.y, dstrect.w, dstrect.h = self.driftwood.widget.widgets[widget].dstrect()
                    if self.driftwood.widget.widgets[widget].type == "container" and \
                            self.driftwood.widget.widgets[widget].image:  # Draw a container image.
                        r = SDL_RenderCopy(self.driftwood.window.renderer,
                                           self.driftwood.widget.widgets[widget].image.texture,
                                           srcrect, dstrect)
                        if r < 0:
                            self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())
                    elif self.driftwood.widget.widgets[widget].type == "text" and \
                            self.driftwood.widget.widgets[widget].texture:  # Draw some text.
                        r = SDL_RenderCopy(self.driftwood.window.renderer,
                                           self.driftwood.widget.widgets[widget].texture,
                                           srcrect, dstrect)
                        if r < 0:
                            self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

        # Tell SDL to switch rendering back to the window's frame.
        r = SDL_SetRenderTarget(self.driftwood.window.renderer, None)
        if r < 0:
            self.driftwood.log.msg("ERROR", "Area", "SDL", SDL_GetError())

        # Give our frame to WindowManager for positioning and display.
        self.driftwood.window.frame(self.__frame, True)

    def _terminate(self):
        if self.__frame:
            SDL_DestroyTexture(self.__frame)
        self.__frame = None
