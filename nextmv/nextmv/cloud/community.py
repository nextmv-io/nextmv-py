"""
This module contains functionality for working with Nextmv community apps.

Community apps are pre-built decision models. They are maintained in the
following GitHub repository: https://github.com/nextmv-io/community-apps

Classes
-------
CommunityApp
    Representation of a Nextmv Cloud Community App.

Functions
---------
list_community_apps
    List the available Nextmv community apps.
clone_community_app
    Clone a community app locally.
"""

import os
import shutil
import sys
import tarfile
import tempfile
from collections.abc import Callable
from typing import Any

import requests
import rich
import yaml
from pydantic import AliasChoices, Field

from nextmv.base_model import BaseModel
from nextmv.cloud.client import Client
from nextmv.logger import log

# Helpful constants.
LATEST_VERSION = "latest"


class CommunityApp(BaseModel):
    """
    Information about a Nextmv community app.

    You can import the `CommunityApp` class directly from `cloud`:

    ```python
    from nextmv.cloud import CommunityApp
    ```

    Parameters
    ----------
    app_versions : list[str]
        Available versions of the community app.
    description : str
        Description of the community app.
    latest_app_version : str
        The latest version of the community app.
    latest_marketplace_version : str
        The latest version of the community app in the Nextmv Marketplace.
    marketplace_versions : list[str]
        Available versions of the community app in the Nextmv Marketplace.
    name : str
        Name of the community app.
    app_type : str
        Type of the community app.
    """

    description: str
    """Description of the community app."""
    name: str
    """Name of the community app."""
    app_type: str = Field(
        serialization_alias="type",
        validation_alias=AliasChoices("type", "app_type"),
    )
    """Type of the community app."""

    app_versions: list[str] | None = None
    """Available versions of the community app."""
    latest_app_version: str | None = None
    """The latest version of the community app."""
    latest_marketplace_version: str | None = None
    """The latest version of the community app in the Nextmv Marketplace."""
    marketplace_versions: list[str] | None = None
    """Available versions of the community app in the Nextmv Marketplace."""

    def has_version(self, version: str) -> bool:
        """
        Check if the community app has the specified version.

        Parameters
        ----------
        version : str
            The version to check.

        Returns
        -------
        bool
            True if the app has the specified version, False otherwise.
        """

        if version == LATEST_VERSION:
            version = self.latest_app_version

        if self.app_versions is not None and version in self.app_versions:
            return True

        return False


def list_community_apps(client: Client) -> list[CommunityApp]:
    """
    List the available Nextmv community apps.

    You can import the `list_community_apps` function directly from `cloud`:

    ```python
    from nextmv.cloud import list_community_apps
    ```

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.

    Returns
    -------
    list[CommunityApp]
        A list of available community apps.
    """

    manifest = _download_manifest(client)
    dict_apps = manifest.get("apps", [])
    apps = [CommunityApp.from_dict(app) for app in dict_apps]

    return apps


def clone_community_app(
    client: Client,
    app: str,
    directory: str | None = None,
    version: str | None = LATEST_VERSION,
    verbose: bool = False,
    rich_print: bool = False,
) -> None:
    """
    Clone a community app locally.

    By default, the `latest` version will be used. You can
    specify a version with the `version` parameter, and customize the output
    directory with the `directory` parameter. If you want to list the available
    apps, use the `list_community_apps` function.

    You can import the `clone_community_app` function directly from `cloud`:

    ```python
    from nextmv.cloud import clone_community_app
    ```

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    app : str
        The name of the community app to clone.
    directory : str | None, optional
        The directory in which to clone the app. Default is the name of the app at current directory.
    version : str | None, optional
        The version of the community app to clone. Default is `latest`.
    verbose : bool, optional
        Whether to print verbose output.
    rich_print : bool, optional
        Whether to use rich printing for output messages.
    """
    comm_app = _find_app(client, app)

    if version is not None and version == "":
        raise ValueError("`version` cannot be an empty string.")

    if not comm_app.has_version(version):
        raise ValueError(f"Community app '{app}' does not have version '{version}'.")

    original_version = version
    if version == LATEST_VERSION:
        version = comm_app.latest_app_version

    # Clean and normalize directory path in an OS-independent way
    if directory is not None and directory != "":
        destination = os.path.normpath(directory)
    else:
        destination = app

    full_destination = _get_valid_path(destination, os.stat)
    os.makedirs(full_destination, exist_ok=True)

    tarball = f"{app}_{version}.tar.gz"
    s3_file_path = f"{app}/{version}/{tarball}"
    downloaded_object = _download_object(
        client=client,
        file=s3_file_path,
        path="community-apps",
        output_dir=full_destination,
        output_file=tarball,
    )

    # Extract the tarball to a temporary directory to handle nested structure
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(downloaded_object, "r:gz") as tar:
            tar.extractall(path=temp_dir)

        # Find the extracted directory (typically the app name)
        extracted_items = os.listdir(temp_dir)
        if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
            # Move contents from the extracted directory to full_destination
            extracted_dir = os.path.join(temp_dir, extracted_items[0])
            for item in os.listdir(extracted_dir):
                shutil.move(os.path.join(extracted_dir, item), full_destination)
        else:
            # If structure is unexpected, move everything directly
            for item in extracted_items:
                shutil.move(os.path.join(temp_dir, item), full_destination)

    # Remove the tarball after extraction
    os.remove(downloaded_object)

    if not verbose:
        return

    if rich_print:
        rich.print(
            f":white_check_mark: Successfully cloned the [magenta]{app}[/magenta] community app, "
            f"using version [magenta]{original_version}[/magenta] in path: [magenta]{full_destination}[/magenta].",
            file=sys.stderr,
        )
        return

    log(
        f"✅ Successfully cloned the {app} community app, using version {original_version} in path: {full_destination}."
    )


