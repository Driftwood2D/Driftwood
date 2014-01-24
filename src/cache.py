###################################
## Project Driftwood             ##
## cache.py                      ##
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


class CacheManager:
    def __init__(self, config):
        """
        CacheManager class initializer.

        @type  config: object
        @param config: The Config class instance.
        """
        self.config = config
        self.__cache = {}
        self.__ticks = 0
        self.__ticks_since_clean = 0

        if self.config["cache"]["enabled"] and self.config["cache"]["size"] > 0 and self.config["cache"]["ttl"] > 0:
            self.__enabled = True
        self.__enabled = False

    def __contains__(self, item):
        if item in self.__cache:
            return True
        return False

    def __getitem__(self, item):
        return self.download(item)

    def __delitem__(self, item):
        self.purge(item)

    def __iter__(self):
        return self.__cache.items()

    def upload(self, filename, contents):
        """
        Upload a file into the cache if enabled.

        @type  filename: str
        @param filename: Name of file to upload.
        @type  contents: str
        @param contents: Contents of file to upload.
        """
        if not self.__enabled:
            pass

        self.__cache[filename] = {}
        self.__cache[filename]["timestamp"] = self.__ticks
        self.__cache[filename]["contents"] = contents

    def download(self, filename):
        """
        Download a file from the cache if present.

        @type  filename: str
        @param filename: Name of file to download.
        """
        if filename in self.__cache:
            return self.__cache[filename]["contents"]

    def purge(self, filename):
        """
        Purge a file from the cache.

        @type  filename: str
        @param filename: Name of file to purge.
        """
        if filename in self.__cache:
            del self.__cache[filename]

    def flush(self):
        """
        Flush the cache.
        """
        self.__cache = {}

    def tick(self, ticks):
        """
        Receives SDL_GetTicks() from the base class, and calls clean() at appropriate times.

        @type  ticks: int
        @param ticks: Milliseconds since start.)
        """
        self.__ticks = ticks
        if self.__ticks / 1000 - self.__ticks_since_clean / 1000 >= self.config["cache"]["clean_rate"]:
            self.clean()

    def clean(self):
        """
        Perform garbage collection on expired files and clear space when overdrawn.
        """
        for filename in self.__cache:
            if self.__ticks / 1000 - self.__cache[filename]["timestamp"] >= self.config["cache"]["ttl"]:
                self.purge(filename)

        # TODO: Optimize this next part.
        oversized = True
        while oversized:  # Check if we're overdrawn and delete the oldest files until under the size limit.
            cachesize = 0
            eldest = [{}, self.__ticks]
            for filename in self.__cache:  # Calculate the size in memory of the cache.
                cachesize += self.__cache[filename]["contents"].__len__()
                if self.__cache[filename]["timestamp"] < eldest[1]:  # Find the oldest file.
                    eldest[0] = filename
                    eldest[1] = self.__cache[filename]["timestamp"]

            if cachesize / 1000 > self.config["cache"]["size"]:  # We're overdrawn, purge it.
                self.purge(eldest[0])
