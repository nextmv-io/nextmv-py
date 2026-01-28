"""
Application mixin for managing app versions.
"""

from typing import TYPE_CHECKING

import requests

from nextmv.cloud.application._utils import _is_not_exist_error
from nextmv.cloud.version import Version
from nextmv.safe import safe_id

if TYPE_CHECKING:
    from . import Application


class ApplicationVersionMixin:
    """
    Mixin class for managing app versions within an application.
    """

    def delete_version(self: "Application", version_id: str) -> None:
        """
        Delete a version.

        Permanently removes the specified version from the application.

        Parameters
        ----------
        version_id : str
            ID of the version to delete.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> app.delete_version("v1.0.0")  # Permanently deletes the version
        """

        _ = self.client.request(
            method="DELETE",
            endpoint=f"{self.endpoint}/versions/{version_id}",
        )

    def list_versions(self: "Application") -> list[Version]:
        """
        List all versions.

        Returns
        -------
        list[Version]
            List of all versions associated with this application.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> versions = app.list_versions()
        >>> for version in versions:
        ...     print(version.name)
        'v1.0.0'
        'v1.1.0'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions",
        )

        return [Version.from_dict(version) for version in response.json()]

    def new_version(
        self: "Application",
        id: str | None = None,
        name: str | None = None,
        description: str | None = None,
        exist_ok: bool = False,
    ) -> Version:
        """
        Create a new version using the latest pushed executable.

        This method creates a new version of the application using the current development
        binary. Application versions represent different iterations of your application's
        code and configuration that can be deployed.

        Parameters
        ----------
        id : Optional[str], default=None
            ID of the version. If not provided, a unique ID will be generated.
        name : Optional[str], default=None
            Name of the version. If not provided, a name will be generated.
        description : Optional[str], default=None
            Description of the version. If not provided, a description will be generated.
        exist_ok : bool, default=False
            If True and a version with the same ID already exists,
            return the existing version instead of creating a new one.
            If True, the 'id' parameter must be provided.

        Returns
        -------
        Version
            The newly created (or existing) version.

        Raises
        ------
        ValueError
            If exist_ok is True and id is None.
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Create a new version
        >>> version = app.new_version(
        ...     id="v1.0.0",
        ...     name="Initial Release",
        ...     description="First stable version"
        ... )
        >>> print(version.id)
        'v1.0.0'

        >>> # Get or create a version with exist_ok
        >>> version = app.new_version(
        ...     id="v1.0.0",
        ...     exist_ok=True
        ... )
        """

        if exist_ok and (id is None or id == ""):
            raise ValueError("If exist_ok is True, id must be provided")

        if exist_ok and self.version_exists(version_id=id):
            return self.version(version_id=id)

        if id is None or id == "":
            id = safe_id(prefix="version")

        if name is None or name == "":
            name = id

        payload = {
            "id": id,
            "name": name,
        }

        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="POST",
            endpoint=f"{self.endpoint}/versions",
            payload=payload,
        )

        return Version.from_dict(response.json())

    def update_version(
        self: "Application",
        version_id: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Version:
        """
        Update a version.

        This method updates a specific version of the application. It mimics a
        PATCH operation by allowing you to update only the name and/or description
        fields while preserving all other fields.

        Parameters
        ----------
        version_id : str
            ID of the version to update.
        name : Optional[str], default=None
            Optional new name for the version.
        description : Optional[str], default=None
            Optional new description for the version.

        Returns
        -------
        Version
            The updated version object.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Update a version's name
        >>> updated = app.update_version("v1.0.0", name="Version 1.0")
        >>> print(updated.name)
        'Version 1.0'

        >>> # Update a version's description
        >>> updated = app.update_version("v1.0.0", description="Initial release")
        >>> print(updated.description)
        'Initial release'
        """

        version = self.version(version_id=version_id)
        version_dict = version.to_dict()
        payload = version_dict.copy()

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description

        response = self.client.request(
            method="PUT",
            endpoint=f"{self.endpoint}/versions/{version_id}",
            payload=payload,
        )

        return Version.from_dict(response.json())

    def version(self: "Application", version_id: str) -> Version:
        """
        Get a version.

        Retrieves a specific version of the application by its ID. Application versions
        represent different iterations of your application's code and configuration.

        Parameters
        ----------
        version_id : str
            ID of the version to retrieve.

        Returns
        -------
        Version
            The version object containing details about the requested application version.

        Raises
        ------
        requests.HTTPError
            If the response status code is not 2xx.

        Examples
        --------
        >>> # Retrieve a specific version
        >>> version = app.version("v1.0.0")
        >>> print(version.id)
        'v1.0.0'
        >>> print(version.name)
        'Initial Release'
        """

        response = self.client.request(
            method="GET",
            endpoint=f"{self.endpoint}/versions/{version_id}",
        )

        return Version.from_dict(response.json())

    def version_exists(self: "Application", version_id: str) -> bool:
        """
        Check if a version exists.

        This method checks if a specific version of the application exists by
        attempting to retrieve it. It handles HTTP errors for non-existent versions
        and returns a boolean indicating existence.

        Parameters
        ----------
        version_id : str
            ID of the version to check for existence.

        Returns
        -------
        bool
            True if the version exists, False otherwise.

        Raises
        ------
        requests.HTTPError
            If an HTTP error occurs that is not related to the non-existence
            of the version.

        Examples
        --------
        >>> # Check if a version exists
        >>> exists = app.version_exists("v1.0.0")
        >>> if exists:
        ...     print("Version exists!")
        ... else:
        ...     print("Version does not exist.")
        """

        try:
            self.version(version_id=version_id)
            return True
        except requests.HTTPError as e:
            if _is_not_exist_error(e):
                return False
            raise e
