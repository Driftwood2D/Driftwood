###################################
## Driftwood 2D Game Dev. Suite  ##
## areamanager.py                ##
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

from sdl2 import *

import tilemap


class AreaManager:
    """The Area Manager

    This class manages the currently focused area.

    Attributes:
        driftwood: Base class instance.
        tilemap: Tilemap instance for the area's tilemap.
        changed: Whether the area should be rebuilt.
    """
    def __init__(self, driftwood):
        """AreaManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.tilemap = tilemap.Tilemap(self)

        self.changed = False

        # The current rendered frame.
        self.__frame = None

        self.__log = self.driftwood.log
        self.__entity = self.driftwood.entity
        self.__filetype = self.driftwood.filetype
        self.__resource = self.driftwood.resource
        self.__window = self.driftwood.window

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture

        # Register the tick callback.
        self.driftwood.tick.register(self.tick)

    def focus(self, filename):
        """Load and make active a new area.

        Args:
            filename: Filename of the area's Tiled map file.

        Returns:
            True if succeeded, False if failed.
        """
        if filename in self.__resource:
            self.tilemap._read(self.__resource[filename])  # This is the only place this should ever be called from.
            self.__prepare_frame()
            self.__build_frame()
            self.__log.info("Area", "loaded", filename)
            return True

        else:
            self.__log.log("ERROR", "Area", "no such area", filename)
            return False

    def __prepare_frame(self):
        """Prepare the local frame.

        Prepare self.__frame as a new SDL_Texture in the size of the area.
        """
        if self.__frame:
            SDL_DestroyTexture(self.__frame)

        self.__frame = SDL_CreateTexture(self.__window.renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_TARGET,
                                         self.tilemap.width * self.tilemap.tilewidth,
                                         self.tilemap.height * self.tilemap.tileheight)

    def __build_frame(self):
        """Build the frame and pass to WindowManager.

        For every tile and entity in each layer, copy its graphic onto the frame, then give the frame to WindowManager
        for display.
        """
        # Tell SDL to render to our frame instead of the window's frame.
        SDL_SetRenderTarget(self.__window.renderer, self.__frame)

        srcrect = SDL_Rect()
        dstrect = SDL_Rect()

        # Start with the bottom layer and work up.
        for l in range(len(self.tilemap.layers)):
            # Draw each tile in the layer into its position.
            for t in range(self.tilemap.width * self.tilemap.height):
                # Retrieve data about the tile.
                tile = self.tilemap.layers[l].tiles[t]

                # This tile has no data and does not exist.
                if not tile:
                    continue

                # Get the source and destination rectangles needed by SDL_RenderCopy.
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = tile.srcrect
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = tile.dstrect

                # Copy the tile onto our frame.
                SDL_RenderCopy(self.__window.renderer, tile.tileset.texture, srcrect,
                               dstrect)

            # Draw each entity on the layer into its position.
            for entity in self.driftwood.entity.layer(l):

                # Get the source and destination rectangles needed by SDL_RenderCopy.
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = entity.gpos
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = entity.x, entity.y, entity.gpos[2], entity.gpos[3]

                # Copy the entity onto our frame.
                SDL_RenderCopy(self.__window.renderer, entity.spritesheet.texture, srcrect,
                               dstrect)

        # Tell SDL to switch rendering back to the window's frame.
        SDL_SetRenderTarget(self.__window.renderer, None)

        # Give our frame to WindowManager for positioning and display.
        self.__window.frame(self.__frame, True)

    def tick(self):
        """Tick callback.
        """
        if self.changed:  # TODO: Only redraw portions that have changed.
            self.__build_frame()
            self.changed = False

    def __del__(self):
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
