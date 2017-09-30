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


def load(filename, vars={}):
    descriptor = Driftwood.resource.request_json(filename, True, vars)
    if not descriptor:
        return None

    # Read the widget.
    if "container" in descriptor:
        c = descriptor["container"]
        wc = Driftwood.widget.insert_container(
            imagefile=c["image"], x=c["x"], y=c["y"], width=c["width"], height=c["height"]
        )

        if "members" in c:
            members = c["members"]

            for m in members:
                if "text" in m:
                    t = m["text"]
                    wt = Driftwood.widget.insert_text(
                        t["contents"], t["font"], t["size"], parent=wc, x=t["x"], y=t["y"], width=t["width"],
                        height=t["height"], color=t["color"], active=True)
