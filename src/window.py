###################################
## Project Driftwood             ##
## window.py                     ##
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

from ctypes import byref
from ctypes import c_int
from sdl2 import *

import filetype


class WindowManager:
    """
    SDL window manager class.
    """

    def __init__(self, config):
        """
        WindowManager class initializer. Initializes SDL, and creates a window and a renderer.

        @type  config: object
        @param config: The Config class instance.
        """
        self.config = config
        self.window = None
        self.renderer = None
        self.__frame = None
        self.__imagefile = None

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture
        self.__sdl_destroyrenderer = SDL_DestroyRenderer
        self.__sdl_destroywindow = SDL_DestroyWindow

        self.__prepare_window()

        self.config.baseclass.tick.register(self.tick)

    def __prepare_window(self):
        """
        Prepare the window for use.
        """
        SDL_Init(SDL_INIT_EVERYTHING)

        if self.config["window"]["fullscreen"]:
            flags = SDL_WINDOW_SHOWN | SDL_WINDOW_FULLSCREEN
        else:
            flags = SDL_WINDOW_SHOWN

        self.window = SDL_CreateWindow(self.config["window"]["title"].encode(), SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, self.config["window"]["width"],
                                       self.config["window"]["height"], flags)
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)

    def title(self, title):
        SDL_SetWindowTitle(self.window, title.encode())

    def frame(self, tex):
        """
        Copy an SDL_Texture frame onto the window.

        @type  tex: SDL_Texture
        @param tex: New frame.
        """
        # Prevent this ImageFile (probably from a script) from losing scope and taking our texture with it.
        if isinstance(tex, filetype.ImageFile):
            self.__imagefile = tex
            texture = self.__imagefile.texture

        # It's just an ordinary texture, probably passed from the engine code.
        else:
            texture = tex

        # Variables for viewport calculation.
        tw, th = c_int(), c_int()
        SDL_QueryTexture(texture, None, None, byref(tw), byref(th))
        tw, th = tw.value, th.value
        srcrect, dstrect = SDL_Rect(), SDL_Rect()
        srcrect.x, srcrect.y, srcrect.w, srcrect.h = 0, 0, tw, th
        dstrect.x, dstrect.y, dstrect.w, dstrect.h = 0, 0, self.config["window"]["width"],\
                                                     self.config["window"]["height"]

        # Area width is smaller than window width.
        if tw < self.config["window"]["width"]:
            dstrect.x = int(self.config["window"]["width"]/2 - tw/2)
            dstrect.w = tw

        # Area width is larger than window width
        elif tw > self.config["window"]["width"]:
            srcrect.x = 0
            srcrect.w = self.config["window"]["width"]

        # Area height is smaller than window height
        if th < self.config["window"]["height"]:
            dstrect.y = int(self.config["window"]["height"]/2 - th/2)
            dstrect.h = th

        # Area height is larger than window height
        elif th > self.config["window"]["height"]:
            srcrect.y = 0
            srcrect.h = self.config["window"]["height"]

        # Adjust and copy the frame onto the window.
        self.__frame = [texture, srcrect, dstrect]

    def tick(self):
        """
        Tick callback which refreshes the renderer.
        """
        SDL_RenderClear(self.renderer)
        if self.__frame:
            SDL_RenderCopy(self.renderer, *self.__frame)
        SDL_RenderPresent(self.renderer)

    def __del__(self):
        """
        Window class destructor.
        """
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
        self.__sdl_destroyrenderer(self.renderer)
        self.__sdl_destroywindow(self.window)

        SDL_Quit()
