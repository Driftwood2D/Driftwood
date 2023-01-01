################################
# Driftwood 2D Game Dev. Suite #
# pathmanager.py               #
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

import os
import platform
import zipfile
from typing import List, Optional, TYPE_CHECKING

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class PathManager:
    """The Path Manager

    Simple path abstraction class which maintains a list of data pathnames and a simple virtual filesystem for files
    therein. The class supports directories and zip archives as valid pathnames.

    The last item on the path has the highest priority; if a file exists in multiple pathnames, the last occurence is
    the only one recorded in the virtual filesystem.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood: "Driftwood"):
        """PathManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__vfs = {}

        self.__root = self.driftwood.config["path"]["root"]  # Path root.
        if not self.__root.endswith("/"):  # Another stupid Windows hack.
            self.__root += "/"

        self.__common = os.path.join(self.__root, "__common__/")
        self.__path = [self.__common]  # Start with base module.

        if self.driftwood.config["path"]["path"]:
            # Start with the configured path.
            self.append(self.driftwood.config["path"]["path"])

        else:
            self.rebuild()

    def __contains__(self, item: str) -> bool:
        if self.find(item):
            return True
        return False

    def __getitem__(self, item: str) -> Optional[str]:
        if self.__contains__(item):
            return self.find(item)

    def examine(self, pathname: str) -> List[str]:
        """Examine a directory or zip archive pathname and return the list of filenames therein.

        Args:
            pathname: Pathname to examine.

        Returns:
            Tuple of files inside the pathname.
        """
        # Input Check
        try:
            CHECK(pathname, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "examine", "bad argument", e)
            return []

        filelist = []

        # Make sure we don't end in a slash.
        if pathname.endswith("/"):
            pathname = pathname[:-1]

        try:
            if os.path.isdir(pathname):  # This is a directory.
                for root, dirs, files in os.walk(pathname):
                    for name in files:
                        filelist.append(os.path.join(root, name))
                for file in range(len(filelist)):
                    if platform.system() == "Windows":  # Fix paths on Windows.
                        filelist[file] = filelist[file].replace("\\", "/")
                    filelist[file] = filelist[file].replace(pathname + "/", "")

            else:  # This is hopefully a zip archive.
                with zipfile.ZipFile(pathname, "r") as zf:
                    for name in zf.namelist():
                        filelist.append(name)

        except:
            self.driftwood.log.msg("ERROR", "Path", "examine", "could not examine pathname", pathname)

        return filelist

    def rebuild(self) -> bool:
        """Rebuild the vfs.

        Rebuild the virtual filesystem from the path list, and make sure the common package is at the top.

        Returns:
            True
        """
        # If the common package is missing, put it back at the top.
        if self.__path[0] != self.__common:
            if self.__common in self.__path:
                self.__path.remove(self.__common)
            self.__path.insert(0, self.__common)

        # Scan all pathnames for the files they contain and rebuild the vfs.
        for pathname in self.__path:
            filelist = self.examine(pathname)
            for name in filelist:
                self.__vfs[name] = pathname

        self.driftwood.log.info("Path", "rebuilt")

        return True

    def prepend(self, pathnames: List[str]) -> bool:
        """Prepend pathnames to the path list.

        Prepend additional pathnames to the path list, preserving their order. If any of the pathnames already exist,
        their priority is adjusted for their new position.

        Args:
            pathnames: List of pathnames to prepend.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(pathnames, list)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "prepend", "bad argument", e)
            return False

        for i in range(len(pathnames)):
            # Jail the pathname to root.
            pathnames[i] = os.path.join(self.__root, pathnames[i])

            # Remove duplicates so they can be added back in the new order.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])

        # Prepend.
        pathnames.extend(self.__path)
        self.__path = pathnames

        self.driftwood.log.info("Path", "prepended", ", ".join(pathnames))

        self.rebuild()

        return True

    def append(self, pathnames: List[str]) -> bool:
        """Append pathnames to the path list.

        Append additional pathnames to the path list, preserving their order. If any of the pathnames already exist,
        their priority is adjusted for their new position.

        Args:
            pathnames: List of pathnames to append.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(pathnames, list)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "append", "bad argument", e)
            return False

        for i in range(len(pathnames)):
            # Jail the pathname to root.
            pathnames[i] = os.path.join(self.__root, pathnames[i])

            # Remove duplicates so they can be added back in the new order.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])

        # Append.
        self.__path.extend(pathnames)

        self.driftwood.log.info("Path", "appended", ", ".join(pathnames))

        self.rebuild()

        return True

    def remove(self, pathnames: List[str]) -> bool:
        """Remove pathnames from the path list if present.

        Args:
            pathnames: List of pathnames to remove.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(pathnames, list)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "remove", "bad argument", e)
            return False

        pathnames = list(pathnames)

        for pn in pathnames:
            # Search in root where pathnames are jailed.
            pn = os.path.join(self.__root, pn)

            # Remove.
            if pn in self.__path:
                self.__path.remove(pn)
            else:
                self.driftwood.log.msg("WARNING", "Path", "remove", "attempt to remove nonexistent pathname", pn)
                return False

        self.driftwood.log.info("Path", "removed", ", ".join(pathnames))

        self.rebuild()

        return True

    def find(self, filename: str, pathname: str = None) -> Optional[str]:
        """Find a filename's pathname.

        Return the pathname which owns the filename, if present. If pathname is set, check that specific pathname for
        existence of the file instead of checking the path list.

        Args:
            filename: The filename whose pathname to find.
            pathname: (optional) Check only this pathname.

        Returns:
            The pathname which owns the filename, if any. Otherwise None.
        """
        # Input Check
        try:
            CHECK(filename, str)
            if pathname is not None:
                CHECK(pathname, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "find", "bad argument", e)
            return None

        if pathname:
            if filename in self.examine(pathname):
                return pathname
        elif filename in self.__vfs:
            return self.__vfs[filename]
        else:
            return None

    def find_script(self, filename: str) -> Optional[str]:
        """Slightly less dumb hack to look for a compiled script if the uncompiled script cannot be found or vice versa."""
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Path", "find_script", "bad argument", e)
            return None

        ret = self.find(filename)
        if not ret:
            if filename.endswith(".py"):
                filename = filename[:-2] + "pyc"
            elif filename.endswith(".pyc"):
                filename = filename[:-3] + "py"
            ret = self.find(filename)
        if not ret:
            return None
        return ret
