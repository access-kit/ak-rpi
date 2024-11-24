"""Main module for the player."""

import logging

from ak_rpi.client import RegistrationData
from ak_rpi.errors import BaseRegistrationError

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        player = RegistrationData.FromConfig()
    except BaseRegistrationError as e:
        logger.exception(
            "Failed to acquire player settings; will start in offline mode.", exc_info=e
        )
        # TODO: implement offline mode
    else:
        player.setup()
        player.run()
