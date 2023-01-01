################################
# Driftwood 2D Game Dev. Suite #
# __main__.py                  #
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
import signal
import sys

VCUR = sys.version_info
VREQ = [3, 6, 0]

# We have to do this here before we start pulling in nonexistent imports.
if __name__ == "__main__":
    # Check Python version.
    if VCUR[0] < VREQ[0] or VCUR[1] < VREQ[1] or (VCUR[1] == VREQ[1] and VCUR[2] < VREQ[2]):
        print("Driftwood 2D\n[0] Starting up...")
        print(
            "[0] FATAL: __main__: Python >= {0}.{1}.{2} required, found Python {3}.{4}.{5}".format(
                VREQ[0], VREQ[1], VREQ[2], VCUR[0], VCUR[1], VCUR[2]
            )
        )
        print("Please make sure to run with a compatible version of Python3.")
        sys.exit(1)  # Fail.

    # Try to import PySDL2.
    try:
        if os.name == "nt":  # Add the current directory to the SDL2 DLL search path on Windows.
            os.environ["PYSDL2_DLL_PATH"] = os.getcwd()
        from sdl2 import *
        import sdl2.ext as sdl2ext
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: PySDL2 required, module "sdl2" not found or sdl missing')
        print("Please make sure that SDL2, SDL2_image, SDL2_mixer, and SDL2_TTF are installed.")
        print('Also make sure that the "pysdl2" Python3 package is installed.')
        print('On most systems, run "pip3 install pysdl2". If pip3 is missing, try pip instead.')
        sys.exit(1)  # Fail.

    # Try to import pygame.
    try:
        os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "true"
        import pygame
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: pygame required, module "pygame" not found')
        print('Please make sure that the "pygame" Python3 module is installed.')
        print('On most systems, run "pip3 install pygame". If pip3 is missing, try pip instead.')
        sys.exit(1)  # Fail.
    try:
        import pygame.mixer
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: pygame required, module "pygame.mixer" not found')
        # TODO: Provide suggestion for the user.
        sys.exit(1)  # Fail.

    # Try to import jsonschema.
    try:
        import jsonschema
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: jsonschema required, module "jsonschema" not found')
        print('Please make sure that the "jsonschema" Python3 module is installed.')
        print('On most systems, run "pip3 install jsonschema". If pip3 is missing, try pip instead.')
        sys.exit(1)  # Fail.

    # Try to import ubjson.
    try:
        import ubjson
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: ubjson required, module "ubjson" not found')
        print('Please make sure that the "py-ubjson" Python3 module is installed.')
        print('On most systems, run "pip3 install py-ubjson". If pip3 is missing, try pip instead.')
        sys.exit(1)  # Fail.

    # Try to import Jinja2.
    try:
        import jinja2
    except ImportError:
        print("Driftwood 2D\n[0] Starting up...")
        print('[0] FATAL: __main__: Jinja2 required, module "jinja2" not found')
        print('Please make sure that the "jinja2" Python3 module is installed.')
        print('On most systems, run "pip3 install jinja2". If pip3 is missing, try pip instead.')
        sys.exit(1)  # Fail.

    # Import main class.
    import driftwood

    import check

    # Place certain items in the global scope.
    import builtins

    builtins.CHECK = check.CHECK
    builtins.CheckFailure = check.CheckFailure
    builtins.fncopy = driftwood.fncopy

    # Set up the entry point.
    entry = driftwood.Driftwood()

    # Make sure scripts have access to the base class by placing it in the global scope.
    builtins.Driftwood = entry

    # Underscore is a shortcut for "Driftwood.vars".
    builtins._ = entry.vars

    # Handle shutting down gracefully on INT and TERM signals.
    def sigint_handler(signum, frame):
        entry.running = False

    # Set up interrupt handlers.
    signal.signal(signal.SIGINT, sigint_handler)
    signal.signal(signal.SIGTERM, sigint_handler)

    # Run Driftwood and exit with its return code.
    sys.exit(entry._run())
