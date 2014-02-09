###################################
## Project Driftwood             ##
## tick.py                       ##
## Copyright 2013 PariahSoft LLC ##
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
    """
    This class manages tick callbacks.
    """

    def __init__(self, config):
        """
        TickManager class initializer.

        @type  config: object
        @param config: The Config class instance.
        """
        self.config = config
        self.__log = self.config.baseclass.log
        self.__registry = []

    def register(self, callback, delay=0, once=False):
        """
        Register a tick callback, with an optional delay between calls.

        @type  callback: function
        @param callback: Callback to register.
        @type  delay: int
        @param delay: (Optional) Delay in milliseconds between calls.
        """
        for reg in self.__registry:
            if reg["callback"] == callback:
                return

        self.__registry.append({"ticks": SDL_GetTicks(), "delay": delay, "callback": callback, "once": once})

        # This log message is only possible in python >= 3.3
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            self.__log.info("Tick", "registered", callback.__qualname__)

    def unregister(self, callback):
        """
        Unregister a tick callback.

        @type  callback: function
        @param callback: Callback to register.
        """
        for n, reg in enumerate(self.__registry):
            if reg["callback"] == callback:
                del self.__registry[n]

        # This log message is only possible in python >= 3.3
        if sys.version_info[0] == 3 and sys.version_info[1] >= 3:
            self.__log.info("Tick", "unregistered", callback.__qualname__)

    def tick(self):
        """
        Call all registered tick callbacks not currently delayed, and regulate tps.
        """
        for n, reg in enumerate(self.__registry):
            # Handle a delayed tick.
            if reg["delay"]:
                if SDL_GetTicks() - reg["ticks"] >= reg["delay"]:
                    self.__registry[n]["ticks"] = SDL_GetTicks()
                    reg["callback"]()

                    # Unregister ticks set to only run once.
                    if reg["once"]:
                        self.unregister(reg["callback"])

            # Don't handle a delayed tick
            else:
                reg["callback"]()

                # Unregister ticks set to only run once.
                if reg["once"]:
                    self.unregister(reg["callback"])

        # Regulate ticks per second.
        SDL_Delay(int(1000 / self.config["tick"]["tps"]))
