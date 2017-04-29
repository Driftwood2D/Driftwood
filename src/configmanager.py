####################################
# Driftwood 2D Game Dev. Suite     #
# configmanager.py                 #
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

import argparse
import json
import jsonschema
import os
import sys
import traceback
import zipfile

VERSION = "Driftwood 2D Alpha-0.0.6"
COPYRIGHT = "Copyright 2016-2017 Michael D. Reiley and Paul Merrill"


class ConfigManager:
    """The Config Manager

    This class reads command line input and a configuration file and presents the resulting configuration for easy
    access. This class' state is not modified after initialization. It also contains no API-accessible methods.

    Note: Command line options always supercede their configuration file equivalents.

    Attributes:
        driftwood: Base class instance.
    """

    def __init__(self, driftwood):
        """ConfigManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood  # A link back to the top-level base class.

        self.selfpath = ""

        self.__config_file = ""
        self.__config = {}
        self.__cmdline_args = self.__read_cmdline()
        self.__prepare_config()

    def __contains__(self, item):
        if item in self.__config:
            return True
        return False

    def __getitem__(self, item):
        if self.__contains__(item):
            return self.__config[item]
        else:
            # This should be initialized by now.
            self.driftwood.log.msg("ERROR", "Config", "__getitem__", "no such entry", item)

    def __iter__(self):
        return self.__config.items()

    def __read_cmdline(self):
        """Read in command line options using ArgumentParser.

        Returns:
            Result of parser.parse_args()
        """
        parser = argparse.ArgumentParser(description=VERSION,
                                         formatter_class=lambda prog: argparse.HelpFormatter(prog,
                                                                                             max_help_position=40))
        parser.add_argument("config", nargs='?', type=str, default="config.json", help="config file to use")
        parser.add_argument("--path", nargs=1, dest="path", type=str, metavar="<name,...>", help="set path")
        parser.add_argument("--root", nargs=1, dest="root", type=str, metavar="<root>", help="set path root")
        parser.add_argument("--db", nargs=1, dest="db", type=str, metavar="<database>", help="set database to use")
        parser.add_argument("--dbroot", nargs=1, dest="dbroot", type=str, metavar="<root>",
                            help="set database root")
        parser.add_argument("--size", nargs=1, dest="size", type=str, metavar="<WxH>", help="set window dimensions")
        parser.add_argument("--tps", nargs=1, dest="tps", type=int, metavar="<hertz>", help="set ticks-per-second")
        parser.add_argument("--ttl", nargs=1, dest="ttl", type=int, metavar="<seconds>", help="set cache time-to-live")
        parser.add_argument("--maxfps", nargs=1, dest="maxfps", type=int, metavar="<fps>", help="set max fps")
        parser.add_argument("--mvol", nargs=1, dest="mvol", type=int, metavar="<0-128>", help="set music volume")
        parser.add_argument("--svol", nargs=1, dest="svol", type=int, metavar="<0-128>", help="set sfx volume")

        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument("--window", default=None, action="store_false", dest="fullscreen",
                            help="run in windowed mode")
        group1.add_argument("--fullscreen", default=None, action="store_true", dest="fullscreen",
                            help="run in fullscreen mode")

        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument("--quiet", default=None, action="store_false", dest="verbose",
                            help="run in quiet logging mode")
        group2.add_argument("--verbose", default=None, action="store_true", dest="verbose",
                            help="run in verbose logging mode")

        group3 = parser.add_mutually_exclusive_group()
        group3.add_argument("--halt", default=None, action="store_true", dest="halt",
                            help="halt execution on errors or warnings")
        group3.add_argument("--continue", default=None, action="store_false", dest="halt",
                            help="continue execution despite errors or warnings")

        parser.add_argument("--version", action="store_true", dest="version", help="print the version string")

        return parser.parse_args()

    def __prepare_config(self):
        """Prepare the configuration for use.

        Combine the command line arguments and the configuration file into the internal __config dictionary, favoring
        command line arguments.
        """
        selfpath = os.path.dirname(os.path.realpath(__file__))

        # Open the configuration file.
        try:
            with open(self.__cmdline_args.config, 'r') as config:
                self.__config = json.load(config)
        except:
            print("Driftwood 2D\nStarting up...")
            print("[0] FATAL: Config: could not read config file")
            sys.exit(1)  # Fail.

        # Try to load the schema for validation.
        try:
            if os.path.isdir(selfpath):  # This is a directory.
                with open(os.path.join(selfpath, "schema/config.json")) as sch:
                    schema = json.load(sch)

            else:  # This is hopefully a zip archive.
                with zipfile.ZipFile(selfpath, 'r') as zf:
                    sch = zf.read("schema/config.json")
                    if type(sch) == bytes:
                        sch = sch.decode()
                    schema = json.loads(sch)
        except:
            print("Driftwood 2D\nStarting up...")
            print("[0] FATAL: Config: could not load schema to validate config file")
            sys.exit(1)  # Fail.

        # Attempt to validate against the schema.
        try:
            jsonschema.validate(self.__config, schema)
        except jsonschema.ValidationError:
            print("Driftwood 2D\nStarting up...")
            print("[0] FATAL: Config: config file failed validation")
            traceback.print_exc(1, sys.stdout)
            sys.stdout.flush()
            sys.exit(1)  # Fail.

        # Set our self path permanently.
        self.selfpath = selfpath

        # If --version was used, print the version string and exit.
        if self.__cmdline_args.version:
            print(VERSION)
            print(COPYRIGHT)
            sys.exit(0)  # Exit here, this is all we're doing today.

        print("Driftwood 2D\nStarting up...")

        # Read the rest of the command line arguments.
        if self.__cmdline_args.path:
            self.__config["path"]["path"] = self.__cmdline_args.path[0].split(',')

        if self.__cmdline_args.root:
            self.__config["path"]["root"] = self.__cmdline_args.root[0]

        if self.__cmdline_args.db:
            self.__config["database"]["name"] = self.__cmdline_args.db[0]

        if self.__cmdline_args.dbroot:
            self.__config["database"]["root"] = self.__cmdline_args.dbroot[0]

        if self.__cmdline_args.size:
            w, h = self.__cmdline_args.size[0].split('x')
            self.__config["window"]["width"], self.__config["window"]["height"] = int(w), int(h)

        if self.__cmdline_args.tps:
            self.__config["tick"]["tps"] = self.__cmdline_args.tps[0]

        if self.__cmdline_args.ttl:
            self.__config["cache"]["ttl"] = self.__cmdline_args.ttl[0]

        if self.__cmdline_args.maxfps:
            self.__config["window"]["maxfps"] = self.__cmdline_args.maxfps[0]

        if self.__cmdline_args.mvol:
            if self.__cmdline_args.mvol[0] > 128:
                self.__config["audio"]["music_volume"] = 128
            elif self.__cmdline_args.mvol[0] < 0:
                self.__config["audio"]["music_volume"] = 0
            else:
                self.__config["audio"]["music_volume"] = self.__cmdline_args.mvol[0]

        if self.__cmdline_args.svol:
            if self.__cmdline_args.svol[0] > 128:
                self.__config["audio"]["sfx_volume"] = 128
            elif self.__cmdline_args.svol[0] < 0:
                self.__config["audio"]["sfx_volume"] = 0
            else:
                self.__config["audio"]["sfx_volume"] = self.__cmdline_args.svol[0]

        if self.__cmdline_args.fullscreen is not None:
            if self.__cmdline_args.fullscreen:
                self.__config["window"]["fullscreen"] = True
            else:
                self.__config["window"]["fullscreen"] = False

        if self.__cmdline_args.verbose is not None:
            if self.__cmdline_args.verbose:
                self.__config["log"]["verbose"] = True
            else:
                self.__config["log"]["verbose"] = False

        if self.__cmdline_args.halt is not None:
            if self.__cmdline_args.halt:
                self.__config["log"]["halt"] = True
            else:
                self.__config["log"]["halt"] = False
