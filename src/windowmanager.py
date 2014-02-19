###################################
## Driftwood 2D Game Dev. Suite  ##
## windowmanager.py              ##
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

from ctypes import byref
from ctypes import c_int
from sdl2 import *

import filetype


class WindowManager:
    """The Window Manager

    This class contains the SDL Window, and handles the viewport and display.

    Attributes:
        driftwood: Base class instance.
        window: The SDL Window.
        renderer: The SDL Renderer attached to the window.
    """

    def __init__(self, driftwood):
        """WindowManager class initializer.

        Initializes SDL, and creates a window and a renderer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # The SDL Window and Renderer.
        self.window = None
        self.renderer = None

        # A copy of the imagefile the texture to be framed belongs to, if any.
        self.__imagefile = None

        # A copy of the texture to be framed.
        self.__texture = None

        # The current frame.
        self.__frame = None

        # Whether the frame has been changed since last display.
        self.__changed = False

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture
        self.__sdl_destroyrenderer = SDL_DestroyRenderer
        self.__sdl_destroywindow = SDL_DestroyWindow

        self.__prepare()

        self.driftwood.tick.register(self.tick)

    def __prepare(self):
        """Prepare the window for use.

        Create a new window and renderer with the configured settings.
        """
        SDL_Init(SDL_INIT_EVERYTHING)

        if self.driftwood.config["window"]["fullscreen"]:
            flags = SDL_WINDOW_SHOWN | SDL_WINDOW_FULLSCREEN
        else:
            flags = SDL_WINDOW_SHOWN

        self.window = SDL_CreateWindow(self.driftwood.config["window"]["title"].encode(), SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, self.driftwood.config["window"]["width"],
                                       self.driftwood.config["window"]["height"], flags)
        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)

    def title(self, title):
        """Set the window title.

        Args:
            title: The new title to be set.
        """
        SDL_SetWindowTitle(self.window, title.encode())

    def frame(self, tex, zoom=False):
        """Copy an SDL_Texture or ImageFile frame onto the window, adjusting the viewport accordingly.

        Args:
            tex: SDL_Texture or filetype.ImageFile instance.
            zoom: Whether or not to zoom the texture.
        """
        # Prevent this ImageFile (probably from a script) from losing scope and taking our texture with it.
        if isinstance(tex, filetype.ImageFile):
            self.__imagefile = tex
            self.__texture = self.__imagefile.texture

        # It's just an ordinary texture, probably passed from the engine code.
        else:
            self.__texture = tex

        # Get texture width and height.
        tw, th = c_int(), c_int()
        SDL_QueryTexture(self.__texture, None, None, byref(tw), byref(th))
        tw, th = tw.value, th.value

        # Zoom the texture.
        if zoom:
            tw *= self.driftwood.config["window"]["zoom"]
            th *= self.driftwood.config["window"]["zoom"]

        # Get current window width and height.
        ww, wh = c_int(), c_int()
        SDL_GetWindowSize(self.window, byref(ww), byref(wh))
        ww, wh = ww.value, wh.value

        # Set up viewport calculation variables.
        srcrect, dstrect = SDL_Rect(), SDL_Rect()
        srcrect.x, srcrect.y, srcrect.w, srcrect.h = 0, 0, tw, th
        dstrect.x, dstrect.y, dstrect.w, dstrect.h = 0, 0, ww, wh

        # Area width is smaller than window width. Center by width on area.
        if tw < ww:
            dstrect.x = int(ww/2 - tw/2)
            dstrect.w = tw

        # Area width is larger than window width. Center by width on player.
        # TODO

        # Area height is smaller than window height. Center by height on area.
        if th < wh:
            dstrect.y = int(wh/2 - th/2)
            dstrect.h = th

        # Area height is larger than window height. Center by height on player.
        # TODO

        # Adjust and copy the frame onto the window.
        self.__frame = [self.__texture, srcrect, dstrect]

        # Mark the frame changed.
        self.__changed = True

    def tick(self):
        """Tick callback which refreshes the renderer.
        """
        if self.__changed:
            SDL_RenderClear(self.renderer)
            SDL_RenderCopy(self.renderer, *self.__frame)
            self.__changed = False

        SDL_RenderPresent(self.renderer)

    def __del__(self):
        """WindowManager class destructor.
        """
        if self.__texture:
            self.__sdl_destroytexture(self.__texture)
        if self.__frame:
            self.__sdl_destroytexture(self.__frame)
        self.__sdl_destroyrenderer(self.renderer)
        self.__sdl_destroywindow(self.window)

        SDL_Quit()
