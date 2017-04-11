####################################
# Driftwood 2D Game Dev. Suite     #
# windowmanager.py                 #
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
from sdl2.sdlimage import *


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

    def __init__(self, driftwood):
        """WindowManager class initializer.

        Initializes SDL, and creates a window and a renderer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # The resolution that the game wants to pretend it is running at.
        # (See physical_width in __prepare() for comparison.)
        self.logical_width = self.driftwood.config["window"]["width"]
        self.logical_height = self.driftwood.config["window"]["height"]

        # The SDL Window and Renderer.
        self.window = None
        self.renderer = None

        self.__prepare()

    def register(self):
        self.driftwood.tick.register(self._tick, delay=1.0 / self.driftwood.config["window"]["maxfps"],
                                     during_pause=True)

    def title(self, title):
        """Set the window title.

        Args:
            title: The new title to be set.

        Returns:
            True
        """
        SDL_SetWindowTitle(self.window, title.encode())
        return True

    def refresh(self, area=False):
        """Force the window to redraw.

        Args:
            area: Whether to mark the area changed as well.

        Returns:
            True
        """
        self.driftwood.frame.changed = self.driftwood.frame.STATE_CHANGED
        if area:
            self.driftwood.area.changed = True
        return True

    def _tick(self, seconds_past):
        """Tick callback which refreshes the renderer.
        """
        if self.driftwood.frame.changed:
            SDL_RenderSetLogicalSize(self.renderer,
                                     self.logical_width, self.logical_height)  # Set logical size.

            SDL_RenderClear(self.renderer)

            r = SDL_RenderCopy(self.renderer, *self.driftwood.frame._frame)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Window", "SDL", SDL_GetError())

            SDL_RenderSetLogicalSize(self.renderer, 0, 0)  # reset
            self.driftwood.frame.changed -= 1

            SDL_RenderPresent(self.renderer)

    def __prepare(self):
        """Prepare the window for use.

        Create a new window and renderer with the configured settings.
        """
        if SDL_Init(SDL_INIT_EVERYTHING) < 0:  # Couldn't init SDL.
            self.driftwood.log.msg("ERROR", "Window", "SDL", SDL_GetError())
        init_flags = IMG_INIT_JPG | IMG_INIT_PNG
        if IMG_Init(init_flags) & init_flags != init_flags:  # Couldn't init SDL_Image.
            self.driftwood.log.msg("ERROR", "Window", "SDL", SDL_GetError())

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
        if not self.renderer:  # We don't have hardware rendering on this machine.
            self.driftwood.log.info("SDL", "falling back to software renderer")
            self.renderer = SDL_CreateRenderer(self.window, -1, SDL_RENDERER_SOFTWARE)
            if not self.renderer:  # Still no.
                self.driftwood.log.msg("ERROR", "Window", "SDL", SDL_GetError())

        # Pixelated goodness, like a rebel.
        SDL_SetHint(SDL_HINT_RENDER_SCALE_QUALITY, b"nearest")

    def _terminate(self):
        """Cleanup before deletion.
        """
        SDL_DestroyRenderer(self.renderer)
        self.renderer = None
        SDL_DestroyWindow(self.window)
        self.window = None

        IMG_Quit()
        SDL_Quit()
