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
        logical_width: The window's width in pixels.
        logical_height: The window's height in pixels.
    """

    # Mac OS X 10.9 with SDL 2.0.1 does double buffering and needs a second rendering of the same image on still frames.
    NOTCHANGED, BACKBUFFER_NEEDS_UPDATE, CHANGED = range(3)

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

        # The resolution that the game wants to pretend it is running at.
        # (See physical_width in __prepare() for comparison.)
        self.logical_width = self.driftwood.config["window"]["width"]
        self.logical_height = self.driftwood.config["window"]["height"]

        # A copy of the imagefile the texture to be framed belongs to, if any.
        self.__imagefile = None

        # A copy of the texture to be framed.
        self.__texture = None

        # The current frame.
        self.__frame = None

        # Whether the frame has been changed since last display.
        self.__changed = WindowManager.NOTCHANGED

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
            # Desktop's current width and height
            physical_width = 0
            physical_height = 0

            # No video mode change
            flags = SDL_WINDOW_FULLSCREEN_DESKTOP
        else:
            # 1-to-1 mapping between logical and physical pixels
            physical_width = self.logical_width
            physical_height = self.logical_height
            flags = 0

        flags |= SDL_WINDOW_ALLOW_HIGHDPI
        self.window = SDL_CreateWindow(self.driftwood.config["window"]["title"].encode(), SDL_WINDOWPOS_CENTERED,
                                       SDL_WINDOWPOS_CENTERED, physical_width, physical_height, flags)

        self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC)

        # Pixelated goodness, like a rebel.
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b"nearest")

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

        # Both the dstrect and the window size are measured in logical
        # coordinates at this stage.  The transformation to physical
        # coordinates happens below in tick().

        # Set up viewport calculation variables.
        srcrect, dstrect = SDL_Rect(), SDL_Rect()
        srcrect.x, srcrect.y, srcrect.w, srcrect.h = 0, 0, tw, th
        dstrect.x, dstrect.y, dstrect.w, dstrect.h = 0, 0, tw, th

        # Get logical window width and height.
        ww = self.logical_width
        wh = self.logical_height

        # Area width is smaller than window width. Center by width on area.
        if tw < ww:
            dstrect.x = int(ww/2 - tw/2)

        # Area width is larger than window width. Center by width on player.
        if tw > ww:
            if self.driftwood.entity.player:
                playermidx = self.driftwood.entity.player.x + (self.driftwood.entity.player.width / 2)
                prepx = int(ww/2 - playermidx*2)

                if prepx > 0:
                    dstrect.x = 0
                elif prepx < ww - tw:
                    dstrect.x = ww - tw
                else:
                    dstrect.x = prepx

            else:
                dstrect.y = int(wh/2 - th/2)

        # Area height is smaller than window height. Center by height on area.
        if th < wh:
            dstrect.y = int(wh/2 - th/2)

        # Area height is larger than window height. Center by height on player.
        if th > wh:
            if self.driftwood.entity.player:
                playermidy = self.driftwood.entity.player.y + (self.driftwood.entity.player.height / 2)
                prepy = int(wh/2 - playermidy*2)

                if prepy > 0:
                    dstrect.y = 0
                elif prepy < wh - th:
                    dstrect.y = wh - th
                else:
                    dstrect.y = prepy

            else:
                dstrect.y = int(wh/2 - th/2)

        # Adjust and copy the frame onto the window.
        self.__frame = [self.__texture, srcrect, dstrect]

        # Mark the frame changed.
        self.__changed = WindowManager.CHANGED

    def tick(self, seconds_past):
        """Tick callback which refreshes the renderer.
        """
        if self.__changed:
            SDL_RenderSetLogicalSize(self.renderer,
                self.logical_width, self.logical_height) # set

            SDL_RenderClear(self.renderer)
            SDL_RenderCopy(self.renderer, *self.__frame)

            SDL_RenderSetLogicalSize(self.renderer, 0, 0) # reset
            self.__changed -= 1

            SDL_RenderPresent(self.renderer)

    def refresh(self):
        """Force the window to redraw.
        """
        self.__changed = WindowManager.CHANGED

    def __del__(self):
        """WindowManager class destructor.
        """
        if self.__texture:
            self.__sdl_destroytexture(self.__texture)
        if self.__frame:
            self.__sdl_destroytexture(self.__frame[0])
        self.__sdl_destroyrenderer(self.renderer)
        self.__sdl_destroywindow(self.window)

        SDL_Quit()
