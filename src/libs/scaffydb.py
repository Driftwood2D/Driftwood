#!/bin/env python3
###################################
## ScaffyDB - A Scaffy Database  ##
## scaffydb.py                   ##
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

import argparse
import os
import struct
import sys


VERSION = "ScaffyDB v0.1.0"
COPYRIGHT = "Copyright 2014 PariahSoft LLC"


class ScaffyDB:
    """ScaffyDB - A Scaffy Database

    A simple on-disk flat file database for storing string key/value pairs.

    ScaffyDB v1 Format:
        MAGIC: "ScaffyDB01"

        FOR EACH KEY:
            1. Key Hash   := 8 BYTES       (unsigned integer) [BIG ENDIAN]
            2. Value Size := 2 BYTES       (unsigned integer) [BIG ENDIAN]
            3. Value      := 0-65535 BYTES (string)

    Attributes:
        filename: Filename of the database.
    """
    def __new__(cls, filename):
        """ScaffyDB class constructor.

        Args:
            filename: Filename of the database to use.

        Returns: ScaffyDB instance if succeeded, None if failed.
        """
        inst = object.__new__(cls)

        inst.filename = filename

        inst.__magic = "ScaffyDB01".encode("utf-8")  # Magic header.

        # Make sure the database is accessible.
        if not inst.__test_open():
            return None  # Fail.

        return inst

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

        Returns: A 64-bit integer hash.
        """
        h = 0
        string += "ohscaffy"  # Pad the end of the string to increase variety.

        # A product-addition and left-shift hash routine using empirically effective values.
        for i in range(len(string)):
            h = (37 * h) + ord(string[i])
        h += (h << 33)  # The left-shift increases variety in the lower half of the integer.

        return h % 2**64  # Overflow into 64-bit integer.

    def dump(self):
        """Dump the database.

        Dump all hash/value pairs in the database.

        Returns: Tuple of two-member hash/value tuples.
        """
        dump = []

        with open(self.filename, "rb") as dbfile:
            dbfile.seek(len(self.__magic))  # Skip the magic header.
            # Search through each key/value block in the database.
            while True:
                # Read the key hash and value size.
                block = dbfile.read(10)
                if not block:
                    break

                # Unpack the key hash and value size.
                stored_key, sz = struct.unpack(">QH", block)

                # Retrieve the value.
                dump.append((stored_key, dbfile.read(sz).decode("utf-8")))

        return tuple(dump)

    def get(self, key):
        """Get a value by key.

        Retrieve a value from the database by its key.

        Args:
            key: The key whose value to retrieve.

        Returns: String value of the key if succeeded, None if failed.
        """
        # Make sure our key is a string.
        key = self.__test_str(key)
        if not key:
            return None

        with open(self.filename, "rb") as dbfile:
            dbfile.seek(len(self.__magic))  # Skip the magic header.
            # Search through each key/value block in the database.
            while True:
                # Read the key hash and value size.
                block = dbfile.read(10)
                if not block:
                    break

                # Unpack the key hash and value size.
                stored_key, sz = struct.unpack(">QH", block)

                # Retrieve the value.
                if self.hash(key) == stored_key:
                    return dbfile.read(sz).decode("utf-8")

                # Skip the value and keep looking.
                else:
                    dbfile.seek(sz, 1)

        # No such key.
        return None

    def put(self, key, value):
        """Put a value by key.

        Create or update a key with a new value.

        Args:
            key: The key to create or update.
            value: The value to store.

        Returns: True if succeeded, false if failed.
        """
        # Make sure our key and value are strings.
        key, value = self.__test_str(key), self.__test_str(value)
        if not key or not value:
            return False

        # We only support 2-byte value sizes.
        if len(value) > 65535:
            return False

        # Try to find the position in the file of the key if it exists.
        pos, psz = self.__get_pos(key)

        # The key exists already, replace its value.
        if pos >= 0:
            with open(self.filename, "rb") as dbfile:
                dbfile.seek(len(self.__magic))
                with open(self.filename+'~', "wb") as tmpfile:
                    # Rebuild the database into a temporary file.
                    tmpfile.write(self.__magic)
                    tmpfile.write(dbfile.read(pos))
                    tmpfile.write(struct.pack(">QH", self.hash(key), len(value)))
                    tmpfile.write(value.encode("utf-8"))
                    dbfile.seek(10+psz, 1)
                    tmpfile.write(dbfile.read())

            # Copy the temporary file over the database.
            os.remove(self.filename)
            os.rename(self.filename+'~', self.filename)

        # The key does not exist yet, add it onto the end of the database.
        else:
            with open(self.filename, "ab") as dbfile:
                dbfile.write(struct.pack(">QH", self.hash(key), len(value)))
                dbfile.write(value.encode("utf-8"))

        return True

    def remove(self, key):
        """Remove a key.

        Removes a key and its value from the database.

        Args:
            key: The key to remove.

        Returns: True if succeeded, False if failed.
        """
        # Make sure our key is a string.
        key = self.__test_str(key)
        if not key:
            return False

        # Try to find the position in the file of the key if it exists.
        pos, psz = self.__get_pos(key)

        # The key exists, remove it.
        if pos >= 0:
            with open(self.filename, "rb") as dbfile:
                dbfile.seek(len(self.__magic))
                with open(self.filename+'~', "wb") as tmpfile:
                    # Rebuild the database into a temporary file.
                    tmpfile.write(self.__magic)
                    tmpfile.write(dbfile.read(pos))
                    dbfile.seek(10+psz, 1)
                    tmpfile.write(dbfile.read())

            # Copy the temporary file over the database.
            os.remove(self.filename)
            os.rename(self.filename+'~', self.filename)

            return True

        # No such key.
        else:
            return False

    def __get_pos(self, key):
        """Get the byte position of a key in the database and the size of its value.

        Returns: (position, size) tuple if succeeded, None if failed.
        """
        pos = -1
        psz = 0

        # Search through each key/value block in the database.
        with open(self.filename, "rb") as dbfile:
            dbfile.seek(len(self.__magic))
            while True:
                ptmp = dbfile.tell() - len(self.__magic)

                # Read the key hash and value size.
                block = dbfile.read(10)
                if not block:
                    break

                # Unpack the key hash and value size.
                stored_key, sz = struct.unpack(">QH", block)

                # The keys match, return this position.
                if self.hash(key) == stored_key:
                    pos = ptmp
                    psz = sz
                    break

                # Skip the value and keep looking.
                else:
                    dbfile.seek(sz, 1)

            return pos, psz

    def __test_str(self, value):
        """Convert a value into a string if possible.

        Returns: String value if succeeded, False if failed.
        """
        if type(value) != str:
            try:
                value = str(value)
                return value
            except ValueError:
                return None

        else:
            return value

    def __test_open(self):
        """Test if we can create or open the database file.

        Returns: True if succeeded, False if failed.
        """
        try:
            # Read the magic header.
            test = open(self.filename, "ab+")
            test.seek(0)
            magic = test.read(len(self.__magic))

            # New file, add magic header.
            if not magic:
                test.write(self.__magic)
                test.close()

            # Wrong magic header.
            elif magic != self.__magic:
                test.close()
                return False

        except ():
            return False

        return True


# Running as a standalone program.
if __name__ == "__main__":
    # Initialize the command line parser.
    parser = argparse.ArgumentParser(description=VERSION,
                                     formatter_class=lambda prog: argparse.HelpFormatter(prog,
                                                                                         max_help_position=40))

    # Setup command line options.
    parser.add_argument("filename", nargs='?', type=str, help="database file to open")
    parser.add_argument("--dump", action="store_true", dest="dump", help="dump key hashes and values")
    parser.add_argument("--get", nargs=1, dest="get", type=str, metavar="<key>", help="get value by key")
    parser.add_argument("--put", nargs=2, dest="put", type=str, metavar=("<key>", "<value>"), help="put value by key")
    parser.add_argument("--remove", nargs=1, dest="remove", type=str, metavar="<key>", help="remove key")
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
    if not args.filename or (not args.dump and not args.get and not args.put and not args.remove):
        parser.print_usage()
        print("{0}: error: filename and option required".format(os.path.basename(__file__)))
        sys.exit(0)

    # Initialize ScaffyDB
    db = ScaffyDB(args.filename)
    if not db:
        if not args.quiet:
            print("FAILURE :: OPEN :: {0}".format(args.filename))

        sys.exit(1)

    # --dump
    if args.dump:
        ret = db.dump()

        for pair in ret:
            print("{0:0{1}x} := {2}".format(pair[0], 16, pair[1]))

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
        ret = db.put(*args.put)

        if not ret:
            if not args.quiet:
                print("FAILURE :: PUT :: {0}".format(args.put[0]))

            sys.exit(3)

    # --remove
    if args.remove:
        ret = db.remove(args.remove[0])

        if not ret:
            if not args.quiet:
                print("FAILURE :: REMOVE :: {0}".format(args.remove[0]))

            sys.exit(4)

    # Finished successfully.
    sys.exit(0)
