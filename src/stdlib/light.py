####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/light.py                  #
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

__ = Driftwood.script["stdlib/__light.py"]


def area(filename, color="FFFFFFFF", blend=False):
    """Convenience function to apply a lightmap over an entire area.

    Be aware that this will create a new layer the first time it's run on an area.
    It will do so again if the area has been unfocused and refocused and its number of layers has changed back.

    Args:
        filename: Filename of the lightmap.
        color: Hexadeximal color and alpha value of the light. "RRGGBBAA"
        blend: Whether to blend light instead of adding it. Useful for dark lights.

    Returns:
        New light if succeeded, None if failed.
    """
    layer = len(Driftwood.area.tilemap.layers) - 1
    if "stdlib_light_area_layer" not in Driftwood.vars or not \
            Driftwood.vars["stdlib_light_area_layer"][0] == Driftwood.area.filename or not \
            Driftwood.vars["stdlib_light_area_layer"][1] == layer:
        Driftwood.area.tilemap.new_layer()
        layer = len(Driftwood.area.tilemap.layers) - 1
        Driftwood.vars["stdlib_light_area_layer"] = [Driftwood.area.filename, layer]

    areasize = [Driftwood.area.tilemap.width * Driftwood.area.tilemap.tilewidth,
                Driftwood.area.tilemap.height * Driftwood.area.tilemap.tileheight]
    insertpos = [areasize[0] // 2, areasize[1] // 2]

    return Driftwood.light.insert(filename, layer, insertpos[0], insertpos[1],
                                  areasize[0], areasize[1], color=color, blend=blend)


def color(lid, c):
    """Change the color and alpha value for a light.

    Args:
        lid: Light ID of the light whose color and alpha to update.
        c: New color and alpha value in hexadecimal. "RRGGBBAA"

    returns:
        True
    """
    colormod = (
        int(c[0:2], 16),
        int(c[2:4], 16),
        int(c[4:6], 16)
    )
    Driftwood.light.light(lid).colormod = colormod
    alpha(lid, int(c[6:8], 16))
    return True


def alpha(lid, a):
    """Change the alpha for a light.

    Args:
        lid: Light ID of the light whose alpha to update.
        a: New alpha value, 0-255

    returns:
        True
    """
    Driftwood.light.light(lid).alpha = a
    return True


def flicker(lid, rx, ry, ralpha, rate, duration=None):
    """Shake a light around randomly while changing its alpha.
    Args:
        lid: Light ID of the light to shimmer.
        rx: Absolute value range for x offset.
        ry: Absolute value range for y offset.
        ralpha: Absolute value range for alpha offset.
        rate: Rate to update the light offset in hertz.
        duration: If set, how long in seconds before stopping.

    Returns:
        True
    """
    ox = Driftwood.light.light(lid).x
    oy = Driftwood.light.light(lid).y
    oalpha = Driftwood.light.light(lid).alpha

    fc = Driftwood.script["stdlib/helper.py"].copy_function(__.flicker_callback)
    fc.active = True
    fc.lid = lid

    if "stdlib_light_flickers" not in Driftwood.vars:
        Driftwood.vars["stdlib_light_flickers"] = set()
    Driftwood.vars["stdlib_light_flickers"].add(fc)

    Driftwood.vars["stdlib_light_flicker_originals"+str(lid)] = [ox, oy, oalpha]

    Driftwood.tick.register(fc, delay=1.0/rate, message=[lid, rx, ry, ralpha, fc])

    if duration:
        Driftwood.tick.register(__.end_flicker, delay=duration, once=True, message=fc)

    return True


def reset_flickers():
    if "stdlib_light_flickers" in Driftwood.vars:
        fcs = Driftwood.vars["stdlib_light_flickers"]
        while len(fcs) > 0:
            fc = fcs.pop()
            __.end_flicker(None, fc)
