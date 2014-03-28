###################################
## Driftwood 2D Game Dev. Suite  ##
## scriptmanager.py              ##
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

import imp
import os
import zipimport


class ScriptManager:
    """The Script Manager

    This class handles loading scripts and calling their functions. It defines its own method for retrieving the
    script file (independant of ResourceManager) and internally caches it forever.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """ScriptManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # Dictionary of module instances mapped by filename.
        self.__modules = {}

    def __convert_path(self, filename):
        """Get around a documented zipimport flaw.

        Args:
            filename: The filename to fix.
        """
        cpath = list(os.path.split(filename))
        cpath[-1] = os.path.splitext(cpath[-1])[0]
        return os.sep.join(cpath)[1:]

    def __load(self, filename):
        """Load a script.

        Args:
            filename: Filename of the python script to load.
        """
        importpath = self.driftwood.path.find(filename)

        if importpath:
            try:
                # This is a directory.
                if os.path.isdir(importpath):
                    mname = os.path.splitext(os.path.split(filename)[-1])[0]
                    self.__modules[filename] = imp.load_source(mname, os.path.join(importpath, filename))

                # This is hopefully a zip archive.
                else:
                    importer = zipimport.zipimporter(importpath)
                    mpath = self.__convert_path(filename)
                    self.__modules[filename] = importer.load_module(mpath)

                self.driftwood.log.info("Script", "loaded", filename)

            except:
                self.driftwood.log.msg("ERROR", "Script", "could not load script", filename)

        else:
            self.driftwood.log.msg("ERROR", "Script", "no such script", filename)

    def call(self, filename, func, arg=None):
        """Call a function from a script, loading if not already loaded.

        Args:
            filename: Filename of the python script containing the function.
            func: Name of the function to call.
            arg: Pass this argument if not None.
        """
        if not filename in self.__modules:
            self.__load(filename)

        if filename in self.__modules and hasattr(self.__modules[filename], func):
            self.driftwood.log.info("Script", "called", filename, func + "()")
            if arg:
                getattr(self.__modules[filename], func)(arg)
            else:
                getattr(self.__modules[filename], func)()

        else:
            self.driftwood.log.msg("ERROR", "Script", filename, "no such function", func + "()")

    def module(self, filename):
        """Return the module instance of a script, loading if not already loaded.

        Args:
            filename: Filename of the python script whose module instance should be returned.

        Returns: Python module instance.
        """
        if not filename in self.__modules:
            self.__load(filename)

        if filename in self.__modules:
            return self.__modules[filename]
