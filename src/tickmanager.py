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
from sdl2 import SDL_Delay, SDL_GetTicks


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
        #     ticks: Ticks (milliseconds since engine start) at registration or
        #            last delayed call.
        #     delay: Delay in milliseconds between calls.
        #     callback: The function to be called.
        #     once: Whether to only call once.
        self.__registry = []

        self.__latest_tick = SDL_GetTicks()

        self.paused = False
        self.paused_at = None

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

        self.__registry.append({"ticks": self.__latest_tick, "delay": delay,
                                "callback": callback, "once": once})

    def unregister(self, callback):
        """Unregister a tick callback.

        Args:
            callback: The function to unregister.
        """
        for n, reg in enumerate(self.__registry):
            if reg["callback"] == callback:
                del self.__registry[n]

    def tick(self):
        """Call all registered tick callbacks not currently delayed, and
           regulate tps.
        """
        current_tick = SDL_GetTicks()
        last_tick = self.__latest_tick
        self.__latest_tick = current_tick

        # Only tick if not paused.
        if not self.paused:
            for reg in self.__registry:
                # Handle a delayed tick.
                millis_past = current_tick - reg["ticks"]
                if reg["delay"]:
                    if millis_past >= reg["delay"]:
                        reg["ticks"] = current_tick
                        reg["callback"](millis_past)

                        # Unregister ticks set to only run once.
                        if reg["once"]:
                            self.unregister(reg["callback"])

                # Don't handle a delayed tick
                else:
                    reg["ticks"] = current_tick
                    reg["callback"](millis_past)

                    # Unregister ticks set to only run once.
                    if reg["once"]:
                        self.unregister(reg["callback"])

        # We're paused, only call ticks for InputManager and WindowManager.
        else:
            self.driftwood.input.tick(None)
            self.driftwood.window.tick(None)

        # Regulate ticks per second.
        tick_delta = current_tick - last_tick
        if tick_delta < 1000 // self.driftwood.config["tick"]["tps"]:
            SDL_Delay((1000 // self.driftwood.config["tick"]["tps"]) - tick_delta)

    def toggle_pause(self):
        """Toggle a pause in all registered ticks.

        During this time, no ticks will get called, and all timing related information is kept track of and is restored
        upon unpause. Contrary to this, this, InputManager and WindowManager still receieve ticks during a pause, but
        they are told that the number of milliseconds that have passed is None (not 0).
        """
        if self.paused:
            self.paused = False
            paused_for = SDL_GetTicks() - self.paused_at
            for reg in self.__registry:
                reg["ticks"] += paused_for
            self.paused_at = None
        else:
            self.paused = True
            self.paused_at = SDL_GetTicks()
