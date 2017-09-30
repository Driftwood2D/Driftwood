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

    Loads a Jinja2 templated JSON descriptor file (a "widget tree") which defines one or more widgets to place on
    the screen.
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
            imagefile=branch["image"], parent=parent, x=branch["x"], y=branch["y"], width=branch["width"],
            height=branch["height"]
        )

        if "branches" in branch:
            # There are more branches. Recurse them.
            for b in branch["branches"]:
                __read_branch(c, b)

    elif branch["type"] == "text":
        # Insert a textbox.
        t = Driftwood.widget.insert_text(
            branch["contents"], branch["font"], branch["size"], parent=parent, x=branch["x"],
            y=branch["y"], width=branch["width"], height=branch["height"], color=branch["color"],
            active=True
        )
