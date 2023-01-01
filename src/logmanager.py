################################
# Driftwood 2D Game Dev. Suite #
# logmanager.py                #
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

import datetime
import sys
from typing import Any, List, TYPE_CHECKING

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class LogManager:
    """The Log Manager

    This class handles the filtering and formatting of log messages.

    Attributes:
        driftwood: Base class instance.
    """

    driftwood: "Driftwood"

    def __init__(self, driftwood: "Driftwood"):
        """LogManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__file = None  # Log file if set.

        # Test if we can open the log file, if we want one.
        if self.driftwood.config["log"]["file"]:
            if not self.__test_file_open():
                self.msg("ERROR", "Log", "cannot open log file for writing", self.driftwood.config["log"]["file"])
            else:
                self.__file = open(self.driftwood.config["log"]["file"], "a+")
                self.__file.write("[" + str(datetime.datetime.now()) + "]\n")
                self.__file.write("[0] Starting up...\n")

    def msg(self, *chain: Any) -> bool:
        """Log a message.

        Args:
            chain: A list of printable values to be separated by colon-spaces and printed.

        Returns:
            True if message was printed, false otherwise.
        """
        chain = list(chain)

        # Convert everything to strings.
        for c in range(len(chain)):
            if type(chain[c]) != str:
                chain[c] = str(chain[c])

        if not self.__check_suppress(chain):
            self.__print(chain)
            # Die on non-info (error or warning) messages.
            if self.driftwood.config["log"]["halt"]:
                # Or not if we suppressed halting on this message.
                if not self.__check_suppress(chain, True):
                    self.driftwood.running = False
            return True
        return False

    def info(self, *chain: Any):
        """Log an info message if verbosity is enabled.

        Args:
            chain: A list of printable values to be separated by colon-spaces and printed.

        Returns:
            True if info was printed, false otherwise.
        """
        chain = list(chain)

        # Convert everything to strings.
        for c in range(len(chain)):
            if type(chain[c]) != str:
                chain[c] = str(chain[c])

        if not self.__check_suppress(chain):
            if self.driftwood.config["log"]["verbose"]:
                self.__print(["INFO"] + chain)
                return True
        return False

    def __print(self, chain: List[str]) -> None:
        """Format and print the string.

        Args:
            chain: A list of strings to be separated by colon-spaces and printed.
        """
        ticks = "[{0}] ".format(self.driftwood.tick.count)
        line = ticks + ": ".join(chain)
        print(line)
        if self.__file:
            self.__file.write(line + "\n")
        sys.stdout.flush()

    def __check_suppress(self, chain: List[str], halt: bool = False) -> bool:
        """Checks whether or not the chain matches a suppression rule."""
        if halt:
            check = self.driftwood.config["log"]["suppress_halt"]
        else:
            check = self.driftwood.config["log"]["suppress"]
        if chain:
            for supp in check:
                if supp[0] == chain[0] and len(chain) >= len(supp):
                    for n, s in enumerate(supp):
                        if s and s != chain[n]:
                            return False
                    return True
        return False

    def __test_file_open(self) -> bool:
        """Test if we can create or open the log file."""
        try:
            with open(self.driftwood.config["log"]["file"], "a+") as test:
                return True
        except:
            return False

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        if self.__file:
            ticks = "[{0}]".format(self.driftwood.tick.count)
            self.__file.write(ticks + " Shutting down...\n\n")
            self.__file.close()
