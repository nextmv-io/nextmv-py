"""
This module defines the local manifest init command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.message import choice, directory_path, enum_values, success
from nextmv.manifest import ManifestType, initialize_manifest

_SUPPORTED_TYPES = [ManifestType.PYTHON, ManifestType.GO, ManifestType.JAVA]

# Set up subcommand application.
app = typer.Typer()


@app.command()
def init(
    dirpath: Annotated[
        str | None,
        typer.Option(
            "--dirpath",
            "-d",
            help="The directory path where the manifest file will be initialized. Useful for non-interactive sessions.",
            metavar="DIRPATH",
        ),
    ] = None,
    manifest_type: Annotated[
        ManifestType | None,
        typer.Option(
            "--type",
            "-t",
            help=f"The type of manifest to initialize. Allowed values are: {enum_values(ManifestType)}. "
            "Useful for non-interactive sessions.",
            metavar="TYPE",
        ),
    ] = None,
) -> None:
    """
    Initialize an [magenta]app.yaml[/magenta] (app manifest) file.

    Creates a sample [magenta]app.yaml[/magenta] manifest file by prompting the
    user to provide the type and directory path. You can use the --dirpath and
    --type options to skip the prompts. If the directory does not exist, it
    will be created. If a manifest file already exists in the directory, it
    will be overwritten.

    [bold][underline]Examples[/underline][/bold]

    - Initialize a Python manifest in the current directory.
        $ [dim]nextmv local manifest init[/dim]

    - Initialize a Go manifest in the [magenta]./my-app[/magenta] directory.
        $ [dim]nextmv local manifest init --type go --dirpath ./my-app[/dim]

    - Initialize a Java manifest in the [magenta]./my-app[/magenta] directory.
        $ [dim]nextmv local manifest init --type java --dirpath ./my-app[/dim]
    """

    if manifest_type is None or manifest_type == "":
        manifest_type = choice(
            msg="What is the type of your Nextmv app?",
            choices=[member.value for member in ManifestType],
            default=ManifestType.PYTHON.value,
        )
        manifest_type = ManifestType(manifest_type)

    if dirpath is None or dirpath == "":
        dirpath = directory_path(
            msg="In which directory would you like to init the manifest?",
            default=".",
        )
        print("This is the directory where the manifest file will be initialized:", dirpath)
        dirpath = dirpath or "."

    dst = initialize_manifest(manifest_type=manifest_type, dirpath=dirpath)
    success(f"Manifest of type [magenta]{manifest_type.value}[/magenta] initialized at [magenta]{dst}[/magenta].")
