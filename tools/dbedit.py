#!/bin/env python3
################################
# UBJSON Database Editor       #
# dbedit.py                    #
# Copyright 2017 Sei Satzparad #
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

import argparse
import json
import os
import sys
import ubjson


VERSION = "Universal Binary JSON Database Editor for Driftwood v0.2.0"
COPYRIGHT = "Copyright 2017 Michael D. Reiley"


class UBJdb:
    """Universal Binary JSON Database Editor

    A simple on-disk flat file database for storing key/object pairs, using Universal Binary JSON.
    <https://ubjson.org/>

    Attributes:
        filename: Filename of the database.
        makenew: Whether to make a database if one does not exist.
    """
    def __init__(self, filename, makenew=False):
        """UBJdb class constructor.

        Args:
            filename: Filename of the database to use.

        Returns: UBJdb instance if succeeded, None if failed.
        """

        self.filename = filename
        self.fail = False
        self.makenew = makenew

        self.database = self.__load()

        # Make sure the database is accessible and real.
        if self.database is None:
            self.fail = True
            return

    def get(self, key):
        """Get an object by key (name).

        Retrieve an object from the database by its key.

        Args:
            key: The key whose object to retrieve.

        Returns: Python object if succeeded, None if failed.
        """
        if key in self.database:
            return self.database[key]

        else:
            return None

    def put(self, key, obj):
        """Put an object by key (name).

        Create or update a key with a new object.

        Args:
            key: The key to create or update.
            obj: The object to store.

        Returns: True if succeeded, False if failed.
        """
        # Test if this is a dict or another kind of object.
        try:
            ret = json.loads(obj)
        except json.JSONDecodeError:

            # It's another kind of object, but is it serializable?
            try:
                ret = json.dumps(obj)
            except TypeError:
                return False

        self.database[key] = ret
        return True

    def remove(self, key):
        """Remove a key.

        Removes a key and its object from the database.

        Args:
            key: The key to remove.

        Returns: True if succeeded, False if failed.
        """
        if key in self.database:
            del self.database[key]
            return True
        else:
            return False

    def __test_db_open(self):
        """Test if we can create or open the database file.
        """
        try:
            if self.makenew:
                with open(self.filename, "ab+") as test:
                    return True
            else:
                with open(self.filename, "rb") as test:
                    return True
        except:
            return False

    def __load(self):
        """Load the database file from disk.
        """
        if not self.__test_db_open():
            return None

        try:
            with open(self.filename, 'rb') as dbfile:
                dbcontents = dbfile.read()
                if len(dbcontents):
                    return ubjson.loadb(dbcontents)
                else:
                    return {}
        except:
            return None


# Running as a standalone program.
if __name__ == "__main__":
    # Initialize the command line parser.
    parser = argparse.ArgumentParser(description=VERSION,
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog,
                                                                                         max_help_position=40))

    # Setup command line options.
    parser.add_argument("filename", nargs='?', type=str, help="database file to open")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--list", action="store_true", dest="list", help="list key names")
    group.add_argument("--dump", action="store_true", dest="dump", help="dump ubjson data")
    group.add_argument("--get", nargs=1, dest="get", type=str, metavar="<key>", help="get ubjson object by key")
    group.add_argument("--put", nargs=2, dest="put", type=str, metavar=("<key>", "<object|->"),
                       help="put ubjson object by key, \'-\' to read stdin")
    group.add_argument("--remove", nargs=1, dest="remove", type=str, metavar="<key>", help="remove key")

    parser.add_argument("--quiet", action="store_true", dest="quiet", help="do not print failure messages")
    parser.add_argument("--version", action="store_true", dest="version", help="print the version string")

    # Retrieve arguments.
    args = parser.parse_args()

    # --version
    if args.version:
        print(VERSION)
        print(COPYRIGHT)
        sys.exit(0)  # Exit here, this is all we're doing today.

    # Nothing was passed.
    if not args.filename or (not args.list and not args.dump and not args.get and not args.put and not args.remove):
        parser.print_usage()
        print("{0}: error: filename and option required".format(os.path.basename(__file__)))
        sys.exit(0)

    # Initialize UBJdb
    if args.put:  # We don't create a new database unless using --put.
        db = UBJdb(args.filename, True)
    else:
        db = UBJdb(args.filename)
    if not db or db.fail:
        if not args.quiet:
            print("FAILURE :: OPEN :: {0}".format(args.filename))

        sys.exit(1)

    # --list
    if args.list:
        for key in db.database.keys():
            print(key)

    # --dump
    if args.dump:
        for key in db.database.keys():
            print(key+' := '+str(db.database[key]))

    # --get
    if args.get:
        ret = db.get(args.get[0])

        if not ret:
            if not args.quiet:
                print("FAILURE :: GET :: {0}".format(args.get[0]))

            sys.exit(2)

        print(ret)

    # --put
    if args.put:
        if args.put[1] == '-':  # Collect from stdin.
            ret = db.put(args.put[0], sys.stdin.read())
        else:
            ret = db.put(*args.put)

        if not ret:
            if not args.quiet:
                print("FAILURE :: PUT :: {0}".format(args.put[0]))

            sys.exit(3)

        try:
            with open(db.filename, 'wb') as dbfile:
                dbfile.write(ubjson.dumpb(db.database))
        except:
            print("FAILURE :: PUT :: {0}".format(args.put[0]))
            sys.exit(5)

    # --remove
    if args.remove:
        ret = db.remove(args.remove[0])

        if not ret:
            if not args.quiet:
                print("FAILURE :: REMOVE :: {0}".format(args.remove[0]))

            sys.exit(4)

        try:
            with open(db.filename, 'wb') as dbfile:
                dbfile.write(ubjson.dumpb(db.database))
        except:
            print("FAILURE :: REMOVE :: {0}".format(args.put[0]))
            sys.exit(6)

    # Finished successfully.
    sys.exit(0)
