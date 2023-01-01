################################
# Driftwood 2D Game Dev. Suite #
# cachemanager.py              #
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

import gc
from typing import Any, KeysView, Optional, TYPE_CHECKING

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class CacheManager:
    """The Cache Manager

    This class handles the cache of recently used files. Files are stored in memory for a specified period of time and
    up to the specified maximum cache size.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood: "Driftwood"):
        """CacheManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__cache = {}
        self.__ticks = 0
        self.__now = 0.0

        # Register the tick callback.
        self.driftwood.tick.register(self._tick, delay=float(self.driftwood.config["cache"]["ttl"]))

    def __contains__(self, item: str) -> bool:
        return item in self.__cache

    def __getitem__(self, item: str) -> Any:
        return self.download(item)

    def __delitem__(self, item: str) -> None:
        self.purge(item)

    def __iter__(self) -> KeysView:
        return self.__cache.keys()

    def upload(self, filename: str, contents: Any, keep_for_ttl: bool = True) -> bool:
        """Upload a file into the cache.

        Args:
            filename: Filename of the file to upload.
            contents: Contents of the file to upload.
            keep_for_ttl: Whether to keep the file around for the whole TTL.

        Returns:
            True if succeeded, false if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(keep_for_ttl, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "upload", "bad argument", e)
            return False

        # If a previous version existed, clean it up properly.
        if filename in self.__cache:
            self.purge(filename)

        self.__cache[filename] = {}
        self.__cache[filename]["timestamp"] = self.__now
        self.__cache[filename]["contents"] = contents
        self.__cache[filename]["keep_for_ttl"] = keep_for_ttl

        self.driftwood.log.info("Cache", "uploaded", filename)

        return True

    def download(self, filename: str) -> Any:
        """Download a file from the cache if present, and update the timestamp.

        Args:
            filename: Filename of the file to download.

        Returns:
            File contents if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "download", "bad argument", e)
            return None

        # Download from the cache.
        if filename in self.__cache:
            self.__cache[filename]["timestamp"] = self.__now
            self.driftwood.log.info("Cache", "downloaded", filename)
            return self.__cache[filename]["contents"]

        return None

    def purge(self, filename: str) -> Optional[bool]:
        """Purge a file from the cache.

        Args:
            filename: Filename of the file to purge.

        Returns:
            True
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "purge", "bad argument", e)
            return None

        # Purge the file from the cache.
        if filename in self.__cache:
            # If this file has a _terminate() function, be sure to call it first.
            if getattr(self.__cache[filename]["contents"], "_terminate", None):
                self.__cache[filename]["contents"]._terminate()

            if filename in self.__cache:
                self.driftwood.log.info("Cache", "purged", filename)
                del self.__cache[filename]
            else:
                self.driftwood.log.msg(
                    "WARNING", "Cache", "purge", filename, "file removed itself from cache while terminating"
                )

        return True

    def flush(self) -> bool:
        """Empty the cache.

        Returns:
            True
        """
        for item in self.__cache:
            self.purge(item)
        self.driftwood.log.info("Cache", "flushed")

        return True

    def clean(self) -> bool:
        """Perform garbage collection on expired files.

        Returns:
            True
        """
        ttl = self.driftwood.config["cache"]["ttl"]

        expired = []

        # Collect expired filenames to be purged.
        for filename in self.__cache:
            entry = self.__cache[filename]

            being_kept_alive = entry["keep_for_ttl"] and self.__now < entry["timestamp"] + ttl

            if not being_kept_alive:
                referrers = gc.get_referrers(entry["contents"])
                referrers.remove(entry)

                self.driftwood.log.info("Cache", "clean", "referrers", filename, referrers)

                if not referrers:
                    expired.append(filename)

        # Clean expired files
        if expired:
            for filename in expired:
                self.purge(filename)

            self.driftwood.log.info("Cache", "cleaned", str(len(expired)) + " file(s)")

        return True

    def _reverse_purge(self, inst: Any) -> None:
        """Purge an item from the cache by checking if the passed instance is cached, rather than searching by
        filename.
        """
        for items in self.__cache:
            if self.__cache[items]["contents"] is inst:
                del self.__cache[items]
                self.driftwood.log.info("Cache", "reverse-purged", items)
                break

    def _tick(self, seconds_past: float) -> None:
        self.__now += seconds_past

        self.clean()
