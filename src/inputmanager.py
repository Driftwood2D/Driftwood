###################################
## Driftwood 2D Game Dev. Suite  ##
## inputmanager.py               ##
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

class InputManager:
    """The Input Manager

    This class manages keyboard input.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """InputManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood

        self.__registry = {}
        self.__stack = []

        # Register the tick callback.
        self.driftwood.tick.register(self.tick)

    def key_down(self, keysym):
        """Push a keypress onto the input stack if not present.

        Args:
            keysym: SDLKey for the key which was pressed.
        """
        if not keysym in self.__stack:
            self.__stack.insert(0, keysym)

    def key_up(self, keysym):
        """Remove a keypress from the input stack if present.

        Args:
            keysym: SDLKey for the key which was released.
        """
        if keysym in self.__stack:
            self.__stack.remove(keysym)

    def register(self, keysym, callback):
        """Register an input callback.

        Args:
            keysym: SDLKey for the key which triggers the callback.
            callback: Function to be called on keypress.
        """
        if not keysym in self.__registry:
            self.__registry[keysym] = callback

    def unregister(self, keysym):
        """Unregister an input callback.

        Args:
            keysym: SDLKey for the key which triggers the callback.
        """
        if keysym in self.__registry:
            del self.__registry[keysym]

    def tick(self):
        """Tick callback.

        If there is a keypress on top of the stack and it maps to a callback in the registry, call it.
        """
        if self.__stack:
            if self.__stack[0] in self.__registry:
                self.__registry[self.__stack[0]]()
