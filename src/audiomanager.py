################################
# Driftwood 2D Game Dev. Suite #
# audiomanager.py              #
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

# A big thank-you to Lazy Foo's SDL_Audio tutorial. It would've taken me a lot longer to build this without such clear
# instruction. Link: <http://lazyfoo.net/SDL_tutorials/lesson11/>

from typing import Optional, TYPE_CHECKING

import pygame as pg

from check import CHECK, CheckFailure
from filetype import AudioFile

if TYPE_CHECKING:  # Avoid circuluar import.
    from driftwood import Driftwood

# We have 8 channels. Channel 0 is for music, and the rest are for sound effects.
MAX_CHAN = 8
MUSIC_CHAN = 0
FIRST_SFX_CHAN = 1


class AudioManager:
    """The Audio Manager

    This class manages the audio subsystem and allows playing sound effects and music.

    Attributes:
        driftwood: Base class instance.
        playing_music: Whether we are currently playing music or not.
        playing_sfx: Whether we are currently playing sfx or not.
    """

    __music: Optional[AudioFile]
    driftwood: "Driftwood"

    def __init__(self, driftwood: "Driftwood"):
        self.driftwood = driftwood

        self.playing_music = False
        self.playing_sfx = False

        self.__music = None
        self.__init_success = False

        # Attempt to initialize mixer output.
        audio_config = self.driftwood.config["audio"]
        frequency = audio_config["frequency"]
        try:
            pg.mixer.init(frequency=frequency)
        except pg.error as e:
            self.driftwood.log.msg("ERROR", "Audio", "__init__", "failed to initialize mixer output", str(e))
            return

        pg.mixer.set_num_channels(MAX_CHAN)
        pg.mixer.set_reserved(1)  # Reserved for music.

        self.driftwood.log.info("Audio", "initialized mixer output")
        self.__init_success = True

        # Register the cleanup function.
        self.driftwood.tick.register(self._cleanup, delay=0.01, during_pause=True)

    def play_sfx(
        self,
        filename: str,
        volume: int = None,
        loop: Optional[int] = 0,
        fade: float = 0.0,
    ) -> Optional[pg.mixer.Channel]:
        """Load and play a sound effect from an audio file.

        Args:
            filename: Filename of the sound effect.
            volume: Overrides the sfx_volume in the config for this sound effect. 0-128
            loop: Number of times to loop the audio. 0 for none, None for infinite.
            fade: If set, number of seconds to fade in sfx.

        Returns:
            Channel number if succeeded, None if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            CHECK(volume, int)
            if loop is not None:
                CHECK(loop, int, _min=0)
            CHECK(fade, [int, float])
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "play_sfx", "bad argument", e)
            return None

        # Give up if we didn't initialize properly.
        if not self.__init_success:
            self.driftwood.log.msg(
                "WARNING", "Audio", "play_sfx", "cannot play sfx due to initialization failure", filename
            )
            return None

        # Load the sound effect.
        audio_file: Optional[AudioFile] = self.driftwood.resource.request_audio(filename, False)
        if not audio_file:
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
            audio_file.audio.set_volume(volume / 128)
        else:
            volume = self.driftwood.config["audio"]["sfx_volume"]
            audio_file.audio.set_volume(volume / 128)

        if loop is None:
            # Loop infinitely
            loop = -1

        channel = audio_file.audio.play(loops=loop, fade_ms=int(fade * 1000))

        if channel is None:
            self.driftwood.log.msg("WARNING", "Audio", "play_sfx", "could not play sfx on channel", str(channel))
            return None

        self.playing_sfx = True

        return channel

    def volume_sfx(self, channel: Optional[pg.mixer.Channel], volume: int = None) -> Optional[int]:
        """Get or adjust the volume of a sound effect channel.

        Args:
            channel: Audio channel of the sound effect whose volume to adjust or query. None adjusts all channels.
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded (average volume of sfx if no channel is passed), None if failed.
        """
        # Input Check
        try:
            if channel is not None:
                CHECK(channel, int)
            if volume is not None:
                CHECK(volume, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_sfx", "bad argument", e)
            return None

        if volume is not None:  # Set the volume.
            # Keep volume within bounds.
            if volume > 128:
                self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is more than 128", volume)
                volume = 128
            if volume < 0:
                self.driftwood.log.msg("WARNING", "Audio", "volume_sfx", "volume is less than 0", volume)
                volume = 0

            if channel:
                channel.set_volume(volume / 128)
            else:
                for idx in range(FIRST_SFX_CHAN, MAX_CHAN):
                    pg.mixer.Channel(idx).set_volume(volume / 128)
            return volume
        else:  # Get the volume.
            if channel:
                return int(channel.get_volume() * 128)

    def stop_sfx(self, channel: pg.mixer.Channel, fade: float = 0.0) -> bool:
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

        channel.fadeout(int(fade * 1000))
        return True

    def stop_all_sfx(self) -> bool:
        """Stop all currently playing sound effects.

        Returns:
            True
        """
        for idx in range(FIRST_SFX_CHAN, MAX_CHAN):
            pg.mixer.Channel(idx).stop()
        return True

    def play_music(self, filename: str, volume: int = None, loop: Optional[int] = 0, fade: float = 0.0) -> bool:
        """Load and play music from an audio file. Also stops and unloads any previously loaded music.

        Args:
            filename: Filename of the music.
            volume: Overrides the music_volume in the config for this music. 0-128
            loop: Number of times to loop the audio. 0 for none, None for infinite.
            fade: If set, number of seconds to fade in music.

        Returns:
            True if succeeded, False if failed.
        """
        # Input Check
        try:
            CHECK(filename, str)
            if volume is not None:
                CHECK(volume, int)
            if loop is not None:
                CHECK(loop, int, _min=-1)
            CHECK(fade, [int, float], _min=0)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "play_music", "bad argument", e)
            return False

        # Give up if we didn't initialize properly.
        if not self.__init_success:
            self.driftwood.log.msg(
                "WARNING", "Audio", "play_music", "cannot play music due to initialization failure", filename
            )
            return False

        # Stop and unload any previously loaded music.
        self.stop_music()

        # Load the music.
        self.__music = self.driftwood.resource.request_audio(filename, True)
        if not self.__music or not self.__music.audio:
            self.driftwood.log.msg("ERROR", "Audio", "play_music", "could not load music", filename)
            return False

        if loop is None:
            loop = -1

        channel = pg.mixer.Channel(MUSIC_CHAN)

        # Play the music.
        try:
            channel.play(self.__music.audio, loop, int(fade * 1000))
        except Exception as e:
            self.driftwood.log.msg("WARNING", "Audio", "play_music", "could not play music", e)
            return False

        if volume is not None:
            # Keep volume within bounds.
            if volume > 128:
                volume = 128
                self.driftwood.log.msg("WARNING", "Audio", "play_music", "volume is more than 128", volume)
            if volume < 0:
                self.driftwood.log.msg("WARNING", "Audio", "play_music", "volume is less than 0", volume)
                volume = 0

            # Set the volume.
            channel.set_volume(volume)
        else:
            channel.set_volume(self.driftwood.config["audio"]["music_volume"])

        self.playing_music = True

        return True

    def volume_music(self, volume: int = None) -> Optional[int]:
        """Get or adjust the volume of the currently playing music.

        Args:
            volume: Optional, sets a new volume. Integer between 0 and 128, or no volume to just query.

        Returns:
            Integer volume if succeeded, None if failed.
        """
        # Input Check
        try:
            if volume is not None:
                CHECK(volume, int)
        except CheckFailure as e:
            self.driftwood.log.msg("ERROR", "Audio", "volume_music", "bad argument", e)
            return None

        # Search for the sound effect.
        channel = pg.mixer.Channel(MUSIC_CHAN)
        playing_music = channel.get_busy()
        if playing_music:
            if volume is not None:
                # Keep volume within bounds.
                if volume > 128:
                    volume = 128
                    self.driftwood.log.msg("WARNING", "Audio", "volume_music", "volume is more than 128", volume)
                if volume < 0:
                    self.driftwood.log.msg("WARNING", "Audio", "volume_music", "volume is less than 0", volume)
                    volume = 0

                # Set the volume.
                channel.set_volume(volume / 128)
                return volume
            else:  # Get the volume.
                return int(channel.get_volume() * 128)

        self.driftwood.log.msg("WARNING", "Audio", "volume_music", "cannot adjust volume for nonexistent music")
        return None

    def stop_music(self, fade: float = 0.0) -> bool:
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

        channel = pg.mixer.Channel(MUSIC_CHAN)
        if channel.get_busy():
            if not fade:  # Stop the music.
                channel.stop()
                self.__music = None
                self.playing_music = False
            else:  # Fade out the music.
                channel.fadeout(int(fade * 1000))
                # Cleanup callback will handle deletion.

        return True

    def _cleanup(self, seconds_past: float) -> None:
        # Tick callback to clean up files we're done with.
        if self.__music and not pg.mixer.Channel(MUSIC_CHAN).get_busy():
            self.__music = None
            self.playing_music = False
        self.playing_sfx = any(pg.mixer.Channel(idx).get_busy() for idx in range(FIRST_SFX_CHAN, MAX_CHAN))

    def _terminate(self) -> None:
        """Prepare for shutdown."""
        self.stop_music()
        self.stop_all_sfx()
        pg.mixer.quit()
