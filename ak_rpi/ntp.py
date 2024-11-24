"""A module for performing NTP sync."""

import logging
import time

from pydantic import BaseModel, Field, ValidationError

from ak_rpi.client import Client

logger = logging.getLogger(__name__)


def monotonic_time_ms():
    """Get the monotonic time."""
    # return int(time.monotonic() * 1000)
    return int(time.perf_counter() * 1000)


class NTP(BaseModel):
    """A class for performing NTP sync."""

    server_time_offset: int = Field(
        default=0, description="The offset between the server and the player in ms."
    )
    n_cyles: int = Field(default=20, description="The number of cycles to perform.")
    startup_time: int = Field(
        default_factory=lambda: int(time.time() * 1000),
        description="The time the player started up in ms.",
    )
    startup_time_monotonic: int = Field(
        default_factory=monotonic_time_ms,
        description="The time the player started up in monotonic ms.",
    )
    client: Client

    @property
    def local_time(self):
        """Get the local time."""
        return self.startup_time + (monotonic_time_ms() - self.startup_time_monotonic)

    def sync(self):
        """Perform an NTP sync algorithm which will determine the offset between the server and the player."""
        res = [self.sync_cycle() for _ in range(self.n_cyles)]
        offsets: list[float] = [offset for offset in res if offset is not None]
        if len(offsets) == 0:
            logger.error("Failed to get any offsets.")
            return self.server_time_offset
        average_offset = sum(offsets) / len(offsets)
        std_offset = sum((offset - average_offset) ** 2 for offset in offsets) / len(
            offsets
        )
        non_outliers = [
            offset for offset in offsets if abs(offset - average_offset) < std_offset
        ]
        if len(non_outliers) == 0:
            logger.error("Failed to get any non-outliers.")
            return self.server_time_offset
        average_offset_no_outliers = sum(non_outliers) / len(non_outliers)
        self.server_time_offset = int(average_offset_no_outliers)
        return int(average_offset_no_outliers)

    def sync_cycle(self):
        """Perform a single NTP sync cycle."""
        local_time_at_req = self.local_time
        response = self.client.get_sync(local_time_at_req)
        local_time_at_res = self.local_time
        if response.status_code != 200:
            logger.error(
                f"Failed to get sync response: {response.status_code}, {response.text}"
            )
            return None
        try:
            sync_res = SyncResponse(**response.json(), resReceivedAt=local_time_at_res)
        except ValidationError as e:
            logger.exception("Failed to parse sync response", exc_info=e)
            return None
        return sync_res.offset

    @property
    def server_time(self):
        """Get the server time."""
        return self.local_time + self.server_time_offset


class SyncResponse(BaseModel):
    """A response from the server."""

    reqSentAt: int
    reqReceivedAt: int
    resSentAt: int
    resReceivedAt: int

    @property
    def oneway_latency(self):
        """Get the offset between the server and the player."""
        round_trip = (self.resReceivedAt - self.reqSentAt) - (
            self.resSentAt - self.reqReceivedAt
        )
        return round_trip / 2

    @property
    def offset(self):
        """Get the offset between the server and the player."""
        expected_server_receipt_time = self.reqSentAt + self.oneway_latency
        server_leads_by = self.reqReceivedAt - expected_server_receipt_time
        return server_leads_by
