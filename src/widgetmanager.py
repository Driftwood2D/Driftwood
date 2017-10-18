####################################
# Driftwood 2D Game Dev. Suite     #
# widgetmanager.py                 #
# Copyright 2014-2017              #
# Michael D. Reiley & Paul Merrill #
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

import collections
from ctypes import byref, c_int
from typing import ItemsView, Optional

from sdl2 import *
from sdl2.ext import *
from sdl2.sdlttf import *

import widget


class WidgetManager:
    """The Widget Manager
    
    This class keeps track of widgets. These are things like text dialogs and UI elements.
    
    Attributes:
        driftwood: Base class instance.
        widgets: The dictionary of widgets, sorted by widget id.
        selected: Whether or not this widget is the selected widget. ex. a selected button in a UI menu.
    """

    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.widgets = {}
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

    def __getitem__(self, wid: int) -> Optional['widget.Widget']:
        return self.widget(wid)

    def __delitem__(self, wid) -> bool:
        return self.kill(wid)

    def __iter__(self) -> ItemsView:
        return self.widgets.items()

    def load(self, filename, template_vars={}):
        """Widget Tree Loader

        Loads and inserts a Jinja2 templated JSON descriptor file (a "widget tree") which defines one or more
        widgets to place on the screen.

        Args:
            * filename: Filename of the widget tree to load and insert.
            * template_vars: A dictionary of variables to apply to the Jinja2 template.
        """
        widget_list = []

        tree = self.driftwood.resource.request_template(filename, template_vars)
        if not tree:
            Driftwood.log.msg("WARNING", "Widget", "load", "Failed to read widget tree", filename)
            return None

        for branch in tree:
            # Read the widget tree, one base branch at a time.
            res = self.__read_branch(None, branch, template_vars)
            if res is None:
                Driftwood.log.msg("WARNING", "Widget", "load", "Failed to read widget tree branch")
                return None
            widget_list.append(res)

        # Return a list of IDs of all widgets that were constructed.
        return list(self.__flatten(widget_list))

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
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Widget", "select", "bad argument", e)
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

    def insert_container(self,
                         imagefile: str=None,
                         parent: int=None,
                         x: int=None,
                         y: int=None,
                         width: int=0,
                         height: int=0,
                         active: bool=True) -> Optional[int]:
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
            if new_widget.wid is 0:
                self.driftwood.log.msg("ERROR", "Widget", "insert_container", "could not create root widget")
            else:
                self.driftwood.log.msg("ERROR", "Widget", "insert_container", "could not create container widget")
            return None

        if active:  # Do we activate it to be drawn/used?
            self.activate(new_widget.wid)

        return new_widget.wid

    def insert_text(self,
                    contents: str,
                    fontfile: str,
                    ptsize: int,
                    parent: int=None,
                    x: int=None,
                    y: int=None,
                    width: int=None,
                    height: int=None,
                    color: str="000000FF",
                    active: bool=True):
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
        if not font:
            self.driftwood.log.msg("ERROR", "Widget", "insert_text", "no such font", fontfile)
            return None

        new_widget = widget.TextWidget(self, self.__last_wid, parent, contents, font, ptsize, x, y, width, height,
                                       color)
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

        if wid in self.widgets:
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
        """Destroy all widgets.
        """
        for widget in self.widgets:
            if getattr(self.widgets[widget], "_terminate", None):
                self.widgets[widget]._terminate()
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
                    if type(self.widgets[wid]) is widget.ContainerWidget and self.widgets[wid].image:
                        # Draw a container.
                        r = self.driftwood.frame.overlay(self.widgets[wid].image.texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())
                    elif type(self.widgets[wid]) is widget.TextWidget and self.widgets[wid].texture:
                        # Draw some text.
                        r = self.driftwood.frame.overlay(self.widgets[wid].texture, srcrect, dstrect)
                        if type(r) is int and r < 0:
                            self.driftwood.log.msg("ERROR", "Widget", "_draw_widgets", "SDL", SDL_GetError())

    def __prepare(self) -> None:
        """Initialize some things we need to get started.
        """
        if TTF_Init() < 0:
            self.driftwood.log.msg("ERROR", "Widget", "__prepare", "SDL_TTF", TTF_GetError())
        self.__spritefactory = SpriteFactory(sprite_type=TEXTURE, renderer=self.driftwood.window.renderer)
        self.__uifactory = UIFactory(self.__spritefactory)
        self.__uiprocessor = UIProcessor()

    def __insert_root_widget(self) -> None:
        """Insert the root widget, which is the parent of parentless widgets.
        """
        # Our size is the window resolution.
        res = self.driftwood.window.resolution()

        # Create the root widget.
        self.widgets[0] = widget.ContainerWidget(manager=self.driftwood, wid=0, parent=0, image=None,
                                                 x=0, y=0, width=res[0], height=res[1])
        self.widgets[0]._prepare()
        self.widgets[0].active = True

    def __read_branch(self, parent, branch, template_vars={}):
        """Recursively read and process widget tree branches."""
        widget_list = []

        if "include" in branch:
            # Replace this branch with an included tree.
            if "vars" in branch:
                # We are overlaying variables.
                branch = self.__include(branch["include"], {**template_vars, **branch["vars"]})
            else:
                branch = self.__include(branch["include"], template_vars)
            if not branch:
                return None

        if type(branch) == list:
            # This is a list of branches.
            for b in branch:
                res = self.__read_branch(parent, b, template_vars)
                if res is None:
                    Driftwood.log.msg("WARNING", "Widget", "__read_branch", "Failed to read widget tree branch")
                    return None
                widget_list.append(res)
            return widget_list

        if branch["type"] in ["container", "menu"]:
            # Insert a container or menu.
            c = self.insert_container(
                imagefile=self.__gp(branch, "image", None),
                x=self.__gp(branch, "x", None),
                y=self.__gp(branch, "y", None),
                width=self.__gp(branch, "width", 0),
                height=self.__gp(branch, "height", 0),
                parent=parent,
                active=True
            )

            if branch["type"] == "container":
                # It's a regular container.
                if c is None:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                           "failed to prepare container widget")
                    return None
                if not self.__postprocess_container(c, branch):
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                           "Failed to post-process container widget", c)
                    return None
                widget_list.append(c)

                if "members" in branch:
                    # There are more branches. Recurse them.
                    for b in branch["members"]:
                        res = self.__read_branch(c, b, template_vars)
                        if res is None:
                            self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                                   "failed to read widget tree branch")
                            return None
                        widget_list.append(res)

            else:
                # It's a menu.
                if c is None:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                           "failed to prepare menu widget")
                    return None
                if not self.__postprocess_container(c, branch):
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                           "Failed to post-process menu widget", c)
                    return None
                slotmap = self.__build_menu(c, branch)
                if not slotmap:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                           "Failed to build menu widget", c)
                    return None
                widget_list.append(c)
                widget_list.append(slotmap)

            return widget_list

        elif branch["type"] == "text":
            # Process and insert a text widget.
            res = self.__process_text(parent, branch)
            if res is None:
                self.driftwood.log.msg("WARNING", "Widget", "__read_branch",
                                       "Failed to process text widgets")
                return None

            widget_list.append(res)
            return widget_list

        return None

    def __process_text(self, parent, branch):
        """Process Text

        Process and insert a text widget, accounting for multiple lines and line-spacing.
        """
        # There are several ways this value could be input.
        if type(branch["contents"]) is str:
            contents = [branch["contents"]]
        elif type(branch["contents"]) is list:
            contents = branch["contents"]
        else:
            self.driftwood.log.msg("WARNING", "Widget", "__process_text", "text contents must be string or list")
            return None

        font = self.driftwood.resource.request_font(branch["font"], branch["size"]).font
        tw, th = c_int(), c_int()

        # Wrap text.
        if "wrap" in branch:
            wrapped_contents = []
            for n in range(len(contents)):
                # Go through each existing line separately.
                current = contents[n]
                while current:
                    for p in reversed(range(len(current))):
                        # Slice back through the line in reverse until it's small enough.
                        if p:
                            TTF_SizeUTF8(font, current[:p].encode(), byref(tw), byref(th))
                        if tw.value > branch["wrap"]:
                            # Segment is not small enough yet.
                            continue
                        if p:
                            # Append the small-enough line segment to the new list of lines and cut it off of what's
                            # left to be processed.
                            wrapped_contents.append(current[:p].strip())
                            current = current[p:]
                        else:
                            # We are done.
                            current = ""
                        break
            # Replace contents with wrapped contents.
            contents = wrapped_contents

        # Find text proportions.
        TTF_SizeUTF8(font, contents[0].encode(), byref(tw), byref(th))
        textheight = th.value
        totalheight = th.value * len(contents)

        # Calculate positions.
        if branch["y"] is None:
            branch["y"] = (self.widget(parent).height - totalheight) // 2

        # Place lines of text.
        t = []

        for n in range(len(contents)):
            # Check if wrapping put us in an impossible position.
            tmpy = int((branch["y"] + n * textheight * self.__gp(branch, "line-height", 1.0)
                        + n * self.__gp(branch, "line-spacing", 0)))
            if tmpy < 0:
                tmpy = 0
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "text wrapped to negative position")

            # Insert a textbox.
            t.append(self.insert_text(
                contents=contents[n],
                fontfile=branch["font"],
                ptsize=branch["size"],
                x=self.__gp(branch, "x", None),
                y=tmpy,
                width=self.__gp(branch, "width", None),
                height=self.__gp(branch, "height", None),
                color=self.__gp(branch, "color", "000000FF"),
                parent=parent,
                active=True
            ))
            if t[-1] is None:
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "failed to prepare text widget")
                return None

            if not self.__postprocess_text(t, branch):
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "failed to postprocess text widgets",
                                  t)
                return None

        return t

    def __postprocess_text(self, widgets, branch):
        # Collect some needed information.
        w = self.widget(widgets[0])
        lheight = int(w.height * self.__gp(branch, "line-height", 1.0))
        lspacing = self.__gp(branch, "line-spacing", 0)
        sep = lheight + lspacing

        # Work through the list of widgets in this branch.
        for seq, wid in enumerate(widgets):
            w = self.widget(wid)
            parent = self.widget(w.parent)

            # Justify text.
            if "align" in branch:
                found = False
                if "left" in branch["align"] and type(branch["align"]["left"]) is int:
                    w.x = branch["align"]["left"]
                    w.realx = branch["align"]["left"] + parent.realx
                    found = True
                if "right" in branch["align"] and type(branch["align"]["right"]) is int:
                    w.x = parent.width - w.width - branch["align"]["right"]
                    w.realx = parent.realx + parent.width - w.width - branch["align"]["right"]
                    found = True
                if "top" in branch["align"] and type(branch["align"]["top"]) is int:
                    w.y = branch["align"]["top"] + sep * seq
                    w.realy = branch["align"]["top"] + parent.realy + sep * seq
                    found = True
                if "bottom" in branch["align"] and type(branch["align"]["bottom"]) is int:
                    w.y = parent.height - w.height - (len(widgets) - 1 - seq) * sep - branch["align"]["bottom"]
                    w.realy = parent.realy + parent.height - w.height - (len(widgets) - 1 - seq) * sep - \
                              branch["align"]["bottom"]
                    found = True
                if not found:
                    self.driftwood.log.msg("WARNING", "Widget", "__postprocess_text",
                                           "\"align\" property contains incorrect values")
                    return False

        return True

    def __postprocess_container(self, widget, branch):
        # Collect some needed information.
        w = self.widget(widget)
        parent = self.widget(w.parent)

        # Justify container.
        if "align" in branch:
            found = False
            if "left" in branch["align"] and type(branch["align"]["left"]) is int:
                w.x = branch["align"]["left"]
                w.realx = branch["align"]["left"] + parent.realx
                found = True
            if "right" in branch["align"] and type(branch["align"]["right"]) is int:
                w.x = parent.width - w.width - branch["align"]["right"]
                w.realx = parent.realx + parent.width - w.width - branch["align"]["right"]
                found = True
            if "top" in branch["align"] and type(branch["align"]["top"]) is int:
                w.y = branch["align"]["top"]
                w.realy = branch["align"]["top"] + parent.realy
                found = True
            if "bottom" in branch["align"] and type(branch["align"]["bottom"]) is int:
                w.y = parent.height - w.height - branch["align"]["bottom"]
                w.realy = parent.realy + parent.height - w.height - branch["align"]["bottom"]
                found = True
            if not found:
                self.driftwood.log.msg("WARNING", "Widget", "__postprocess_container",
                                       "\"align\" property contains incorrect values")
                return False

        return True

    def __build_menu(self, widget, branch):
        """Build Menu

        Build a menu widget out of its component controls, and return a map of control placements."""
        slotmap = []
        lookups = {}

        for segment in branch["slots"]:
            if type(segment[0]) == object:
                # 1-Dimensional Menu
                slotmap.append(self.__process_control(widget, segment))
                lookups[slotmap[-1]] = segment

                if slotmap[-1] is None:
                    self.driftwood.log.msg("WARNING", "Widget", "__build_menu",
                                           "failed to prepare menu control widget")
                    return None
                if not self.__postprocess_container(widget, segment):
                    self.driftwood.log.msg("WARNING", "Widget", "__build_menu",
                                           "Failed to post-process menu control widget", widget)
                    return None

            else:
                # 2-Dimensional Menu
                slotmap.append([])
                for control in segment:
                    slotmap[-1].append(self.__process_control(widget, control))
                    lookups[slotmap[-1][-1]] = control

                    if slotmap[-1][-1] is None:
                        self.driftwood.log.msg("WARNING", "Widget", "__build_menu",
                                               "failed to prepare menu control widget")
                        return None
                    if not self.__postprocess_container(widget, control):
                        self.driftwood.log.msg("WARNING", "Widget", "__build_menu",
                                               "Failed to post-process menu control widget", widget)
                        return None

        self.__setup_menu(branch, slotmap, lookups)
        return slotmap

    def __process_control(self, parent, branch):
        """Process a menu control."""
        c = self.insert_container(
            imagefile=self.__gp(branch["images"], "deselected", None),
            x=self.__gp(branch, "x", None),
            y=self.__gp(branch, "y", None),
            width=self.__gp(branch, "width", 0),
            height=self.__gp(branch, "height", 0),
            parent=parent,
            active=True
        )
        return c

    def __setup_menu(self, branch, slotmap, lookups):
        """Set up menu."""
        if "default" in branch:
            # Select default control.
            self.__select_menu_control(branch, slotmap, lookups, branch["default"])
        else:
            # Select first control.
            if type(slotmap[0]) is int:
                # 1-Dimensional menu.
                self.__select_menu_control(branch, slotmap, lookups, 0)
            else:
                # 2-Dimensional menu.
                self.__select_menu_control(branch, slotmap, lookups, [0, 0])

        oldcontext = self.__register_menu_callbacks(branch["keybinds"])

    def __select_menu_control(self, branch, slotmap, lookups, position):
        """Select a control."""
        if type(slotmap[0]) is int:
            # 1-Dimensional menu.
            w = slotmap[position]
            control = branch["slots"][position]
        else:
            # 2-Dimensional menu.
            w = slotmap[position[0]][position[1]]
            control = branch["slots"][position[0]][position[1]]

        if self.selected is not None:
            # Deselect previously selected control.
            dw = self.selected
            self.widget(dw).image = self.driftwood.resource.request_image(lookups[dw]["images"]["deselected"])
            self.driftwood.area.changed = True
            if "select" in lookups[dw]["triggers"]:
                self.driftwood.script.call(*lookups[dw]["triggers"]["select"])

        # Select new control.
        self.select(w)
        self.widget(w).image = self.driftwood.resource.request_image(control["images"]["selected"])
        self.driftwood.area.changed = True
        if "select" in control["triggers"]:
            self.driftwood.script.call(*control["triggers"]["select"])

    def __register_menu_callbacks(self, keybinds):
        def kb_select_up(keyevent):
            print("menu up")

        def kb_select_down(keyevent):
            print("menu down")

        def kb_select_left(keyevent):
            print("menu left")

        def kb_select_right(keyevent):
            print("menu right")

        def kb_toggle(keyevent):
            print("menu toggle")

        oldcontext = Driftwood.input.context("menu")
        Driftwood.input.register(keybinds["select_up"], kb_select_up)
        Driftwood.input.register(keybinds["select_down"], kb_select_down)
        Driftwood.input.register(keybinds["select_left"], kb_select_left)
        Driftwood.input.register(keybinds["select_right"], kb_select_right)
        Driftwood.input.register(keybinds["toggle"], kb_toggle)
        return oldcontext

    def __gp(self, branch, prop, fallback):
        """Get Property

        Helper function to get a property from a branch, or return the fallback value if it doesn't exist."""
        if prop in branch:
            return branch[prop]
        else:
            return fallback

    def __include(self, filename, template_vars={}):
        """Include branches from another file.
        """
        tree = self.driftwood.resource.request_template(filename, template_vars)
        if not tree:
            self.driftwood.log.msg("WARNING", "Widget", "__include", "failed to read widget include", filename)
            return None

        return tree

    def __flatten(self, l):
        """https://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists/2158532#2158532"""
        for el in l:
            if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
                yield from self.__flatten(el)
            else:
                yield el

    def _terminate(self) -> None:
        """Cleanup before deletion.
        """
        for widget in self.widgets:
            if getattr(self.widgets[widget], "_terminate", None):
                self.widgets[widget]._terminate()
        self.widgets = {}
        TTF_Quit()
