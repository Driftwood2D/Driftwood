####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/__widget.py               #
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

# Driftwood STDLib widget private functions and variables.

import ast
from ctypes import byref, c_int

from sdl2.sdlttf import TTF_SizeText


def read_branch(parent, branch, template_vars={}):
    """Recursively read and process widget tree branches."""
    if "include" in branch:
        # Replace this branch with an included tree.
        if "vars" in branch:
            # We are overlaying variables.
            branch = include(branch["include"], {**template_vars, **branch["vars"]})
        else:
            branch = include(branch["include"], template_vars)
        if not branch:
            return False

    if type(branch) == list:
        # This is a list of branches.
        for b in branch:
            if not(read_branch(parent, b, template_vars)):
                Driftwood.log.msg("WARNING", "stdlib", "widget", "load", "Failed to read widget tree branch")
        return True

    if branch["type"] == "container":
        # Insert a container.
        c = Driftwood.widget.insert_container(
            imagefile=gp(branch, "image", None),
            x=gp(branch, "x", None),
            y=gp(branch, "y", None),
            width=gp(branch, "width", 0),
            height=gp(branch, "height", 0),
            parent=parent,
            active=True
        )
        if c is None:
            Driftwood.log.msg("WARNING", "stdlib", "widget", "read_branch", "Failed to prepare container widget")
            return False

        if branch["type"] == "container" and "members" in branch:
            # There are more branches. Recurse them.
            for b in branch["members"]:
                if not(read_branch(c, b, template_vars)):
                    Driftwood.log.msg("WARNING", "stdlib", "widget", "load", "Failed to read widget tree branch")
            return True

    elif branch["type"] == "text":
        # Process and insert a text widget.
        process_text(parent, branch)

    return True


def process_text(parent, branch):
    """Process Text

    Process and insert a text widget, accounting for multiple lines and line-spacing.
    """
    # There are several ways this value could be input.
    if type(branch["contents"]) is str:
        contents = [branch["contents"]]
    elif type(branch["contents"]) is list:
        contents = branch["contents"]
    else:
        Driftwood.log.msg("WARNING", "stdlib", "widget", "process_text", "Text contents must be string or list")
        return False

    # Find text proportions.
    tw, th = c_int(), c_int()
    TTF_SizeText(Driftwood.resource.request_font(branch["font"], branch["size"]).font, contents[0].encode(),
                 byref(tw), byref(th))
    textheight = th.value
    totalheight = th.value * len(contents)

    # Calculate positions.
    if branch["y"] is None:
        if parent is not None:
            branch["y"] = (Driftwood.widget[parent].height - totalheight) // 2
        else:
            branch["y"] = (self.manager.driftwood.window.resolution()[1] - totalheight) // 2

    # Place lines of text.
    for n in range(len(contents)):
        # Insert a textbox.
        t = Driftwood.widget.insert_text(
            contents=contents[n],
            fontfile=branch["font"],
            ptsize=branch["size"],
            x=gp(branch, "x", None),
            y=int((branch["y"] + n*textheight*gp(branch, "line-height", 1.0) + n*gp(branch, "line-spacing", 0))),
            width=gp(branch, "width", None),
            height=gp(branch, "height", None),
            color=gp(branch, "color", "000000FF"),
            parent=parent,
            active=True
        )
        if t is None:
            Driftwood.log.msg("WARNING", "stdlib", "widget", "process_text", "Failed to prepare text widget")
            return False


def gp(branch, prop, fallback):
    """Get Property

    Helper function to get a property from a branch, or return the fallback value if it doesn't exist."""
    if prop in branch:
        return branch[prop]
    else:
        return fallback


def include(filename, template_vars={}):
    """Include branches from another file.
    """
    tree = Driftwood.resource.request_template(filename, template_vars)
    if not tree:
        Driftwood.log.msg("WARNING", "stdlib", "widget", "load", "Failed to read widget include", filename)
        return None

    return tree
