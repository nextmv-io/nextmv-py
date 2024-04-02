"""This module contains definitions for input sets."""

from datetime import datetime
from typing import List

from nextmv.base_model import BaseModel


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
    input_ids: List[str]
    """IDs of the inputs in the input set."""
    name: str
    """Name of the input set."""
    updated_at: datetime
    """Last update time of the input set."""
