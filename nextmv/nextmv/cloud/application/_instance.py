"""
Application mixin for managing app instances.
"""

from typing import TYPE_CHECKING, Any

import requests

from nextmv.cloud.application._utils import _is_not_exist_error
from nextmv.cloud.instance import Instance, InstanceConfiguration
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationInstanceMixin:
    """
    Mixin class for managing app instances within an application.
    """

    def delete_instance(self: "Application", instance_id: str) -> None:
        """
        Delete an instance.

        Permanently removes the specified instance from the application.

        Parameters
        ----------
        instance_id : str
            ID of the instance to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_instance("prod-instance")  # Permanently deletes the instance
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/instances/{instance_id}",
        )

    def instance(self: "Application", instance_id: str) -> Instance:
        """
        Get an instance.

        Parameters
        ----------
        instance_id : str
            ID of the instance to retrieve.

        Returns
        -------
        Instance
            The requested instance details.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> instance = app.instance("instance-123")
        >>> print(instance.name)
        'Production Instance'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/instances/{instance_id}",
        )

        return Instance.from_dict(response.json())

    def instance_exists(self: "Application", instance_id: str) -> bool:
        """
        Check if an instance exists.

        Parameters
        ----------
        instance_id : str
            ID of the instance to check.

        Returns
        -------
        bool
            True if the instance exists, False otherwise.

        Examples
        --------
        >>> app.instance_exists("instance-123")
        True
        """

        try:
            self.instance(instance_id=instance_id)
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            raise e

    def list_instances(self: "Application") -> list[Instance]:
        """
        List all instances.

        Returns
        -------
        list[Instance]
            List of all instances associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> instances = app.list_instances()
        >>> for instance in instances:
        ...     print(instance.name)
        'Development Instance'
        'Production Instance'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/instances",
        )

        return [Instance.from_dict(instance) for instance in response.json()]

    def new_instance(
        self: "Application",
        version_id: str,
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        configuration: InstanceConfiguration | None = None,
        exist_ok: bool = False,
    ) -> Instance:
        """
        Create a new instance and associate it with a version.

        This method creates a new instance associated with a specific version
        of the application. Instances are configurations of an application
        version that can be executed.

        Parameters
        ----------
        version_id : str
            ID of the version to associate the instance with.
        id : str | None, default=None
            ID of the instance. Will be generated if not provided.
        name : str | None, default=None
            Name of the instance. Will be generated if not provided.
        description : Optional[str], default=None
            Description of the instance.
        configuration : Optional[InstanceConfiguration], default=None
            Configuration to use for the instance. This can include resources,
            timeouts, and other execution parameters.
        exist_ok : bool, default=False
            If True and an instance with the same ID already exists,
            return the existing instance instead of creating a new one.

        Returns
        -------
        Instance
            The newly created (or existing) instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        ValueError
            If exist_ok is True and id is None.

        Examples
        --------
        >>> # Create a new instance for a specific version
        >>> instance = app.new_instance(
        ...     version_id="version-123",
        ...     id="prod-instance",
        ...     name="Production Instance",
        ...     description="Instance for production use"
        ... )
        >>> print(instance.name)
        'Production Instance'
        """

        if exist_ok and (id is None or id == ""):
            raise ValueError("If exist_ok is True, id must be provided")

        if exist_ok and self.instance_exists(instance_id=id):
            return self.instance(instance_id=id)

        if id is None or id == "":
            id = safe_id(prefix="instance")
        if name is None or name == "":
            name = id

        payload = {
            "id": id,
            "name": name,
            "version_id": version_id,
        }

        if description is not None:
            payload["description"] = description
        if configuration is not None:
            payload["configuration"] = configuration.to_dict()

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/instances",
            payload=payload,
        )

        return Instance.from_dict(response.json())

    def update_instance(
        self: "Application",
        id: str,
        name: str | None = None,
        version_id: str | None = None,
        description: str | None = None,
        configuration: InstanceConfiguration | dict[str, Any] | None = None,
    ) -> Instance:
        """
        Update an instance.

        Parameters
        ----------
        id : str
            ID of the instance to update.
        name : Optional[str], default=None
            Optional name of the instance.
        version_id : Optional[str], default=None
            Optional ID of the version to associate the instance with.
        description : Optional[str], default=None
            Optional description of the instance.
        configuration : Optional[InstanceConfiguration | dict[str, Any]], default=None
            Optional configuration to use for the instance.

        Returns
        -------
        Instance
            The updated instance.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.
        """

        # Get the instance as it currently exsits.
        instance = self.instance(id)
        instance_dict = instance.to_dict()
        payload = instance_dict.copy()

        if name is not None:
            payload["name"] = name
        if version_id is not None:
            payload["version_id"] = version_id
        if description is not None:
            payload["description"] = description
        if configuration is not None:
            if isinstance(configuration, dict):
                config_dict = configuration
            elif isinstance(configuration, InstanceConfiguration):
                config_dict = configuration.to_dict()
            else:
                raise TypeError("configuration must be either a dict or InstanceConfiguration object")

            payload["configuration"] = config_dict

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/instances/{id}",
            payload=payload,
        )

        return Instance.from_dict(response.json())
