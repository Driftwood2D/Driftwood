####################################
# Driftwood 2D Game Dev. Suite     #
# scriptmanager.py                 #
# Copyright 2014 PariahSoft LLC    #
# Copyright 2017 Michael D. Reiley #
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

import importlib.machinery
import importlib.util
import inspect
import os
import platform
import sys
import traceback
import zipimport


class ScriptManager:
    """The Script Manager

    This class handles loading scripts and calling their functions. It defines its own method for retrieving the
    script file (independent of ResourceManager) and internally caches it forever.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """ScriptManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # Double dictionary of custom triggers mapped by name.
        self.custom_triggers = {}  # {name: {"event", "func", "nargs", "minargs"}}

        # Dictionary of module instances mapped by filename.
        self.__modules = {}

    def __contains__(self, item):
        return self._module(item) is not None

    def __getitem__(self, item):
        if self._module(item) is not None:
            return _ModuleGuard(self, item, self._module(item))
        self.driftwood.log.msg("ERROR", "Script", "no such module", item)
        return None

    def call(self, filename, func, *args):
        """Call a function from a script, loading if not already loaded.

        Usually you just want to run "Driftwood.script[path].function(args)". This wraps around that, and is cleaner
        for the engine to use in some cases.

        Args:
            filename: Filename of the python script containing the function.
            func: Name of the function to call.
            args: Arguments to pass.

        Returns:
            Function return code if succeeded, None if failed.
        """
        if args:
            return getattr(self[filename], func)(*args)
        return getattr(self[filename], func)()

    def define(self, name, event, filename, func, nargs, minargs=None):
        """Define a custom trigger that can be called directly from a map property.

        Ex. A trigger named "mytrigger" of type "on_tile" with 4 arguments can be called when the player steps onto
        that tile by setting the property "mytrigger": "a,b,c,d" on the tile in the map editor. All comma-separated
        arguments are passed as strings.

        Args:
            name: Name by which the trigger is referenced.
            event: Type of event on which to activate the trigger. [on_tile, on_layer, on_enter, on_exit, on_focus,
                                                                    on_blur]
            filename: The filename where the function is located.
            func: The name of the function to be called when the trigger is activated.
            nargs: Number of arguments to take.
            minargs: If set, a minimum number of arguments less than nargs which may be taken.

        Returns:
            True if succeeded, False if failed.
        """
        # Perform checks on input.
        if name in self.custom_triggers:
            self.driftwood.log.msg("ERROR", "Script", "define", "already defined", name)
            return False

        if event not in ["on_tile", "on_layer", "on_enter", "on_exit", "on_focus", "on_blur"]:
            self.driftwood.log.msg("ERROR", "Script", "define", "invalid event", event)
            return False

        if not isinstance(filename, str):
            self.driftwood.log.msg("ERROR", "Script", "define", "not a string", filename)
            return False

        if not isinstance(func, str):
            self.driftwood.log.msg("ERROR", "Script", "define", "not a string", func)
            return False

        if nargs < 0:
            self.driftwood.log.msg("ERROR", "Script", "define", "nargs is less than 0")
            return False

        if minargs and minargs > nargs:
            self.driftwood.log.msg("ERROR", "Script", "define", "minargs is more than nargs")
            return False

        # Insert the trigger.
        self.custom_triggers[name] = {
            "event": event,
            "filename": filename,
            "func": func,
            "nargs": nargs,
            "minargs": minargs
        }
        self.driftwood.log.info("Script", "defined", "{0} trigger \"{1}\"".format(event, name))
        return True

    def undefine(self, name):
        """Undefine a custom trigger that was defined earlier.
        
        Args:
            name: Name of the trigger to undefine.
        
        Returns:
            True if succeeded, False if failed.
        """
        # Does this exist?
        if name in self.custom_triggers:
            del self.custom_triggers[name]
            self.driftwood.log.info("Script", "undefined trigger", name)
            return True

        # Failure.
        self.driftwood.log.msg("ERROR", "Script", "undefine", "no such trigger", name)
        return False

    def is_custom_trigger(self, property_name):
        return property_name in self.custom_triggers

    def lookup(self, property_name, property):
        if property_name in self.custom_triggers:
            custom_trigger = self.custom_triggers[property_name]

            event = custom_trigger["event"]
            filename = custom_trigger["filename"]
            func = custom_trigger["func"]
            minargs = custom_trigger["minargs"]
            nargs = custom_trigger["nargs"]

            args = property.split(',')

            if minargs is not None:
                if args < minargs:
                    self.driftwood.log.msg("ERROR", "Tilemap", "read", property_name, "too few args")
                    return None
            elif nargs != len(args):
                self.driftwood.log.msg("ERROR", "Tilemap", "read", property_name, "incorrect number of args")
                return None
            return event, filename + "," + func + "," + ",".join(args)
        else:
            return None

    def _module(self, filename):
        """Return the module instance of a script, loading if not already loaded.

        This method is not crash-safe. If you call a method in a module you got from this function, errors will
        not be caught and the engine will crash if a problem occurs. This is mostly used internally by ScriptManager
        to load a module or check if one exists.

        Args:
            filename: Filename of the python script whose module instance should be returned.

        Returns: Python module instance if succeeded, None if failed.
        """
        if filename not in self.__modules:
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
        return os.sep.join(cpath)  # [1:]

    def __load(self, filename):
        """Load a script.

        Args:
            filename: Filename of the python script to load.
        """
        importpath = self.driftwood.path.find_script(filename)

        if importpath:
            try:
                # This is a directory.
                if os.path.isdir(importpath):
                    mname = os.path.splitext(os.path.split(filename)[-1])[0]

                    # Build the module.
                    spec = importlib.util.spec_from_file_location(mname, os.path.join(importpath, filename))
                    mod = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mod)
                    self.__modules[filename] = mod

                # This is hopefully a zip archive.
                else:
                    importer = zipimport.zipimporter(importpath)
                    mpath = self.__convert_path(filename)
                    if platform.system() == "Windows":  # Fix imports on Windows.
                        mpath = mpath.replace('/', '\\')
                    self.__modules[filename] = importer.load_module(mpath)

                self.driftwood.log.info("Script", "loaded", filename)
                return True

            except:
                self.driftwood.log.msg("ERROR", "Script", "__load", "broken script", filename)
                traceback.print_exc(0, sys.stdout)
                sys.stdout.flush()
                return False

        else:
            self.driftwood.log.msg("ERROR", "Script", "__load", "no such script", filename)
            return False


