"""Defines the input class."""

from typing import Any

from nextmv.base_model import BaseModel
from nextmv.nextroute.schema.stop import AlternateStop, Stop, StopDefaults
from nextmv.nextroute.schema.vehicle import Vehicle, VehicleDefaults


class Defaults(BaseModel):
    """Default values for vehicles and stops."""

    stops: StopDefaults | None = None
    """Default values for stops."""
    vehicles: VehicleDefaults | None = None
    """Default values for vehicles."""


class DurationGroup(BaseModel):
    """Represents a group of stops that get additional duration whenever a stop
    of the group is approached for the first time."""

    duration: int
    """Duration to add when visiting the group."""
    group: list[str]
    """Stop IDs contained in the group."""


class Input(BaseModel):
    """Input schema for Nextroute."""

    stops: list[Stop]
    """Stops that must be visited by the vehicles."""
    vehicles: list[Vehicle]
    """Vehicles that service the stops."""

    alternate_stops: list[AlternateStop] | None = None
    """A set of alternate stops for the vehicles."""
    custom_data: Any | None = None
    """Arbitrary data associated with the input."""
    defaults: Defaults | None = None
    """Default values for vehicles and stops."""
    distance_matrix: list[list[float]] | None = None
    """Matrix of travel distances in meters between stops."""
    duratrion_groups: list[DurationGroup] | None = None
    """Duration in seconds added when approaching the group."""
    duration_matrix: list[list[float]] | None = None
    """Matrix of travel durations in seconds between stops."""
    options: Any | None = None
    """Arbitrary options."""
    stop_groups: list[list[str]] | None = None
    """Groups of stops that must be part of the same route."""
