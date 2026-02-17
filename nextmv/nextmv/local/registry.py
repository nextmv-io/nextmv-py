"""
Local app registry for app interactions.

This module provides functionality for interacting with the local registry of Nextmv
applications. The registry allows users to manage applications they have created locally
on their machine.

Classes
-------
AppEntry
    Represents an entry in the local app registry.
Registry
    Represents the local app registry and provides methods for managing registry entries.
"""

import os
import pathlib
from datetime import datetime, timezone

import yaml
from pydantic import Field

from nextmv.base_model import BaseModel
from nextmv.input import InputFormat
from nextmv.local.local import NEXTMV_DIR, REGISTRY_FILE
from nextmv.manifest import Manifest
from nextmv.safe import safe_id


class AppEntry(BaseModel):
    """
    Represents an entry in the local app registry.

    You can import the `AppEntry` class directly from `local`:

    ```python
    from nextmv.local import AppEntry
    ```

    This class contains information about a Nextmv application on the local machine.

    Attributes
    ----------
    app_id : str
        The unique identifier of the application.
    src : str
        The file system path where the application is located.
    content_format : InputFormat
        The content format of the application, which is determined by the manifest.
    created_at : datetime
        The timestamp when the application was registered in the local registry.
    updated_at : datetime
        The timestamp when the application entry was last updated in the local registry.
    description : str | None
        An optional description of the application.
    """

    app_id: str
    """
    The unique identifier of the application.
    """
    src: str
    """
    The file system path where the application is located.
    """
    content_format: InputFormat
    """
    The content format of the application, which is determined by the manifest.
    """
    created_at: datetime
    """
    The timestamp when the application was registered in the local registry.
    """
    updated_at: datetime
    """
    The timestamp when the application entry was last updated in the local registry.
    """
    description: str | None = None
    """
    An optional description of the application.
    """


