"""Main module for the player."""

from ak_rpi.client import RegistrationData

if __name__ == "__main__":
    player = RegistrationData.FromConfig()
    player.ntp.sync()
    print(player.ntp.server_time_offset)
