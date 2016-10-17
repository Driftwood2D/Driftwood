####################################
# Driftwood 2D Game Dev. Suite     #
# libs/stdlib/viewport.py          #
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

# Driftwood STDLib viewport functions.

import random

def rumble(rate, intensity, duration=None):
    """Rumble the viewport.

    Args:
        rate: Rate to update the viewport offset in hertz.
        intensity: Maximum viewport offset.
        duration: If set, how long in seconds before stopping.

    Returns:
        True
    """
    Driftwood.tick.register(__rumble_callback, delay=1.0/rate, message=intensity)
    if duration:
        Driftwood.tick.register(__end_rumble, delay=duration, once=True)

def __rumble_callback(seconds_past, intensity):
    Driftwood.area.offset = [
        random.randint(intensity*-1, intensity),
        random.randint(intensity * -1, intensity)
    ]
    Driftwood.area.changed = True

def __end_rumble():
    Driftwood.tick.unregister(__rumble_callback)
    Driftwood.area.offset = [0, 0]
    Driftwood.area.changed = True
