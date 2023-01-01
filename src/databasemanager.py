################################
# Driftwood 2D Game Dev. Suite #
# databasemanager.py           #
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

import json
import os
import sys
from typing import Any, Optional, TYPE_CHECKING

import ubjson

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class DatabaseManager:
    """The Database Manager

    Stores and retrieves named objects through a Universal Binary JSON file.
    Any object type supported by JSON may be stored.

    Attributes:
        driftwood: Base class instance.
        filename: Filename of the database.
    """

    def __init__(self, driftwood: "Driftwood"):
        """DatabaseManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.filename = os.path.join(
            self.driftwood.config["database"]["root"], self.driftwood.config["database"]["name"]
        )

        # Has the database changed in memory?
        self.__changed = False

        # Make sure the database directory is accessible.
        if not self.__test_db_dir():
            sys.exit(1)  # Fail.

        self.__database = self.__load()

        # Make sure the database is accessible.
        if self.__database is None:
            self.driftwood.log.msg("FATAL", "Database", "__init__", "cannot open database", self.filename)
            sys.exit(1)  # Fail.

        self.driftwood.tick.register(self._tick, during_pause=True)

    def __contains__(self, item: str) -> bool:
        if item in self.__database:
            return True
        return False

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __setitem__(self, item: str, obj: Any) -> None:
        self.put(item, obj)

    def __delitem__(self, item: str) -> None:
        self.remove(item)

    def open(self, filename: str) -> Optional[bool]:
        """Opens a new database and closes the current one.

        If opening the new database fails, the old one stays loaded.

        Args:
            filename: The filename of the database to load, relative to the database root.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Database", "open", "bad argument", e)
            return None

        self.flush()  # Write the current database to disk first.

        filename = os.path.join(self.driftwood.config["database"]["root"], filename)
        oldfn = self.filename  # Keep track of the old filename.
        self.filename = filename  # Set the new filename.

        if not self.__test_db_open():  # Test and possibly create the new file.
            self.filename = oldfn  # We failed, revert.
            self.driftwood.log.msg("ERROR", "Database", "open", "cannot open database", filename)
            return False

        newdb = self.__load()  # Load the new database into a temporary variable.

        if newdb is None:  # Did it not load correctly?
            self.filename = oldfn  # We failed, revert.
            self.driftwood.log.msg("ERROR", "Database", "open", "cannot open database", filename)
            return False

        self.__database = newdb  # Replace the old database in memory with the new one.
        self.driftwood.log.info("Database", "open", self.filename)
        return True  # Success

    def get(self, key: str) -> Any:
        """Get an object by key (name).

        Retrieve an object from the database by its key.

        Args:
            key: The key whose object to retrieve.

        Returns: Python object if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(key, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "get", "bad argument", e)
            return None

        # Get the key.
        if key in self.__database:
            self.driftwood.log.info("Database", "get", '"{0}"'.format(key))
            return self.__database[key]

        else:
            self.driftwood.log.msg("ERROR", "Database", "get", "no such key", '"{0}"'.format(key))
            return None

    def put(self, key: str, obj: Any) -> Optional[bool]:
        """Put an object by key (name).

        Create or update a key with a new object.

        Args:
            key: The key to create or update.
            obj: The object to store.

        Returns: True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(key, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "put", "bad argument", e)
            return None

        # Is it serializable?
        try:
            ret = json.dumps(obj)
        except TypeError:
            self.driftwood.log.msg("ERROR", "Database", "put", "bad object type for key", '"{0}"'.format(key))
            return False

        self.__database[key] = obj
        self.__changed = True
        self.driftwood.log.info("Database", "put", '"{0}"'.format(key))
        return True

    def remove(self, key: str) -> Optional[bool]:
        """Remove a key.

        Removes a key and its object from the database.

        Args:
            key: The key to remove.

        Returns: True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(key, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Cache", "remove", "bad argument", e)
            return None

        # Remove the key.
        if key in self.__database:
            del self.__database[key]
            self.driftwood.log.info("Database", "remove", '"{0}"'.format(key))
            self.__changed = True
            return True
        else:
            self.driftwood.log.msg("ERROR", "Database", "remove", "no such key", '"{0}"'.format(key))
            return False

    def flush(self) -> bool:
        """Force the database to write to disk now.

        Returns:
            True
        """
        self.__changed = True
        self._tick(0)
        self.driftwood.log.info("Database", "flush", self.filename)
        return True

    def __test_db_dir(self) -> bool:
        """Test if we can create or open the database directory."""
        db_dir_path = self.driftwood.config["database"]["root"]
        try:
            # Create db directory
            if not os.path.isdir(db_dir_path):
                self.driftwood.log.info("Database", "creating database directory", db_dir_path)
                os.mkdir(db_dir_path)
        except:
            self.driftwood.log.msg(
                "FATAL", "Database", "__test_db_dir", "cannot create database directory", db_dir_path
            )
            return False

        try:
            # Try opening the directory
            os.listdir(db_dir_path)
        except:
            self.driftwood.log.msg("FATAL", "Database", "__test_db_dir", "cannot open database directory", db_dir_path)
            return False

        return True

    def __test_db_open(self) -> bool:
        """Test if we can create or open the database file."""
        try:
            with open(self.filename, "ab+") as test:
                return True
        except:
            return False

    def __load(self) -> Optional[dict]:
        """Load the database file from disk."""
        if not self.__test_db_open():
            return None

        try:
            with open(self.filename, "rb") as dbfile:
                dbcontents = dbfile.read()
                if len(dbcontents):
                    return ubjson.loadb(dbcontents)
                else:
                    return {}
        except:
            return None

    def _tick(self, seconds_past: float) -> None:
        """Tick callback.

        If there have been any changes to the database in memory, write them to disk.
        """
        if self.__changed:
            try:
                with open(self.filename, "wb") as dbfile:
                    dbfile.write(ubjson.dumpb(self.__database))
            except:
                self.driftwood.log.msg("FATAL", "Database", "_tick", "cannot write database to disk", self.filename)
                sys.exit(1)
            self.__changed = False

    def _terminate(self) -> None:
        """Cleanup before deletion."""
        # Make sure we write to disk.
        self._tick(0.0)
