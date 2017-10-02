####################################
# Driftwood 2D Game Dev. Suite     #
# stdlib/viewport.py               #
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

# Driftwood STDLib viewport functions.


def zoom(amount):
    """Zoom the window.
    
    Args:
        amount: Integer amount to zoom the window.
    
    Returns:
        Tuple containing new window resolution.
    """
    width = Driftwood.config["window"]["width"]
    height = Driftwood.config["window"]["height"]
    return Driftwood.window.resolution(width // amount, height // amount)


def rumble(rate, intensity, duration=None):
    """Rumble the viewport.

    Args:
        rate: Rate to update the viewport offset in hertz.
        intensity: Maximum viewport offset.
        duration: If set, how long in seconds before stopping.

    Returns:
        Function to end the rumble.
    """
    end_rumble()
    Driftwood.script["stdlib/__viewport.py"].cancel_end_rumble_tick()

    Driftwood.tick.register(Driftwood.script["stdlib/__viewport.py"].rumble_callback, delay=1.0/rate,
                            message=intensity)
    Driftwood.vars["rumbling"] = True

    if duration:
        Driftwood.tick.register(Driftwood.script["stdlib/__viewport.py"].end_rumble_tick, delay=duration, once=True)
        Driftwood.vars["will_end_rumbling"] = True


def end_rumble():
    if "rumbling" in Driftwood.vars and Driftwood.vars["rumbling"]:
        Driftwood.tick.unregister(Driftwood.script["stdlib/__viewport.py"].rumble_callback)
        Driftwood.area.offset = [0, 0]
        Driftwood.area.changed = True
        Driftwood.vars["rumbling"] = False
