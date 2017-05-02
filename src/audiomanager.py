####################################
# Driftwood 2D Game Dev. Suite     #
# audiomanager.py                  #
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
        self.__sfx = {}  # key: channel; [filename, file]
        self.__init_success = [False, False]

        # Attempt to initialize mixer output.
        if Mix_OpenAudio(self.driftwood.config["audio"]["frequency"], MIX_DEFAULT_FORMAT, 2,
                         self.driftwood.config["audio"]["chunksize"]) == -1:
            self.driftwood.log.msg("ERROR", "Audio", "__init__", "failed to initialize mixer output",
                                   str(Mix_GetError()))
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

        # Did we succeed?
        if Mix_Init(init_flags) & init_flags != init_flags:
            self.driftwood.log.msg("ERROR", "Audio", "__init__","failed to initialize audio format support",
                                   str(Mix_GetError()))
        else:
            self.driftwood.log.info("Audio", "initialized mixer audio format support",
                                    " ,".join(self.driftwood.config["audio"]["support"]))
            self.__init_success[1] = True

        # Register the cleanup function.
        self.driftwood.tick.register(self._cleanup, delay=0.01, during_pause=True)

    def play_sfx(self, filename, volume=None, loop=0, fade=0.0):
        """Load and play a sound effect from an audio file.

        Args:
            filename: Filename of the sound effect.
            volume: Overrides the sfx_volume in the config for this sound effect. 0-128
            loop: Number of times to loop the audio. 0 for none, -1 for infinite.
            fade: If set, number of seconds to fade in sfx.

        Returns:
            Channel number if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(volume, int)
            CHECK(loop, int, _min=-1)
            CHECK(fade, [int, float])
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "play_sfx", "bad argument", e)
            return None

        # Give up if we didn't initialize properly.
        if False in self.__init_success:
            self.driftwood.log.msg("WARNING", "Audio", "play_sfx", "cannot play sfx due to initialization failure",
                                   filename)
            return None

        # Load the sound effect.
        sfx_temp = [filename, None]
        sfx_temp[1] = self.driftwood.resource.request_audio(filename, False)
        if not sfx_temp[1]:
            self.driftwood.log.msg("ERROR", "Audio", "play_sfx", "could not load sfx", filename)
            return None

        if volume is not None:
            # Keep volume within bounds.
            if volume > 128:
                self.driftwood.log.msg("WARNING", "Audio", "play_sfx", "volume is more than 128", volume)
                volume = 128
            if volume < 0:
                self.driftwood.log.msg("WARNING", "Audio", "play_sfx", "volume is less than 0", volume)
                volume = 0

            # Set the volume.
            Mix_VolumeChunk(sfx_temp[1].audio, volume)
        else:
            Mix_VolumeChunk(sfx_temp[1].audio, self.driftwood.config["audio"]["sfx_volume"])

        if not fade:  # Play the sound effect.
            channel = Mix_PlayChannel(-1, sfx_temp[1].audio, loop)
        else:  # Fade in sound effect.
            channel = Mix_FadeInChannel(-1, sfx_temp[1].audio, loop, fade*1000)

        if channel == -1:
            self.driftwood.log.msg("WARNING", "Audio", "play_sfx", "could not play sfx on channel", str(channel))
            return None

        self.__sfx[channel] = sfx_temp
        self.playing_sfx = True

        return channel

    def volume_sfx(self, channel, volume=None):
        """Get or adjust the volume of a sound effect channel.

        Args:
            channel: Audio channel of the sound effect whose volume to adjust or query. -1 adjusts all channels.
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded (average volume of sfx if -1 channel is passed), None if failed.
        """
        # Input Check
        try:
            CHECK(channel, int)
            if volume:
                CHECK(volume, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_sfx", "bad argument", e)
            return None

        # Search for the sound effect.
        if channel in self.__sfx:
            if volume is not None:
                # Keep volume within bounds.
                if volume > 128:
                    volume = 128
                    self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is more than 128", volume)
                if volume < 0:
                    self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is less than 0", volume)
                    volume = 0

                # Set the volume.
                Mix_Volume(channel, volume)
                return volume
            else:  # Get the volume.
                return Mix_Volume(channel, -1)

        self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "cannot adjust sfx volume on nonexistent channel",
                               channel)
        return None

    def volume_sfx_by_filename(self, filename, volume=None):
        """Get or adjust the volume of all currently playing instances of the named sound effect.

        Args:
            filename: Filename of the sound effect whose volume to adjust or query.
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            if volume:
                CHECK(volume, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_sfx_by_filename", "bad argument", e)
            return None

        # Check for the sfx.
        for sfx in self.__sfx:
            if self.__sfx[sfx][0] == filename:
                if volume is not None:
                    # Keep volume within bounds.
                    if volume > 128:
                        volume = 128
                        self.driftwood.log.msg("WARNING", "Audio", "volume_sfx_by_filename",
                                               "volume is more than 128", volume)
                    if volume < 0:
                        self.driftwood.log.msg("WARNING", "Audio", "volume_sfx_by_filename",
                                               "volume is less than 0", volume)
                        volume = 0

                    # Set the volume.
                    Mix_Volume(sfx, volume)
                    return volume
                else:  # Get the volume.
                    return Mix_Volume(sfx, -1)

        # No such filename.
        self.driftwood.log.msg("WARNING", "Audio", "volume_sfx_by_filename",
                               "cannot adjust volume for nonexistent instances of sfx", filename)
        return None

    def stop_sfx(self, channel, fade=0.0):
        """Stop a sound effect. Requires the sound effect's channel number from play_sfx()'s return code.

        Args:
            channel: Audio channel of the sound effect to stop.
            fade: If set, number of seconds to fade out sfx.

        Returns:
            True if succeeded, false if failed.
        """
        # Input Check
        try:
            CHECK(channel, int)
            CHECK(fade, [int, float], _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "stop_sfx", "bad argument", e)
            return False

        if channel in self.__sfx:
            if Mix_Playing(channel):
                if not fade:  # Stop channel.
                    Mix_HaltChannel(channel)
                    del self.__sfx[channel]
                else:  # Fade out channel.
                    Mix_FadeOutChannel(channel, fade*1000)
                    # Cleanup callback will handle deletion.
            return True

        self.driftwood.log.msg("WARNING", "Audio", "stop_sfx", "cannot stop sfx on nonexistent channel",
                               channel)
        return False

    def stop_sfx_by_filename(self, filename, fade=0.0):
        """Stop all currently playing instances of the named sound effect.

        Args:
            filename: Filename of the sound effect instances to stop.
            fade: If set, number of seconds to fade out sfx.

        Returns:
            True if succeeded, false if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(fade, [int, float], _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_sfx", "bad argument", e)
            return False

        for sfx in self.__sfx:
            if self.__sfx[sfx][0] == filename:
                if not Mix_Playing(sfx):
                    return False
                else:
                    if not fade:  # Stop sfx.
                        Mix_HaltChannel(sfx)
                        del self.__sfx[sfx]
                    else:
                        Mix_FadeOutChannel(sfx, fade*1000)
                        # Cleanup callback will handle deletion.
                    return True

        self.driftwood.log.msg("WARNING", "Audio", "stop_sfx_by_filename", "cannot stop nonexistent instances of sfx",
                               filename)
        return False

    def stop_all_sfx(self):
        """Stop all currently playing sound effects.

        Returns:
            True
        """
        for sfx in self.__sfx:
            self.stop_sfx(sfx)
        self.__sfx = {}
        return True

    def play_music(self, filename, volume=None, loop=0, fade=0.0):
        """Load and play music from an audio file. Also stops and unloads any previously loaded music.

        Args:
            filename: Filename of the music.
            volume: Overrides the music_volume in the config for this music. 0-128
            loop: Number of times to loop the audio. 0 for none, -1 for infinite.
            fade: If set, number of seconds to fade in music.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            if volume:
                CHECK(volume, int)
            CHECK(loop, int, _min=-1)
            CHECK(fade, [int, float], _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "play_music", "bad argument", e)
            return False

        # Give up if we didn't initialize properly.
        if 0 in self.__init_success:
            self.driftwood.log.msg("WARNING", "Audio", "play_music","cannot play music due to initialization failure",
                                   filename)
            return False

        # Stop and unload any previously loaded music.
        self.stop_music()

        # Load the music.
        self.__music = self.driftwood.resource.request_audio(filename, True)
        if not self.__music:
            self.driftwood.log.msg("ERROR", "Audio", "play_music", "could not load music", filename)
            return False

        # Stop any currently playing music.
        if Mix_PlayingMusic():
            self.stop_music()

        if not fade:  # Play the music.
            result = Mix_PlayMusic(self.__music.audio, loop)
        else:  # Fade in the music.
            result = Mix_FadeInMusic(self.__music.audio, loop, fade*1000)

        if result == -1:
            self.driftwood.log.msg("WARNING", "Audio", "play_music", "could not play music")
            return

        if volume is not None:
            # Keep volume within bounds.
            if volume > 128:
                volume = 128
                self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is more than 128", volume)
            if volume < 0:
                self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is less than 0", volume)
                volume = 0

            # Set the volume.
            Mix_VolumeMusic(volume)
        else:
            Mix_VolumeMusic(self.driftwood.config["audio"]["music_volume"])

        self.playing_music = True

        return True

    def volume_music(self, volume=None):
        """Get or adjust the volume of the currently playing music.

        Args:
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded, None if failed.
        """
        # Input Check
        try:
            if volume:
                CHECK(volume, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_music", "bad argument", e)
            return None

        # Search for the sound effect.
        if self.playing_music:
            if volume is not None:
                # Keep volume within bounds.
                if volume > 128:
                    volume = 128
                    self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is more than 128", volume)
                if volume < 0:
                    self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is less than 0", volume)
                    volume = 0

                # Set the volume.
                Mix_VolumeMusic(volume)
                return volume
            else:  # Get the volume.
                return Mix_VolumeMusic(-1)

        self.driftwood.log.msg("WARNING", "Audio", "volume_music", "cannot adjust volume for nonexistent music")
        return None

    def stop_music(self, fade=0.0):
        """Stop and unload any currently loaded music.

        Args:
            fade: If set, number of seconds to fade out the music.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(fade, [int, float], _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "stop_music", "bad argument", e)
            return False

        if not self.__music:
            return False

        if Mix_PlayingMusic():
            if not fade:  # Stop the music.
                Mix_HaltMusic()
                self.__music = None
                self.playing_music = False
            else:  # Fade out the music.
                Mix_FadeOutMusic(fade*1000)
                # Cleanup callback will handle deletion.

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
                    if not Mix_Playing(sfx):
                        del self.__sfx[sfx]
        except RuntimeError:
            pass

    def _terminate(self):
        """Prepare for shutdown.
        """
        self.stop_music()
        self.stop_all_sfx()
        Mix_Quit()
        Mix_CloseAudio()
