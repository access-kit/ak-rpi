"""Player module."""

import logging
from pathlib import Path
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field, IPvAnyAddress

from ak_rpi.audio import AudioPlayer
from ak_rpi.client import Client
from ak_rpi.ntp import NTP
from ak_rpi.utils import scan_for_exts

logger = logging.getLogger(__name__)

MediaState = Literal[
    "waiting_to_sync", "syncing", "waiting_to_loop", "starting", "idle"
]

MediaDir = Path(__file__).parent.parent / "media"


class PlayerSettings(BaseModel, extra="ignore"):
    """Settings for the player."""

    id: int
    nickname: str
    ipAddress: IPvAnyAddress
    macAddress: str
    syncUrl: AnyHttpUrl
    firmwareUrl: AnyHttpUrl
    volume: int = Field(..., ge=0, le=100)
    quietMode: float = Field(..., ge=0, le=1)
    serialNumber: str
    duration: int | None = Field(default=None, ge=0)
    workId: int | None = Field(default=None, ge=0)
    lastTimestamp: int | None = Field(default=None, ge=0)
    tenantId: int = Field(..., ge=0)
    client: Client = Field(..., exclude=True)
    ntp: NTP = Field(..., exclude=True)
    mediaPath: str | None = Field(default=None, alias="videoPath")
    audio: AudioPlayer | None = Field(default=None, exclude=True)
    media_state: MediaState = Field(default="idle", exclude=True)

    def load_audio_default(self):
        """Find and load the first available audio file in the media dir.

        Searches for .mp3 and .wav files in the media dir and loads the first one found.

        Mutates self to set the audio attribute.
        """
        logger.info("Attempting to load first available audio file...")
        paths = scan_for_exts(MediaDir, ["mp3", "wav"], recursive=True)
        if len(paths) == 0:
            logger.error("No audio files found.")
            return
        fpath = paths[0].as_posix()
        logger.info(f"Found audio file: {fpath}")
        self.audio = AudioPlayer.Load(fpath)
        logger.info(f"Loaded audio file: {fpath}")

    @property
    def scoped_media_path(self):
        """Get the scoped media path.

        Returns:
            scoped_media_path (Path | None): The scoped media path.
        """
        if self.mediaPath is None:
            return None
        return MediaDir / self.mediaPath

    def load_audio(self):
        """Attempt to load audio data.

        This will attempt to load the audio file from the scoped media path (i.e. the `media/` dir).
        If no file is provided or the file does not exist it will attempt to load the first available audio file.

        Mutates self to set the audio attribute.
        """
        if self.scoped_media_path is None:
            self.load_audio_default()
            return
        if self.scoped_media_path.exists() and self.scoped_media_path.is_file():
            logger.info(f"Attempting to load audio file: {self.scoped_media_path}")
            self.audio = AudioPlayer.Load(self.scoped_media_path.as_posix())
            return
        self.load_audio_default()
        if self.audio is None:
            logger.error("Failed to load audio.")
            return
        dur = self.audio.duration
        self.client.put_duration(self.id, dur)

    def setup(self):
        """Setup the player's media."""
        self.ntp.sync()
        # TODO: load file, update audio duration etc
        self.load_audio()
        if self.audio:
            self.media_state = "starting"
        self.ntp.sync()
        return

    def audio_machine(self):
        """The audio state machine for cooperative multi-tasking."""
        if self.audio is None:
            return
        if self.media_state == "starting":
            self.audio.stop()
            self.audio.play()
            self.lastTimestamp = self.ntp.server_time
            # TODO: submit timestamp
            self.media_state = "waiting_to_sync"
        if self.media_state == "waiting_to_sync":
            remaining_time = self.audio.remaining_ms
            sync_time = min(20000, self.audio.duration)
            self.media_state = (
                "waiting_to_loop" if remaining_time > sync_time else "syncing"
            )
        if self.media_state == "syncing":
            self.ntp.sync()
            self.media_state = "waiting_to_loop"
        if self.media_state == "waiting_to_loop":
            # TODO: should we do a blocking await here?
            remaining_time = self.audio.remaining_ms
            self.media_state = "waiting_to_loop" if remaining_time > 0 else "starting"

    def run(self):
        """Run the player."""
        while True:
            self.audio_machine()