class Registry(BaseModel):
    """
    Represents the local app registry.

    You can import the `Registry` class directly from `local`:

    ```python
    from nextmv.local import Registry
    ```

    This class contains a list of local Nextmv applications registered on the machine.

    Attributes
    ----------
    apps : list[AppEntry]
        A list of locally registered Nextmv applications.
    """

    apps: list[AppEntry] = Field(default_factory=list)
    """
    A list of locally registered Nextmv applications.
    """

    @classmethod
    def from_yaml(cls) -> "Registry":
        """
        Load a Registry from a YAML file.

        The YAML file is expected to be located at `$HOME/.nextmv/registry.yaml`.

        Returns
        -------
        Registry
            The loaded registry.

        Raises
        ------
        FileNotFoundError
            If the `registry.yaml` file is not found in the expected location.
        yaml.YAMLError
            If there is an error parsing the YAML file.

        Examples
        --------
        Assuming an `registry.yaml` file exists in `$HOME/.nextmv/` with the following content:

        ```yaml
        apps:
          - app_id: "app-123"
        ```

        >>> from nextmv.local import Registry
        >>> # registry = Registry.from_yaml()  # This would load the registry from the YAML file
        >>> # assert isinstance(registry, Registry)
        """

        reg_path = _get_registry_path()

        # If no registry file exists yet, create an empty registry.
        if not os.path.exists(reg_path):
            empty_registry = cls(apps=[])
            empty_registry.to_yaml()
            return empty_registry

        # Load and parse the YAML file.
        with open(reg_path) as file:
            raw_registry = yaml.safe_load(file)

        # If the file is empty or does not contain the expected structure,
        # return an empty registry.
        if raw_registry is None:
            empty_registry = cls(apps=[])
            empty_registry.to_yaml()
            return empty_registry

        return cls.from_dict(raw_registry)

    def delete_entry(self, app_id: str | None = None, src: str | None = None) -> None:
        """
        Remove an entry from the local app registry.

        Specify either the `app_id` or the `src` to identify the entry to
        delete. If both are provided, both criteria must match to ensure
        registry consistency.

        Parameters
        ----------
        app_id : str | None
            The ID of the application to remove from the registry.
        src : str | None
            The source path of the application to remove from the registry.

        Examples
        --------
        >>> from nextmv.local import Registry
        >>> registry = Registry.from_yaml()
        >>> # Delete by app_id
        >>> registry.delete_entry(app_id="my-app")
        >>> # Delete by source path
        >>> registry.delete_entry(src="/path/to/app")
        """

        to_delete = self.entry(app_id=app_id, src=src)

        if to_delete is None:
            # No entry found, nothing to delete
            return

        # Remove the entry by matching both app_id and src
        apps = []
        for entry in self.apps:
            should_delete = entry.app_id == to_delete.app_id and entry.src == to_delete.src
            if not should_delete:
                apps.append(entry)

        self.apps = apps
        self.to_yaml()

    def entry(self, app_id: str | None = None, src: str | None = None) -> AppEntry | None:
        """
        Find an entry in the local app registry.

        Specify either the `app_id` or the `src` to identify the entry to
        find. If both are provided, both criteria must match to ensure
        registry consistency.

        Parameters
        ----------
        app_id : str | None
            The ID of the application to find in the registry.
        src : str | None
            The source path of the application to find in the registry.

        Returns
        -------
        AppEntry | None
            The found registry entry, or `None` if no matching entry is found.

        Examples
        --------
        >>> from nextmv.local import Registry
        >>> registry = Registry.from_yaml()
        >>> # Find by app_id
        >>> entry = registry.entry(app_id="my-app")
        >>> # Find by source path
        >>> entry = registry.entry(src="/path/to/app")
        """

        # Normalize src to absolute path if provided
        normalized_src = None
        if src is not None and src != "":
            normalized_src = os.path.abspath(src)

        # Determine which criteria are provided
        has_app_id = app_id is not None and app_id != ""
        has_src = normalized_src is not None

        for entry in self.apps:
            # If both criteria are provided, require both to match
            if has_app_id and has_src:
                if entry.app_id == app_id and entry.src == normalized_src:
                    return entry

            # If only app_id is provided, match by app_id
            elif has_app_id and entry.app_id == app_id:
                return entry

            # If only src is provided, match by src
            elif has_src and entry.src == normalized_src:
                return entry

        return None

    def list_entries(self) -> list[AppEntry]:
        """
        List all entries in the local app registry.

        Returns
        -------
        list[AppEntry]
            A list of all registry entries.

        Examples
        --------
        >>> from nextmv.local import Registry
        >>> registry = Registry.from_yaml()
        >>> entries = registry.list_entries()
        >>> for entry in entries:
        ...     print(entry.app_id)
        """

        return self.apps

    def register(self, src: str, app_id: str | None = None, description: str | None = None) -> AppEntry:
        """
        Store a new entry in the local app registry.

        Parameters
        ----------
        src : str
            The file system path where the application is located. This path
            should point to a dir containing a valid Nextmv application manifest.
        app_id : str | None
            An optional unique identifier for the application. If not provided, a safe ID will be generated.
        description : str | None
            An optional description of the application.

        Returns
        -------
        AppEntry
            The newly created registry entry.

        Raises
        ------
        FileNotFoundError
            If no manifest file is found at the specified source path.

        Examples
        --------
        >>> from nextmv.local import Registry
        >>> registry = Registry.from_yaml()
        >>> # Register with auto-generated ID
        >>> entry = registry.register(src="/path/to/app")
        >>> # Register with custom ID and description
        >>> entry = registry.register(src="/path/to/app", app_id="my-app", description="My application")
        """

        # Normalize src to absolute path
        src = os.path.abspath(src)

        try:
            manifest = Manifest.from_yaml(src)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Registering a local app requires a manifest, which was not found at path: `{src}`"
            ) from e

        if app_id is None or app_id == "":
            app_id = safe_id("local-app")

        content_format = InputFormat.JSON
        if manifest.configuration is not None and manifest.configuration.content is not None:
            content_format = manifest.configuration.content.format

        created_at = datetime.now(timezone.utc)

        entry = AppEntry(
            app_id=app_id,
            src=src,
            content_format=content_format,
            created_at=created_at,
            updated_at=created_at,
            description=description,
        )

        if self.entry(app_id=entry.app_id, src=entry.src) is not None:
            # Ignore duplicate entries.
            return entry

        self.apps.append(entry)
        self.to_yaml()

        return entry

    def to_yaml(self) -> None:
        """
        Write the registry to a YAML file.

        The registry will be written to `$HOME/.nextmv/registry.yaml`.

        Raises
        ------
        IOError
            If there is an error writing the file.
        yaml.YAMLError
            If there is an error serializing the registry to YAML.

        Examples
        --------
        >>> from nextmv.local import Registry
        >>> registry = Registry(apps=[])
        >>> # registry.to_yaml()  # This would write the registry to the YAML file
        """

        with open(_get_registry_path(), "w") as file:
            yaml.dump(
                self.to_dict(),
                file,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
                width=120,
            )

    def update_entry(self, new: AppEntry) -> None:
        """
        Update an existing entry in the local app registry.

        The entry to update is identified by matching both the `app_id` and `src`
        of the provided `new` entry to ensure registry consistency. If no matching
        entry is found, the method will not make any changes.

        Parameters
        ----------
        new : AppEntry
            The new registry entry with updated information. Both the `app_id` and
            `src` of this entry must match an existing entry for it to be updated.

        Examples
        --------
        >>> from nextmv.local import Registry, AppEntry
        >>> from datetime import datetime, timezone
        >>> registry = Registry.from_yaml()
        >>> # Get existing entry and update it
        >>> entry = registry.entry(app_id="my-app")
        >>> if entry:
        ...     entry.description = "Updated description"
        ...     registry.update_entry(entry)
        """

        existing = self.entry(app_id=new.app_id, src=new.src)

        if existing is None:
            # No entry found, nothing to update
            return

        # Replace the existing entry with the new one
        apps = []
        for entry in self.apps:
            should_update = entry.app_id == existing.app_id and entry.src == existing.src
            if should_update:
                updated_at = datetime.now(timezone.utc)
                new.updated_at = updated_at
                apps.append(new)
                continue

            apps.append(entry)

        self.apps = apps
        self.to_yaml()


def _get_registry_path() -> str:
    """
    Get the path to the local registry file.

    This is a private helper function that constructs the path to the registry
    file located at `$HOME/.nextmv/registry.yaml`. It ensures the parent directory
    exists before returning the path.

    Returns
    -------
    str
        The absolute path to the local registry file.
    """
    home_dir = str(pathlib.Path.home())
    nextmv_dir = os.path.join(home_dir, NEXTMV_DIR)
    os.makedirs(nextmv_dir, exist_ok=True)
    registry_path = os.path.join(nextmv_dir, REGISTRY_FILE)
    return registry_path
