####################################
# Driftwood 2D Game Dev. Suite     #
# tickmanager.py                   #
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

from inspect import signature
from types import FunctionType, MethodType
from sdl2 import SDL_Delay, SDL_GetTicks

# Upper bound on latency we can handle from the OS when we expect to return from sleep, measured in seconds.
WAKE_UP_LATENCY = 5.0 / 1000.0


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
            count: Number of ticks since engine start.
        """
        self.driftwood = driftwood
        self.count = 0

        # A list of dicts representing tick callbacks.
        #
        # Dict Keys:
        #     ticks: Ticks (seconds since engine start) at registration or last delayed call.
        #     delay: Delay in seconds between calls.
        #     callback: The function to be called.
        #     once: Whether to only call once.
        self.__registry = []

        # During a tick, this is the time the tick started. In-between ticks, this is the last time a tick started.
        self._most_recent_time = self._get_time()
        self.__last_time = self._most_recent_time

        self.paused = False

    def register(self, func, delay=0.0, once=False, during_pause=False, message=None):
        """Register a tick callback, with an optional delay between calls.

        Each tick callback must take either no arguments or one argument, for which seconds since its last call will be
        passed.

        Args:
            func: The function to be called.
            delay: (optional) Delay in seconds between calls.
            once: (optional) Whether to only call once.
            during_pause: (optional) Whether this tick is also called when the game is paused.
            message: (optional) A value to pass back to the callback as its second argument.

        Returns:
            True if succeeded, False if failed.
        """
        if not type(func) in [FunctionType, MethodType]:
            print(str(type(func)))

        for callback in self.__registry:
            if callback["function"] == func:
                self.unregister(func)

        self.__registry.append({
            "most_recent": self._most_recent_time,
            "delay": delay,
            "function": func,
            "once": once,
            "during_pause": during_pause,
            "message": message
        })

        self.driftwood.log.info("Tick", "registered callback", func.__name__)
        return True

    def unregister(self, func):
        """Unregister a tick callback.

        Args:
            func: The function to unregister.

        Returns:
            True if succeeded, False if failed.
        """
        for n, callback in enumerate(self.__registry):
            if callback["function"] == func:
                del self.__registry[n]
                self.driftwood.log.info("Tick", "unregistered callback", func.__name__)
                return True

        self.driftwood.log.msg("WARNING", "Tick", "unregister", "attempt to unregister nonexistent callback",
                               func.__name__)
        return False

    def registered(self, func):
        """Check if a function is registered.

        Args:
            func: The function to unregister.

        Returns:
            True if registered, False otherwise.
        """
        for callback in self.__registry:
            if callback["function"] == func:
                return True

        return False

    def tick(self):
        """Call all registered tick callbacks not currently delayed, and regulate tps.

        Returns:
            True
        """
        # Regulate ticks per second. Finer-grained busy wait.
        while self._get_delay() > 0.0:
            pass

        self.count += 1

        current_second = self._get_time()
        self.__last_time = self._most_recent_time
        self._most_recent_time = current_second

        for callback in self.__registry:
            self.__call_callback(callback, current_second)

        # Regulate ticks per second. Course-grained sleep by OS.
        delay = self._get_delay()
        if delay - WAKE_UP_LATENCY > 0.0:
            # SDL_Delay delays for AT LEAST as long as we request. So, don't ask to sleep exactly the right amount of
            # time. Ask for less.
            SDL_Delay(int((delay - WAKE_UP_LATENCY) * 1000.0))
        # elif delay < 0.0:
        #    self.driftwood.log.info("Tick", "tick", "tick running behind by {} seconds".format(-delay))

        return True

    def toggle_pause(self):
        """Toggle a pause in most registered ticks.

        During this time, only ticks with during_pause set to true will get called.  All gameplay ticks *should* have
        this set to false, while some UI ticks will have this set to true.

        Returns:
            True
        """
        self.paused = not self.paused
        return True

    def _get_time(self):
        """Returns the number of seconds since the program start.
        """
        return float(SDL_GetTicks()) / 1000.0

    def _get_delay(self):
        """Return delay (in seconds) until the next scheduled game tick.
        """
        now = self._get_time()
        time_delta = now - self._most_recent_time
        tick_duration = 1 / self.driftwood.config["tick"]["tps"]
        delay = tick_duration - time_delta
        return delay

    def __call_callback(self, callback, current_second):
        """Call a registered tick callback if it is time.  Update the callback's state for future ticks.

        Args:
            callback: A registered tick callback.
            current_second: The time that the current system-wide tick started at.
        """
        # Only tick if not paused.
        if self.paused and callback["during_pause"] is False:
            # Ignore this tick's passage of time.
            callback["most_recent"] += current_second - self.__last_time
        else:
            execute = False
            seconds_past = current_second - callback["most_recent"]

            # Handle a delayed tick.
            if callback["delay"]:
                if seconds_past >= callback["delay"]:
                    execute = True
            # Handle an immediate tick.
            else:
                execute = True

            if execute:
                callback["most_recent"] = current_second
                if len(signature(callback["function"]).parameters.keys()) == 0:
                    callback["function"]()
                elif callback["message"]:
                    callback["function"](seconds_past, callback["message"])
                else:
                    callback["function"](seconds_past)

                # Unregister ticks set to only run once.
                if callback["once"]:
                    self.unregister(callback["function"])
