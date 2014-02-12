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
    """The Cache Manager

    This class handles the cache of recently used files. If enabled, files are stored in memory for a specified period
    of time and up to the specified maximum cache size.

    Attributes:
        config: ConfigManager instance.
    """

    def __init__(self, config):
        """CacheManager class initializer.

        Args:
            config: Link back to the ConfigManager.
        """
        self.config = config

        self.__log = self.config.baseclass.log
        self.__cache = {}
        self.__ticks = 0

        # Check if the cache should be enabled.
        if self.config["cache"]["enabled"] and self.config["cache"]["ttl"] > 0:
            self.__enabled = True

            # Register the tick callback.
            self.config.baseclass.tick.register(self.clean, self.config["cache"]["ttl"] * 1000)

        else:
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
        """Upload a file into the cache if the cache is enabled.

        Args:
            filename: Filename of the file to upload.
            contents: Contents of the file to upload.
        """
        if not self.__enabled:
            return

        self.__cache[filename] = {}
        self.__cache[filename]["timestamp"] = SDL_GetTicks()
        self.__cache[filename]["contents"] = contents

        self.__log.info("Cache", "uploaded", filename)

    def download(self, filename):
        """Download a file from the cache if present, and update the timestamp.

        Args:
            filename: Filename of the file to download.
        """
        if filename in self.__cache:
            self.__cache[filename]["timestamp"] = SDL_GetTicks()
            self.__log.info("Cache", "downloaded", filename)
            return self.__cache[filename]["contents"]

    def purge(self, filename):
        """Purge a file from the cache.

        Args:
            filename: Filename of the file to purge.
        """
        if filename in self.__cache:
            del self.__cache[filename]
            self.__log.info("Cache", "purged", filename)

    def flush(self):
        """Empty the cache.
        """
        self.__cache = {}
        self.__log.info("Cache", "flushed")

    def clean(self):
        """Perform garbage collection on expired files.
        """
        expired = []

        # Collect expired filenames to be purged.
        for filename in self.__cache:
            if SDL_GetTicks() / 1000 - self.__cache[filename]["timestamp"] / 1000 >= self.config["cache"]["ttl"]:
                expired.append(filename)

        # Clean expired files
        if expired:
            for filename in expired:
                self.purge(filename)

            self.__log.info("Cache", "cleaned", str(len(expired))+" file(s)")
