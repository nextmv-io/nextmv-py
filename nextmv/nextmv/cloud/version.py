"""Manages application versions within the Nextmv Cloud API.

This module provides data models for representing application versions,
their executables, and associated requirements. These models are used
for interacting with version-related endpoints of the Nextmv Cloud API,
allowing users to define, retrieve, and manage different versions of their
decision applications.

Classes
-------
VersionExecutableRequirements
    Defines the requirements for a version's executable, such as type and runtime.
VersionExecutable
    Represents the executable artifact for a specific application version.
Version
    Represents a version of an application, linking to its executable and metadata.
"""

from datetime import datetime

from nextmv.base_model import BaseModel


class VersionExecutableRequirements(BaseModel):
    """
    Requirements for a version executable.

    You can import the `VersionExecutableRequirements` class directly from `cloud`:

    ```python
    from nextmv.cloud import VersionExecutableRequirements
    ```

    These requirements specify the environment and type of executable needed
    to run a particular version of an application.

    Parameters
    ----------
    executable_type : str
        The type of the executable (e.g., "binary", "docker").
    runtime : str
        The runtime environment for the executable (e.g., "go", "python").

    Examples
    --------
    >>> requirements = VersionExecutableRequirements(
    ...     executable_type="binary",
    ...     runtime="go1.x"
    ... )
    >>> print(requirements.executable_type)
    binary
    """

    executable_type: str
    """Type of the executable."""
    runtime: str
    """Runtime for the executable."""


class VersionExecutable(BaseModel):
    """
    Executable for a version.

    You can import the `VersionExecutable` class directly from `cloud`:

    ```python
    from nextmv.cloud import VersionExecutable
    ```

    This class holds information about the actual executable file or image
    associated with an application version, including who uploaded it and when.

    Parameters
    ----------
    id : str
        Unique identifier for the version executable.
    user_email : str
        Email of the user who uploaded the executable.
    uploaded_at : datetime
        Timestamp indicating when the executable was uploaded.
    requirements : VersionExecutableRequirements
        The specific requirements for this executable.

    Examples
    --------
    >>> from datetime import datetime
    >>> reqs = VersionExecutableRequirements(executable_type="docker", runtime="custom")
    >>> executable = VersionExecutable(
    ...     id="exec-123",
    ...     user_email="user@example.com",
    ...     uploaded_at=datetime.now(),
    ...     requirements=reqs
    ... )
    >>> print(executable.id)
    exec-123
    """

    id: str
    """ID of the version."""
    user_email: str
    """Email of the user who uploaded the executable."""
    uploaded_at: datetime
    """Time the executable was uploaded."""
    requirements: VersionExecutableRequirements
    """Requirements for the executable."""


class Version(BaseModel):
    """
    A version of an application representing a code artifact or a compiled binary.

    You can import the `Version` class directly from `cloud`:

    ```python
    from nextmv.cloud import Version
    ```

    This class encapsulates all details of a specific version of an application,
    including its metadata, associated executable, and timestamps.

    Parameters
    ----------
    id : str
        Unique identifier for the version.
    application_id : str
        Identifier of the application to which this version belongs.
    name : str
        User-defined name for the version (e.g., "v1.0.0", "feature-branch-build").
    description : str
        A more detailed description of the version and its changes.
    executable : VersionExecutable
        The executable artifact associated with this version.
    created_at : datetime
        Timestamp indicating when the version was created.
    updated_at : datetime
        Timestamp indicating when the version was last updated.

    Examples
    --------
    >>> from datetime import datetime
    >>> reqs = VersionExecutableRequirements(executable_type="binary", runtime="java11")
    >>> exe = VersionExecutable(
    ...     id="exec-abc",
    ...     user_email="dev@example.com",
    ...     uploaded_at=datetime.now(),
    ...     requirements=reqs
    ... )
    >>> version_info = Version(
    ...     id="ver-xyz",
    ...     application_id="app-123",
    ...     name="Initial Release",
    ...     description="First stable release of the model.",
    ...     executable=exe,
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now()
    ... )
    >>> print(version_info.name)
    Initial Release
    """

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
