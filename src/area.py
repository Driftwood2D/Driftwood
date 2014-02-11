###################################
## Project Driftwood             ##
## tick.py                       ##
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

import json
import math
from sdl2 import *


class AreaManager:
    def __init__(self, config):
        self.config = config
        self.__log = self.config.baseclass.log
        self.__filetype = self.config.baseclass.filetype
        self.__resource = self.config.baseclass.resource
        self.__window = self.config.baseclass.window
        self.__area = []
        self.__map = {}
        self.__tileset = [[]]
        self.__tileset_textures = []
        self.__frame = None
        self.__img = []  # Save images so their textures dob't vanish

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture

        self.config.baseclass.tick.register(self.tick)

    def focus(self, filename):
        if filename in self.__resource:
            self.__map = json.loads(self.__resource[filename])
            self.__prepare_frame()
            self.__prepare_tilesets()
            self.__prepare_layers()
            self.__build_frame()
            self.__log.info("Area", "loaded", filename)
            return True

        else:
            self.__log.log("ERROR", "Area", "no such area", filename)
            return False

    def tick(self):
        pass

    def __prepare_frame(self):
        if self.__frame:
            SDL_DestroyTexture(self.__frame)

        self.__frame = SDL_CreateTexture(self.__window.renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_TARGET,
                                         self.__map["width"] * self.__map["tilewidth"],
                                         self.__map["height"] * self.__map["tileheight"])

    def __prepare_tilesets(self):
        for ts, tileset in enumerate(self.__map["tilesets"]):
            # Request the image for the first tileset.
            self.__img.append(self.__filetype.ImageFile(self.__resource.request(self.__map["tilesets"][ts]["image"],
                                                                                True)))
            self.__tileset_textures.append(self.__img[-1].texture)

            # Calculate width and height in tiles and number of tiles.
            imgw = int(self.__map["tilesets"][ts]["imagewidth"] / self.__map["tilesets"][ts]["tilewidth"])
            imgh = int(self.__map["tilesets"][ts]["imageheight"] / self.__map["tilesets"][ts]["tileheight"])
            imgs = int(imgw * imgh)

            # Precalculate the coordinates of tile graphics in the tileset.
            i = 0
            while i < imgs:
                cx = i % imgw
                cy = math.floor(i / imgw)
                self.__tileset.append([int(cx), int(cy), ts])
                i += 1

    def __prepare_layers(self):
        for l, layer in enumerate(self.__map["layers"]):
            self.__area.append([])

            for t, tile in enumerate(layer["data"]):
                if tile == 0:
                    self.__area[l].append(None)
                    continue

                self.__area[l].append({})

                self.__area[l][t]["srcrect"] = [
                    self.__tileset[tile][0] * self.__map["tilesets"][self.__tileset[tile][2]]["tilewidth"],
                    self.__tileset[tile][1] * self.__map["tilesets"][self.__tileset[tile][2]]["tileheight"],
                    self.__map["tilesets"][self.__tileset[tile][2]]["tilewidth"],
                    self.__map["tilesets"][self.__tileset[tile][2]]["tileheight"]
                ]

                self.__area[l][t]["dstrect"] = [
                    (t % self.__map["width"]) * self.__map["tilesets"][self.__tileset[tile][2]]["tilewidth"],
                    math.floor(t / self.__map["width"]) * self.__map["tilesets"][self.__tileset[tile][2]]["tileheight"],
                    self.__map["tilesets"][self.__tileset[tile][2]]["tilewidth"],
                    self.__map["tilesets"][self.__tileset[tile][2]]["tileheight"]
                ]

                self.__area[l][t]["tileset"] = self.__tileset_textures[self.__tileset[tile][2]]

    def __build_frame(self):
        for l, layer in enumerate(self.__area):
            srcrect, dstrect = SDL_Rect(), SDL_Rect()

            SDL_SetRenderTarget(self.__window.renderer, self.__frame)

            for tile in layer:
                if not tile:
                    continue

                srcrect.x, srcrect.y, srcrect.w, srcrect.h = tile["srcrect"]
                dstrect.x, dstrect.y, dstrect.w, dstrect.h = tile["dstrect"]

                SDL_RenderCopy(self.__window.renderer, tile["tileset"], srcrect, dstrect)

        SDL_SetRenderTarget(self.__window.renderer, None)
        self.__window.frame(self.__frame)

    def __del__(self):
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
        for texture in self.__tileset_textures:
            self.__sdl_destroytexture(texture)
