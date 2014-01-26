###################################
## Project Driftwood             ##
## __main__.py                   ##
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

import signal
import sys
from sdl2 import *
import sdl2.ext as sdl2ext

import config
import log
import tick
import cache
import path
import resource
import window


class Driftwood:
    """
    The top-level base class, containing the manager class instances and the mainloop. The instance of this class is
    passed to event scripts as an API reference.
    """

    def __init__(self):
        """Base class initializer. Also initialize manager classes."""
        self.config = config.ConfigManager(self)
        self.log = log.LogManager(self.config)
        self.tick = tick.TickManager(self.config)
        self.cache = cache.CacheManager(self.config)
        self.path = path.PathManager(self.config)
        self.resource = resource.ResourceManager(self.config)
        self.window = window.WindowManager(self.config)
        self.running = False

    def run(self):
        """
        The mainloop.
        """
        if not self.running:  # Only run if not already running.
            self.running = True

            while self.running:
                sdlevents = sdl2ext.get_events() # Process SDL events.
                for event in sdlevents:
                    if event.type == SDL_QUIT:
                        self.running = False

                self.tick.tick() # Process tick callbacks.

            return 0


if __name__ == "__main__":
    print("-------------------\n|Project Driftwood|\n-------------------\n\nStarting up...")

    entry = Driftwood()

    def sigint_handler(signum, frame):
        entry.running = False

    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    sys.exit(entry.run())