class _ModuleGuard:
    """This class helps us safely encapsulate a module so exceptions can be caught.
    """
    def __init__(self, manager, name, item):
        self.manager = manager
        self.__name = name
        self.__module = item

    def __getattr__(self, item):
        if hasattr(self.__module, item):
            attr = getattr(self.__module, item)
            if inspect.isfunction(attr) or inspect.isclass(attr):  # This is a callable.
                return _CallGuard(self.manager, self.__name, item, attr)
            return attr  # This is just some other data.
        self.driftwood.log.msg("ERROR", "Script", "module", "no such attribute", self.__name, item + "()")
        return None


class _CallGuard:
    """This class helps us safely encapsulate a constructor or method call so exceptions can be caught.
    """
    def __init__(self, manager, modulename, name, item):
        self.manager = manager
        self.__modulename = modulename
        self.__name = name
        self.__callable = item

    def __call__(self, *args):
        try:  # Try calling the function.
            self.manager.driftwood.log.info("Script", "called", self.__modulename, self.__name + "()")
            if args:  # We have arguments.
                return self.__callable(*args)
            else:  # We have no arguments.
                return self.__callable()

        except:  # Failure
            self.manager.driftwood.log.msg("ERROR", "Script", "call", "broken function", self.__modulename,
                                           self.__name + "()")
            traceback.print_exc(file=sys.stdout)
            sys.stdout.flush()
            return None
