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

__ = Driftwood.script["stdlib/__widget.py"]


def load(filename, template_vars={}):
    """Widget Tree Loader

    Loads and inserts a Jinja2 templated JSON descriptor file (a "widget tree") which defines one or more
    widgets to place on the screen.

    Args:
        * filename: Filename of the widget tree to load and insert.
        * template_vars: A dictionary of variables to apply to the Jinja2 template.
    """
    tree = Driftwood.resource.request_template(filename, template_vars)
    if not tree:
        Driftwood.log.msg("WARNING", "sdtlib", "widget", "load", "Failed to read widget tree", filename)
        return False

    # Allow single branches or lists of branches. Our code reads lists.
    if type(tree) is dict:
        tree = [tree]

    for branch in tree:
        # Read the widget tree, one base branch at a time.
        if not __.read_branch(None, branch, template_vars):
            Driftwood.log.msg("WARNING", "sdtlib", "widget", "load", "Failed to read widget tree branch")

    return True
