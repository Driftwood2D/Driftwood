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

from sdl2 import SDL_GetTicks


class CacheManager:
    """
    This class handles the cache of recently used files. If enabled, files are stored in memory for a specified period
    of time and up to the specified maximum cache size.
    """

    def __init__(self, config):
        """
        CacheManager class initializer.

        @type  config: object
        @param config: The Config class instance.
        """
        self.config = config
        self.__log = self.config.baseclass.log
        self.__cache = {}
        self.__cachesize = 0
        self.__ticks = 0

        if self.config["cache"]["enabled"] and self.config["cache"]["size"] > 0 and self.config["cache"]["ttl"] > 0:
            self.__enabled = True
            self.config.baseclass.tick.register(self.tick, self.config["cache"]["cycle"] * 1000)

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
        Upload a file into the cache if the cache is enabled and the file won't push the cache over its size limit.

        @type  filename: str
        @param filename: Name of file to upload.
        @type  contents: str
        @param contents: Contents of file to upload.
        """
        if not self.__enabled:
            return

        if (self.__cachesize + len(contents)) / 1048576 > self.config["cache"]["size"]:
            self.__log.log("WARNING", "Cache", "upload", "cache full")
            return

        self.__cache[filename] = {}
        self.__cache[filename]["timestamp"] = self.__ticks
        self.__cache[filename]["contents"] = contents
        self.__cachesize += len(contents)

        self.__log.info("Cache", "uploaded", filename)

    def download(self, filename):
        """
        Download a file from the cache if present, and update the timestamp.

        @type  filename: str
        @param filename: Name of file to download.
        """
        if filename in self.__cache:
            self.__cache[filename]["timestamp"] = self.__ticks
            self.__log.info("Cache", "downloaded", filename)
            return self.__cache[filename]["contents"]

    def purge(self, filename):
        """
        Purge a file from the cache.

        @type  filename: str
        @param filename: Name of file to purge.
        """
        if filename in self.__cache:
            self.__cachesize -= len(self.__cache[filename]["contents"])
            del self.__cache[filename]
            self.__log.info("Cache", "purged", filename)

    def flush(self):
        """
        Flush the cache.
        """
        self.__cache = {}
        self.__log.info("Cache", "flushed")

    def tick(self):
        """
        Tick callback which calls clean() at appropriate times.
        """
        self.__ticks = SDL_GetTicks()
        self.clean()

    def clean(self):
        """
        Perform garbage collection on expired files.
        """
        for filename in self.__cache:
            if self.__ticks / 1000 - self.__cache[filename]["timestamp"] / 1000 >= self.config["cache"]["ttl"]:
                self.purge(filename)

        self.__log.info("Cache", "cleaned")
