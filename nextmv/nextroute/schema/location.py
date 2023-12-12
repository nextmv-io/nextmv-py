"""Defines the location class."""


from nextmv.base_model import BaseModel


class Location(BaseModel):
    """Location represents a geographical location."""

    lat: float
    """Latitude of the location."""
    lon: float
    """Longitude of the location."""