def _download_manifest(client: Client) -> dict[str, Any]:
    """
    Downloads and returns the community apps manifest.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.

    Returns
    -------
    dict[str, Any]
        The community apps manifest as a dictionary.

    Raises
    requests.HTTPError
        If the response status code is not 2xx.
    """

    response = _download_file(client=client, directory="community-apps", file="manifest.yml")
    manifest = yaml.safe_load(response.text)

    return manifest


def _download_file(
    client: Client,
    directory: str,
    file: str,
) -> requests.Response:
    """
    Gets a file from an internal bucket and return it.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    directory : str
        The directory in the bucket where the file is located.
    file : str
        The name of the file to download.

    Returns
    -------
    requests.Response
        The response object containing the file data.

    Raises
    requests.HTTPError
        If the response status code is not 2xx.
    """

    # Request the download URL for the file.
    response = client.request(
        method="GET",
        endpoint="v0/internal/tools",
        headers=client.headers | {"request-source": "cli"},  # Pass `client.headers` to preserve auth.
        query_params={"file": f"{directory}/{file}"},
    )

    # Use the URL obtained to download the file.
    body = response.json()
    download_response = client.request(
        method="GET",
        endpoint=body.get("url"),
        headers={"Content-Type": "application/json"},
    )

    return download_response


def _download_object(client: Client, file: str, path: str, output_dir: str, output_file: str) -> str:
    """
    Downloads an object from the internal bucket and saves it to the specified
    output directory.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    file : str
        The name of the file to download.
    path : str
        The directory in the bucket where the file is located.
    output_dir : str
        The local directory where the file will be saved.
    output_file : str
        The name of the output file.

    Returns
    -------
    str
        The path to the downloaded file.
    """

    response = _download_file(client=client, directory=path, file=file)
    file_name = os.path.join(output_dir, output_file)

    with open(file_name, "wb") as f:
        f.write(response.content)

    return file_name


def _get_valid_path(path: str, stat_fn: Callable[[str], os.stat_result], ending: str = "") -> str:
    """
    Validates and returns a non-existing path. If the path exists,
    it will append a number to the path and return it. If the path does not
    exist, it will return the path as is.

    The ending parameter is used to check if the path ends with a specific
    string. This is useful to specify if it is a file (like foo.json, in which
    case the next iteration is foo-1.json) or a directory (like foo, in which
    case the next iteration is foo-1).

    Parameters
    ----------
    path : str
        The initial path to validate.
    stat_fn : Callable[[str], os.stat_result]
        A function that takes a path and returns its stat result.
    ending : str, optional
        The expected ending of the path (e.g., file extension), by default "".

    Returns
    -------
    str
        A valid, non-existing path.

    Raises
    ------
    RuntimeError
        If an unexpected error occurs during path validation
    """
    base_name = os.path.basename(path)
    name_without_ending = base_name.removesuffix(ending) if ending else base_name

    while True:
        try:
            stat_fn(path)
            # If we get here, the path exists
            # Get folder/file name number, increase it and create new path
            name = os.path.basename(path)

            # Get folder/file name number
            parts = name.split("-")
            last = parts[-1].removesuffix(ending) if ending else parts[-1]

            # Save last folder name index to be changed
            i = path.rfind(name)

            try:
                num = int(last)
                # Increase number and create new path
                if ending:
                    temp_path = path[:i] + f"{name_without_ending}-{num + 1}{ending}"
                else:
                    temp_path = path[:i] + f"{base_name}-{num + 1}"
                path = temp_path
            except ValueError:
                # If there is no number, add it
                if ending:
                    temp_path = path[:i] + f"{name_without_ending}-1{ending}"
                else:
                    temp_path = path[:i] + f"{name}-1"
                path = temp_path

        except FileNotFoundError:
            # Path doesn't exist, we can use it
            return path
        except Exception as e:
            # Re-raise unexpected errors
            raise RuntimeError(f"An unexpected error occurred while validating the path: {path} ") from e


def _find_app(client: Client, app: str) -> CommunityApp:
    """
    Finds and returns a community app from the manifest by its name.

    Parameters
    ----------
    client : Client
        The Nextmv Cloud client to use for the request.
    app : str
        The name of the community app to find.

    Returns
    -------
    CommunityApp
        The community app if found.

    Raises
    ------
    ValueError
        If the community app is not found.
    """

    comm_apps = list_community_apps(client)
    for comm_app in comm_apps:
        if comm_app.name == app:
            return comm_app

    raise ValueError(f"Community app '{app}' not found.")
