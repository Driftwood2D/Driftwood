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

import jinja2
import json


def load(filename, vars={}):
    data = Driftwood.resource.request_raw(filename)
    if not data:
        return None

    # Render the widget template.
    template_loader = jinja2.DictLoader({filename: data})
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(filename)
    descriptor_text = template.render(vars)
    descriptor = json.loads(descriptor_text)

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
