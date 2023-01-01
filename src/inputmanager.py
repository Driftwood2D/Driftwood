################################
# Driftwood 2D Game Dev. Suite #
# inputmanager.py              #
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

import types
from typing import Callable, Optional, Union, TYPE_CHECKING

from sdl2 import SDL_GetKeyName

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class InputManager:
    """The Input Manager

    This class manages keyboard input.

    Attributes:
        driftwood: Base class instance.
        handler: Optional callback to a function that receives keypresses after we do.
    """

    ONDOWN, ONREPEAT, ONUP = range(3)

    def __init__(self, driftwood: "Driftwood"):
        """InputManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.handler = None

        self.__current_context = None

        self.__contexts = {
            None: {  # None is the default context populated on engine start.
                # {keysym: {callback, throttle, delay, last_called, repeats, mod}}
                "registry": {},
                "stack": [],
                "modifier_stack": [],
                "keybinds": {},
            }
        }

        self.__now = 0.0

        # Register the tick callback.
        self.driftwood.tick.register(self._tick, during_pause=True)

    def __contains__(self, item: int) -> bool:
        if item in self.__fetch("registry"):
            return True
        return False

    def __setitem__(self, item: Union[int, str], value: Callable) -> None:
        self.register(item, value)

    def __delitem__(self, item: int) -> None:
        self.unregister(item)

    def keyname(self, keysym: int) -> Optional[str]:
        """Return a string naming a keysym. The up arrow key returns "Up," etc.

        Args:
            keysym: SDLKey which should be named

        Returns:
            Keyname if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(keysym, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "keyname", "bad argument", e)
            return None

        # Retrieve.
        try:
            # TODO: This does not work as we expected. A single character is usually returned.
            return SDL_GetKeyName(keysym).decode().replace("SDLK_", "")
        except:
            return None

    def keysym(self, keyname: str) -> Optional[int]:
        """Return a keysym for the named keybinding.

        Args:
            keyname: The name of the keybinding for which to return a keysym.

        Returns:
            Keysym if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(keyname, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "keysym", "bad argument", e)
            return None

        # Retrieve
        try:
            keybinds = {
                **self.driftwood.config["input"]["keybinds"],
                **self.__contexts[self.__current_context]["keybinds"],
            }
            return getattr(self.driftwood.keycode, "SDLK_" + keybinds[keyname].upper())
        except:
            return None

    def register(
        self, keyid: Union[int, str], callback: Callable, throttle: float = 0.0, delay: float = 0.0, mod: bool = False
    ) -> bool:
        """Register an input callback.

        The callback function will receive a call every tick that the key is on top of the input stack. (the key which
        was most recently pressed.)

        Args:
            keyid: SDLKey keysym or key name for the key which triggers the callback. (int or string)
            callback: Function to be called on the registered keypress.  It should take a single integer parameter with
                a value of InputManager.ONDOWN, ONREPEAT, or ONUP.
            throttle: Number of seconds to wait between ONREPEAT calls when the key is held down.
            delay: Number of seconds to wait after the key is pressed before making the first ONREPEAT call.
            mod: Whether this is a modifier key. Modifier keys do not compete for the top of the input stack.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(keyid, [int, str], _min=0)
            CHECK(callback, [types.FunctionType, types.MethodType])
            CHECK(throttle, [int, float], _min=0)
            CHECK(delay, [int, float], _min=0)
            CHECK(mod, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "register", "bad argument", e)
            return False

        # Find keysym.
        if type(keyid) == int:
            keysym = keyid
        elif type(keyid) == str:
            keysym = self.keysym(keyid)
        else:
            self.driftwood.log.msg("WARNING", "InputManager", "register", "no such key", str(keyid))
            return False

        if delay == 0.0:
            delay = throttle

        self.__contexts[self.__current_context]["registry"][keysym] = {
            "callback": callback,
            "throttle": throttle,
            "delay": delay,
            "last_called": self.__now,
            "repeats": 0,
            "mod": mod,
        }

        return True

    def unregister(self, keysym: int) -> bool:
        """Unregister an input callback.

        Args:
            keysym: SDLKey for the key which triggers the callback.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(keysym, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "unregister", "bad argument", e)
            return False

        # Unregister.
        if keysym in self.__fetch("registry"):
            del self.__contexts[self.__current_context]["registry"][keysym]
            return True
        else:
            self.driftwood.log.msg("WARNING", "InputManager", "unregister", "key not registered", self.keyname(keysym))
            return False

    def pressed(self, keysym: int) -> bool:
        """Check if a key is currently being pressed.

        Args:
            keysym: SDLKey for the keypress to check.
        """
        # Input Check
        try:
            CHECK(keysym, int, _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "pressed", "bad argument", e)
            return False

        # Is pressed.
        if keysym in self.__fetch("stack"):
            return True

        return False

    def context(self, name: str = None, keybinds: dict = {}) -> str:
        """Check or change the current context.

        Args:
            name: If set, name of the context to switch to.
            keybinds: If set, a dictionary of keybinds to layer over the default dictionary from the config file.
                Any duplicates are overridden.

        Returns:
            Previous context (or current context if unchanged.)
        """
        # Input Check
        try:
            CHECK(name, str)
            CHECK(keybinds, dict)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Input", "context", "bad argument", e)
            return self.__current_context

        oldcontext = self.__current_context
        self.__current_context = name
        if name not in self.__contexts:
            self.__contexts[name] = {
                # {keysym: {callback, throttle, delay, last_called, repeats, mod}}
                "registry": {},
                "stack": [],
                "modifier_stack": [],
                "keybinds": keybinds,
            }
            # Escape key pauses the engine.
            self.register(self.driftwood.keycode.SDLK_ESCAPE, self.driftwood._handle_pause)
        return oldcontext

    def _key_down(self, keysym: int) -> None:
        """Push a keypress onto the input stack if not present.

        Args:
            keysym: SDLKey for the key which was pressed.
        """
        if keysym not in self.__fetch("stack"):
            if keysym in self.__fetch("registry") and not self.__fetch("registry")[keysym]["mod"]:
                # TODO: Implement modifier keys.
                self.__contexts[self.__current_context]["stack"].insert(0, keysym)
                self.__fetch("registry")[keysym]["callback"](InputManager.ONDOWN)
            elif keysym in self.__fetch("registry"):
                # Registered keypress.
                self.__contexts[self.__current_context]["modifier_stack"].insert(0, keysym)
                self.__fetch("registry")[keysym]["callback"](InputManager.ONDOWN)
            else:
                # Unregistered keypress.
                self.__contexts[self.__current_context]["stack"].insert(0, keysym)
        else:
            # SDL2 gives us key-repeat events so this is actually okay.
            # self.driftwood.log.msg("WARNING", "InputManager", "key_down", "key already down", self.keyname(keysym))
            pass

    def _key_up(self, keysym: int) -> None:
        """Remove a keypress from the input stack if present.

        Args:
            keysym: SDLKey for the key which was released.
        """
        found = False
        if keysym in self.__fetch("stack"):
            self.__contexts[self.__current_context]["stack"].remove(keysym)
            found = True
        elif keysym in self.__fetch("modifier_stack"):
            self.__contexts[self.__current_context]["modifier_stack"].remove(keysym)
            found = True

        if found:
            # Set the key callback as not called yet.
            if keysym in self.__fetch("registry"):
                self.__fetch("registry")[keysym]["repeats"] = 0
                self.__fetch("registry")[keysym]["callback"](InputManager.ONUP)

    def _tick(self, seconds_past: float) -> None:
        """Tick callback.

        If there is a keypress on top of the stack and it maps to a callback in the registry, call it. Also pass the
        keypress to the secondary handler if it exists.

        If a second-callback delay is set, make sure to wait the proper amount of time before the second call.
        """
        self.__now += seconds_past

        # TODO: Remove duplicate code.
        if self.__fetch("modifier_stack"):
            for mod_key in self.__fetch("modifier_stack"):
                mod_callback = self.__fetch("registry")[mod_key]

                # Have we waited long enough between calls?
                if mod_callback["repeats"] == 0:
                    waiting_until = mod_callback["delay"]
                else:
                    waiting_until = mod_callback["throttle"]

                if self.__now - mod_callback["last_called"] >= waiting_until:
                    # Update time last called.
                    mod_callback["last_called"] = self.__now

                    # Call the callback.
                    mod_callback["callback"](InputManager.ONREPEAT)

                    # Update number of times called.
                    mod_callback["repeats"] += 1

                # Call the handler if set.
                if self.handler:
                    self.handler(mod_key)

        if self.__fetch("stack"):
            # The user's current (or latest, if multiple ongoing,) keydown.
            top_key = self.__fetch("stack")[0]

            # Is the keypress in the registry?
            if top_key in self.__fetch("registry"):
                # The callback entry for the top_key.
                top_callback = self.__fetch("registry")[top_key]

                # Have we waited long enough between calls?
                if top_callback["repeats"] == 0:
                    waiting_until = top_callback["delay"]
                else:
                    waiting_until = top_callback["throttle"]

                if self.__now - top_callback["last_called"] >= waiting_until:
                    # Update time last called.
                    top_callback["last_called"] = self.__now

                    # Call the callback.
                    top_callback["callback"](InputManager.ONREPEAT)

                    # Update number of times called.
                    top_callback["repeats"] += 1

            # Call the handler if set.
            if self.handler:
                self.handler(top_key)

    def __fetch(self, key):
        """Fetch data from the current context."""
        return self.__contexts[self.__current_context][key]
