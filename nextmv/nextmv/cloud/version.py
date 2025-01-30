"""This module contains definitions for versions."""

from datetime import datetime

from nextmv.base_model import BaseModel


class VersionExecutableRequirements(BaseModel):
    """Requirements for a version executable."""

    executable_type: str
    """Type of the executable."""
    runtime: str
    """Runtime for the executable."""


class VersionExecutable(BaseModel):
    """Executable for a version."""

    id: str
    """ID of the version."""
    user_email: str
    """Email of the user who uploaded the executable."""
    uploaded_at: datetime
    """Time the executable was uploaded."""
    requirements: VersionExecutableRequirements
    """Requirements for the executable."""


class Version(BaseModel):
    """A version of an application representing a code artifact or a compiled binary."""

    id: str
    """ID of the version."""
    application_id: str
    """ID of the application that this is a version of."""
    name: str
    """Name of the version."""
    description: str
    """Description of the version."""
    executable: VersionExecutable
    """Executable for the version."""
    created_at: datetime
    """Creation time of the version."""
    updated_at: datetime
    """Last update time of the version."""
