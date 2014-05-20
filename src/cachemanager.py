###################################
## Driftwood 2D Game Dev. Suite  ##
## cachemanager.py               ##
## Copyright 2014 PariahSoft LLC ##
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
    """The Cache Manager

    This class handles the cache of recently used files. If enabled, files are stored in memory for a specified period
    of time and up to the specified maximum cache size.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """CacheManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__cache = {}
        self.__ticks = 0
        self.__now = 0.0

        # Check if the cache should be enabled.
        if self.driftwood.config["cache"]["enabled"] and self.driftwood.config["cache"]["ttl"] > 0.0:
            self.__enabled = True

            # Register the tick callback.
            self.driftwood.tick.register(self.clean, float(self.driftwood.config["cache"]["ttl"]))

        else:
            self.__enabled = False

    def __contains__(self, item):
        return item in self.__cache

    def __getitem__(self, item):
        return self.download(item)

    def __delitem__(self, item):
        self.purge(item)

    def __iter__(self):
        return self.__cache.keys()

    def upload(self, filename, contents):
        """Upload a file into the cache if the cache is enabled.

        Args:
            filename: Filename of the file to upload.
            contents: Contents of the file to upload.
        """
        if not self.__enabled:
            return

        self.__cache[filename] = {}
        self.__cache[filename]["timestamp"] = self.__now
        self.__cache[filename]["contents"] = contents

        self.driftwood.log.info("Cache", "uploaded", filename)

    def download(self, filename):
        """Download a file from the cache if present, and update the timestamp.

        Args:
            filename: Filename of the file to download.
        """
        if filename in self.__cache:
            self.__cache[filename]["timestamp"] = self.__now
            self.driftwood.log.info("Cache", "downloaded", filename)
            return self.__cache[filename]["contents"]

    def purge(self, filename):
        """Purge a file from the cache.

        Args:
            filename: Filename of the file to purge.
        """
        if filename in self.__cache:
            del self.__cache[filename]
            self.driftwood.log.info("Cache", "purged", filename)

    def flush(self):
        """Empty the cache.
        """
        self.__cache = {}
        self.driftwood.log.info("Cache", "flushed")

    def tick(self, seconds_past):
        self.__now += seconds_past

        self.clean()

    def clean(self):
        """Perform garbage collection on expired files.
        """
        expired = []

        # Collect expired filenames to be purged.
        for filename in self.__cache:
            if self.__now - self.__cache[filename]["timestamp"] >= self.driftwood.config["cache"]["ttl"]:
                expired.append(filename)

        # Clean expired files
        if expired:
            for filename in expired:
                self.purge(filename)

            self.driftwood.log.info("Cache", "cleaned", str(len(expired))+" file(s)")
