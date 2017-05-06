####################################
# Driftwood 2D Game Dev. Suite     #
# logmanager.py                    #
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

import sys


class LogManager:
    """The Log Manager

    This class handles the filtering and formatting of log messages.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
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
                self.__file.write("Starting up...\n")

    def msg(self, *chain):
        """Log a message.

        Args:
            chain: A list of printable values to be separated by colon-spaces and printed.

        Returns:
            True if message was printed, false otherwise.
        """
        if not self.__check_suppress(chain):
            self.__print(list(chain))
            # Die on non-info (error or warning) messages.
            if self.driftwood.config["log"]["halt"]:
                # Or not if we suppressed halting on this message.
                if not self.__check_suppress(chain, True):
                    self.driftwood.running = False
            return True
        return False

    def info(self, *chain):
        """Log an info message if verbosity is enabled.

        Args:
            chain: A list of printable values to be separated by colon-spaces and printed.

        Returns:
            True if info was printed, false otherwise.
        """
        if not self.__check_suppress(chain):
            if self.driftwood.config["log"]["verbose"]:
                self.__print(["INFO"] + list(chain))
                return True
        return False

    def __print(self, chain):
        """Format and print the string.

        Args:
            chain: A list of strings to be separated by colon-spaces and printed.
        """

        # Convert everything to strings.
        for c in range(len(chain)):
            if type(chain[c]) != str:
                chain[c] = str(chain[c])

        # Print it.
        ticks = "[{0}] ".format(self.driftwood.tick.count)
        line = ticks + ": ".join(chain)
        print(line)
        if self.__file:
            self.__file.write(line+'\n')
        sys.stdout.flush()

    def __check_suppress(self, chain, halt=False):
        """Checks whether or not the chain matches a suppression rule.
        """
        if halt:
            check = self.driftwood.config["log"]["suppress_halt"]
        else:
            check = self.driftwood.config["log"]["suppress"]
        for supp in check:
            if supp[0] == chain[0] and len(chain) >= len(supp):
                for n, s in enumerate(supp):
                    if s and s != chain[n]:
                        return False
                return True
        return False

    def __test_file_open(self):
        """Test if we can create or open the log file.
        """
        try:
            with open(self.driftwood.config["log"]["file"], "a+") as test:
                return True
        except:
            return False

    def _terminate(self):
        """Cleanup before deletion.
        """
        if self.__file:
            self.__file.write("Shutting down...\n")
            self.__file.close()
