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

import copy
import random

from sdl2 import *

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
    if not "stdlib_light_area_layer" in Driftwood.vars or not\
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
    Driftwood.light.light(lid).color = c
    SDL_SetTextureColorMod(Driftwood.light.light(lid).lightmap.texture, int(c[0:2], 16), int(c[2:4], 16),
                           int(c[4:6], 16))
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
    Driftwood.light.light(lid).color = Driftwood.light.light(lid).color[6:8] + '%02X'%a
    SDL_SetTextureAlphaMod(Driftwood.light.light(lid).lightmap.texture, a)
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
    oalpha = int(Driftwood.light.light(lid).color[6:], 16)
    Driftwood.vars["stdlib_light_flicker_originals"+str(lid)] = [ox, oy, oalpha]
    FC = Driftwood.script.module("libs/stdlib/helper.py").copy_function(__flicker_callback)
    Driftwood.tick.register(FC, delay=1.0/rate, message=[lid, rx, ry, ralpha, FC])
    if duration:
        Driftwood.tick.register(__end_flicker, delay=duration, once=True, message=[lid, FC])
    return True

def __flicker_callback(seconds_past, msg):
    if not Driftwood.light.light(msg[0]):
        Driftwood.tick.unregister(msg[4])
        return
    fval = copy.deepcopy(Driftwood.vars["stdlib_light_flicker_originals"+str(msg[0])])
    fval[0] += random.randint(msg[1] * -1, msg[1])
    fval[1] += random.randint(msg[2] * -1, msg[2])
    fval[2] += random.randint(msg[3] * -1, msg[3])
    if fval[2] > 255:
        fval[2] = 255
    if fval[2] < 0:
        fval[2] = 0
    Driftwood.light.light(msg[0]).x = fval[0]
    Driftwood.light.light(msg[0]).y = fval[1]
    Driftwood.light.light(msg[0]).color = Driftwood.light.light(msg[0]).color[6:8] + '%02X'%fval[2]
    SDL_SetTextureAlphaMod(Driftwood.light.light(msg[0]).lightmap.texture, fval[2])
    Driftwood.area.changed = True

def __end_flicker(seconds_past, msg):
    Driftwood.tick.unregister(msg[1])
    Driftwood.light.light(msg[0]).x = Driftwood.vars["stdlib_light_flicker_originals"+str(msg[0])][0]
    Driftwood.light.light(msg[0]).y = Driftwood.vars["stdlib_light_flicker_originals"+str(msg[0])][1]
    Driftwood.light.light(msg[0]).color = Driftwood.light.light(msg[0]).color[6:8] +\
                                          '%02X'%Driftwood.vars["stdlib_light_flicker_originals"+str(msg[0])][2]
    SDL_SetTextureAlphaMod(Driftwood.light.light(msg[0]).lightmap.texture,
                           Driftwood.vars["stdlib_light_flicker_originals"+str(msg[0])][2])
    Driftwood.area.changed = True