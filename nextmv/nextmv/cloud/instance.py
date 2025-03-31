"""This module contains definitions for instances."""

from datetime import datetime
from typing import Optional

from nextmv.base_model import BaseModel


class InstanceConfiguration(BaseModel):
    """Configuration for an instance."""

    execution_class: Optional[str] = None
    """Execution class for the instance."""
    options: Optional[dict] = None
    """Options of the app that the instance uses."""
    secrets_collection_id: Optional[str] = None
    """ID of the secrets collection that the instance uses."""


class Instance(BaseModel):
    """A instance of an application tied to a version and further configuration."""

    id: str
    """ID of the instance."""
    application_id: str
    """ID of the application that this is an instance of."""
    version_id: str
    """ID of the version that this instance is uses."""
    name: str
    """Name of the instance."""
    description: str
    """Description of the instance."""
    configuration: InstanceConfiguration
    """Configuration for the instance."""
    locked: bool
    """Whether the instance is locked."""
    created_at: datetime
    """Creation time of the instance."""
    updated_at: datetime
    """Last update time of the instance."""
