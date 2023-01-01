################################
# Driftwood 2D Game Dev. Suite #
# widgetmanager.py             #
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

from typing import Dict, ItemsView, Optional, TYPE_CHECKING

from sdl2.ext import *
from sdl2.sdlttf import *

from check import CHECK, CheckFailure
import widget
import widgettree

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class WidgetManager:
    """The Widget Manager

    This class keeps track of widgets. These are things like text dialogs and UI elements.

    Attributes:
        driftwood: Base class instance.
        widgets: The dictionary of widgets, sorted by widget id.
        selected: Whether or not this widget is the selected widget. ex. a selected button in a UI menu.
    """

    driftwood: "Driftwood"
    widgets: Dict[int, widget.Widget]

    def __init__(self, driftwood: "Driftwood"):
        self.driftwood = driftwood

        self.widgets = {}
        self.trees = []
        self.selected = None

        self.__last_wid = 0

        self.__spritefactory = None  # The sdlext sprite factory.
        self.__uifactory = None  # The sdlext ui factory.
        self.__uiprocessor = None  # The sdlext ui processor.

        self.__prepare()
        self.__insert_root_widget()

    def __contains__(self, wid: int) -> bool:
        if self.widget(wid):
            return True
        return False

    def __getitem__(self, wid: int) -> Optional["widget.Widget"]:
        return self.widget(wid)

    def __delitem__(self, wid) -> bool:
        return self.kill(wid)

    def __iter__(self) -> ItemsView:
        return self.widgets.items()

    def load(self, filename: str, template_vars: dict) -> Optional[list]:
        """Widget Tree Loader

        Loads and inserts a Jinja2 templated JSON descriptor file (a "widget tree") which defines one or more
        widgets to place on the screen.

        Args:
            * filename: Filename of the widget tree to load and insert.
            * template_vars: A dictionary of variables to apply to the Jinja2 template.

        Returns a list of widgets created if succeeded, None if failed.
        """
        if template_vars is None:
            template_vars = {}
        tree = widgettree.WidgetTree(self, filename, template_vars)
        self.trees.append(tree)
        return tree.widgets

    def select(self, wid: int) -> bool:
        """Select the specified widget. Previously selected widget is released.

        An example is selecting a button in a menu or selecting a text input box, out of the other widgets on
        screen.

        Args:
             wid: Widget ID of the widget to select.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(wid, int, _min=0)
        except CheckFailure as ex:
            self.driftwood.log.msg("ERROR", "Widget", "select", "bad argument", ex)
            return False

        if wid not in self.widgets:
            self.driftwood.log.msg("ERROR", "Widget", "select", "Cannot select nonexistent widget", wid)
            return False
        if self.selected is not None:
            self.widgets[self.selected].selected = False
        self.widgets[wid].selected = True
        self.selected = wid
        return True

    def release(self) -> bool:
        """Release the currently selected widget so that no widgets are selected.

        Returns:
            True if succeeded, False if failed.
        """
        if self.selected is None:
            self.driftwood.log.msg("ERROR", "Widget", "release", "Cannot release if no widget selected")
            return False
        self.widgets[self.selected].selected = False
        self.selected = None
        return True

    def insert_container(
        self,
        imagefile: str = None,
        parent: int = None,
        x: int = None,
        y: int = None,
        width: int = 0,
        height: int = 0,
        active: bool = True,
    ) -> Optional[int]:
        """Create a new container widget.

        A container widget can have a background image, and other widgets can be contained by it. Widgets in a
        container are drawn together and the container's x and y positions are added to the widget's x and y
        positions.

        All widgets except for text widgets are containers.

        Args:
            imagefile: If set, filename of the image file to use as a background.
            parent: If set, the wid of the parent container.
            x: The x position of the container on the window. Center if None.
            y: The y position of the container on the window. Center if None.
            width: The width of the container.
            height: The height of the container.
            active: Whether to make the widget active right away.

        Returns:
            Widget ID of the new container widget if succeeded, None if failed.
        """
        # Input Check
        try:
            if imagefile is not None:
                CHECK(imagefile, str)
            if parent is not None:
                CHECK(parent, int, _min=0)
            else:
                parent = 0
            if x is not None:
                CHECK(x, int, _min=0)
            if y is not None:
                CHECK(y, int, _min=0)
            CHECK(width, int, _min=0)
            CHECK(height, int, _min=0)
            CHECK(active, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "insert_container", "bad argument", e)
            return None

        self.__last_wid += 1

        if imagefile:  # It has a background.
            image = self.driftwood.resource.request_image(imagefile)
            if not image:
                self.driftwood.log.msg("ERROR", "Widget", "insert_container", "no such image", imagefile)
                return None
        else:
            image = None

        new_widget = widget.ContainerWidget(self, self.__last_wid, parent, image, x, y, width, height)
        self.widgets[self.__last_wid] = new_widget

        ret = new_widget._prepare()
        if ret is None:
            if new_widget.wid == 0:
                self.driftwood.log.msg("ERROR", "Widget", "insert_container", "could not create root widget")
            else:
                self.driftwood.log.msg("ERROR", "Widget", "insert_container", "could not create container widget")
            return None

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def insert_text(
        self,
        contents: str,
        fontfile: str,
        ptsize: int,
        parent: int = None,
        x: int = None,
        y: int = None,
        width: int = None,
        height: int = None,
        color: str = "000000FF",
        active: bool = True,
    ):
        """Create a new text widget.

        A text widget puts text on the screen. It cannot have a background image, but can have a color.

        Args:
            contents: The contents of the text.
            fontfile: Filename of the font to render the text with.
            ptsize: The point size of the text.
            parent: If set, the wid of the parent container.
            x: The x position of the text on the window. Center if None.
            y: The y position of the text on the window. Center if None.
            width: The width of the text. If None don't alter it.
            height: The height of the container. If None don't alter it.
            color: The color and alpha to draw the text in.
            active: Whether to make the widget active right away.

        Returns:
            Widget ID of the new text widget if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(contents, str)
            CHECK(fontfile, str)
            CHECK(ptsize, int, _min=1)
            if parent is not None:
                CHECK(parent, int, _min=0)
            else:
                parent = 0
            if x is not None:
                CHECK(x, int, _min=-1)
            if y is not None:
                CHECK(y, int, _min=-1)
            if width is not None:
                CHECK(width, int, _min=-1)
            if height is not None:
                CHECK(height, int, _min=-1)
            CHECK(color, str, _equals=8)
            CHECK(active, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "insert_text", "bad argument", e)
            return None

        self.__last_wid += 1

        font = self.driftwood.resource.request_font(fontfile, ptsize)
        if not font or not font.font:
            self.driftwood.log.msg("ERROR", "Widget", "insert_text", "no such font", fontfile)
            return None

        new_widget = widget.TextWidget(
            self, self.__last_wid, parent, contents, font, ptsize, x, y, width, height, color
        )
        self.widgets[self.__last_wid] = new_widget

        ret = new_widget._prepare()
        if ret is None:
            self.driftwood.log.msg("ERROR", "Widget", "insert_text", "could not create text widget")
            return None

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def activate(self, wid: int) -> bool:
        """Activate a widget. This widget becomes visible.

        Args:
            wid: Widget id of widget to activate.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(wid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "activate", "bad argument", e)
            return False

        if wid in self.widgets:
            self.widgets[wid].active = True
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "activate", "attempt to activate nonexistent widget", wid)
        return False

    def deactivate(self, wid: int) -> bool:
        """Deactivate a widget. This widget becomes invisible.

        Args:
            wid: Widget id of widget to deactivate.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(wid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "deactivate", "bad argument", e)
            return False

        if wid in self.widgets:
            self.widgets[wid].active = False
            self.driftwood.area.changed = False
            return True
        self.driftwood.log.msg("ERROR", "Widget", "deactivate", "attempt to deactivate nonexistent widget", wid)
        return False

    def kill(self, wid: int) -> bool:
        """Kill a widget.

        Args:
            wid: Widget id of widget to kill.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(wid, int, _min=1)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "kill", "bad argument", e)
            return False

        if wid in self.widgets.items():
            if getattr(self.widgets[wid], "_terminate", None):
                self.widgets[wid]._terminate()
            del self.widgets[wid]
            self.driftwood.area.changed = True
            return True
        self.driftwood.log.msg("ERROR", "Widget", "kill", "attempt to kill nonexistent widget", wid)
        return False

    def widget(self, wid: int) -> Optional[widget.Widget]:
        """Get a widget by widget id.

        Args:
            wid: The widget id of the widget to return.

        Returns:
            Widget instance if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(wid, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "widget", "bad argument", e)
            return None

        if wid in self.widgets:
            return self.widgets[wid]
        return None

    def reset(self) -> bool:
        """Destroy all widgets."""
        for item in self.widgets.items():
            if getattr(item, "_terminate", None):
                item._terminate()
        self.widgets = {}
        self.selected = None
        self.__insert_root_widget()
        return True

    def _draw_widgets(self) -> None:
        """Copy the widgets into FrameManager. This is signaled by AreaManager once the area is drawn."""
        for wid in sorted(self.widgets.keys()):
            if self.widgets[wid].active and self.widgets[wid].srcrect():  # It's visible, draw it.
                # But ignore inactive containers.
                if (not self.widgets[wid].parent) or self.widgets[self.widgets[wid].parent].active:
                    srcrect = self.widgets[wid].srcrect()
                    dstrect = list(self.widgets[wid].dstrect())
                    if isinstance(self.widgets[wid], widget.ContainerWidget) and self.widgets[wid].image:
                        # Draw a container.
                        r = self.driftwood.frame.overlay(self.widgets[wid].image.texture, srcrect, dstrect)
                        if isinstance(r, int) and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())
                    elif isinstance(self.widgets[wid], widget.TextWidget) and self.widgets[wid].texture:
                        # Draw some text.
                        r = self.driftwood.frame.overlay(self.widgets[wid].texture, srcrect, dstrect)
                        if isinstance(r, int) and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())

    def __prepare(self) -> None:
        """Initialize some things we need to get started."""
        if TTF_Init() < 0:
            self.driftwood.log.msg("ERROR", "Widget", "__prepare", "SDL_TTF", TTF_GetError())
        self.__spritefactory = SpriteFactory(sprite_type=TEXTURE, renderer=self.driftwood.window.renderer)
        self.__uifactory = UIFactory(self.__spritefactory)
        self.__uiprocessor = UIProcessor()

    def __insert_root_widget(self) -> None:
        """Insert the root widget, which is the parent of parentless widgets."""
        # Our size is the window resolution.
        res = self.driftwood.window.resolution()

        # Create the root widget.
        self.widgets[0] = widget.ContainerWidget(
            manager=self.driftwood, wid=0, parent=0, image=None, x=0, y=0, width=res[0], height=res[1]
        )
        self.widgets[0]._prepare()
        self.widgets[0].active = True

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        for item in self.widgets.items():
            if getattr(item, "_terminate", None):
                item._terminate()
        self.widgets = {}
        TTF_Quit()
