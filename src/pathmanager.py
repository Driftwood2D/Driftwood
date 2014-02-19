###################################
## Driftwood 2D Game Dev. Suite  ##
## pathmanager.py                ##
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
import zipfile


class PathManager:
    """The Path Manager

    Simple path abstraction class which maintains a list of data pathnames and a simple virtual filesystem for files
    therein. The class supports directories and zip archives as valid pathnames.

    The last item on the path has the highest priority; if a file exists in multiple pathnames, the last occurence is
    the only one recorded in the virtual filesystem.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """PathManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__vfs = {}

        self.__config = self.driftwood.config
        self.__log = self.driftwood.log

        self.__root = self.__config["path"]["root"] # Path root.
        self.__path = [self.__config["path"]["self"]] # Start with base module.

        if self.__config["path"]["path"]:
            # Start with the configured path.
            self.append(self.__config["path"]["path"])

        else:
            self.rebuild()

    def __contains__(self, item):
        if self.find(item):
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.find(item)

    def examine(self, pathname):
        """Examine a directory or zip archive pathname and return the list of filenames therein.

        Args:
            pathname: Pathname to examine.

        Returns:
            List of files inside the pathname.
        """
        filelist = []

        try:
            # This is a directory.
            if os.path.isdir(pathname):
                for root, dirs, files in os.walk(pathname):
                    for name in files:
                        filelist.append(name)

            # This is hopefully a zip archive.
            else:
                with zipfile.ZipFile(pathname, 'r') as zf:
                    for name in zf.namelist():
                        filelist.append(name)

        except ():
            self.__log.log("ERROR", "Path", "could not examine pathname", pathname)

        return filelist

    def rebuild(self):
        """Rebuild the vfs.

        Rebuild the virtual filesystem from the path list, and make sure the base module is at the top.
        """
        basepath = self.__config["path"]["self"]

        # If the base module is missing, put it back at the top.
        if self.__path[0] != basepath:
            if basepath in self.__path:
                self.__path.remove(basepath)
            self.__path.insert(0, basepath)

        # Scan all pathnames for the files they contain and rebuild the vfs.
        for pathname in self.__path:
            filelist = self.examine(pathname)
            for name in filelist:
                self.__vfs[name] = pathname

        self.__log.info("Path", "rebuilt")

    def prepend(self, pathnames):
        """Prepend pathnames to the path list.

        Prepend additional pathnames to the path list, preserving their order. If any of the pathnames already exist,
        their priority is adjusted for their new position.

        Args:
            pathnames: List of pathnames to prepend.
        """
        if not pathnames:
            return
        pathnames = list(pathnames)

        for i in range(len(pathnames)):
            # Jail the pathname to root.
            pathnames[i] = os.path.join(self.__root, pathnames[i])

            # Remove duplicates so they can be added back in the new order.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])

        # Prepend.
        pathnames.extend(self.__path)
        self.__path = pathnames

        self.__log.info("Path", "prepended", ", ".join(pathnames))

        self.rebuild()

    def append(self, pathnames):
        """Append pathnames to the path list.

        Append additional pathnames to the path list, preserving their order. If any of the pathnames already exist,
        their priority is adjusted for their new position.

        Args:
            pathnames: List of pathnames to append.
        """
        if not pathnames:
            return
        pathnames = list(pathnames)

        for i in range(len(pathnames)):
            # Jail the pathname to root.
            pathnames[i] = os.path.join(self.__root, pathnames[i])

            # Remove duplicates so they can be added back in the new order.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])

        # Append.
        self.__path.extend(pathnames)

        self.__log.info("Path", "appended", ", ".join(pathnames))

        self.rebuild()

    def remove(self, pathnames):
        """Remove pathnames from the path list if present.

        Args:
            pathnames: List of pathnames to remove.
        """
        if not pathnames:
            return
        pathnames = list(pathnames)

        for pn in pathnames:
            # Search in root where pathnames are jailed.
            pn = os.path.join(self.__root, pn)

            # Remove.
            if pn in self.__path:
                self.__path.remove(pn)

        self.__log.info("Path", "removed", ", ".join(pathnames))

        self.rebuild()

    def find(self, filename, pathname=None):
        """Find a filename's pathname.

        Return the pathname which owns the filename, if present. If pathname is set, check that specific pathname for
        existence of the file instead of checking the path list.

        Args:
            filename: The filename whose pathname to find.
            pathname: (optional) Check only this pathname.

        Returns:
            The pathname which owns the filename, if any.
        """
        if pathname:
            if filename in self.examine(pathname):
                return pathname
        elif filename in self.__vfs:
            return self.__vfs[filename]
