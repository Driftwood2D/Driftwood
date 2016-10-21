####################################
# Driftwood 2D Game Dev. Suite     #
# resourcemanager.py               #
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

import json
import os
import zipfile

import filetype


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
        self.__injections = {}

    def __contains__(self, item):
        if self.driftwood.path[item]:
            return True
        return False

    def __getitem__(self, item):
        return self.request(item)

    def request(self, filename, binary=False):
        """Retrieve the contents of a file.

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

        # If the file is already cached, return the cached version.
        if filename in self.driftwood.cache:
            return self.driftwood.cache[filename]

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
                    with zipfile.ZipFile(pathname, 'r') as zf:
                        contents = zf.read(filename)

                # Upload the file to the cache.
                self.driftwood.cache.upload(filename, contents)

                return contents

            except:
                self.driftwood.log.msg("ERROR", "Resource", "could not read file", filename)
                return None

        else:
            self.driftwood.log.msg("ERROR", "Resource", "no such file", filename)
            return None

    def inject(self, filename, data):
        """Inject data to be retrieved later by a fake filename.

        This is checked before path or cache, so if you overwrite an existing filename you won't have access to it
        anymore!

        Args:
            filename: The fake filename by which to retrieve the stored data.
            data: The data to inject.

        Returns:
            True
        """
        self.__injections[filename] = data
        self.driftwood.log.info("Resource", "injected", filename)
        return True

    def uninject(self, filename):
        """Delete injected data.

        Args:
            filename: Fake filename to uninject.

        Returns:
            True if succeeded, False if failed.
        """
        if filename in self.__injections:
            del self.__injections[filename]
            return True
        self.driftwood.log.msg("ERROR", "Resource", "could not uninject", filename)
        return False

    def request_json(self, filename):
        """Retrieve a dictionary of JSON data.

        Args:
            filename: The filename of the JSON file to load.

        Returns:
            Dictionary of JSON data if succeeded, None if failed.
        """
        data = self.request(filename)
        if data:
            if type(data) == bytes:
                data = data.decode()
            return json.loads(data)
        return None

    def request_image(self, filename):
        """Retrieve an internal abstraction of an image file.

        Args:
            filename: The filename of the image file to load.

        Returns:
            Image filetype abstraction if succeeded, None if failed.
        """
        data = self.request(filename, True)
        if data:
            return filetype.ImageFile(self.driftwood, data, self.driftwood.window.renderer)
        return None

    def request_audio(self, filename, music=False):
        """Retrieve an internal abstraction of an audio file.

        Args:
            filename: The filename of the audio file to load.
            music: Whether to load the file as music.

        Returns:
            Audio filetype abstraction if succeeded, None if failed.
        """
        data = self.request(filename, True)
        if data:
            return filetype.AudioFile(self.driftwood, data, music)
        return None
