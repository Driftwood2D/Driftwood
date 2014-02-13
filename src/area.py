###################################
## Project Driftwood             ##
## area.py                       ##
## Copyright 2013 PariahSoft LLC ##
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

import map

class AreaManager:
    """The Area Manager

    This class manages the currently focused area.

    Attributes:
        config: ConfigManager instance.
        map: MapManager instance.
    """
    def __init__(self, config):
        """AreaManager class initializer.

        Args:
            config: Link back to the ConfigManager.
        """
        self.config = config
        self.map = map.MapManager(self.config)

        self.__log = self.config.baseclass.log
        self.__filetype = self.config.baseclass.filetype
        self.__resource = self.config.baseclass.resource
        self.__window = self.config.baseclass.window
        self.__frame = None

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture

        # Register the tick callback.
        self.config.baseclass.tick.register(self.tick)

    def focus(self, filename):
        """Load and make active a new area.

        Args:
            filename: Filename of the area's Tiled map file.

        Returns:
            True if succeeded, False if failed.
        """
        if filename in self.__resource:
            self.map._read(self.__resource[filename])  # This is the only place this should ever be called from.
            self.__prepare_frame()
            self.__build_frame()
            self.__log.info("Area", "loaded", filename)
            return True

        else:
            self.__log.log("ERROR", "Area", "no such area", filename)
            return False

    def tick(self):
        """Tick callback.
        """
        pass

    def __prepare_frame(self):
        """Prepare the local frame.

        Prepare self.__frame as a new SDL_Texture in the size of the area.
        """
        if self.__frame:
            SDL_DestroyTexture(self.__frame)

        self.__frame = SDL_CreateTexture(self.__window.renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_TARGET,
                                         self.map.width * self.map.tilewidth, self.map.height * self.map.tileheight)

    def __build_frame(self):
        """Build the frame and pass to WindowManager.

        For every tile in each layer, copy its graphic onto the frame, then give the frame to WindowManager for display.
        """
        # Tell SDL to render to our frame instead of the window's frame.
        SDL_SetRenderTarget(self.__window.renderer, self.__frame)

        srcrect = SDL_Rect()
        dstrect = SDL_Rect()

        # Start with the bottom layer and work up.
        for layer in range(self.map.num_layers):
            # Draw each tile in the layer into its position.
            for t in range(self.map.width * self.map.height):
                # Figure out the coordinates of the tile.
                x, y = self.map.get_tile_coords(layer, t)

                # Retrieve data about the tile.
                tile = self.map.get_tile(layer, x, y)

                # This tile has no data and does not exist.
                if not tile:
                    continue

                # Get the source and destination rectangles needed by SDL_RenderCopy.
                srcrect.x, srcrect.y, srcrect.w, srcrect.h = self.map.get_tile_srcrect(layer, x, y)
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = self.map.get_tile_dstrect(layer, x, y)

                # Copy the tile onto our frame.
                SDL_RenderCopy(self.__window.renderer, self.map.get_tileset(tile["tileset"])["texture"], srcrect,
                               dstrect)

        # Tell SDL to switch rendering back to the window's frame.
        SDL_SetRenderTarget(self.__window.renderer, None)

        # Give our frame to WindowManager for positioning and display.
        self.__window.frame(self.__frame, True)

    def __del__(self):
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
