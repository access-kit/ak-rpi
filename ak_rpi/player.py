"""Player module."""

import logging
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, Field, IPvAnyAddress

from ak_rpi.audio import AudioPlayer
from ak_rpi.client import Client
from ak_rpi.ntp import NTP

logger = logging.getLogger(__name__)

MediaState = Literal[
    "waiting_to_sync", "syncing", "waiting_to_loop", "starting", "idle"
]


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
    audio: AudioPlayer | None = Field(default=None, exclude=True)
    media_state: MediaState = Field(default="idle", exclude=True)

    def setup(self):
        """Setup the player's media."""
        self.ntp.sync()
        # TODO: load file, update audio duration etc
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
