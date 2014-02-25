###################################
## Driftwood 2D Game Dev. Suite  ##
## tickmanager.py                ##
## Copyright 2014 PariahSoft LLC ##
###################################

## **********
## Permission is hereby granted, free of charge, to any person obtaining a copy
## of this software and associated documentation files (the "Software"), to
## deal in the Software without restriction, including without limitation the
## rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
## sell copies of the Software, and to permit persons to whom the Software is
## furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice shall be included in
## all copies or substantial portions of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
## IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
## FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
## AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
## LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
## FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
## IN THE SOFTWARE.
## **********

import sys
from sdl2 import SDL_Delay
from sdl2 import SDL_GetTicks


class TickManager:
    """The Tick Manager

    This class manages tick callbacks.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """TickManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # A list of dicts representing tick callbacks.
        #
        # Dict Keys:
        #     ticks: Ticks (milliseconds since engine start) at registration or last delayed call.
        #     delay: Delay in milliseconds between calls.
        #     callback: The function to be called.
        #     once: Whether to only call once.
        self.__registry = []

        self.paused = False

    def register(self, callback, delay=0, once=False):
        """Register a tick callback, with an optional delay between calls.

        Args:
            callback: The function to be called.
            delay: (optional) Delay in milliseconds between calls.
            once: Whether to only call once.
        """
        for reg in self.__registry:
            if reg["callback"] == callback:
                self.unregister(callback)

        self.__registry.append({"ticks": SDL_GetTicks(), "delay": delay, "callback": callback, "once": once})

        self.driftwood.log.info("Tick", "registered", callback.__qualname__)

    def unregister(self, callback):
        """Unregister a tick callback.

        Args:
            callback: The function to unregister.
        """
        for n, reg in enumerate(self.__registry):
            if reg["callback"] == callback:
                del self.__registry[n]
                self.driftwood.log.info("Tick", "unregistered", callback.__qualname__)

    def tick(self):
        """Call all registered tick callbacks not currently delayed, and regulate tps.
        """
        for reg in self.__registry:
            # Only tick if not paused. FIXME: This will throw off the timing of callbacks.
            if not self.paused:
                # Handle a delayed tick.
                millis_past = SDL_GetTicks() - reg["ticks"]
                if reg["delay"]:
                    if millis_past >= reg["delay"]:
                        reg["ticks"] = SDL_GetTicks()
                        reg["callback"](millis_past)

                        # Unregister ticks set to only run once.
                        if reg["once"]:
                            self.unregister(reg["callback"])

                # Don't handle a delayed tick
                else:
                    reg["ticks"] = SDL_GetTicks()
                    reg["callback"](millis_past)

                    # Unregister ticks set to only run once.
                    if reg["once"]:
                        self.unregister(reg["callback"])

            # We're paused, only call ticks for InputManager and WindowManager.
            else:
                self.driftwood.input.tick(None)
                self.driftwood.window.tick(None)

        # Regulate ticks per second.
        SDL_Delay(1000 // self.driftwood.config["tick"]["tps"])
