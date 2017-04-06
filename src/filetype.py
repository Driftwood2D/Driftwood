####################################
# Driftwood 2D Game Dev. Suite     #
# inputmanager.py                  #
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

from ctypes import byref, c_int
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlmixer import *
from sdl2.sdlttf import *


class AudioFile:
    """This class represents and abstracts a single OGG Vorbis audio file.
    """

    def __init__(self, driftwood, data, music=False):
        self.driftwood = driftwood

        self.audio = None
        self.__is_music = music
        self.__data = data

        self.__load(self.__data)

    def __load(self, data):
        """Load the audio data with SDL_Mixer.
        """
        if data:
            if self.__is_music:
                self.audio = Mix_LoadMUS_RW(SDL_RWFromConstMem(data, len(data)), 1)
            else:
                self.audio = Mix_LoadWAV_RW(SDL_RWFromConstMem(data, len(data)), 1)

            if not self.audio:
                self.driftwood.log.msg("ERROR", "AudioFile", "SDL_Mixer", SDL_GetError())

    def _terminate(self):
        """Cleanup before deletion.
        """
        if self.__is_music:
            Mix_FreeMusic(self.audio)
            self.audio = None
        else:
            Mix_FreeChunk(self.audio)
            self.audio = None
        if self.driftwood.cache.enabled:
            self.driftwood.cache._reverse_purge(self)

    def __del__(self):
        """Best effort to cleanup properly if deleted by a script.
        """
        self._terminate()


class FontFile:
    """This class represents and abstracts a single font file.
    """
    def __init__(self, driftwood, data, ptsize):
        """FontFile class initializer.
        """
        self.driftwood = driftwood

        self.font = None
        self.ptsize = ptsize
        self.__data = data

        self.__load(self.__data)

    def __load(self, data):
        """Load the font data with SDL_TTF.
        """
        if data:
            self.font = TTF_OpenFontRW(SDL_RWFromConstMem(data, len(data)), 0, self.ptsize)
            if not self.font:
                self.driftwood.log.msg("ERROR", "FontFile", "SDL_TTF", TTF_GetError())

    def _terminate(self):
        if self.font:
            TTF_CloseFont(self.font)
            self.font = None
        if self.driftwood.cache.enabled:
            self.driftwood.cache._reverse_purge(self)

    def __del__(self):
        """Best effort to cleanup properly if deleted by a script.
        """
        self._terminate()


class ImageFile:
    """This class represents and abstracts a single image file.
    """

    def __init__(self, driftwood, data, renderer):
        """ImageFile class initializer.
        """
        self.driftwood = driftwood

        self.surface = None
        self.texture = None
        self.__renderer = renderer
        self.__data = data

        self.__load(self.__data)

        # Get image width and height.
        tw, th = c_int(), c_int()
        SDL_QueryTexture(self.texture, None, None, byref(tw), byref(th))
        self.width, self.height = tw.value, th.value

    def __load(self, data):
        """Load the image data with SDL_Image.
        """
        if data:
            self.surface = IMG_Load_RW(SDL_RWFromConstMem(data, len(data)), 1)
            if not self.surface:
                self.driftwood.log.msg("ERROR", "ImageFile", "SDL_Image", IMG_GetError())

            self.texture = SDL_CreateTextureFromSurface(self.__renderer, self.surface)
            if not self.texture:
                self.driftwood.log.msg("ERROR", "ImageFile", "SDL_Image", IMG_GetError())

    def _terminate(self):
        if self.surface:
            SDL_FreeSurface(self.surface)
            self.surface = None
        if self.texture:
            SDL_DestroyTexture(self.texture)
            self.texture = None
        if self.driftwood.cache.enabled:
            self.driftwood.cache._reverse_purge(self)

    def __del__(self):
        """Best effort to cleanup properly if deleted by a script.
        """
        self._terminate()
