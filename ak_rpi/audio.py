"""Audio player."""

import logging
import time
from pathlib import Path

import pygame
from pydantic import BaseModel
from pydub.utils import mediainfo

logger = logging.getLogger(__name__)


class AudioPlayer(BaseModel):
    """A class for playing audio."""

    channel: pygame.mixer.Channel
    sound: pygame.mixer.Sound
    duration: int
    audio_file: Path
    start_time: int = 0

    @classmethod
    def Load(cls, audio_file: str):
        """Load an audio file.

        Returns:
            player (AudioPlayer): The audio player
        """
        logger.info(f"Playing {audio_file}")
        sound = pygame.mixer.Sound(audio_file)
        duration = int(mediainfo(audio_file)["duration"] * 1000)
        channel = pygame.mixer.find_channel()
        if channel is None:
            msg = "No available channels."
            logger.error(msg)
            raise ValueError(msg)
        return cls(
            channel=channel, sound=sound, duration=duration, audio_file=Path(audio_file)
        )

    def play(self):
        """Play the audio file."""
        self.channel.play(self.sound)
        self.start_time = int(time.perf_counter() * 1000)

    @property
    def remaining_ms(self):
        """Get the remaining time in ms.

        Returns:
            int: The remaining time in ms.
        """
        return self.duration - int(time.perf_counter() * 1000 - self.start_time)

    def stop(self):
        """Stop the audio."""
        self.channel.stop()
        self.start_time = 0
