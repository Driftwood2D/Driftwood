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

from dbm import dumb as dumbdbm
import os
import sys


class DatabaseManager:
    """The Database Manager

    Manages a simple database for storing persistent values, using Python's dumbdbm.

    Args:
        driftwood: Base class instance.

    Note: The database only accepts string values.
    """
    def __init__(self, driftwood):
        """DatabaseManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__database = None

        self.__open(self.driftwood.config["database"]["name"])

    def __contains__(self, item):
        if item in self.__database:
            return True
        return False

    def __getitem__(self, item):
        return self.__database[item]

    def __setitem__(self, item, value):
        if type(value) != str:
            try:
                value = str(value)
            except ValueError:
                self.driftwood.log.msg("ERROR", "Database", "cannot convert value to string", value)

        self.__database[item] = value

    def __delitem__(self, item):
        del self.__database[item]

    def __iter__(self):
        return self.__database.keys()

    def __open(self, name):
        """Open the database.

        Args:
            Basename of database to open.
        """
        try:
            self.__database = dumbdbm.open(os.path.join(self.driftwood.config["database"]["root"], name), 'c')

        except FileNotFoundError:
            self.driftwood.log.msg("FATAL", "Database", "cannot open database in directory",
                           self.driftwood.config["database"]["root"])
            sys.exit(1)

        self.driftwood.log.info("Database", "opened", name)

    def __del__(self):
        """DatabaseManager class destructor.
        """
        if self.__database:
            self.__database.close()
