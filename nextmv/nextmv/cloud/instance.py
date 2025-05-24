"""Classes for working with Nextmv Cloud Instances.

This module provides classes for interacting with instances in Nextmv Cloud.
It defines the core data structures for both instance configuration and the
instance itself.

Classes
-------
InstanceConfiguration
    Configuration settings for a Nextmv Cloud instance.
Instance
    Representation of a Nextmv Cloud instance tied to an application version.
"""

from datetime import datetime
from typing import Optional

from nextmv.base_model import BaseModel


class InstanceConfiguration(BaseModel):
    """Configuration for a Nextmv Cloud instance.

    You can import the `InstanceConfiguration` class directly from `cloud`:

    ```python
    from nextmv.cloud import InstanceConfiguration
    ```

    This class represents the configuration settings that can be applied to a
    Nextmv Cloud instance, including execution class, options, and secrets.

    Parameters
    ----------
    execution_class : str, optional
        The execution class for the instance, which determines compute resources.
    options : dict, optional
        Runtime options/parameters for the application.
    secrets_collection_id : str, optional
        ID of the secrets collection to use with this instance.

    Examples
    --------
    >>> config = InstanceConfiguration(
    ...     execution_class="small",
    ...     options={"max_runtime": 30},
    ...     secrets_collection_id="sc_1234567890"
    ... )
    """

    execution_class: Optional[str] = None
    """Execution class for the instance."""
    options: Optional[dict] = None
    """Options of the app that the instance uses."""
    secrets_collection_id: Optional[str] = None
    """ID of the secrets collection that the instance uses."""


class Instance(BaseModel):
    """An instance of an application tied to a version with configuration.

    You can import the `Instance` class directly from `cloud`:

    ```python
    from nextmv.cloud import Instance
    ```

    A Nextmv Cloud instance represents a deployable configuration of an application
    version. Instances have their own unique identity and can be used to run jobs
    with specific configurations.

    Parameters
    ----------
    id : str
        The unique identifier of the instance.
    application_id : str
        ID of the application that this instance belongs to.
    version_id : str
        ID of the application version this instance uses.
    name : str
        Human-readable name of the instance.
    description : str
        Detailed description of the instance.
    configuration : InstanceConfiguration
        Configuration settings for this instance.
    locked : bool
        Whether the instance is locked for modifications.
    created_at : datetime
        Timestamp when the instance was created.
    updated_at : datetime
        Timestamp when the instance was last updated.

    Examples
    --------
    >>> from nextmv.cloud import Instance, InstanceConfiguration
    >>> instance = Instance(
    ...     id="inst_1234567890",
    ...     application_id="app_1234567890",
    ...     version_id="ver_1234567890",
    ...     name="Production Routing Instance",
    ...     description="Instance for daily production routing jobs",
    ...     configuration=InstanceConfiguration(execution_class="small"),
    ...     locked=False,
    ...     created_at=datetime.now(),
    ...     updated_at=datetime.now()
    ... )
    """

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
