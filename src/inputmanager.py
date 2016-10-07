####################################
# Driftwood 2D Game Dev. Suite     #
# inputmanager.py                  #
# Copyright 2014 PariahSoft LLC    #
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

from sdl2 import SDL_GetKeyName


class InputManager:
    """The Input Manager

    This class manages keyboard input.

    Attributes:
        driftwood: Base class instance.
    """

    ONDOWN, ONREPEAT, ONUP = range(3)

    def __init__(self, driftwood):
        """InputManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__handler = None

        # {keysym: {callback, throttle, delay, last_called, repeats}}
        self.__registry = {}

        self.__stack = []

        self.__now = 0.0

        # Register the tick callback.
        self.driftwood.tick.register(self._tick, during_pause=True)

    def __contains__(self, item):
        if item in self.__registry:
            return True
        return False

    def __getitem__(self, item):
        return self.__registry[item][0]

    def __setitem__(self, item, value):
        self.register(item, value)

    def __delitem__(self, item):
        self.unregister(item)

    def keyname(self, keysym):
        """Return a string naming a keysym. The up arrow key returns "Up," etc.

        Args:
            keysym: SDLKey which should be named

        Returns:
            Keyname if succeeded, None if failed.
        """
        try:
            return SDL_GetKeyName(keysym).decode()
        except:
            return None

    def keysym(self, keyname):
        """Return a keysym for the named keybinding.

        Args:
            keyname: The name of the keybinding for which to return a keysym.

        Returns:
            Keysym if succeeded, None if failed.
        """
        try:
            return getattr(self.driftwood.keycode, self.driftwood.config["input"]["keybindings"][keyname])
        except:
            return None

    def handler(self, callback):
        """Register the handler callback.

        The handler callback function will receive a call every tick that a key is being pressed. The handler must take
        one argument: the SDLKey for the key on top of the input stack. (the key which was most recently pressed.)

        Args:
            callback: Handler function to be called on any keypress.

        Returns:
            True
        """
        self.__handler = callback
        return True

    def unhandle(self):
        """Unregister the handler callback.

        Returns:
            True
        """
        self.__handler = None
        return True

    def register(self, keyid, callback, throttle=0.0, delay=0.0):
        """Register an input callback.

        The callback function will receive a call every tick that the key is on top of the input stack. (the key which
        was most recently pressed.)

        Args:
            keyid: SDLKey keysym or key name for the key which triggers the callback. (int or string)
            callback: Function to be called on the registered keypress.  It should take a single integer parameter with
                a value of InputManager.ONDOWN, ONREPEAT, or ONUP.
            throttle: Number of seconds to wait between ONREPEAT calls when the key is held down.
            delay: Number of seconds to wait after the key is pressed before making the first ONREPEAT call.

        Returns:
            True if succeeded, False if failed.
        """
        if type(keyid) == int:
            keysym = keyid
        elif type(keyid) == str:
            keysym = self.keysym(keyid)
        else:
            self.driftwood.log.msg("WARNING", "InputManager", "register", "no such key", str(keyid))
            return False

        if delay == 0.0:
            delay = throttle

        self.__registry[keysym] = {
            "callback": callback,
            "throttle": throttle,
            "delay": delay,
            "last_called": self.__now,
            "repeats": 0
        }

        return True

    def unregister(self, keysym):
        """Unregister an input callback.

        Args:
            keysym: SDLKey for the key which triggers the callback.

        Returns:
            True if succeeded, False if failed.
        """
        if keysym in self.__registry:
            del self.__registry[keysym]
            return True
        else:
            self.driftwood.log.msg("WARNING", "InputManager", "unregister", "key not registered", self.keyname(keysym))
            return False

    def pressed(self, keysym):
        """Check if a key is currently being pressed.

        Args:
            keysym: SDLKey for the keypress to check.
        """
        if keysym in self.__stack:
            return True

        return False

    def _key_down(self, keysym):
        """Push a keypress onto the input stack if not present.

        Args:
            keysym: SDLKey for the key which was pressed.
        """
        if not keysym in self.__stack:
            self.__stack.insert(0, keysym)
            if keysym in self.__registry:
                self.__registry[keysym]["callback"](InputManager.ONDOWN)
        else:
            # SDL2 gives us key-repeat events so this is actually okay.
            #self.driftwood.log.msg("WARNING", "InputManager", "key_down", "key already down", self.keyname(keysym))
            pass

    def _key_up(self, keysym):
        """Remove a keypress from the input stack if present.

        Args:
            keysym: SDLKey for the key which was released.
        """
        if keysym in self.__stack:
            self.__stack.remove(keysym)

            # Set the key callback as not called yet.
            if keysym in self.__registry:
                self.__registry[keysym]["repeats"] = 0
                self.__registry[keysym]["callback"](InputManager.ONUP)

    def _tick(self, seconds_past):
        """Tick callback.

        If there is a keypress on top of the stack and it maps to a callback in the registry, call it. Also pass the
        keypress to the secondary handler if it exists.

        If a second-callback delay is set, make sure to wait the proper amount of time before the second call.
        """
        self.__now += seconds_past

        if self.__stack:
            # The user's current (or latest, if multiple ongoing,) keydown.
            top_key = self.__stack[0]

            # Is the keypress in the registry?
            if top_key in self.__registry:
                # The callback entry for the top_key.
                top_callback = self.__registry[top_key]

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
            if self.__handler:
                self.__handler(top_key)
