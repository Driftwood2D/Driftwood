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

import builtins
import signal
import sys
from sdl2 import *
import sdl2.ext as sdl2ext

import config
import log
import filetype
import tick
import path
import cache
import resource
import input
import window
import area
import script


class Driftwood:
    """
    The top-level base class, containing the manager class instances and the mainloop. The instance of this class is
    passed to scripts as an API reference.
    """

    def __init__(self):
        """
        Base class initializer. Also initialize manager classes. Manager classes and their methods form the Driftwood
        Scripting API.
        """
        self.config = config.ConfigManager(self)
        self.log = log.LogManager(self.config)
        self.filetype = filetype  # Provide this interface to scripts.
        self.tick = tick.TickManager(self.config)
        self.path = path.PathManager(self.config)
        self.cache = cache.CacheManager(self.config)
        self.resource = resource.ResourceManager(self.config)
        self.input = input.InputManager(self.config)
        self.window = window.WindowManager(self.config)
        self.area = area.AreaManager(self.config)
        self.script = script.ScriptManager(self.config)

        # filetype API cleanup
        setattr(self.filetype, "renderer_ATTR", self.window.renderer)

        self.running = False

    def run(self):
        """
        Perform startup procedures and enter the mainloop.
        """
        # Only run if not already running.
        if not self.running:
            self.running = True

            # Execute the init function of the init script if present.
            if not self.path["init.py"]:
                self.log.log("WARNING", "Driftwood", "init.py missing, nothing will happen")
            else:
                self.script.call("init.py", "init")

            # This is the mainloop.
            while self.running:
                # Process SDL events.
                sdlevents = sdl2ext.get_events()
                for event in sdlevents:
                    if event.type == SDL_QUIT:
                        # Stop running.
                        self.running = False

                    elif event.type == SDL_KEYDOWN:
                        # Pass a keydown to the Input Manager.
                        self.input.key_down(event.key.keysym.sym)

                    elif event.type == SDL_KEYUP:
                        # Pass a keyup to the Input Manager.
                        self.input.key_up(event.key.keysym.sym)

                self.tick.tick()  # Process tick callbacks.

            print("Shutting down...")
            return 0


if __name__ == "__main__":
    # Set up the entry point.
    entry = Driftwood()

    # Make sure scripts have access to the base class.
    builtins.Driftwood = entry

    # Handle shutting down gracefully on INT and TERM signals.
    def sigint_handler(signum, frame):
        entry.running = False
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    # Run Driftwood and exit with its return code.
    sys.exit(entry.run())
