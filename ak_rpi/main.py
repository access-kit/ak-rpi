"""Main module for the player."""

import logging

from ak_rpi.client import RegistrationData
from ak_rpi.errors import BaseRegistrationError

logger = logging.getLogger(__name__)


def offline_mode():
    """Run the player in offline mode.

    In this mode, the player will play the first available audio file in the media dir and loop indefinitely.
    """
    from ak_rpi.audio import AudioPlayer
    from ak_rpi.player import MediaDir
    from ak_rpi.utils import scan_for_exts

    paths = scan_for_exts(MediaDir, ["mp3", "wav"], recursive=True)
    if len(paths) == 0:
        logger.exception("No audio files found.")
        return
    fpath = paths[0].as_posix()
    logger.info(f"Found audio file: {fpath}")
    audio = AudioPlayer.Load(fpath)
    while True:
        audio.stop()
        audio.play()
        while audio.remaining_ms > 0:
            pass


def main():
    """Main function."""
    try:
        player = RegistrationData.FromConfig()
    except BaseRegistrationError as e:
        logger.exception(
            "Failed to acquire player settings; will start in offline mode.", exc_info=e
        )
        offline_mode()
    else:
        player.setup()
        player.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
