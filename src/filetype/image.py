###################################
## Project Driftwood             ##
## image.py                      ##
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

import sys
from io import BytesIO
from sdl2 import *
from sdl2.ext.common import SDLError
from PIL import Image as PILImage


class ImageFile:
    """
    This class represents and abstracts a single image file. The code is mostly a copy of PySDL2's sdl2.ext.load_image,
    adapted to allow for loading from a buffer. The class loads an image with PIL and then converts it into an SDL
    Surface and an SDL Texture.
    """

    def __init__(self, renderer, data):
        """
        ImageFile class initializer.

        @type  renderer: SDL_Renderer
        @param renderer: WindowManager's renderer.
        @type  data: bytes
        @param renderer: Image data from ResourceManager.
        """
        self.pil_image = None
        self.sdl_surface = None
        self.sdl_texture = None
        self.__renderer = renderer
        self.__data = data
        self.__open(self.__data)

    def __open(self, data):
        """
        Open the image data with PIL.
        """
        self.pil_image = PILImage.open(BytesIO(data))
        self.rebuild()

    def rebuild(self):
        """
        Rebuild sdl_surface and sdl_texture from pil_image.
        """
        mode = self.pil_image.mode
        width, height = self.pil_image.size
        rmask = gmask = bmask = amask = 0

        if mode in ("1", "L", "P"):
            # 1 = B/W, 1 bit per byte
            # "L" = greyscale, 8-bit
            # "P" = palette-based, 8-bit
            pitch = width
            depth = 8

        elif mode == "RGB":
            # 3x8-bit, 24bpp
            if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
                rmask = 0x0000FF
                gmask = 0x00FF00
                bmask = 0xFF0000
            else:
                rmask = 0xFF0000
                gmask = 0x00FF00
                bmask = 0x0000FF
            depth = 24
            pitch = width * 3

        elif mode in ("RGBA", "RGBX"):
            # RGBX: 4x8-bit, no alpha
            # RGBA: 4x8-bit, alpha
            if endian.SDL_BYTEORDER == endian.SDL_LIL_ENDIAN:
                rmask = 0x000000FF
                gmask = 0x0000FF00
                bmask = 0x00FF0000
                if mode == "RGBA":
                    amask = 0xFF000000
            else:
                rmask = 0xFF000000
                gmask = 0x00FF0000
                bmask = 0x0000FF00
                if mode == "RGBA":
                    amask = 0x000000FF
            depth = 32
            pitch = width * 4
        else:
            # We do not support CMYK or YCbCr for now
            raise TypeError("unsupported image format")

        pxbuf = self.pil_image.tostring()
        imgsurface = surface.SDL_CreateRGBSurfaceFrom(pxbuf, width, height,
                                                      depth, pitch, rmask,
                                                      gmask, bmask, amask)
        if not imgsurface:
            raise SDLError()
        imgsurface = imgsurface.contents

        if mode == "P":
            # Create a SDL_Palette for the SDL_Surface
            def _chunk(seq, size):
                for x in range(0, len(seq), size):
                    yield seq[x:x + size]

            rgbcolors = self.pil_image.getpalette()
            sdlpalette = pixels.SDL_AllocPalette(len(rgbcolors) // 3)
            if not sdlpalette:
                raise SDLError()
            sdlpalette = sdlpalette.contents
            SDL_Color = pixels.SDL_Color
            for idx, (r, g, b) in enumerate(_chunk(rgbcolors, 3)):
                sdlpalette.colors[idx] = SDL_Color(r, g, b)
            ret = surface.SDL_SetSurfacePalette(imgsurface, sdlpalette)
            # This will decrease the refcount on the palette, so it gets
            # freed properly on releasing the SDL_Surface.
            pixels.SDL_FreePalette(sdlpalette)
            if ret != 0:
                raise SDLError()

        self.sdl_surface = imgsurface
        self.sdl_texture = SDL_CreateTextureFromSurface(self.__renderer, imgsurface)

    def __del__(self):
        SDL_FreeSurface(self.sdl_surface)
        SDL_DestroyTexture(self.sdl_texture)
