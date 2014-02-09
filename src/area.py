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
        self.__area = {}
        self.__tileset = []
        self.__tileset_texture = None
        self.__frame = None
        self.__img = None  # Save image so its texture doesn't vanish
        self.__imgw, self.__imgh, self.__imgs = 0, 0, 0

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture

        self.config.baseclass.tick.register(self.tick)

    def focus(self, filename):
        if filename in self.__resource:
            self.__area = json.loads(self.__resource[filename])
            self.__prepare_frame()
            self.__prepare_tileset()
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
                                         self.__area["width"] * self.__area["tilewidth"],
                                         self.__area["height"] * self.__area["tileheight"])

    def __prepare_tileset(self):
        # Request the image for the first tileset.
        self.__img = self.__filetype.ImageFile(self.__resource.request(self.__area["tilesets"][0]["image"], True))
        self.__tileset_texture = self.__img.texture

        # Calculate width and height in tiles and number of tiles.
        self.__imgw = int(self.__area["tilesets"][0]["imagewidth"] / self.__area["tilesets"][0]["tilewidth"])
        self.__imgh = int(self.__area["tilesets"][0]["imageheight"] / self.__area["tilesets"][0]["tileheight"])
        self.__imgs = int(self.__imgw * self.__imgh)

        # Precalculate the coordinates of tile graphics in the tileset.
        i = 0
        while i < self.__imgs:
            cx = i % self.__imgw
            cy = math.floor(i / self.__imgw)
            self.__tileset.append([int(cx), int(cy)])
            i += 1

    def __build_frame(self):
        srcrect, dstrect = SDL_Rect(), SDL_Rect()

        SDL_SetRenderTarget(self.__window.renderer, self.__frame)
        for i, tile in enumerate(self.__area["layers"][0]["data"]):
            srcrect.x = self.__tileset[tile-1][0] * self.__area["tilesets"][0]["tilewidth"]
            srcrect.y = self.__tileset[tile-1][1] * self.__area["tilesets"][0]["tileheight"]
            srcrect.w, srcrect.h = self.__area["tilesets"][0]["tilewidth"], self.__area["tilesets"][0]["tileheight"]

            dstrect.x = (i % self.__area["width"]) * self.__area["tilesets"][0]["tilewidth"]
            dstrect.y = math.floor(i / self.__area["width"]) * self.__area["tilesets"][0]["tileheight"]
            dstrect.w, dstrect.h = self.__area["tilesets"][0]["tilewidth"], self.__area["tilesets"][0]["tileheight"]

            SDL_RenderCopy(self.__window.renderer, self.__tileset_texture, srcrect, dstrect)

        SDL_SetRenderTarget(self.__window.renderer, None)
        self.__window.frame(self.__frame)

    def __del__(self):
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
        if self.__tileset_texture:
            self.__sdl_destroytexture(self.__tileset_texture)
