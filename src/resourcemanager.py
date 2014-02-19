###################################
## Driftwood 2D Game Dev. Suite  ##
## resourcemanager.py            ##
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


class ResourceManager:
    """The Resource Manager

    Simple resource management class which retrieves the contents of a file in the path vfs.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """ResourceManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__log = self.driftwood.log
        self.__cache = self.driftwood.cache
        self.__path = self.driftwood.path

    def __contains__(self, item):
        if self.__path[item]:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.request(item)

    def request(self, filename, binary = False):
        """Retrieve the contents of a file.

        Args:
            filename: Filename of the file to read.
            binary: Whether the file is a binary file, rather than a plaintext file.

        Returns:
            Contents of the requested file, if present.
        """
        self.__log.info("Resource", "requested", filename)

        # If the file is already cached, return the cached version.
        if filename in self.__cache:
            return self.__cache[filename]

        pathname = self.__path[filename]
        if pathname:
            try:
                # This is a directory.
                if os.path.isdir(pathname):
                    if binary:
                        f = open(os.path.join(pathname, filename), "rb")
                    else:
                        f = open(os.path.join(pathname, filename))
                    contents = f.read()
                    f.close()

                # This is hopefully a zip archive.
                else:
                    with zipfile.ZipFile(pathname, 'r') as zf:
                        contents = zf.read(filename)

                # Upload the file to the cache.
                self.__cache.upload(filename, contents)

                return contents

            except ():
                self.__log.log("ERROR", "Resource", "could not read file", filename)

        else:
            self.__log.log("ERROR", "Resource", "no such file", filename)
