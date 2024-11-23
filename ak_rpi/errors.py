"""Errors for the ak_rpi package."""


class BaseRegistrationError(Exception):
    """Base class for registration errors."""


class RegistrationError(BaseRegistrationError):
    """An error occurred during registration."""


class NoRegistrationPossibleError(BaseRegistrationError):
    """An error occurred during registration."""


class CouldNotFindPlayerError(BaseRegistrationError):
    """An error occurred while fetching the mediaplayer."""


class MismatchedSerialNumberError(BaseRegistrationError):
    """The serial number does not match the one on the server."""
