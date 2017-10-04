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

from ctypes import byref, c_int

from sdl2.sdlttf import TTF_SizeUTF8


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
                Driftwood.log.msg("WARNING", "stdlib", "__widget", "load", "Failed to read widget tree branch")
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
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "read_branch", "Failed to prepare container widget")
            return False
        if not postprocess_container(c, branch):
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "process_container",
                              "Failed to postprocess text widgets", c)
            return False

        if branch["type"] == "container" and "members" in branch:
            # There are more branches. Recurse them.
            for b in branch["members"]:
                if not(read_branch(c, b, template_vars)):
                    Driftwood.log.msg("WARNING", "stdlib", "__widget", "load", "Failed to read widget tree branch")
                    return False
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
        Driftwood.log.msg("WARNING", "stdlib", "__widget", "process_text", "Text contents must be string or list")
        return False

    font = Driftwood.resource.request_font(branch["font"], branch["size"]).font
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
    TTF_SizeUTF8(font, contents[0].encode(),
                 byref(tw), byref(th))
    textheight = th.value
    totalheight = th.value * len(contents)

    # Calculate positions.
    if branch["y"] is None:
        branch["y"] = (Driftwood.widget[parent].height - totalheight) // 2

    # Place lines of text.
    t = []

    for n in range(len(contents)):
        # Check if wrapping put us in an impossible position.
        tmpy = int((branch["y"] + n * textheight * gp(branch, "line-height", 1.0)
                    + n * gp(branch, "line-spacing", 0)))
        if tmpy < 0:
            tmpy = 0
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "process_text", "text wrapped to negative position")

        # Insert a textbox.
        t.append(Driftwood.widget.insert_text(
            contents=contents[n],
            fontfile=branch["font"],
            ptsize=branch["size"],
            x=gp(branch, "x", None),
            y=tmpy,
            width=gp(branch, "width", None),
            height=gp(branch, "height", None),
            color=gp(branch, "color", "000000FF"),
            parent=parent,
            active=True
        ))
        if t[-1] is None:
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "process_text", "Failed to prepare text widget")
            return False

        if not postprocess_text(t, branch):
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "process_text", "Failed to postprocess text widgets",
                              t)
            return False

    return True


def postprocess_text(widgets, branch):
    # Collect some needed information.
    w = Driftwood.widget[widgets[0]]
    lheight = int(w.height*gp(branch, "line-height", 1.0))
    lspacing = gp(branch, "line-spacing", 0)
    sep = lheight + lspacing

    # Work through the list of widgets in this branch.
    for seq, wid in enumerate(widgets):
        w = Driftwood.widget[wid]
        parent = Driftwood.widget[w.parent]

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
                w.y = branch["align"]["top"] + sep*seq
                w.realy = branch["align"]["top"] + parent.realy + sep*seq
                found = True
            if "bottom" in branch["align"] and type(branch["align"]["bottom"]) is int:
                w.y = parent.height - w.height - (len(widgets)-1-seq)*sep - branch["align"]["bottom"]
                w.realy = parent.realy + parent.height - w.height - (len(widgets)-1-seq)*sep - \
                          branch["align"]["bottom"]
                found = True
            if not found:
                Driftwood.log.msg("WARNING", "stdlib", "__widget", "postprocess_text",
                                  "\"align\" property contains incorrect values")
                return False

    return True


def postprocess_container(widget, branch):
    # Collect some needed information.
    w = Driftwood.widget[widget]
    parent = Driftwood.widget[w.parent]

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
            w.y = parent.height - w.height  - branch["align"]["bottom"]
            w.realy = parent.realy + parent.height - w.height - branch["align"]["bottom"]
            found = True
        if not found:
            Driftwood.log.msg("WARNING", "stdlib", "__widget", "postprocess_container",
                              "\"align\" property contains incorrect values")
            return False

    return True


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
        Driftwood.log.msg("WARNING", "stdlib", "__widget", "load", "Failed to read widget include", filename)
        return None

    return tree
