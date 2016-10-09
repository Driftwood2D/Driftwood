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

# A big thank-you to Lazy Foo's SDL_Audio tutorial. It would've taken me a lot longer to build this without such clear
# instruction. Link: <http://lazyfoo.net/SDL_tutorials/lesson11/>

from sdl2.sdlmixer import *


class AudioManager:
    """The Audio Manager

        This class manages the audio subsystem and allows playing sound effects and music.

        Attributes:
            driftwood: Base class instance.
            playing_music: Whether we are currently playing music or not.
            playing_sfx: Whether we are currently playing sfx or not.
    """

    def __init__(self, driftwood):
        self.driftwood = driftwood

        self.playing_music = False
        self.playing_sfx = False

        self.__music = None
        self.__sfx = {}  # [file, channel]
        self.__init_success = [False, False]

        # Save SDL's destructors for shutdown.
        self.__mix_quit = Mix_Quit
        self.__mix_closeaudio = Mix_CloseAudio

        # Attempt to initialize mixer output.
        if Mix_OpenAudio(self.driftwood.config["audio"]["frequency"], MIX_DEFAULT_FORMAT, 2,
                         self.driftwood.config["audio"]["chunksize"]) == -1:
            self.driftwood.log.msg("ERROR", "Audio", "failed to initialize mixer output", str(Mix_GetError()))
        else:
            self.driftwood.log.info("Audio", "initialized mixer output")
            self.__init_success[0] = True

        # Attempt to initialize mixer support for selected audio formats.
        init_flags = 0
        if "ogg" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_OGG
        if "mp3" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_MP3
        if "flac" in self.driftwood.config["audio"]["support"]:
            init_flags |= MIX_INIT_FLAC

        if Mix_Init(init_flags) & init_flags != init_flags:
            self.driftwood.log.msg("ERROR", "Audio", "failed to initialize audio format support", str(Mix_GetError()))
        else:
            self.driftwood.log.info("Audio", "initialized mixer audio format support",
                                    " ,".join(self.driftwood.config["audio"]["support"]))
            self.__init_success[1] = True

        # Register the cleanup function.
        self.driftwood.tick.register(self._cleanup, delay=0.01, during_pause=True)

    def play_sfx(self, filename, volume=None, loop=0):
        """Load and play a sound effect from an audio file.

        Args:
            filename: Filename of the sound effect.
            volume: Overrides the sfx_volume in the config for this sound effect. 1-128
            loop: Number of times to loop the audio. 0 for none, -1 for infinite.

        Returns:
            Channel number if succeeded, None if failed.
        """
        # Give up if we didn't initialize properly.
        if False in self.__init_success:
            self.driftwood.log.msg("ERROR", "Audio", "cannot play sfx due to initialization failure", filename)
            return None

        # Load the sound effect.
        self.__sfx[filename] = [None, 0]
        self.__sfx[filename][0] = self.driftwood.resource.request_audio(filename, False)
        if not self.__sfx[filename][0]:
            self.driftwood.log.msg("ERROR", "Audio", "could not load sfx", filename)
            return None

        # Set the volume.
        if volume is not None:
            Mix_VolumeChunk(self.__sfx[filename][0].audio, volume)
        else:
            Mix_VolumeChunk(self.__sfx[filename][0].audio, self.driftwood.config["audio"]["sfx_volume"])

        # Play the sound effect.
        channel = Mix_PlayChannel(-1, self.__sfx[filename][0].audio, loop)
        if channel == -1:
            self.driftwood.log.msg("ERROR", "Audio", "could not play sfx on channel", str(channel))
            return None

        self.__sfx[filename][1] = channel
        self.playing_sfx = True

        return channel

    def stop_sfx(self, channel):
        """Stop a sound effect. Requires the sound effect's channel number from play_sfx()'s return code.

        Args:
            channel: Audio channel of the sound effect to stop.

        Returns:
            True if succeeded, false if failed.
        """
        for sfx in self.__sfx.keys():
            if self.__sfx[sfx][1] == channel:
                if Mix_Playing(self.__sfx[sfx][1]):
                    Mix_HaltChannel(self.__sfx[sfx][1])
                del self.__sfx[sfx]
                return True
        self.driftwood.log.msg("ERROR", "Audio", "cannot stop sfx on nonexistent channel", channel)
        return False

    def stop_sfx_by_filename(self, filename):
        """Stop all currently playing instances of the named sound effect.

        Args:
            filename: Filename of the sound effect instances to stop.

        Returns:
            True if succeeded, false if failed.
        """
        if not filename in self.__sfx:
            self.driftwood.log.msg("ERROR", "Audio", "cannot stop nonexistent instances of sfx", filename)
            return False

        if not Mix_Playing(self.__sfx[filename][1]):
            return False
        else:
            Mix_HaltChannel(self.__sfx[filename][1])
            del self.__sfx[filename]
            return True

    def stop_all_sfx(self):
        """Stop all currently playing sound effects.

        Returns:
            True
        """
        for sfx in self.__sfx.keys():
            self.stop_sfx(sfx)
        return True

    def play_music(self, filename, volume=None, loop=0):
        """Load and play music from an audio file. Also stops and unloads any previously loaded music.

        Args:
            filename: Filename of the music.
            volume: Overrides the music_volume in the config for this music. 1-128
            loop: Number of times to loop the audio. 0 for none, -1 for infinite.

        Returns:
            True if succeeded, False if failed.
        """
        # Give up if we didn't initialize properly.
        if 0 in self.__init_success:
            self.driftwood.log.msg("ERROR", "Audio", "cannot play music due to initialization failure", filename)
            return False

        # Stop and unload any previously loaded music.
        self.stop_music()

        # Load the music.
        self.__music = self.driftwood.resource.request_audio(filename, True)
        if not self.__music:
            self.driftwood.log.msg("ERROR", "Audio", "could not load music", filename)
            return False

        # Play the music.
        if Mix_PlayingMusic():
            self.stop_music()
        if Mix_PlayMusic(self.__music.audio, loop) == -1:
            self.driftwood.log.msg("ERROR", "Audio", "could not play music")
            return

        # Set the volume.
        if volume is not None:
            Mix_VolumeMusic(volume)
        else:
            Mix_VolumeMusic(self.driftwood.config["audio"]["music_volume"])

        self.playing_music = True

        return True

    def stop_music(self):
        """Stop and unload any currently loaded music.

        Returns:
            True if succeeded, False if failed.
        """
        if not self.__music:
            return False

        if Mix_PlayingMusic():
            Mix_HaltMusic()
        self.__music = None
        self.playing_music = False

        return True

    def _cleanup(self, seconds_past):
        # Tick callback to clean up files we're done with.
        if self.__music and not Mix_PlayingMusic():
            self.__music = None
            self.playing_music = False
        try:
            if not len(self.__sfx):
                self.playing_sfx = False
            else:
                for sfx in self.__sfx:
                    if not Mix_Playing(self.__sfx[sfx][1]):
                        del self.__sfx[sfx]
        except (RuntimeError):
            pass

    def __del__(self):
        self.stop_music()
        self.__mix_quit()
        self.__mix_closeaudio()
