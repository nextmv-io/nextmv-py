"""
Local app registry for app interactions.

This module provides functionality for interacting with the local registry of Nextmv
applications. The registry allows users to manage applications they have created locally
on their machine.

Classes
-------
LocalRegistry
    A class to interact with the local Nextmv application registry.

Functions
---------
read_local_registry
    Retrieve an instance of the LocalRegistry.
add_registry_entry
    Store a new entry in the local app registry.
delete_registry_entry
    Remove an entry from the local app registry.
create_app_from_registry_entry
    Create a Nextmv application instance from a registry entry.
"""

import os
import pathlib

import yaml

from nextmv.base_model import BaseModel
from nextmv.local.local import NEXTMV_DIR, REGISTRY_FILE


class AppEntry(BaseModel):
    """
    Represents an entry in the local app registry.

    You can import the `RegistryEntry` class directly from `local`:

    ```python
    from nextmv.local import RegistryEntry
    ```

    This class contains information about a Nextmv application on the local machine.

    Attributes
    ----------
    app_id : str
        The unique identifier of the application.
    path : str
        The file system path where the application is located.
    """

    app_id: str
    """
    The unique identifier of the application.
    """
    path: str
    """
    The file system path where the application is located.
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
    apps : list[RegistryEntry]
        A list of locally registered Nextmv applications.
    """

    apps: list[AppEntry]
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

        >>> from nextmv import Registry
        >>> # registry = Registry.from_yaml()  # This would load the registry from the YAML file
        >>> # assert isinstance(registry, Registry)
        """
        reg_path = get_registry_path()

        # If no registry file exists yet, create an empty registry.
        if not os.path.exists(reg_path):
            empty_registry = cls(apps=[])
            empty_registry.to_yaml()
            return empty_registry

        # Load and parse the YAML file.
        with open(reg_path) as file:
            raw_manifest = yaml.safe_load(file)
        return cls.from_dict(raw_manifest)

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
        >>> from nextmv import Registry
        >>> registry = Registry(apps=[])
        >>> # registry.to_yaml()  # This would write the registry to the YAML file
        """

        with open(get_registry_path(), "w") as file:
            yaml.dump(
                self.to_dict(),
                file,
                sort_keys=False,
                default_flow_style=False,
                indent=2,
                width=120,
            )


def get_registry_path() -> str:
    """
    Returns the path to the local registry file.

    Returns
    -------
    str
        The path to the local registry file.
    """
    home_dir = str(pathlib.Path.home())
    nextmv_dir = os.path.join(home_dir, NEXTMV_DIR)
    os.makedirs(nextmv_dir, exist_ok=True)
    registry_path = os.path.join(nextmv_dir, REGISTRY_FILE)
    return registry_path


def read_local_registry() -> Registry:
    """
    Retrieve an instance of the LocalRegistry.

    Returns
    -------
    Registry
        The local app registry.
    """
    return Registry.from_yaml()


def add_registry_entry(entry: AppEntry) -> None:
    """
    Store a new entry in the local app registry.

    Parameters
    ----------
    entry : RegistryEntry
        The registry entry to add.
    """
    registry = Registry.from_yaml()
    if any(app.app_id == entry.app_id for app in registry.apps):
        # Ignore duplicate entries.
        return
    registry.apps.append(entry)
    registry.to_yaml()


def delete_registry_entry(app_id: str) -> None:
    """
    Remove an entry from the local app registry.

    Parameters
    ----------
    app_id : str
        The ID of the application to remove from the registry.
    """
    registry = Registry.from_yaml()
    registry.apps = [entry for entry in registry.apps if entry.app_id != app_id]
    registry.to_yaml()
