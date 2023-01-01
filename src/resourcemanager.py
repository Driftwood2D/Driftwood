################################
# Driftwood 2D Game Dev. Suite #
# resourcemanager.py           #
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

import json
import os
import sys
import traceback
import zipfile
from typing import Any, Optional, TYPE_CHECKING

import jinja2

from check import CHECK, CheckFailure
import filetype

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood


class ResourceManager:
    """The Resource Manager

    Simple resource management class which retrieves the contents of a file in the path vfs.

    Attributes:
        driftwood: Base class instance.
    """

    driftwood: "Driftwood"

    def __init__(self, driftwood: "Driftwood"):
        """ResourceManager class initializer.

        Args:
            driftwood: Base class instance.
        """
        self.driftwood = driftwood
        self.__injections = {}
        self.__duplicate_file_counts = {}

    def inject(self, filename: str, data: Any) -> bool:
        """Inject data to be retrieved later by a fake filename.

        This is checked before the filesystem and invalidates the cache, so if you overwrite an existing filename you
        won't have access to it anymore!

        Args:
            filename: The fake filename by which to retrieve the stored data.
            data: The data to inject.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "inject", "bad argument", e)
            return False

        self.__injections[filename] = data
        if filename in self.driftwood.cache:
            del self.driftwood.cache[filename]
        self.driftwood.log.info("Resource", "injected", filename)
        return True

    def uninject(self, filename: str) -> bool:
        """Delete injected data.

        Args:
            filename: Fake filename to uninject.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "uninject", "bad argument", e)
            return False

        if filename in self.__injections:
            if filename in self.driftwood.cache:
                del self.driftwood.cache[filename]
            del self.__injections[filename]
            return True
        self.driftwood.log.msg("ERROR", "Resource", "uninject", "no such file", filename)
        return False

    def request_json(self, filename: str) -> Optional[Any]:
        """Retrieve a dictionary of JSON data.

        Args:
            filename: The filename of the JSON file to load.

        Returns:
            Dictionary of JSON data if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_json", "bad argument", e)
            return None

        if filename in self.driftwood.cache:
            return self.driftwood.cache[filename]
        data = self.request_raw(filename, binary=False)
        if data:
            if type(data) == bytes:
                data = data.decode()
            try:
                obj = json.loads(data, strict=False)
            except json.decoder.JSONDecodeError:
                self.driftwood.log.msg("ERROR", "Resource", "request_json", "malformed json", filename)
                traceback.print_exc(1, sys.stdout)
                return None
            self.driftwood.cache.upload(filename, obj)
            return obj
        else:
            self.driftwood.cache.upload(filename, None)
            return None

    def request_template(self, filename: str, template_vars: dict = {}) -> Optional[Any]:
        """Retrieve a Jinja2-templated JSON file.

        Args:
            filename: The filename of the Jinja2-templated JSON file to load.
            template_vars: A dictionary of variables to apply to the template.

        Returns:
            Dictionary of JSON data if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(template_vars, dict)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_template", "bad argument", e)
            return None

        if filename in self.driftwood.cache:
            # Get the template from the cache.
            template = self.driftwood.cache[filename]
            try:
                # Render the template.
                data = template.render(template_vars)
            except jinja2.exceptions.TemplateError:
                self.driftwood.log.msg("ERROR", "Resource", "request_template", "could not render", filename)
                traceback.print_exc(1, sys.stdout)
                return None
        else:
            # Load the file from disk.
            data = self.request_raw(filename, binary=False)
            if not data:
                # Failure.
                self.driftwood.cache.upload(filename, None)
                return None

            # Success.
            if type(data) == bytes:
                data = data.decode()

            # Create a template.
            try:
                template_loader = jinja2.DictLoader({filename: data})
                template_env = jinja2.Environment(loader=template_loader)
                template_env.filters = {"json": lambda a: json.dumps(a)}
                template = template_env.get_template(filename)
            except jinja2.exceptions.TemplateError:
                self.driftwood.log.msg("ERROR", "Resource", "request_template", "malformed template", filename)
                traceback.print_exc(1, sys.stdout)
                return None

            # Upload the template.
            self.driftwood.cache.upload(filename, template)

            # Render the template.
            try:
                data = template.render(template_vars)
            except jinja2.exceptions.TemplateError:
                self.driftwood.log.msg("ERROR", "Resource", "request_template", "could not render", filename)
                traceback.print_exc(1, sys.stdout)
                return None

        # Load the rendered JSON.
        try:
            obj = json.loads(data, strict=False)
        except json.decoder.JSONDecodeError:
            self.driftwood.log.msg("ERROR", "Resource", "request_template", "malformed json", filename)
            traceback.print_exc(1, sys.stdout)
            return None
        return obj

    def request_audio(self, filename: str, music: bool = False) -> Optional[filetype.AudioFile]:
        """Retrieve an internal abstraction of an audio file.

        Args:
            filename: The filename of the audio file to load.
            music: Whether to load the file as music.

        Returns:
            Audio filetype abstraction if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(music, bool)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_audio", "bad argument", e)
            return None

        if filename in self.driftwood.cache:
            return self.driftwood.cache[filename]
        data = self.request_raw(filename, binary=True)
        if data:
            obj = filetype.AudioFile(self.driftwood, data, music)
            self.driftwood.cache.upload(filename, obj)
            return obj
        else:
            self.driftwood.cache.upload(filename, None)
            return None

    def request_font(self, filename: str, ptsize: int) -> Optional[filetype.FontFile]:
        """Retrieve an internal abstraction of a font file.

        Args:
            filename: The filename of the font file to load.
            ptsize: The point size to load the font in.

        Returns:
            Font filetype abstraction if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(ptsize, int, _min=1)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_font", "bad argument", e)
            return None

        cache_name = filename + ":" + str(ptsize)
        if cache_name in self.driftwood.cache:
            return self.driftwood.cache[cache_name]
        data = self.request_raw(filename, binary=True)
        if data:
            obj = filetype.FontFile(self.driftwood, data, ptsize)
            self.driftwood.cache.upload(cache_name, obj)
            return obj
        else:
            self.driftwood.cache.upload(cache_name, None)
            return None

    def request_image(self, filename: str) -> Optional[filetype.ImageFile]:
        """Retrieve an internal abstraction of an image file.

        Args:
            filename: The filename of the image file to load.

        Returns:
            Image filetype abstraction if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_image", "bad argument", e)
            return None

        if filename in self.driftwood.cache:
            return self.driftwood.cache[filename]
        data = self.request_raw(filename, binary=True)
        if data:
            obj = filetype.ImageFile(self.driftwood, data, self.driftwood.window.renderer)
            self.driftwood.cache.upload(filename, obj)
            return obj
        else:
            self.driftwood.cache.upload(filename, None)
            return None

    def request_duplicate_image(self, filename: str) -> Optional[filetype.ImageFile]:
        """Retrieve an internal abstraction of an image file. This object will not be shared with any other
        consumers so is free to be modified.

        Args:
            filename: The filename of the image file to load.

        Returns:
            Image filetype abstraction if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Resource", "request_duplicate_image", "bad argument", e)
            return None

        obj = None

        if filename in self.__duplicate_file_counts:
            self.__duplicate_file_counts[filename] += 1
        else:
            self.__duplicate_file_counts[filename] = 1

        cache_name = "{} duplicate {}".format(filename, self.__duplicate_file_counts[filename])

        data = self.request_raw(filename, binary=True)
        if data:
            obj = filetype.ImageFile(self.driftwood, data, self.driftwood.window.renderer)
            if obj:
                self.driftwood.cache.upload(cache_name, obj, keep_for_ttl=False)

        return obj

    def request_raw(self, filename: str, binary: bool = False) -> Optional[bytes]:
        """Retrieve the raw contents of a file.

        Args:
            filename: Filename of the file to read.
            binary: Whether the file is a binary file, rather than a plaintext file.

        Returns:
            Contents of the requested file, if present. Otherwise None.
        """
        self.driftwood.log.info("Resource", "requested", filename)

        # If the filename is in our injections list, return the injected data.
        if filename in self.__injections:
            return self.__injections[filename]

        pathname = self.driftwood.path[filename]
        if pathname:
            try:
                if os.path.isdir(pathname):  # This is a directory.
                    if binary:
                        f = open(os.path.join(pathname, filename), "rb")
                    else:
                        f = open(os.path.join(pathname, filename))
                    contents = f.read()
                    f.close()

                else:  # This is hopefully a zip archive.
                    with zipfile.ZipFile(pathname, "r") as zf:
                        contents = zf.read(filename)

                return contents

            except:
                self.driftwood.log.msg("ERROR", "Resource", "request_raw", "could not read file", filename)
                return None

        else:
            self.driftwood.log.msg("ERROR", "Resource", "request_raw", "no such file", filename)
            return None
