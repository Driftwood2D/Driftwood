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

from sdl2 import *


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
        self.__frame = None

        SDL_Init(SDL_INIT_EVERYTHING)

        if config["window"]["fullscreen"] == True:
            flags = SDL_WINDOW_SHOWN | SDL_WINDOW_FULLSCREEN
        else:
            flags = SDL_WINDOW_SHOWN

        self.window = SDL_CreateWindow(config["window"]["title"].encode(), SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, config["window"]["width"], config["window"]["height"],
                                       flags)
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)

        self.config.baseclass.tick.register(self.tick)

    def frame(self, tex):
        """
        Copy an SDL_Texture frame onto the window.

        @type  tex: SDL_Texture
        @param tex: New frame.
        """
        self.__frame = tex

    def tick(self):
        """
        Tick callback which refreshes the renderer.
        """
        SDL_RenderClear(self.renderer)
        if self.__frame:
            SDL_RenderCopy(self.renderer, self.__frame, None, None)
        SDL_RenderPresent(self.renderer)

    def __del__(self):
        """
        Window class destructor.
        """
        SDL_DestroyWindow(self.window)
        SDL_DestroyRenderer(self.renderer)
        SDL_Quit()
