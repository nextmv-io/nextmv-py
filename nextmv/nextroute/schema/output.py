"""Defines the output class."""


from datetime import datetime
from typing import Any

from pydantic import Field

from nextmv.base_model import BaseModel
from nextmv.nextroute.check import Output as checkOutput
from nextmv.nextroute.schema.location import Location


class Version(BaseModel):
    """A version used for solving."""

    sdk: str
    """Nextmv SDK."""


class StopOutput(BaseModel):
    """Basic structure for the output of a stop."""

    id: str
    """ID of the stop."""
    location: Location
    """Location of the stop."""

    custom_data: Any | None = None
    """Custom data of the stop."""


class PlannedStopOutput(BaseModel):
    """Output of a stop planned in the solution."""

    stop: StopOutput
    """Basic information on the stop."""

    arrival_time: datetime | None = None
    """Actual arrival time at this stop."""
    cumulative_travel_distance: float | None = None
    """Cumulative distance to travel from the first stop to this one, in meters."""
    cumulative_travel_duration: float | None = None
    """Cumulative duration to travel from the first stop to this one, in seconds."""
    custom_data: Any | None = None
    """Custom data of the stop."""
    duration: float | None = None
    """Duration of the service at the stop, in seconds."""
    early_arrival_duration: float | None = None
    """Duration of early arrival at the stop, in seconds."""
    end_time: datetime | None = None
    """End time of the service at the stop."""
    late_arrival_duration: float | None = None
    """Duration of late arrival at the stop, in seconds."""
    mix_items: Any | None = None
    """Mix items at the stop."""
    start_time: datetime | None = None
    """Start time of the service at the stop."""
    target_arrival_time: datetime | None = None
    """Target arrival time at this stop."""
    travel_distance: float | None = None
    """Distance to travel from the previous stop to this one, in meters."""
    travel_duration: float | None = None
    """Duration to travel from the previous stop to this one, in seconds."""
    waiting_duration: float | None = None
    """Waiting duratino at the stop, in seconds."""


class VehicleOutput(BaseModel):
    """Output of a vehicle in the solution."""

    id: str
    """ID of the vehicle."""

    alternate_stops: list[str] | None = None
    """List of alternate stops that were planned on the vehicle."""
    custom_data: Any | None = None
    """Custom data of the vehicle."""
    route: list[PlannedStopOutput] | None = None
    """Route of the vehicle, which is a list of stops that were planned on
    it."""
    route_duration: float | None = None
    """Total duration of the vehicle's route, in seconds."""
    route_stops_duration: float | None = None
    """Total duration of the stops of the vehicle, in seconds."""
    route_travel_distance: float | None = None
    """Total travel distance of the vehicle, in meters."""
    route_travel_duration: float | None = None
    """Total travel duration of the vehicle, in seconds."""
    route_waiting_duration: float | None = None
    """Total waiting duration of the vehicle, in seconds."""


class ObjectiveOutput(BaseModel):
    """Information of the objective (value function)."""

    name: str
    """Name of the objective."""

    base: float | None = None
    """Base of the objective."""
    custom_data: Any | None = None
    """Custom data of the objective."""
    factor: float | None = None
    """Factor of the objective."""
    objectives: list[dict[str, Any]] | None = None
    """List of objectives. Each list is actually of the same class
    `ObjectiveOutput`, but we avoid a recursive definition here."""
    value: float | None = None
    """Value of the objective, which is equivalent to `self.base *
    self.factor`."""


class Solution(BaseModel):
    """Solution to a Vehicle Routing Problem (VRP)."""

    unplanned: list[StopOutput] | None = None
    """List of stops that were not planned in the solution."""
    vehicles: list[VehicleOutput] | None = None
    """List of vehicles in the solution."""
    objective: ObjectiveOutput | None = None
    """Information of the objective (value function)."""
    check: checkOutput | None = None
    """Check of the solution, if enabled."""


class RunStatistics(BaseModel):
    """Statistics about a general run."""

    duration: float | None = None
    """Duration of the run in seconds."""
    iterations: int | None = None
    """Number of iterations."""
    custom: Any | None = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class ResultStatistics(BaseModel):
    """Statistics about a specific result."""

    duration: float | None = None
    """Duration of the run in seconds."""
    value: float | None = None
    """Value of the result."""
    custom: Any | None = None
    """Custom statistics created by the user. Can normally expect a `dict[str,
    Any]`."""


class DataPoint(BaseModel):
    """A data point."""

    x: float
    """X coordinate of the data point."""
    y: float
    """Y coordinate of the data point."""


class Series(BaseModel):
    """A series of data points."""

    name: str | None = None
    """Name of the series."""
    data_points: list[DataPoint] | None = None
    """Data of the series."""


class SeriesData(BaseModel):
    """Data of a series."""

    value: Series | None = None
    """A series for the value of the solution."""
    custom: list[Series] | None = None
    """A list of series for custom statistics."""


class Statistics(BaseModel):
    """Statistics of a solution."""

    run: RunStatistics | None = None
    """Statistics about the run."""
    result: ResultStatistics | None = None
    """Statistics about the last result."""
    series_data: SeriesData | None = None
    """Data of the series."""
    statistics_schema: str | None = Field(alias="schema")
    """Schema (version)."""


class Output(BaseModel):
    """Output schema for Nextroute."""

    options: dict[str, Any]
    """Options used to obtain this output."""
    version: Version
    """Versions used for the solution."""

    solutions: list[Solution] | None = None
    """Solutions to the problem."""
    statistics: Statistics | None = None
    """Statistics of the solution."""
