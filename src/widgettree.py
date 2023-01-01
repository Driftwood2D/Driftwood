################################
# Driftwood 2D Game Dev. Suite #
# widgettree.py                #
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

import collections
from ctypes import c_int, byref
from typing import TYPE_CHECKING

from sdl2.sdlttf import *

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood
    from widgetmanager import WidgetManager


class WidgetTree:
    """This class reads and builds Widget Trees."""

    driftwood: "Driftwood"

    def __init__(self, manager: "WidgetManager", filename, template_vars):
        """Wrapped from WidgetManager.load()."""
        self.manager = manager
        self.driftwood = self.manager.driftwood

        widget_list = []

        self.__success = True

        tree = self.driftwood.resource.request_template(filename, template_vars)
        if not tree:
            self.__success = False
            self.driftwood.log.msg("WARNING", "Widget", "load", "Failed to read widget tree", filename)

        if self.__success:
            for branch in tree:
                # Read the widget tree, one base branch at a time.
                res = self.__read_branch(None, branch, template_vars)
                if res is None:
                    self.__success = False
                    self.driftwood.log.msg("WARNING", "Widget", "load", "Failed to read widget tree branch")
                    break
                widget_list.append(res)

        if not self.__success:
            self.widgets = None
        else:
            # Collect a list of IDs of all widgets that were constructed.
            self.widgets = list(self.__flatten(widget_list))

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
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch", "Failed to read widget tree branch")
                    return None
                widget_list.append(res)
            return widget_list

        if branch["type"] in ["container", "menu"]:
            # Insert a container or menu.
            c = self.manager.insert_container(
                imagefile=self.__gp(branch, "image", None),
                x=self.__gp(branch, "x", None),
                y=self.__gp(branch, "y", None),
                width=self.__gp(branch, "width", 0),
                height=self.__gp(branch, "height", 0),
                parent=parent,
                active=True,
            )

            if branch["type"] == "container":
                # It's a regular container.
                if c is None:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch", "failed to prepare container widget")
                    return None
                if not self.__postprocess_container(c, branch):
                    self.driftwood.log.msg(
                        "WARNING", "Widget", "__read_branch", "Failed to post-process container widget", c
                    )
                    return None
                widget_list.append(c)

                if "members" in branch:
                    # There are more branches. Recurse them.
                    for b in branch["members"]:
                        res = self.__read_branch(c, b, template_vars)
                        if res is None:
                            self.driftwood.log.msg(
                                "WARNING", "Widget", "__read_branch", "failed to read widget tree branch"
                            )
                            return None
                        widget_list.append(res)

            else:
                # It's a menu.
                if c is None:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch", "failed to prepare menu widget")
                    return None
                if not self.__postprocess_container(c, branch):
                    self.driftwood.log.msg(
                        "WARNING", "Widget", "__read_branch", "Failed to post-process menu widget", c
                    )
                    return None
                slotmap = self.__build_menu(c, branch)
                if not slotmap:
                    self.driftwood.log.msg("WARNING", "Widget", "__read_branch", "Failed to build menu widget", c)
                    return None
                widget_list.append(c)
                widget_list.append(slotmap)

            return widget_list

        elif branch["type"] == "text":
            # Process and insert a text widget.
            res = self.__process_text(parent, branch)
            if res is None:
                self.driftwood.log.msg("WARNING", "Widget", "__read_branch", "Failed to process text widgets")
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
            branch["y"] = (self.manager[parent].height - totalheight) // 2

        # Place lines of text.
        t = []

        for n in range(len(contents)):
            # Check if wrapping put us in an impossible position.
            tmpy = int(
                (
                    branch["y"]
                    + n * textheight * self.__gp(branch, "line-height", 1.0)
                    + n * self.__gp(branch, "line-spacing", 0)
                )
            )
            if tmpy < 0:
                tmpy = 0
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "text wrapped to negative position")

            # Insert a textbox.
            t.append(
                self.manager.insert_text(
                    contents=contents[n],
                    fontfile=branch["font"],
                    ptsize=branch["size"],
                    x=self.__gp(branch, "x", None),
                    y=tmpy,
                    width=self.__gp(branch, "width", None),
                    height=self.__gp(branch, "height", None),
                    color=self.__gp(branch, "color", "000000FF"),
                    parent=parent,
                    active=True,
                )
            )
            if t[-1] is None:
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "failed to prepare text widget")
                return None

            if not self.__postprocess_text(t, branch):
                self.driftwood.log.msg("WARNING", "Widget", "__process_text", "failed to postprocess text widgets", t)
                return None

        return t

    def __postprocess_text(self, widgets, branch):
        # Collect some needed information.
        w = self.manager[widgets[0]]
        lheight = int(w.height * self.__gp(branch, "line-height", 1.0))
        lspacing = self.__gp(branch, "line-spacing", 0)
        sep = lheight + lspacing

        # Work through the list of widgets in this branch.
        for seq, wid in enumerate(widgets):
            w = self.manager[wid]
            parent = self.manager[w.parent]

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
                    w.realy = (
                        parent.realy
                        + parent.height
                        - w.height
                        - (len(widgets) - 1 - seq) * sep
                        - branch["align"]["bottom"]
                    )
                    found = True
                if not found:
                    self.driftwood.log.msg(
                        "WARNING", "Widget", "__postprocess_text", '"align" property contains incorrect values'
                    )
                    return False

        return True

    def __postprocess_container(self, widget, branch):
        # Collect some needed information.
        w = self.manager[widget]
        parent = self.manager[w.parent]

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
                self.driftwood.log.msg(
                    "WARNING", "Widget", "__postprocess_container", '"align" property contains incorrect values'
                )
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
                    self.driftwood.log.msg("WARNING", "Widget", "__build_menu", "failed to prepare menu control widget")
                    return None
                if not self.__postprocess_container(widget, segment):
                    self.driftwood.log.msg(
                        "WARNING", "Widget", "__build_menu", "Failed to post-process menu control widget", widget
                    )
                    return None

            else:
                # 2-Dimensional Menu
                slotmap.append([])
                for control in segment:
                    slotmap[-1].append(self.__process_control(widget, control))
                    lookups[slotmap[-1][-1]] = control

                    if slotmap[-1][-1] is None:
                        self.driftwood.log.msg(
                            "WARNING", "Widget", "__build_menu", "failed to prepare menu control widget"
                        )
                        return None
                    if not self.__postprocess_container(widget, control):
                        self.driftwood.log.msg(
                            "WARNING", "Widget", "__build_menu", "Failed to post-process menu control widget", widget
                        )
                        return None

        self.__setup_menu(branch, slotmap, lookups)
        return slotmap

    def __process_control(self, parent, branch):
        """Process a menu control."""
        c = self.manager.insert_container(
            imagefile=self.__gp(branch["images"], "deselected", None),
            x=self.__gp(branch, "x", None),
            y=self.__gp(branch, "y", None),
            width=self.__gp(branch, "width", 0),
            height=self.__gp(branch, "height", 0),
            parent=parent,
            active=True,
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

        if self.manager.selected is not None:
            # Deselect previously selected control.
            dw = self.manager.selected
            self.manager[dw].image = self.driftwood.resource.request_image(lookups[dw]["images"]["deselected"])
            self.driftwood.area.changed = True
            if "select" in lookups[dw]["triggers"]:
                self.driftwood.script.call(*lookups[dw]["triggers"]["select"])

        # Select new control.
        self.manager.select(w)
        self.manager[w].image = self.driftwood.resource.request_image(control["images"]["selected"])
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

        oldcontext = self.driftwood.input.context("__widget_tree_menu_" + str(id(self)), keybinds)
        self.driftwood.input.register("select_up", kb_select_up)
        self.driftwood.input.register("select_down", kb_select_down)
        self.driftwood.input.register("select_left", kb_select_left)
        self.driftwood.input.register("select_right", kb_select_right)
        self.driftwood.input.register("toggle", kb_toggle)
        return oldcontext

    def __gp(self, branch, prop, fallback):
        """Get Property

        Helper function to get a property from a branch, or return the fallback value if it doesn't exist."""
        return branch[prop] if prop in branch else fallback

    def __include(self, filename, template_vars={}):
        """Include branches from another file."""
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
