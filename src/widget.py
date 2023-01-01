################################
# Driftwood 2D Game Dev. Suite #
# widget.py                    #
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
from typing import List, Optional, TYPE_CHECKING

from sdl2 import *
from sdl2.sdlttf import *

import filetype

if TYPE_CHECKING:
    import widgetmanager


class Widget:
    """This parent class represents a widget. It is subclassed by one of the widget types.

    Attributes:
        manager: Link back to the WidgetManager.
        wid: Widget id of this widget.
        active: Whether the widget is active or not.
        selected: Whether this widget is the selected widget.
        x: The x position of the widget, relative to its parent (if one exists).
        y: The y position of the widget, relative to its parent (if one exists).
        realx: The real x position of the widget, relative to the viewport.
        realy: The real y position of the widget, relative to the viewport.
        width: The width of the widget.
        height: The height of the widget.
        parent: The parent of the widget if one exists. Otherwise None.

    """

    def __init__(
        self,
        manager: "widgetmanager.WidgetManager",
        wid: int,
        parent: Optional[int],
        x: int,
        y: int,
        width: int,
        height: int,
    ):
        self.manager = manager
        self.wid = wid

        self.active = False
        self.selected = False
        self.x = x
        self.y = y
        self.realx = None
        self.realy = None
        self.width = width
        self.height = height
        self.parent = parent

    def dstrect(self) -> List[int]:
        """Return the destination rectangle for drawing the widget."""
        return [self.realx, self.realy, self.width, self.height]


class ContainerWidget(Widget):
    """This subclass represents a Container widget.

    Attributes:
        image: The graphic for the container, if it has one.
        contains: List of widgets contained by this container.
    """

    def __init__(
        self,
        manager: "widgetmanager.WidgetManager",
        wid: int,
        parent: Optional[int],
        image: filetype.ImageFile,
        x: Optional[int],
        y: Optional[int],
        width: int,
        height: int,
    ):
        super(ContainerWidget, self).__init__(manager, wid, parent, x, y, width, height)

        self.image = image
        self.contains = []

    def srcrect(self) -> Optional[List[int]]:
        """Return the source rectangle for the widget graphic, if it has one."""
        if self.image:
            return [0, 0, self.image.width, self.image.height]
        return None

    def _prepare(self) -> Optional[bool]:
        if self.wid == 0:
            self.x = 0
            self.realx = 0
            self.y = 0
            self.realy = 0

        # Center if not in a container.
        elif self.parent == 0:
            window_logical_width, window_logical_height = self.manager.driftwood.window.resolution()
            if self.x is None:
                self.x = (window_logical_width - self.width) // 2
            self.realx = self.x
            if self.y is None:
                self.y = (window_logical_height - self.height) // 2
            self.realy = self.y

        # Register and center if in a container.
        elif type(self.manager.widgets[self.parent]) is ContainerWidget:
            container = self.manager.widgets[self.parent]
            container.contains.append(self.wid)
            if container.realx is not None and container.realy is not None:  # Set the adjusted x and y.
                # Either center or place in a defined position.
                if self.x is None:
                    self.realx = container.realx + (container.width - self.width) // 2
                else:
                    self.realx = self.x + container.realx

                if self.y is None:
                    self.realy = container.realy + (container.height - self.height) // 2
                else:
                    self.realy = self.y + container.realy

        # Fake container.
        else:
            self.manager.driftwood.log.msg(
                "ERROR", "Widget", "ContainerWidget", "_prepare", "not a container", self.parent
            )
            return None

        return True


class TextWidget(Widget):
    """This subclass represents a text widget.

    Attributes:
        contents: The text content of the widget.
        font: FontFile for the font being used.
        color: The color of the font.
        ptsize: The size of the font in pt.
        textwidth: The width of the text in pixels.
        textheight: The height of the text in pixels.
        texture: A texture containing the rendered graphic for the text.
    """

    def __init__(
        self,
        manager: "widgetmanager.WidgetManager",
        wid: int,
        parent: int,
        contents: str,
        font: filetype.FontFile,
        ptsize: int,
        x: Optional[int],
        y: Optional[int],
        width: Optional[int],
        height: Optional[int],
        color: str,
    ):
        super(TextWidget, self).__init__(manager, wid, parent, x, y, width, height)

        self.contents = contents
        self.font = font
        self.color = color
        self.ptsize = ptsize
        self.textwidth = None
        self.textheight = None
        self.texture = None

    def srcrect(self) -> Optional[List[int]]:
        if self.texture:
            return [0, 0, self.textwidth, self.textheight]
        return None

    def _prepare(self) -> Optional[bool]:
        # Get text width and height.
        tw, th = c_int(), c_int()
        TTF_SizeUTF8(self.font.font, self.contents.encode(), byref(tw), byref(th))
        self.textwidth, self.textheight = tw.value, th.value

        # Set width and height if not overridden.
        if self.width is None:
            self.width = tw.value
        if self.height is None:
            self.height = th.value

        # Center if not in a container.
        if self.parent == 0:
            window_logical_width, window_logical_height = self.manager.driftwood.window.resolution()
            if self.x is None:
                self.x = (window_logical_width - self.width) // 2
            self.realx = self.x
            if self.y is None:
                self.y = (window_logical_height - self.height) // 2
            self.realy = self.y

        # Register and center if in a container.
        elif type(self.manager.widgets[self.parent]) is ContainerWidget:
            container = self.manager.widgets[self.parent]
            container.contains.append(self.wid)
            if container.realx is not None and container.realy is not None:  # Set the adjusted x and y.
                # Either center or place in a defined position.
                if self.x is None:
                    self.realx = container.realx + (container.width - self.width) // 2
                elif self.realx is None:
                    self.realx = self.x + container.realx
                else:
                    self.realx += container.realx

                if self.y is None:
                    self.realy = container.realy + (container.height - self.height) // 2
                elif self.realy is None:
                    self.realy = self.y + container.realy
                else:
                    self.realy += container.realy

        # Fake container.
        else:
            self.manager.driftwood.log.msg("ERROR", "Widget", "TextWidget", "_prepare", "not a container", self.parent)
            return None

        # Render.
        color_temp = SDL_Color()
        color_temp.r, color_temp.g, color_temp.b, color_temp.a = (
            int(self.color[0:2], 16),
            int(self.color[2:4], 16),
            int(self.color[4:6], 16),
            int(self.color[6:8], 16),
        )
        surface_temp = TTF_RenderUTF8_Solid(self.font.font, self.contents.encode(), color_temp)

        # Convert to a texture we can use internally.
        if surface_temp:
            self.texture = SDL_CreateTextureFromSurface(self.manager.driftwood.window.renderer, surface_temp)
            SDL_FreeSurface(surface_temp)
            if not self.texture:
                self.manager.driftwood.log.msg("ERROR", "Widget", "TextWidget", "_prepare", "SDL", SDL_GetError())
                return None
        else:
            self.manager.driftwood.log.msg("ERROR", "Widget", "TextWidget", "_prepare", "TTF", TTF_GetError())
            return None

        return True

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if self.texture:
            SDL_DestroyTexture(self.texture)
            self.texture = None
