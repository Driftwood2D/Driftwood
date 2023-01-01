################################
# Driftwood 2D Game Dev. Suite #
# inputmanager.py              #
# Copyright 2014-2017          #
# Sei Satzparad & Paul Merrill #
################################

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
from typing import Optional, TYPE_CHECKING

import pygame as pg
from sdl2 import *
from sdl2.sdlimage import *
from sdl2.sdlttf import *

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class BytesStream:
    """A file-like object that wraps a bytes object which can be given to PyGame in places where it wants a file.

    It is used by PyGame to construct an SDL_RWops object in C, and then passed to various SDL file loading functions
    within PyGame.
    """

    __data: bytes
    __pos: int

    def __init__(self, data: bytes):
        """Construct a BytesSteam that will read data from an in-memory bytes object."""
        self.__data = data
        self.__pos = 0

    def read(self, num: int) -> bytes:
        """Called by PyGame to read from this file-like object.

        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L118
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L642
        """
        start = self.__pos
        end = min(start + num, len(self.__data))
        self.__pos = end
        return self.__data[start:end]

    def seek(self, offset: int, whence: int = 0):
        """Called by PyGame to seek in this file-like object.

        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L136
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L316
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L340
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L559
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L596
        """
        if whence == 0:
            self.__pos = offset
        elif whence == 1:
            self.__pos += offset
        else:
            self.__pos = offset + len(self.__data)
        self.__pos = max(0, min(len(self.__data), self.__pos))
        return self.__pos

    def tell(self) -> int:
        """Called by PyGame to find the current offset in this file-like object.

        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L143
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L569
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L603
        """
        return self.__pos

    def close(self):
        """Called by PyGame to close this file-like object.

        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L150
        @see https://github.com/pygame/pygame/blob/v2.1.3/src_c/rwobject.c#L417
        """
        pass


class AudioFile:
    """This class represents and abstracts a single OGG Vorbis audio file.

    Attributes:
        audio: The PyGame audio handle.
    """

    __data: bytes
    __is_music: bool
    audio: Optional[pg.mixer.Sound]
    driftwood: "Driftwood"

    def __init__(self, driftwood: "Driftwood", data: bytes, is_music: bool = False):
        self.driftwood = driftwood

        self.audio = None
        self.__is_music = is_music
        self.__data = data

        self.__load(self.__data)

    def __load(self, data: bytes) -> None:
        """Load the audio data with pygame."""
        if data:
            try:
                self.audio = pg.mixer.Sound(file=BytesStream(data))
            except Exception as e:
                self.driftwood.log.msg("ERROR", "AudioFile", "__load", "PyGame", e)

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if self.audio:
            self.audio = None
        else:
            self.driftwood.log.msg("WARNING", "AudioFile", "terminate", "subsequent termination of same object")


class FontFile:
    """This class represents and abstracts a single font file.

    Attributes:
        font: The SDL_ttf font handle.
        ptsize: The size of the font in pt.
    """

    __data: bytes
    driftwood: "Driftwood"
    font: Optional[TTF_Font]
    ptsize: int

    def __init__(self, driftwood: "Driftwood", data: bytes, ptsize: int):
        """FontFile class initializer."""
        self.driftwood = driftwood

        self.font = None
        self.ptsize = ptsize
        self.__data = data

        self.__load(self.__data)

    def __load(self, data: bytes) -> None:
        """Load the font data with SDL_TTF."""
        if data:
            self.font = TTF_OpenFontRW(SDL_RWFromConstMem(data, len(data)), 0, self.ptsize)
            if not self.font:
                self.driftwood.log.msg("ERROR", "FontFile", "__load", "SDL_TTF", TTF_GetError())

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if self.font:
            TTF_CloseFont(self.font)
            self.font = None
        else:
            self.driftwood.log.msg("WARNING", "FontFile", "terminate", "subsequent termination of same object")


class ImageFile:
    """This class represents and abstracts a single image file.

    Attributes:
        surface: An SDL surface containing the image.
        texture: An SDL texture containing the image.
    """

    def __init__(self, driftwood: "Driftwood", data: bytes, renderer: SDL_Renderer):
        """ImageFile class initializer."""
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

    def __load(self, data: bytes) -> None:
        """Load the image data with SDL_Image."""
        if data:
            self.surface = IMG_Load_RW(SDL_RWFromConstMem(data, len(data)), 1)
            if not self.surface:
                self.driftwood.log.msg("ERROR", "ImageFile", "__load", "SDL_Image", IMG_GetError())

            self.texture = SDL_CreateTextureFromSurface(self.__renderer, self.surface)
            if not self.texture:
                self.driftwood.log.msg("ERROR", "ImageFile", "__load", "SDL_Image", IMG_GetError())

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if not self.surface and not self.texture:
            self.driftwood.log.msg("WARNING", "ImageFile", "terminate", "subsequent termination of same object")
        if self.surface:
            SDL_FreeSurface(self.surface)
            self.surface = None
        if self.texture:
            SDL_DestroyTexture(self.texture)
            self.texture = None
