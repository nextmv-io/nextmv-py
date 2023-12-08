"""Defines the location class."""


from dataclasses import dataclass

from .base import _Base


@dataclass
class Location(_Base):
    """Location represents a geographical location."""

    lon: float
    """Longitude of the location."""
    lat: float
    """Latitude of the location."""
