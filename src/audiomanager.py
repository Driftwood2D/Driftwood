####################################
# Driftwood 2D Game Dev. Suite     #
# audiomanager.py                  #
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

from sdl2.sdlmixer import *


class AudioManager:
    """The Audio Manager

        This class manages the audio subsystem and allows playing sound effects and music.

        Attributes:
            driftwood: Base class instance.
    """
    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.__music = None
        self.__sfx = {} # [file, channel]
        self.__init_success = [0, 0]

        # Save SDL's destructors for shutdown.
        self.__mix_quit = Mix_Quit
        self.__mix_closeaudio = Mix_CloseAudio

        # Attempt to initialize mixer output.
        if Mix_OpenAudio(self.driftwood.config["audio"]["frequency"], MIX_DEFAULT_FORMAT, 2,
                         self.driftwood.config["audio"]["chunksize"]) == -1:
            self.driftwood.log.msg("ERROR", "Audio", "failed to initialize mixer output", str(Mix_GetError()))
        else:
            self.__init_success[0] = 1

        # Attempt to initialize mixer support for selected audio formats.
        init_flags = 0
        if "ogg" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_OGG
        if "mp3" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_MP3
        if "flac" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_FLAC

        if Mix_Init(init_flags)&init_flags != init_flags:
            self.driftwood.log.msg("ERROR", "Audio", "failed to initialize audio format support", str(Mix_GetError()))
        else:
            self.__init_success[1] = 1

        # Register the cleanup function.
        self.driftwood.tick.register(self._cleanup, delay=0.01, during_pause=True)

    def play_sfx(self, filename, volume=None, loops=0):
        # Give up if we didn't initialize properly.
        if 0 in self.__init_success:
            return

        # Load the sound effect.
        self.__sfx[filename] = [None, 0]
        self.__sfx[filename][0] = self.driftwood.resource.request_audio(filename, False)
        if not self.__sfx[filename][0]:
            self.driftwood.log.msg("ERROR", "Audio", "could not load sfx", filename)
            return

        # Set the volume.
        if volume:
            Mix_VolumeChunk(self.__sfx[filename][0].audio, volume)
        else:
            Mix_VolumeChunk(self.__sfx[filename][0].audio, self.driftwood.config["audio"]["sfx_volume"])

        # Play the sound effect.
        channel = Mix_PlayChannel(-1, self.__sfx[filename][0].audio, loops)
        if channel == -1:
            self.driftwood.log.msg("ERROR", "Audio", "could not allocate sfx to channel", str(channel))
            return

        self.__sfx[filename][1] = channel

    def load_music(self, filename):
        pass

    def play_music(self, volume=None, loops=0):
        pass

    def stop_music(self):
        pass

    def _cleanup(self, seconds_past):
        if not Mix_PlayingMusic():
            self.__music = None
        try:
            for sfx in self.__sfx:
                if not Mix_Playing(self.__sfx[sfx][1]):
                    del self.__sfx[sfx]
        except (RuntimeError):
            pass

    def __del__(self):
        self.__mix_quit()
        self.__mix_closeaudio()
