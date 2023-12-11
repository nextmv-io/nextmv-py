"""Defines the location class."""


from nextmv.base_model import BaseModel


class Location(BaseModel):
    """Location represents a geographical location."""

    lon: float
    """Longitude of the location."""
    lat: float
    """Latitude of the location."""
