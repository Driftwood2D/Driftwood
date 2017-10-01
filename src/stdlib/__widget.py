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


# Properties to check for while preprocessing.
widget_preprocessing_properties = {
    "text": [
        "wrap",
        "line-spacing"
    ]
}

# Properties to check for while postprocessing.
widget_postprocessing_properties = {
    "any": [
        "top", "bottom", "left", "right",
    ]
}


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
                Driftwood.log.msg("WARNING", "sdtlib", "widget", "load", "Failed to read widget tree branch")
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
            Driftwood.log.msg("WARNING", "sdtlib", "widget", "read_branch", "Failed to prepare container widget")
            return False

        if branch["type"] == "container" and "members" in branch:
            # There are more branches. Recurse them.
            for b in branch["members"]:
                if not(read_branch(c, b, template_vars)):
                    Driftwood.log.msg("WARNING", "sdtlib", "widget", "load", "Failed to read widget tree branch")
            return True

    elif branch["type"] == "text":
        # Insert a textbox.
        t = Driftwood.widget.insert_text(
            contents=branch["contents"],
            fontfile=branch["font"],
            ptsize=branch["size"],
            x=gp(branch, "x", None),
            y=gp(branch, "y", None),
            width=gp(branch, "width", None),
            height=gp(branch, "height", None),
            color=gp(branch, "color", "000000FF"),
            parent=parent,
            active=True
        )
        if t is None:
            Driftwood.log.msg("WARNING", "sdtlib", "widget", "read_branch", "Failed to prepare text widget")
            return False

    return True


def post_process():
    pass


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
    tree = Driftwood.resource.request_json(filename, True, template_vars)
    if not tree:
        Driftwood.log.msg("WARNING", "sdtlib", "widget", "load", "Failed to read widget include", filename)
        return None

    return tree
