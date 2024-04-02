"""Defines the output class."""

from datetime import datetime
from typing import Any, Dict, List, Optional

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

    custom_data: Optional[Any] = None
    """Custom data of the stop."""


class PlannedStopOutput(BaseModel):
    """Output of a stop planned in the solution."""

    stop: StopOutput
    """Basic information on the stop."""

    arrival_time: Optional[datetime] = None
    """Actual arrival time at this stop."""
    cumulative_travel_distance: Optional[float] = None
    """Cumulative distance to travel from the first stop to this one, in meters."""
    cumulative_travel_duration: Optional[float] = None
    """Cumulative duration to travel from the first stop to this one, in seconds."""
    custom_data: Optional[Any] = None
    """Custom data of the stop."""
    duration: Optional[float] = None
    """Duration of the service at the stop, in seconds."""
    early_arrival_duration: Optional[float] = None
    """Duration of early arrival at the stop, in seconds."""
    end_time: Optional[datetime] = None
    """End time of the service at the stop."""
    late_arrival_duration: Optional[float] = None
    """Duration of late arrival at the stop, in seconds."""
    mix_items: Optional[Any] = None
    """Mix items at the stop."""
    start_time: Optional[datetime] = None
    """Start time of the service at the stop."""
    target_arrival_time: Optional[datetime] = None
    """Target arrival time at this stop."""
    travel_distance: Optional[float] = None
    """Distance to travel from the previous stop to this one, in meters."""
    travel_duration: Optional[float] = None
    """Duration to travel from the previous stop to this one, in seconds."""
    waiting_duration: Optional[float] = None
    """Waiting duratino at the stop, in seconds."""


class VehicleOutput(BaseModel):
    """Output of a vehicle in the solution."""

    id: str
    """ID of the vehicle."""

    alternate_stops: Optional[List[str]] = None
    """List of alternate stops that were planned on the vehicle."""
    custom_data: Optional[Any] = None
    """Custom data of the vehicle."""
    route: Optional[List[PlannedStopOutput]] = None
    """Route of the vehicle, which is a list of stops that were planned on
    it."""
    route_duration: Optional[float] = None
    """Total duration of the vehicle's route, in seconds."""
    route_stops_duration: Optional[float] = None
    """Total duration of the stops of the vehicle, in seconds."""
    route_travel_distance: Optional[float] = None
    """Total travel distance of the vehicle, in meters."""
    route_travel_duration: Optional[float] = None
    """Total travel duration of the vehicle, in seconds."""
    route_waiting_duration: Optional[float] = None
    """Total waiting duration of the vehicle, in seconds."""


class ObjectiveOutput(BaseModel):
    """Information of the objective (value function)."""

    name: str
    """Name of the objective."""

    base: Optional[float] = None
    """Base of the objective."""
    custom_data: Optional[Any] = None
    """Custom data of the objective."""
    factor: Optional[float] = None
    """Factor of the objective."""
    objectives: Optional[List[Dict[str, Any]]] = None
    """List of objectives. Each list is actually of the same class
    `ObjectiveOutput`, but we avoid a recursive definition here."""
    value: Optional[float] = None
    """Value of the objective, which is equivalent to `self.base *
    self.factor`."""


class Solution(BaseModel):
    """Solution to a Vehicle Routing Problem (VRP)."""

    unplanned: Optional[List[StopOutput]] = None
    """List of stops that were not planned in the solution."""
    vehicles: Optional[List[VehicleOutput]] = None
    """List of vehicles in the solution."""
    objective: Optional[ObjectiveOutput] = None
    """Information of the objective (value function)."""
    check: Optional[checkOutput] = None
    """Check of the solution, if enabled."""


class RunStatistics(BaseModel):
    """Statistics about a general run."""

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    iterations: Optional[int] = None
    """Number of iterations."""
    custom: Optional[Any] = None
    """Custom statistics created by the user. Can normally expect a `Dict[str,
    Any]`."""


class ResultStatistics(BaseModel):
    """Statistics about a specific result."""

    duration: Optional[float] = None
    """Duration of the run in seconds."""
    value: Optional[float] = None
    """Value of the result."""
    custom: Optional[Any] = None
    """Custom statistics created by the user. Can normally expect a `Dict[str,
    Any]`."""


class DataPoint(BaseModel):
    """A data point."""

    x: float
    """X coordinate of the data point."""
    y: float
    """Y coordinate of the data point."""


class Series(BaseModel):
    """A series of data points."""

    name: Optional[str] = None
    """Name of the series."""
    data_points: Optional[List[DataPoint]] = None
    """Data of the series."""


class SeriesData(BaseModel):
    """Data of a series."""

    value: Optional[Series] = None
    """A series for the value of the solution."""
    custom: Optional[List[Series]] = None
    """A list of series for custom statistics."""


class Statistics(BaseModel):
    """Statistics of a solution."""

    run: Optional[RunStatistics] = None
    """Statistics about the run."""
    result: Optional[ResultStatistics] = None
    """Statistics about the last result."""
    series_data: Optional[SeriesData] = None
    """Data of the series."""
    statistics_schema: Optional[str] = Field(alias="schema")
    """Schema (version)."""


class Output(BaseModel):
    """Output schema for Nextroute."""

    options: Dict[str, Any]
    """Options used to obtain this output."""
    version: Version
    """Versions used for the solution."""

    solutions: Optional[List[Solution]] = None
    """Solutions to the problem."""
    statistics: Optional[Statistics] = None
    """Statistics of the solution."""
