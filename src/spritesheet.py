################################
# Driftwood 2D Game Dev. Suite #
# spritesheet.py               #
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

from ctypes import byref
from typing import TYPE_CHECKING

from sdl2 import *

if TYPE_CHECKING:
    import entitymanager


class Spritesheet:
    """This class abstracts a sprite sheet.

    Attributes:
        entitymanager: Parent EntityManager instance.

        filename: Filename of the sprite sheet image.
        image: The filetype.ImageFile instance for the sprite sheet image.
        texture: The SDL_Texture for the sprite sheet image.
        imagewidth: Width of the sprite sheet in pixels.
        imageheight: Height of the sprite sheet in pixels.
    """

    def __init__(self, entitymanager: "entitymanager.EntityManager", filename: str):
        """Spritesheet class initializer.

        Args:
            entitymanager: Link back to the parent EntityManager instance.
            filename: Filename of the sprite sheet image.
        """
        self.entitymanager = entitymanager

        self.filename = filename
        self.image = None
        self.texture = None
        self.imagewidth = 0
        self.imageheight = 0
        self.__resource = self.entitymanager.driftwood.resource

        self.__prepare_spritesheet()

    def __prepare_spritesheet(self) -> None:
        self.image = self.__resource.request_image(self.filename)
        self.texture = self.image.texture

        tw, th = c_int(), c_int()
        SDL_QueryTexture(self.texture, None, None, byref(tw), byref(th))
        self.imagewidth, self.imageheight = tw.value, th.value
