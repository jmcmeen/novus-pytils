"""The package's exceptions. Everything raised here derives from :class:`NovusPytilsError`."""


class NovusPytilsError(Exception):
    """Base class for errors raised by novus-pytils."""


class UnsupportedFormatError(NovusPytilsError):
    """The file's format is not one this function can handle."""


class ConversionError(NovusPytilsError):
    """A format conversion failed in the backend (pydub, Pillow)."""


class MissingDependencyError(NovusPytilsError):
    """An optional extra needed for this operation is not installed."""
