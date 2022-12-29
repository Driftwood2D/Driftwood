################################
# Driftwood 2D Game Dev. Suite #
# driftwood.py                 #
# Copyright 2014-2017          #
# Sei Satzparad & Paul Merrill #
################################

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

import functools
import pdb
import time
import types
from typing import Any

from sdl2 import *
import sdl2.ext as sdl2ext

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
        # Space to store global temporary values that disappear on shutdown. Variables may be accessed either as
        # keys in a dictionary or as attributes.
        self.vars = AttrDict()

        # Instantiate subsystems and API.
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

        # SDL Keycodes.
        self.keycode = keycode

        # True while running. If set back to false, the engine will shutdown at the end of the tick.
        self.running = False

        # Check for problems.
        if self.config["window"]["maxfps"] < 10:
            self.log.msg("WARNING", "Driftwood", "Very low fps values may cause unexpected behavior")

    def _console(self, evtype: int) -> None:
        """Drop to a pdb console if the console key is pressed."""
        if evtype is self.input.ONDOWN:
            pdb.set_trace()

    def _run(self) -> int:
        """Perform startup procedures and enter the mainloop."""
        # Only run if not already running.
        if not self.running:
            self.running = True

            # Execute the init function of the init script if present.
            if not self.path["init.py"]:
                self.log.msg("WARNING", "Driftwood", "init.py missing, nothing will happen")
            else:
                self.script.call("init.py", "init")

            # Escape key pauses the engine.
            self.input.register(self.keycode.SDLK_ESCAPE, self._handle_pause)

            # Register the debug console key if debug mode is enabled.
            if self.config["input"]["debug"]:
                self.input.register("console", self._console)

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
                    self.tick._tick()
                    time.sleep(0.01)  # Cap mainloop speed.

            ticks = "[{0}]".format(self.tick.count)
            print(ticks + " Shutting down...")
            self._terminate()
            return 0
        return 0

    def _handle_pause(self, keyevent: int) -> None:
        """Check if we are shutting down, otherwise just pause."""
        if keyevent == InputManager.ONDOWN:
            # Shift+Escape shuts down the engine.
            if self.input.pressed(self.keycode.SDLK_LSHIFT) or self.input.pressed(self.keycode.SDLK_RSHIFT):
                self.running = False

            else:
                self.tick.toggle_pause()

    def _terminate(self) -> None:
        """Cleanup before shutdown. Here we tell all the relevant parts of the engine to free their resources
        before being deleted. We do this because Python's __del__ method is nearly useless as a destructor and we
        are using C constructs that need to be freed manually.
        """
        self.audio._terminate()
        self.widget._terminate()
        self.entity._terminate()
        self.database._terminate()
        self.frame._terminate()
        self.window._terminate()
        self.log._terminate()


class AttrDict(dict):
    """An abstraction which can be accessed as a dictionary or as a class, using keys or attributes."""

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def fncopy(f: Any) -> Any:
    """Deep copy a function. Needed to pass more than one of the same callback function to tick.register().
    Args:
        f: Function to copy.

    Returns:
        Copied function.

    Based on http://stackoverflow.com/a/6528148/190597 (Glenn Maynard)
    """
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__, argdefs=f.__defaults__, closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g
