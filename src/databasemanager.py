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

import os
import sys

from libs import scaffydb


class DatabaseManager:
    """The Database Manager

    Manages a wrapper around ScaffyDB for storing persistent values.

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

        self.__scaffydb = scaffydb.ScaffyDB(self.filename)

        # Make sure the database is accessible.
        if not self.__scaffydb or not self.__test_db_dir():
            self.driftwood.log.msg("FATAL", "Database", "cannot open database", self.filename)
            sys.exit(1)  # Fail.

    def __contains__(self, item):
        if "DB:"+item in self.driftwood.cache or self.__scaffydb.getpos(item)[0] >= 0:
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

        Returns: A 64-bit integer hash.
        """
        return self.__scaffydb.hash(string)

    def get(self, key):
        """Get a value by key.

        Retrieve a value from the database by its key.

        Args:
            key: The key whose value to retrieve.

        Returns: String value of the key if succeeded, None if failed.
        """
        value = self.driftwood.cache.download("DB:"+key)  # Check if the value is cached.

        if not value:
            value = self.__scaffydb.get(key)

        if not value:
            self.driftwood.log.msg("ERROR", "Database", "no such key", "\"{0}\"".format(key))
            return None

        self.driftwood.log.info("Database", "get", "\"{0}\"".format(key))
        return value

    def put(self, key, value):
        """Put a value by key.

        Create or update a key with a new value.

        Args:
            key: The key to create or update.
            value: The value to store.

        Returns: True if succeeded, false if failed.
        """
        ret = self.__scaffydb.put(key, value)

        if not ret:
            self.driftwood.log.msg("ERROR", "Database", "could not assign value to key", "\"{0}\"".format(key))
            return False

        self.driftwood.cache.upload("DB:"+key, value)  # Cache the value.
        self.driftwood.log.info("Database", "put", "\"{0}\"".format(key))
        return True

    def remove(self, key):
        """Remove a key.

        Removes a key and its value from the database.

        Args:
            key: The key to remove.

        Returns: True if succeeded, False if failed.
        """
        ret = self.__scaffydb.remove(key)

        if not ret:
            self.driftwood.log.msg("ERROR", "Database", "no such key", "\"{0}\"".format(key))
            return False

        self.driftwood.cache.purge("DB:"+key)  # Remove the value from the cache.
        self.driftwood.log.info("Database", "remove", "\"{0}\"".format(key))
        return True

    def __test_db_dir(self):
        """Test if we can create or open the database directory.
        """
        db_dir_path = self.driftwood.config["database"]["root"]
        try:
            # Create db directory
            if not os.path.isdir(db_dir_path):
                self.driftwood.log.info("Database", "creating database directory", db_dir_path)
                os.mkdir(db_dir_path)
        except ():
            self.driftwood.log.msg("FATAL", "Database", "cannot create database directory", db_dir_path)
            return False

        try:
            # Try openning the dir
            files = os.listdir(db_dir_path)
        except ():
            self.driftwood.log.msg("FATAL", "Database", "cannot open database directory", db_dir_path)
            return False

        return True
