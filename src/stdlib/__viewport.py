####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/__viewport.py             #
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

# Driftwood STDLib viewport private functions and variables.

import random


def rumble_callback(seconds_past, intensity):
    Driftwood.area.offset = [
        random.randint(intensity * -1, intensity),
        random.randint(intensity * -1, intensity)
    ]
    Driftwood.area.changed = True


def end_rumble_tick():
    end_rumble()
    Driftwood.vars["will_end_rumbling"] = False


def cancel_end_rumble_tick():
    if "will_end_rumbling" in Driftwood.vars and Driftwood.vars["will_end_rumbling"]:
        Driftwood.tick.unregister(end_rumble_tick)
        Driftwood.vars["will_end_rumbling"] = False
