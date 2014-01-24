###################################
## Project Driftwood             ##
## path.py                       ##
## Copyright 2013 PariahSoft LLC ##
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
    """
    Simple path abstraction class which maintains a list of data pathnames and a simple virtual filesystem for files
    therein. The class supports directories and zip archives as valid pathnames.

    The last item on the path has the highest priority; if a file exists in multiple pathnames, the last occurence is
    the only one recorded in the virtual filesystem.

    This class keeps track of files, but does not read them. For file management, see the File class.
    """

    def __init__(self, config):
        """
        PathManager class initializer.

        @type  config: object
        @param config: The Config class instance.
        """
        self.config = config
        self.__root = self.config["path"]["root"] # Path root.
        self.__path = [self.config["path"]["self"]] # Start with base module.
        self.__vfs = {}

        self.append(self.config["path"]["path"]) # Start with the configured path.

    def examine(self, pathname):
        """
        Examine a directory or zip archive pathname and return the list of filenames therein.

        @type  pathname: str
        @param pathname: Pathname to examine.
        @rtype:          str
        @return:         List of files inside the pathname.
        """
        filelist = []

        if os.path.isdir(pathname):  # This is a directory.
            for root, dirs, files in os.walk(pathname):
                for name in files:
                    filelist.append(name)

        else:  # This is hopefully a zip archive.
            with zipfile.ZipFile(pathname, 'r') as zf:
                for name in zf.namelist():
                    filelist.append(name)

        return filelist

    def rebuild(self):
        """
        Rebuild the virtual filesystem from the path list, and make sure the base module is at the top.
        """
        basepath = self.config["path"]["self"]

        if self.__path[0] != basepath:  # Base module missing.
            if basepath in self.__path:  # Is it not at the top?
                self.__path.remove(basepath)  # Remove it from its current position.
            self.__path.insert(0, basepath)  # Put it back at the top.

        for pathname in self.__path:
            filelist = self.examine(pathname)
            for name in filelist:
                self.__vfs[name] = pathname

    def prepend(self, pathnames):
        """
        Prepend additional pathnames to the path list, preserving their order. If any of the pathnames already exist,
        they are moved to the new location.

        @type  pathnames: list(str)
        @param pathnames: Pathnames to prepend.
        """
        pathnames = list(pathnames)

        i = 0
        while i < len(pathnames):
            pathnames[i] = os.path.join(self.__root, pathnames[i])  # Jail the pathname to root.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])
            i += 1

        pathnames.extend(self.__path)
        self.__path = pathnames
        self.rebuild()

    def append(self, pathnames):
        """
        Append additional pathnames to the path list. If any of the pathnames already exist, they are moved to the new
        location.

        @type  pathnames: list(str)
        @param pathnames: Pathnames to append.
        """
        pathnames = list(pathnames)

        i = 0
        while i < len(pathnames):
            pathnames[i] = os.path.join(self.__root, pathnames[i])  # Jail the pathname to root.
            if pathnames[i] in self.__path:
                self.__path.remove(pathnames[i])
            i += 1

        self.__path.extend(pathnames)
        self.rebuild()

    def remove(self, pathnames):
        """
        Remove pathnames from the path list if present.

        @type  pathnames: list(str)
        @param pathnames: Pathnames to remove.
        """
        pathnames = list(pathnames)

        for pn in pathnames:
            pn = os.path.join(self.__root, pn)  # Search in root where pathnames are jailed.
            if pn in self.__path:
                self.__path.remove(pn)

        self.rebuild()

    def check(self, filename, pathname=None):
        """
        Return the pathname which owns the filename, if present. If pathname is set, check that specific pathname for
        existence of the file instead of checking the path list.

        @type  filename: str
        @param filename: The filename whose pathname to return.
        @type  pathname: str
        @param pathname: (optional) Check only this pathname for the filename.
        @rtype:          str
        @return:         The pathname which owns filename.
        """
        if pathname:
            if filename in self.examine(pathname):
                return pathname
        elif filename in self.__vfs:
            return self.__vfs[filename]
