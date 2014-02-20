###################################
## Driftwood 2D Game Dev. Suite  ##
## databasemanager.py            ##
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

import base64
import os
import struct


class DatabaseManager:
    """The Database Manager

    Manages a simple database for storing persistent values, using a custom format.

    Attributes:
        driftwood: Base class instance.
        filename: Filename of the database.

    Note: The database only accepts string keys and values.
    """
    def __init__(self, driftwood):
        """DatabaseManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.filename = os.path.join(self.driftwood.config["database"]["root"],
                                     self.driftwood.config["database"]["name"])

        if not os.path.exists(self.filename):
            open(self.filename, "a+").close()

    def __contains__(self, item):
        if self.__get_pos(item)[0] >= 0:
            return True
        return False

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, item, value):
        self.put(item, value)

    def __delitem__(self, item):
        self.remove(item)

    def hash(self, string):
        """Hash a string.

        Perform a hashing function on a string. This is used to hash the keys in the database file.

        Args:
            string: The string to hash.

        Returns: A 64-bit integer.
        """
        h = 0
        string += "ohscaffy"

        for i in range(len(string)):
            h = (37 * h) + ord(string[i])
        h += (h << 33)

        return h % 2**64

    def get(self, key):
        """Get a value by key.

        Retrieve a value from the database by its key.

        Args:
            key: The key whose value to retrieve.

        Returns: String value of the key.
        """
        key = self.__test_str(key)
        if not key:
            return

        with open(self.filename, "rb") as dbfile:
            while True:
                block = dbfile.read(10)
                if not block:
                    break

                stored_key, sz = struct.unpack("<QH", block)

                if self.hash(key) == stored_key:
                    self.driftwood.log.info("Database", "get", "\"{0}\"".format(key))
                    return base64.b64decode(dbfile.read(sz)).decode("utf-8")
                else:
                    dbfile.read(sz)

        self.driftwood.log.msg("ERROR", "Database", "no such key", "\"{0}\"".format(key))

    def put(self, key, value):
        """Put a value by key.

        Create or update a key with a new value.

        Args:
            key: The key to create or update.
            value: The value to store.
        """
        key, value = self.__test_str(key), self.__test_str(value)
        if not key or not value:
            print(type(key))
            return

        origvalue = value
        value = base64.b64encode(value.encode("utf-8"))
        if len(value) > 65535:
            self.driftwood.log.msg("ERROR", "Database", "value too long", "\"{0}\"".format(key))

        pos, psz = self.__get_pos(key)

        if pos >= 0:
            with open(self.filename, "rb") as dbfile:
                with open(self.filename+'~', "wb") as tmpfile:
                    tmpfile.write(dbfile.read(pos))
                    tmpfile.write(struct.pack("<QH", self.hash(key), len(value)))
                    tmpfile.write(value)
                    dbfile.seek(10+psz, 1)
                    tmpfile.write(dbfile.read())

            os.remove(self.filename)
            os.rename(self.filename+'~', self.filename)

        else:
            with open(self.filename, "ab") as dbfile:
                dbfile.write(struct.pack("<QH", self.hash(key), len(value)))
                dbfile.write(value)

        self.driftwood.log.info("Database", "put", "\"{0}\"".format(key))

    def remove(self, key):
        """Remove a key.

        Removes a key and its value from the database.

        Args:
            key: The key to remove.
        """
        key = self.__test_str(key)
        if not key:
            return

        pos, psz = self.__get_pos(key)

        if pos >= 0:
            with open(self.filename, "rb") as dbfile:
                with open(self.filename+'~', "wb") as tmpfile:
                    tmpfile.write(dbfile.read(pos))
                    dbfile.seek(10+psz, 1)
                    tmpfile.write(dbfile.read())

            os.remove(self.filename)
            os.rename(self.filename+'~', self.filename)

            self.driftwood.log.info("Database", "remove", "\"{0}\"".format(key))

        else:
            self.driftwood.log.msg("ERROR", "Database", "no such key", "\"{0}\"".format(key))

    def __get_pos(self, key):
        """Get the byte position of a key in the database and the size of its value.
        """
        pos = -1
        psz = 0

        with open(self.filename, "rb") as dbfile:
            while True:
                ptmp = dbfile.tell()

                block = dbfile.read(10)
                if not block:
                    break

                stored_key, sz = struct.unpack("<QH", block)

                if self.hash(key) == stored_key:
                    pos = ptmp
                    psz = sz
                    break
                else:
                    dbfile.seek(sz, 1)

            return (pos, psz)

    def __test_str(self, value):
        """Convert a value into a string if possible.
        """
        if type(value) != str:
            try:
                value = str(value)
                return value
            except ValueError:
                self.driftwood.log.msg("ERROR", "Database", "cannot convert to string", "\"{0}\"".format(value))

        else:
            return value
