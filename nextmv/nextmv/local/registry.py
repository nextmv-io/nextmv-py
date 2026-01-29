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
from dataclasses import dataclass

import yaml

from nextmv.base_model import BaseModel
from nextmv.local.local import NEXTMV_DIR, REGISTRY_FILE


@dataclass
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


@dataclass
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


def _load_registry() -> Registry:
    """
    Loads the local registry from the config directory.

    Returns
    -------
    Registry
        The local app registry.
    """
    reg_path = get_registry_path()
    if not os.path.exists(reg_path):
        return Registry(apps=[])

    with open(reg_path) as f:
        data = yaml.safe_load(f)

    if data is None:
        return Registry(apps=[])
    return data


def _save_registry(registry: Registry) -> None:
    """
    Saves the local registry to the config directory.

    Parameters
    ----------
    registry : Registry
        The local app registry to save.
    """
    reg_path = get_registry_path()
    with open(reg_path, "w") as f:
        yaml.safe_dump(registry, f)


def read_local_registry() -> Registry:
    """
    Retrieve an instance of the LocalRegistry.

    Returns
    -------
    Registry
        The local app registry.
    """
    return _load_registry()


def add_registry_entry(entry: AppEntry) -> None:
    """
    Store a new entry in the local app registry.

    Parameters
    ----------
    entry : RegistryEntry
        The registry entry to add.
    """
    registry = _load_registry()
    if any(app.app_id == entry.app_id for app in registry.apps):
        # Ignore duplicate entries.
        return
    registry.apps.append(entry)
    _save_registry(registry)


def delete_registry_entry(app_id: str) -> None:
    """
    Remove an entry from the local app registry.

    Parameters
    ----------
    app_id : str
        The ID of the application to remove from the registry.
    """
    registry = _load_registry()
    registry.apps = [entry for entry in registry.apps if entry.app_id != app_id]
    _save_registry(registry)
