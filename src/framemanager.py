################################
# Driftwood 2D Game Dev. Suite #
# framemanager.py              #
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

from ctypes import byref, c_ubyte
from typing import List, Tuple, TYPE_CHECKING

from sdl2 import *

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class FrameManager:
    """The Frame Manager

    This class manages the current graphical frame. It allows manipulating and adding content to its back buffer,
    which can then be copied onto the front buffer and framed in the window. Alternatively, a texture or ImageFile
    may be given to replace the current frame. WindowManager queries us for the current frame each tick.

    Attributes:
        driftwood: Base class instance.
        offset: Offset at which to draw the viewport.
        centering: Whether to center on the player in large areas.
        changed: Whether the frame has been changed. [STATE_NOTCHANGED, STATE_BACKBUFFER_NEEDS_UPDATE, STATE_CHANGED]
    """

    def __init__(self, driftwood: "Driftwood"):
        """FrameManager class initializer.

        Initializes frame handling.

        Args:
            driftwood: Base class instance.
        """
        # Mac OS X 10.9 with SDL 2.0.1 does double buffering and needs a second rendering of the same image on
        # still frames.
        #
        # self.STATE_NOTCHANGED, self.STATE_BACKBUFFER_NEEDS_UPDATE, self.STATE_CHANGED = range(3)
        #
        # Fixed in macOS 10.12 and SDL 2.0.5.
        #
        self.STATE_NOTCHANGED, self.STATE_CHANGED = range(2)

        self.driftwood = driftwood
        self._frame = None  # [self.__backbuffer, srcrect, dstrect]

        # Offset at which to draw the viewport.
        self.offset = [0, 0]

        # Whether to center on the player in large areas.
        self.centering = True

        self.__imagefile = None
        self.__backbuffer = None
        self.__overlay = []

        self.changed = self.STATE_NOTCHANGED

    def clear(self) -> bool:
        """Clear the back buffer.

        Returns:
            True if succeeded, False if failed.
        """
        r = SDL_SetRenderTarget(self.driftwood.window.renderer, self.__backbuffer)
        if type(r) is int and r < 0:
            self.driftwood.log.msg("ERROR", "Frame", "clear", "SDL", SDL_GetError())
            return False

        # Clear the current back buffer.
        SDL_RenderClear(self.driftwood.window.renderer)

        # Tell SDL to switch rendering back to the window's frame.
        r = SDL_SetRenderTarget(self.driftwood.window.renderer, None)
        if type(r) is int and r < 0:
            self.driftwood.log.msg("ERROR", "Frame", "clear", "SDL", SDL_GetError())
            return False

        return True

    def prepare(self, width: int, height: int) -> bool:
        """Prepare and clear the back buffer.

        Set up our back buffer as a texture of the specified size. This also clears the back buffer.

        Args:
            width: Width in pixels.
            height: Height in pixels.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(width, int)
            CHECK(height, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Frame", "prepare", "bad argument", e)
            return False

        # Clear backbuffer
        if self.__backbuffer:
            SDL_DestroyTexture(self.__backbuffer)

        # Recreate backbuffer
        self.__backbuffer = SDL_CreateTexture(
            self.driftwood.window.renderer, SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_TARGET, width, height
        )

        if type(self.__backbuffer) is int and self.__backbuffer < 0:
            self.driftwood.log.msg("ERROR", "Frame", "prepare", "SDL", SDL_GetError())
            return False

        return True

    def calc_rects(self) -> None:
        """Calculate the srcrect and dstrect for copying the back buffer onto the window's renderer.

        Can be run after a world update but before drawing starts for a frame.
        """
        # Get texture width and height.
        tw, th = c_int(), c_int()
        SDL_QueryTexture(self.__backbuffer, None, None, byref(tw), byref(th))
        tw, th = tw.value, th.value

        # Both the dstrect and the window size are measured in logical
        # coordinates at this stage.  The transformation to physical
        # coordinates happens below in tick().

        # Set up viewport calculation variables.
        srcrect, dstrect = SDL_Rect(), SDL_Rect()
        srcrect.x, srcrect.y, srcrect.w, srcrect.h = 0, 0, tw, th
        dstrect.x, dstrect.y, dstrect.w, dstrect.h = 0, 0, tw, th

        # Get logical window width and height.
        ww, wh = self.driftwood.window.resolution()

        # Area width is smaller than window width. Center by width on area.
        if tw < ww:
            dstrect.x = int(ww / 2 - tw / 2)

        # Area width is larger than window width. Center by width on player.
        if tw > ww and self.centering:
            if self.driftwood.entity.player:
                playermidx = self.driftwood.entity.player.x + (self.driftwood.entity.player.width / 2)
                prepx = int(ww / 2 - playermidx)

                if prepx > 0:
                    dstrect.x = 0
                elif prepx < ww - tw:
                    dstrect.x = ww - tw
                else:
                    dstrect.x = prepx

            else:
                dstrect.x = int(ww / 2 - tw / 2)

        # Area height is smaller than window height. Center by height on area.
        if th < wh:
            dstrect.y = int(wh / 2 - th / 2)

        # Area height is larger than window height. Center by height on player.
        if th > wh and self.centering:
            if self.driftwood.entity.player:
                playermidy = self.driftwood.entity.player.y + (self.driftwood.entity.player.height / 2)
                prepy = int(wh / 2 - playermidy)

                if prepy > 0:
                    dstrect.y = 0
                elif prepy < wh - th:
                    dstrect.y = wh - th
                else:
                    dstrect.y = prepy

            else:
                dstrect.y = int(wh / 2 - th / 2)

        # Adjust the viewport offset.
        dstrect.x += self.offset[0]
        dstrect.y += self.offset[1]

        # Adjust and copy the frame onto the viewport.
        self._frame = [self.__backbuffer, srcrect, dstrect]

    def finish_frame(self) -> bool:
        """Draw the last components of a frame, including widgets and overlays.

        Requires that calc_rects have already been called for the frame.

        Returns:
            True if succeeded, False if failed.
        """
        # Tell WidgetManager it should draw the widgets now.
        self.driftwood.widget._draw_widgets()

        dstrect = self._frame[2]

        # Draw overlays, taking into account the viewport position.
        for overlay in self.__overlay:
            overlay[2][0] -= dstrect.x
            overlay[2][1] -= dstrect.y
            ok = self.copy(*overlay)
            if not ok:
                self.driftwood.log.msg("ERROR", "Frame", "finish_frame", "failed to copy overlay", str(overlay))
                self.__overlay = []
                return False
        self.__overlay = []  # These should only be texture references.

        # Mark the frame changed.
        self.changed = self.STATE_CHANGED

        return True

    def copy(
        self,
        tex: SDL_Texture,
        srcrect: List[int],
        dstrect: List[int],
        alpha: int = None,
        blendmode: int = None,
        colormod: Tuple[int, int, int] = None,
    ) -> bool:
        """Copy a texture onto the back buffer.

        Copy the source rectangle from the texture tex to the destination rectangle in our back buffer.

        Args:
            tex: Texture to copy.
            srcrect: Source rectangle [x, y, w, h]
            dstrect: Destination rectangle [x, y, w, h]
            alpha: (optional) An additional alpha value multiplied into the copy.
            blendmode: (optional) Which SDL2 blend mode to use.
            colormod: (optional) An additional color value multiplied into the copy.
        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(tex, SDL_Texture)
            CHECK(srcrect, list, _equals=4)
            CHECK(dstrect, list, _equals=4)
            CHECK(alpha, int)
            CHECK(blendmode, int)
            CHECK(colormod, list)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Frame", "copy", "bad argument", e)
            return False

        # We have to finish before we return.
        ret = True

        # Set up the rectangles.
        src = SDL_Rect()
        dst = SDL_Rect()
        src.x, src.y, src.w, src.h = srcrect
        dst.x, dst.y, dst.w, dst.h = dstrect

        r = SDL_SetRenderTarget(self.driftwood.window.renderer, self.__backbuffer)
        if type(r) is int and r < 0:
            self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
            ret = False

        prev_alpha = None
        prev_blendmode = None
        prev_colormod = None

        if alpha:
            prev_alpha = c_ubyte()
            r = SDL_GetTextureAlphaMod(tex, byref(prev_alpha))
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

            r = SDL_SetTextureAlphaMod(tex, alpha)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        if blendmode:
            prev_blendmode = c_int()
            r = SDL_GetTextureBlendMode(tex, byref(prev_blendmode))
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

            r = SDL_SetTextureBlendMode(tex, blendmode)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        if colormod:
            prev_colormod = (c_ubyte(), c_ubyte(), c_ubyte())
            r = SDL_GetTextureColorMod(tex, byref(prev_colormod[0]), byref(prev_colormod[1]), byref(prev_colormod[2]))
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

            r = SDL_SetTextureColorMod(tex, *colormod)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        # Copy the texture onto the back buffer.
        r = SDL_RenderCopy(self.driftwood.window.renderer, tex, src, dst)
        if type(r) is int and r < 0:
            self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
            ret = False

        if alpha:
            r = SDL_SetTextureAlphaMod(tex, prev_alpha.value)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        if blendmode:
            r = SDL_SetTextureBlendMode(tex, prev_blendmode.value)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        if colormod:
            r = SDL_SetTextureColorMod(tex, prev_colormod[0].value, prev_colormod[1].value, prev_colormod[2].value)
            if type(r) is int and r < 0:
                self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
                ret = False

        # Tell SDL to switch rendering back to the window's frame.
        r = SDL_SetRenderTarget(self.driftwood.window.renderer, None)
        if type(r) is int and r < 0:
            self.driftwood.log.msg("ERROR", "Frame", "copy", "SDL", SDL_GetError())
            ret = False

        return ret

    def overlay(self, tex: SDL_Texture, srcrect: List[int], dstrect: List[int]) -> bool:
        """Schedule to copy a texture directly onto the window, ignoring any frame or viewport calculations.

        Args:
            tex: Texture to copy.
            srcrect: Source rectangle [x, y, w, h]
            dstrect: Destination rectangle [x, y, w, h]

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(tex, SDL_Texture)
            CHECK(srcrect, list, _equals=4)
            CHECK(dstrect, list, _equals=4)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Frame", "overlay", "bad argument", e)
            return False

        # Set up the rectangles.
        self.__overlay.append([tex, list(srcrect), list(dstrect)])

        return True

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if self.__backbuffer:
            SDL_DestroyTexture(self.__backbuffer)
            self.__backbuffer = None
        if self._frame:
            self._frame = None
