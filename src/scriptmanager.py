####################################
# Driftwood 2D Game Dev. Suite     #
# scriptmanager.py                 #
# Copyright 2014 PariahSoft LLC    #
# Copyright 2016 Michael D. Reiley #
# & Paul Merrill                   #
####################################

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

import importlib.machinery, importlib.util
import os
import sys
import traceback
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

    def call(self, filename, func, *args):
        """Call a function from a script, loading if not already loaded.

        Args:
            filename: Filename of the python script containing the function.
            func: Name of the function to call.
            args: Arguments to pass.

        Returns:
            True if succeeded, False if failed.
        """
        if not filename in self.__modules:
            # Load the module if not loaded.
            res = self.__load(filename)
            if not res:
                return False

        if filename in self.__modules and hasattr(self.__modules[filename], func):
            try: # Try calling the function.
                self.driftwood.log.info("Script", "called", filename, func + "()")
                if args: # We have arguments.
                    getattr(self.__modules[filename], func)(*args)
                    return True
                else: # We have no arguments.
                    getattr(self.__modules[filename], func)()
                    return True

            except: # Failure
                self.driftwood.log.msg("ERROR", "Script", "broken function", filename, func + "()")
                traceback.print_exc(0, sys.stdout)
                sys.stdout.flush()
                return False

        else:
            self.driftwood.log.msg("ERROR", "Script", "no such function", filename, func + "()")
            return False

    def module(self, filename):
        """Return the module instance of a script, loading if not already loaded.

        Args:
            filename: Filename of the python script whose module instance should be returned.

        Returns: Python module instance if succeeded, None if failed.
        """
        if not filename in self.__modules:
            self.__load(filename)

        if filename in self.__modules:
            return self.__modules[filename]
        else:
            return None

    def __convert_path(self, filename):
        """Get around a documented zipimport flaw.

        Args:
            filename: The filename to fix.
        """
        cpath = list(os.path.split(filename))
        cpath[-1] = os.path.splitext(cpath[-1])[0]
        return os.sep.join(cpath)#[1:]

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

                    # Different import code recommended for different Python versions.
                    if sys.version_info[1] < 5:
                        self.__modules[filename] = importlib.machinery.SourceFileLoader(mname, os.path.join(importpath, filename)).load_module()
                    else:
                        spec = importlib.util.spec_from_file_location(mname, os.path.join(importpath, filename))
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        self.__modules[filename] = module

                # This is hopefully a zip archive.
                else:
                    importer = zipimport.zipimporter(importpath)
                    mpath = self.__convert_path(filename)
                    self.__modules[filename] = importer.load_module(mpath)

                self.driftwood.log.info("Script", "loaded", filename)
                return True

            except:
                self.driftwood.log.msg("ERROR", "Script", "broken script", filename)
                traceback.print_exc(0, sys.stdout)
                sys.stdout.flush()
                return False

        else:
            self.driftwood.log.msg("ERROR", "Script", "no such script", filename)
            return False