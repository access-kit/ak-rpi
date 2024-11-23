"""Settings for the player."""

import json
from pathlib import Path

import httpx
from pydantic import BaseModel, HttpUrl, IPvAnyAddress, SecretStr

from ak_rpi.errors import (
    CouldNotFindPlayerError,
    MismatchedSerialNumberError,
    NoRegistrationPossibleError,
    RegistrationError,
)
from ak_rpi.utils import get_ip_addresses, get_mac_address, get_serial_number

REGISTRATION_PATH = Path("registered")


class Client(BaseModel, arbitrary_types_allowed=True):
    """A client for the player."""

    syncUrl: HttpUrl
    password: SecretStr
    client: httpx.Client

    def register_new(
        self, ip_address: IPvAnyAddress | str, mac_address: str, serial_number: str
    ):
        """Register the player with the server.

        Args:
            ip_address (IPvAnyAddress | str): The ip address of the player.
            mac_address (str): The mac address of the player.
            serial_number (str): The serial number of the player.

        Returns:
            player (PlayerSettings): The player
        """
        from ak_rpi.ntp import NTP
        from ak_rpi.player import PlayerSettings

        response = self.client.post(
            "/api/mediaplayer/serialnumber",
            json={
                "ipAddress": ip_address,
                "macAddress": mac_address,
                "serialNumber": serial_number,
                "syncUrl": str(self.syncUrl),
            },
        )
        if response.status_code != 200:
            msg = f"{response.status_code}: {response.text}"
            raise RegistrationError(msg)
        data = response.json()
        registration_data = RegistrationData(
            **data, password=self.password.get_secret_value()
        )
        with open(REGISTRATION_PATH, "w") as f:
            json.dump(registration_data.model_dump(), f)

        return PlayerSettings(**data, client=self, ntp=NTP(client=self))

    def get_mediaplayer(self, player_id: int):
        """Get the player settings from the server.

        Args:
            player_id (int): The id of the player.

        Returns:
            player (PlayerSettings): The player settings.
        """
        from ak_rpi.ntp import NTP
        from ak_rpi.player import PlayerSettings

        response = self.client.get(f"/api/mediaplayer/{player_id}")
        if response.status_code != 200:
            msg = f"{response.status_code}: {response.text}"
            raise CouldNotFindPlayerError(msg)
        data = response.json()
        return PlayerSettings(**data, client=self, ntp=NTP(client=self))

    def get_sync(self, req_sent_at: int):
        """Get the current timestamp from the server."""
        url = "/api/sync"
        response = self.client.get(url, params={"reqSentAt": req_sent_at})
        return response


class ClientBase(BaseModel, extra="ignore"):
    """Base settings for the client."""

    syncUrl: HttpUrl
    password: SecretStr

    def create_client(self) -> Client:
        """Create a new httpx client and store it.

        Returns:
            client (Client): The client.
        """
        client = httpx.Client(
            base_url=str(self.syncUrl),
            params={"password": self.password.get_secret_value()},
        )
        return Client(syncUrl=self.syncUrl, password=self.password, client=client)


class RegistrationData(BaseModel, extra="ignore"):
    """Registration data indicating the player already exists."""

    id: int
    password: str

    @classmethod
    def FromConfig(cls):
        """Create a player from the config file.

        If the player is not registered, it will be registered.

        Otherwise, the player will be fetched from the server.

        Returns:
            player (PlayerSettings): The player.
        """
        with open("config.json") as f:
            data = json.load(f)
        has_password = "password" in data
        registration_exists = REGISTRATION_PATH.exists()
        if not has_password and not registration_exists:
            raise NoRegistrationPossibleError()
        if has_password and not registration_exists:
            client_base = ClientBase(**data)
            client = client_base.create_client()
            return cls.Register(client)
        else:
            with open(REGISTRATION_PATH) as f:
                reg = RegistrationData(**json.load(f))
            client_base = ClientBase(**data)
            client = client_base.create_client()
            return cls.FromId(reg.id, client)

    @classmethod
    def FromId(cls, player_id: int, client: Client):
        """Create a player from the id by fetching it from the server.

        Args:
            player_id (int): The id of the player.
            client (Client): The client.

        Returns:
            player (PlayerSettings): The player.
        """
        serial_number = get_serial_number()
        res = client.get_mediaplayer(player_id)
        if res.serialNumber != serial_number:
            raise MismatchedSerialNumberError()
        return res

    @classmethod
    def Register(cls, client: Client):
        """Register the player with the server.

        Args:
            client (Client): The client.

        Returns:
            player (PlayerSettings): The player.
        """
        serial_number = get_serial_number()
        mac_address = get_mac_address()
        ip_addresses = get_ip_addresses()
        ip_address = ip_addresses.get("eth0", ip_addresses.get("wlan0", ""))
        res = client.register_new(ip_address, mac_address, serial_number)
        return res
