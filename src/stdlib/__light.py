####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/__light.py                #
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

# Driftwood STDLib lighting private functions and variables.

import copy
import random


def flicker_callback(seconds_past, msg):
    lid, rx, ry, ralpha, fc = msg
    if not Driftwood.light.light(lid):
        fc.active = False
        __remove_flicker(fc)
        return
    ox, oy, oalpha = copy.deepcopy(Driftwood.vars["stdlib_light_flicker_originals"+str(lid)])
    ox += random.randint(rx * -1, rx)
    oy += random.randint(ry * -1, ry)
    oalpha += random.randint(ralpha * -1, ralpha)
    if oalpha > 255:
        oalpha = 255
    if oalpha < 0:
        oalpha = 0
    Driftwood.light.light(lid).x = ox
    Driftwood.light.light(lid).y = oy
    Driftwood.light.light(lid).alpha = oalpha
    Driftwood.area.changed = True


def end_flicker(seconds_past, msg):
    fc = msg
    lid = fc.lid

    __remove_flicker(fc)

    if fc.active:
        fc.active = False

        Driftwood.light.light(lid).x = Driftwood.vars["stdlib_light_flicker_originals"+str(lid)][0]
        Driftwood.light.light(lid).y = Driftwood.vars["stdlib_light_flicker_originals"+str(lid)][1]
        Driftwood.light.light(lid).alpha = Driftwood.vars["stdlib_light_flicker_originals"+str(lid)][2]
        Driftwood.area.changed = True


def remove_flicker(fc):
    Driftwood.tick.unregister(fc)
    Driftwood.vars["stdlib_light_flickers"].discard(fc)
