####################################
# Driftwood 2D Game Dev. Suite     #
# __main__.py                      #
# Copyright 2014 PariahSoft LLC    #
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

import signal
import sys
import time

VCUR = sys.version_info
VREQ = [3, 3, 3]

# We have to do this here before we start pulling in nonexistent imports.
if __name__ == "__main__":
    # Check Python version.
    if VCUR[0] < VREQ[0] or VCUR[1] < VREQ[1] or (VCUR[1] == VREQ[1] and VCUR[2] < VREQ[2]):
        print("Driftwood 2D\nStarting up...")
        print("[0] FATAL: python >= {0}.{1}.{2} required, found python {3}.{4}.{5}".format(VREQ[0], VREQ[1], VREQ[2],
                                                                                           VCUR[0], VCUR[1], VCUR[2]))
        sys.exit(1)  # Fail.

    # Try to import PySDL2.
    try:
        from sdl2 import *
        import sdl2.ext as sdl2ext
    except ImportError:
        print("Driftwood 2D\nStarting up...")
        print("[0] FATAL: PySDL2 required, module \"sdl2\" not found")
        sys.exit(1)  # Fail.

    # Try to import jsonschema.
    try:
        import jsonschema
    except ImportError:
        print("Driftwood 2D\nStarting up...")
        print("[0] FATAL: jsonschema required, module \"jsonschema\" not found")
        sys.exit(1)  # Fail.

# Import manager classes.
from configmanager import ConfigManager
from logmanager import LogManager
from tickmanager import TickManager
from databasemanager import DatabaseManager
from pathmanager import PathManager
from cachemanager import CacheManager
from resourcemanager import ResourceManager
from inputmanager import InputManager
from windowmanager import WindowManager
from framemanager import FrameManager
from entitymanager import EntityManager
from lightmanager import LightManager
from areamanager import AreaManager
from audiomanager import AudioManager
from widgetmanager import WidgetManager
from scriptmanager import ScriptManager


class Driftwood:
    """The top-level base class

    This class contains the top level manager class instances and the mainloop. The instance of this class is
    passed to scripts as an API reference.
    """

    def __init__(self):
        """Base class initializer.

        Initialize base class and manager classes. Manager classes and their methods form the Driftwood Scripting API.

        Attributes:
            config: ConfigManager instance.
            log: LogManager instance.
            tick: TickManager instance.
            database: DatabaseManager instance.
            path: PathManager instance.
            cache: CacheManager instance.
            resource: ResourceManager instance.
            input: InputManager instance.
            window: WindowManager instance.
            frame: FrameManager instance.
            entity: EntityManager instance.
            area: AreaManager instance.
            audio: AudioManager instance.
            widget: WidgetManager instance.
            script: ScriptManager instance.

            keycode: Contains the SDL keycodes.

            vars: A globally accessible dictionary for storing values until shutdown.

            running: Whether the mainloop should continue running. Set False to shut down the engine.
        """
        self.config = ConfigManager(self)
        self.log = LogManager(self)
        self.tick = TickManager(self)
        self.database = DatabaseManager(self)
        self.path = PathManager(self)
        self.cache = CacheManager(self)
        self.resource = ResourceManager(self)
        self.input = InputManager(self)
        self.window = WindowManager(self)
        self.frame = FrameManager(self)
        self.entity = EntityManager(self)
        self.light = LightManager(self)
        self.area = AreaManager(self)
        self.audio = AudioManager(self)
        self.widget = WidgetManager(self)
        self.script = ScriptManager(self)
        self.area.register()
        self.window.register()

        # SDL Keycodes.
        self.keycode = keycode

        # Space to store global temporary values that disappear on shutdown.
        self.vars = {}

        # Are we going to continue running?
        self.running = False

    def _run(self):
        """Perform startup procedures and enter the mainloop.
        """
        # Only run if not already running.
        if not self.running:
            self.running = True

            # Execute the init function of the init script if present.
            if not self.path["init.py"]:
                self.log.msg("WARNING", "Driftwood", "init.py missing, nothing will happen")
            else:
                self.script.call("init.py", "init")

            # Escape key pauses the engine.
            self.input.register(self.keycode.SDLK_ESCAPE, self.__handle_pause)

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
                        self.input._key_down(event.key.keysym.sym)

                    elif event.type == SDL_KEYUP:
                        # Pass a keyup to the Input Manager.
                        self.input._key_up(event.key.keysym.sym)

                    elif event.type == SDL_WINDOWEVENT and event.window.event == SDL_WINDOWEVENT_EXPOSED:
                        self.window.refresh()

                # Process tick callbacks.
                if self.running:
                    self.tick.tick()
                    time.sleep(0.01)  # Cap mainloop speed.

            print("Shutting down...")
            self._terminate()
            return 0

    def __handle_pause(self, keyevent):
        """Check if we are shutting down, otherwise just pause.
        """
        if keyevent == InputManager.ONDOWN:
            # Shift+Escape shuts down the engine.
            if self.input.pressed(self.keycode.SDLK_LSHIFT) or self.input.pressed(self.keycode.SDLK_RSHIFT):
                self.running = False

            else:
                self.tick.toggle_pause()

    def _terminate(self):
        """Cleanup before shutdown.
        """
        self.audio._terminate()
        self.widget._terminate()
        self.light._terminate()
        self.entity._terminate()
        self.database._terminate()
        self.frame._terminate()
        self.window._terminate()


if __name__ == "__main__":
    # Set up the entry point.
    entry = Driftwood()

    # Make sure scripts have access to the base class.
    import builtins
    builtins.Driftwood = entry

    # Handle shutting down gracefully on INT and TERM signals.
    def sigint_handler(signum, frame):
        entry.running = False

    # Set up interrupt handlers
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    # Run Driftwood and exit with its return code.
    sys.exit(entry._run())
