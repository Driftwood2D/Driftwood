####################################
# Driftwood 2D Game Dev. Suite     #
# libs/stdlib/light.py             #
# Copyright 2016 Michael D. Reiley #
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

# Driftwood STDLib lighting functions.

def area(filename, color="FFFFFFFF", blend=False):
    """Convenience function to apply a lightmap over an entire area.

    Be aware that this will create a new layer the first time it's run on an area.
    It will do so again if the area has been unfocused and refocused and its number of layers has changed back.

    Args:
        filename: Filename of the lightmap.
        color: Hexadeximal color and alpha value of the light. "RRGGBBAA"
        blend: Whether to blend light instead of adding it. Useful for dark lights.

    Returns:
        Returns: New light if succeeded, None if failed.
    """
    layer = len(Driftwood.area.tilemap.layers) - 1
    if not "stdlib_light_area_layer" in Driftwood.vars or not\
            Driftwood.vars["stdlib_light_area_layer"][0] == Driftwood.area.filename or not \
            Driftwood.vars["stdlib_light_area_layer"][1] == layer:
        Driftwood.area.tilemap.new_layer()
        layer = len(Driftwood.area.tilemap.layers) - 1
        Driftwood.vars["stdlib_light_area_layer"] = [Driftwood.area.filename, layer]

    areasize = [Driftwood.area.tilemap.width * Driftwood.area.tilemap.tilewidth,
                Driftwood.area.tilemap.height * Driftwood.area.tilemap.tileheight]
    insertpos = [areasize[0] // 2, areasize[1] // 2]

    Driftwood.light.insert(filename, layer, insertpos[0], insertpos[1],
                           areasize[0], areasize[1], color=color, blend=blend)