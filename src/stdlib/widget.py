####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/widget.py                 #
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

# Driftwood STDLib widget functions.


def load(filename, template_vars={}):
    """Widget Tree Loader

    Loads and inserts a Jinja2 templated JSON descriptor file (a "widget tree") which defines one or more
    widgets to place on the screen.

    Args:
        * filename: Filename of the widget tree to load and insert.
        * template_vars: A dictionary of variables to apply to the Jinja2 template.
    """
    tree = Driftwood.resource.request_json(filename, True, template_vars)
    if not tree:
        return None

    for branch in tree:
        # Read the widget tree, one base branch at a time.
        __read_branch(None, branch)


def __read_branch(parent, branch):
    """Recursively read and process widget tree branches."""
    if branch["type"] == "container":
        # Insert a container.
        c = Driftwood.widget.insert_container(
            imagefile=__gp(branch, "image", None),
            x=__gp(branch, "x", None),
            y=__gp(branch, "y", None),
            width=__gp(branch, "width", 0),
            height=__gp(branch, "height", 0),
            parent=parent,
            active=True
        )

        if "members" in branch:
            # There are more branches. Recurse them.
            for b in branch["members"]:
                __read_branch(c, b)

    elif branch["type"] == "text":
        # Insert a textbox.
        t = Driftwood.widget.insert_text(
            contents=branch["contents"],
            fontfile=branch["font"],
            ptsize=branch["size"],
            x=__gp(branch, "x", None),
            y=__gp(branch, "y", None),
            width=__gp(branch, "width", None),
            height=__gp(branch, "height", None),
            color=__gp(branch, "color", "000000FF"),
            parent=parent,
            active=True
        )


def __gp(branch, prop, fallback):
    """Get Property

    Helper function to get a property from a branch, or return the fallback value if it doesn't exist."""
    if prop in branch:
        return branch[prop]
    else:
        return fallback
