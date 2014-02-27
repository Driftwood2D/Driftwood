###################################
## Driftwood 2D Game Dev. Suite  ##
## filetype.py                   ##
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
from sdl2.sdlimage import *


class AudioFile:
    """This class represents and abstracts a single OGG Vorbis audio file.
    """

    def __init__(self, data):
        self.__data = data
        self.__open(self.__data)

    def __open(self, data):
        pass
        # TODO: Complicated magic with Mix_LoadMUS_RW


class ImageFile:
    """This class represents and abstracts a single image file.
    """

    def __init__(self, data, renderer):
        """
        ImageFile class initializer.

        @type  data: bytes
        @param data: Image data from ResourceManager.
        """
        self.texture = None
        self.__renderer = renderer
        self.__data = data

        # We need to save SDL's destructors because their continued existence is undefined during shutdown.
        self.__sdl_destroytexture = SDL_DestroyTexture

        self.__load(self.__data)

        # Get image width and height.
        tw, th = c_int(), c_int()
        SDL_QueryTexture(self.texture, None, None, byref(tw), byref(th))
        self.width, self.height = tw.value, th.value

    def __load(self, data):
        """
        Load the image data with SDL_Image.
        """
        if data:
            img = IMG_Load_RW(SDL_RWFromConstMem(data, len(data)), 1)
            self.texture = SDL_CreateTextureFromSurface(self.__renderer, img)
            SDL_FreeSurface(img)

    def __del__(self):
        if self.texture:
            self.__sdl_destroytexture(self.texture)
