################################
# Driftwood 2D Game Dev. Suite #
# scriptmanager.py             #
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

import importlib.util
import inspect
import os
import platform
import traceback
import types
from typing import Any, Callable, Optional, Tuple, TYPE_CHECKING
import zipimport

from check import CHECK, CheckFailure

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class ScriptManager:
    """The Script Manager

    This class handles loading scripts and calling their functions. It defines its own method for retrieving the
    script file (independent of ResourceManager) and internally caches it forever.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood: "Driftwood"):
        """ScriptManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        # Double dictionary of custom triggers mapped by name.
        self.custom_triggers = {}  # {name: {"event", "func", "nargs", "minargs"}}

        self.global_triggers = {}

        # Dictionary of module instances mapped by filename.
        self.__modules = {}

    def __contains__(self, item: str) -> bool:
        return self._module(item) is not None

    def __getitem__(self, item: str) -> Any:
        ret = self._module(item)
        if ret not in [None, False]:
            return ret
        elif ret is False:
            self.driftwood.log.msg("ERROR", "Script", "no such module", item)
        else:
            self.driftwood.log.msg("ERROR", "Script", "error from module", item)
        return None

    def call(self, filename: str, func: str, *args: Any) -> Any:
        """Call a function from a script, loading if not already loaded.

        Usually you just want to run "Driftwood.script[path].function(args)". This wraps around that, and is cleaner
        for the engine to use in most cases. It also prevents exceptions from raising into the engine scope and
        crashing it, so the engine will always call scripts through this method.

        Args:
            filename: Filename of the python script containing the function.
            func: Name of the function to call.
            args: Arguments to pass.

        Returns:
            Function return code if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(func, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "call", "bad argument", e)
            return None

        try:
            return getattr(self[filename], func)(*args)
        except Exception:
            self.driftwood.log.msg(
                "ERROR",
                "Script",
                "call",
                "error from function",
                filename,
                func + "()",
                "\n" + traceback.format_exc().rstrip(),
            )
            return None

    def define(self, name: str, event: str, filename: str, func: str, nargs: int, minargs: int = None) -> bool:
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
        # Input Check
        try:
            CHECK(name, str)
            CHECK(event, str)
            CHECK(filename, str)
            CHECK(func, str)
            CHECK(nargs, int, _min=0)
            if minargs is not None:
                CHECK(minargs, int, _max=nargs)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "define", "bad argument", e)
            return False

        if name in self.custom_triggers:
            self.driftwood.log.msg("ERROR", "Script", "define", "already defined", name)
            return False

        if event not in ["on_tile", "on_layer", "on_enter", "on_exit", "on_focus", "on_blur"]:
            self.driftwood.log.msg("ERROR", "Script", "define", "invalid event", event)
            return False

        # Insert the trigger.
        self.custom_triggers[name] = {
            "event": event,
            "filename": filename,
            "func": func,
            "nargs": nargs,
            "minargs": minargs,
        }
        self.driftwood.log.info("Script", "defined", '{0} trigger "{1}"'.format(event, name))
        return True

    def undefine(self, name: str) -> bool:
        """Undefine a custom trigger that was defined earlier.

        Args:
            name: Name of the trigger to undefine.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(name, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "undefine", "bad argument", e)
            return False

        # Does this exist?
        if name in self.custom_triggers:
            del self.custom_triggers[name]
            self.driftwood.log.info("Script", "undefined trigger", name)
            return True

        # Failure.
        self.driftwood.log.msg("ERROR", "Script", "undefine", "no such trigger", name)
        return False

    def register(self, event: str, func: Callable[[], None]) -> bool:
        """Define a global trigger that is called everytime a particular type of event happens.

        Args:
            event: Type of event on which to activate the trigger. [on_enter, on_exit, on_focus, on_blur]
            func: The function to be called. Must take no arguments.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(event, str)
            CHECK(func, [types.FunctionType, types.MethodType])
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "register", "bad argument", e)
            return False

        # Perform checks on input.
        if event not in ["on_enter", "on_exit", "on_focus", "on_blur"]:
            self.driftwood.log.msg("ERROR", "Script", "register", "invalid event", event)
            return False

        args, varargs, keywords, defaults = inspect.getfullargspec(func)
        if not (args == [] and varargs is None and keywords is None and defaults is None):
            self.driftwood.log.msg("ERROR", "Script", "register", "not nullary", func)
            return False

        # Insert the trigger.
        if event not in self.global_triggers:
            self.global_triggers[event] = []
        self.global_triggers[event].append(func)
        self.driftwood.log.info("Script", "registered", '{0} trigger "{1}"'.format(event, func))
        return True

    def unregister(self, event: str, func: Callable[[], None]) -> bool:
        """Undefine a global trigger that was defined earlier.

        Args:
            event: The global trigger the event was registered under.
            func: The trigger to remove.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(event, str)
            CHECK(func, [types.FunctionType, types.MethodType])
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "unregister", "bad argument", e)
            return False

        # Does this exist?
        if event in self.global_triggers and func in self.global_triggers[event]:
            self.global_triggers[event].remove(func)
            self.driftwood.log.info("Script", "unregistered trigger", func)
            return True

        # Failure.
        self.driftwood.log.msg("ERROR", "Script", "unregister", "no such trigger", func)
        return False

    def is_custom_trigger(self, property_name: str) -> bool:
        # Input Check
        try:
            CHECK(property_name, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Script", "is_custom_trigger", "bad argument", e)
            return False

        return property_name in self.custom_triggers

    def lookup(self, property_name: str, property: str) -> Optional[Tuple[str, str]]:
        """Attempt to decode a custom map trigger into a normal map trigger.

        Args:
            property_name: Name of the custom trigger.
            property: Comma separated string which contains a list of arguments for the trigger.

        Returns:
            None, if there is no custom trigger with a name of property_name.
            Otherwise, a string that mimics the appearance of a normal Tiled map trigger.

        See also:
            define()
            undefine()
        """
        if property_name in self.custom_triggers:
            custom_trigger = self.custom_triggers[property_name]

            event = custom_trigger["event"]
            filename = custom_trigger["filename"]
            func = custom_trigger["func"]
            minargs = custom_trigger["minargs"]
            nargs = custom_trigger["nargs"]

            args = property.split(",")

            if minargs is not None:
                if args < minargs:
                    self.driftwood.log.msg("ERROR", "Script", "lookup", property_name, "too few args")
                    return None
            elif nargs != len(args):
                self.driftwood.log.msg("ERROR", "Script", "lookup", property_name, "incorrect number of args")
                return None
            return event, filename + "," + func + "," + ",".join(args)
        else:
            return None

    def _call_global_triggers(self, event: str) -> None:
        if event in self.global_triggers:
            for func in self.global_triggers[event]:
                func()

    # _module() returns an Any rather than Optional[module] because the latter results in a NameError.
    #
    # Python user bjs says:
    # "there is a module type in python but i have a feeling that [forgetting to allow it in type annotations] was a
    # oversight when the typehint / typechecking peps were being written"
    def _module(self, filename: str) -> Any:
        """Return the module instance of a script, loading if not already loaded.

        This method is not crash-safe. If you call a method in a module you got from this function, errors will
        not be caught and the engine will crash if a problem occurs. This is mostly used internally by ScriptManager
        to load a module or check if one exists.

        Args:
            filename: Filename of the python script whose module instance should be returned.

        Returns: Python module instance if succeeded, False if nonexistent, or None if error.
        """
        if filename not in self.__modules:
            ret = self.__load(filename)

        if filename in self.__modules:
            return self.__modules[filename]

        return ret

    def __convert_path(self, filename: str) -> str:
        """Get around a documented zipimport flaw.

        Args:
            filename: The filename to fix.
        """
        cpath = list(os.path.split(filename))
        cpath[-1] = os.path.splitext(cpath[-1])[0]
        return os.sep.join(cpath)  # [1:]

    def __load(self, filename: str) -> Optional[bool]:
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
                        mpath = mpath.replace("/", "\\")
                    self.__modules[filename] = importer.load_module(mpath)

                self.driftwood.log.info("Script", "loaded", filename)
                return True

            except:
                self.driftwood.log.msg(
                    "ERROR", "Script", "__load", "error from script", filename, "\n" + traceback.format_exc(10).rstrip()
                )
                return None

        else:
            self.driftwood.log.msg("ERROR", "Script", "__load", "no such script", filename)
            return False
