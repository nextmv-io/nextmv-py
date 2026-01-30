"""
This module defines the community clone command for the Nextmv CLI.
"""

import os
import shutil
import tarfile
import tempfile
from collections.abc import Callable
from typing import Annotated

import rich
import typer

from nextmv.cli.community.list import download_file, download_manifest, find_app, versions_table
from nextmv.cli.message import error, success
from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()

# Helpful constants.
LATEST_VERSION = "latest"


@app.command()
def clone(
    app: Annotated[
        str,
        typer.Option("--app", "-a", help="The name of the community app to clone.", metavar="COMMUNITY_APP"),
    ],
    directory: Annotated[
        str | None,
        typer.Option(
            "--directory",
            "-d",
            help="The directory in which to clone the app. Default is the name of the app at current directory.",
            metavar="DIRECTORY",
        ),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option(
            "--version",
            "-v",
            help="The version of the community app to clone.",
            metavar="VERSION",
        ),
    ] = LATEST_VERSION,
    profile: ProfileOption = None,
) -> None:
    """
    Clone a community app locally.

    By default, the [magenta]latest[/magenta] version will be used. You can
    specify a version with the --version flag, and customize the output
    directory with the --directory flag. If you want to list the available
    apps, use the [code]nextmv community list[/code] command.

    [bold][underline]Examples[/underline][/bold]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using the [magenta]latest[/magenta] version.
        $ [dim]nextmv community clone --app go-nextroute[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app under the
      [magenta]"~/sample/my_app"[/magenta] directory, using the [magenta]latest[/magenta] version.
        $ [dim]nextmv community clone --app go-nextroute --directory ~/sample/my_app[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using version [magenta]v1.2.0[/magenta].
        $ [dim]nextmv community clone --app go-nextroute --version v1.2.0[/dim]

    - Clone the [magenta]go-nextroute[/magenta] community app (under the
      [magenta]"go-nextroute"[/magenta] directory), using the [magenta]latest[/magenta] version
      and a profile named [magenta]hare[/magenta].
        $ [dim]nextmv community clone --app go-nextroute --profile hare[/dim]
    """

    manifest = download_manifest(profile=profile)
    app_obj = find_app(manifest, app)

    if version is not None and version == "":
        error("The --version flag cannot be an empty string.")

    if not app_has_version(app_obj, version):
        # We don't use error() here to allow printing something before exiting.
        rich.print(
            f"[red]Error:[/red] Version [magenta]{version}[/magenta] not found "
            f"for community app [magenta]{app}[/magenta]. Available versions are:"
        )
        versions_table(manifest, app)

        raise typer.Exit(code=1)

    original_version = version
    if version == LATEST_VERSION:
        version = app_obj.get("latest_app_version")

    # Clean and normalize directory path in an OS-independent way
    if directory is not None and directory != "":
        destination = os.path.normpath(directory)
    else:
        destination = app

    full_destination = get_valid_path(destination, os.stat)
    os.makedirs(full_destination, exist_ok=True)

    tarball = f"{app}_{version}.tar.gz"
    s3_file_path = f"{app}/{version}/{tarball}"
    downloaded_object = download_object(
        file=s3_file_path,
        path="community-apps",
        output_dir=full_destination,
        output_file=tarball,
        profile=profile,
    )

    # Extract the tarball to a temporary directory to handle nested structure
    with tempfile.TemporaryDirectory() as temp_dir:
        with tarfile.open(downloaded_object, "r:gz") as tar:
            tar.extractall(path=temp_dir, filter=None)

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

    success(
        f"Successfully cloned the [magenta]{app}[/magenta] community app, "
        f"using version [magenta]{original_version}[/magenta] in path: [magenta]{full_destination}[/magenta]."
    )


def app_has_version(app_obj: dict, version: str) -> bool:
    """
    Check if the given app object has the specified version.

    Parameters
    ----------
    app_obj : dict
        The community app object.
    version : str
        The version to check.

    Returns
    -------
    bool
        True if the app has the specified version, False otherwise.
    """

    if version == LATEST_VERSION:
        version = app_obj.get("latest_app_version")

    if version in app_obj.get("app_versions", []):
        return True

    return False


def get_valid_path(path: str, stat_fn: Callable[[str], os.stat_result], ending: str = "") -> str:
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
    Exception
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
        except Exception:
            # Re-raise unexpected errors
            error(f"An unexpected error occurred while validating the path: {path}")


def download_object(file: str, path: str, output_dir: str, output_file: str, profile: str | None = None) -> str:
    """
    Downloads an object from the internal bucket and saves it to the specified
    output directory.

    Parameters
    ----------
    file : str
        The name of the file to download.
    path : str
        The directory in the bucket where the file is located.
    output_dir : str
        The local directory where the file will be saved.
    output_file : str
        The name of the output file.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    str
        The path to the downloaded file.
    """

    response = download_file(directory=path, file=file, profile=profile)
    file_name = os.path.join(output_dir, output_file)

    with open(file_name, "wb") as f:
        f.write(response.content)

    return file_name
    return file_name
