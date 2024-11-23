"""Player module."""

from pydantic import AnyHttpUrl, BaseModel, Field, IPvAnyAddress

from ak_rpi.client import Client
from ak_rpi.ntp import NTP


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
    duration: int = Field(..., ge=0)
    workId: int = Field(..., ge=0)
    lastTimestamp: int = Field(..., ge=0)
    tenantId: int = Field(..., ge=0)
    client: Client = Field(..., exclude=True)
    ntp: NTP = Field(..., exclude=True)
