"""This module contains definitions for input sets."""

from datetime import datetime
from typing import Optional

from nextmv.base_model import BaseModel
from nextmv.cloud.run import Format


class ManagedInput(BaseModel):
    """An input created for experimenting with an application."""

    id: str
    """ID of the input."""

    name: Optional[str] = None
    """Name of the input."""
    description: Optional[str] = None
    """Description of the input."""
    run_id: Optional[str] = None
    """ID of the run that created the input."""
    upload_id: Optional[str] = None
    """ID of the upload that created the input."""
    format: Optional[Format] = None
    """Format of the input."""
    created_at: Optional[datetime] = None
    """Creation time of the input."""
    updated_at: Optional[datetime] = None
    """Last update time of the input."""


class InputSet(BaseModel):
    """An input set is the collection of inputs from the associated runs."""

    app_id: str
    """ID of the application that the input set belongs to."""
    created_at: datetime
    """Creation time of the input set."""
    description: str
    """Description of the input set."""
    id: str
    """ID of the input set."""
    input_ids: list[str]
    """IDs of the inputs in the input set."""
    name: str
    """Name of the input set."""
    updated_at: datetime
    """Last update time of the input set."""
    inputs: list[ManagedInput]
    """List of inputs in the input set."""
