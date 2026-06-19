"""
This module defines the manifest init command for the Nextmv CLI.
"""

from typing import Annotated

import questionary
import typer

from nextmv.cli.message import choice, confirmation, directory_path, enum_values, error, parse_content_format, success
from nextmv.cli.options import DebugOption
from nextmv.content_format import ContentFormat
from nextmv.input import InputFormat
from nextmv.manifest import ManifestType, initialize_manifest

# Set up subcommand application.
app = typer.Typer()


@app.command()
def init(
    content_format: Annotated[
        InputFormat | None,  # Keep deprecated type for backwards compatibility, translated in the code.
        typer.Option(
            "--content-format",
            "-c",
            help=f"The content format of the manifest. Allowed values are: {enum_values(ContentFormat)}. "
            "Useful for non-interactive sessions.",
            metavar="CONTENT_FORMAT",
        ),
    ] = None,
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
    options_yes: Annotated[
        bool | None,
        typer.Option(
            "--options-yes",
            "-y",
            help="Add options (parameters) to the manifest. Useful for non-interactive sessions.",
        ),
    ] = None,
    options_no: Annotated[
        bool | None,
        typer.Option(
            "--options-no",
            "-n",
            help="Do not add options (parameters) to the manifest. Useful for non-interactive sessions.",
        ),
    ] = None,
    _: DebugOption = False,
) -> None:
    """
    Initialize an [magenta]app.yaml[/magenta] (app manifest) file.

    Creates a sample [magenta]app.yaml[/magenta] manifest file by prompting the
    user to provide certain information. You can use --content-format,
    --dirpath, --type, --options-yes, and --options-no to skip the prompts. If
    the directory does not exist, it will be created. If a manifest file
    already exists in the directory, it will be overwritten.

    [bold][underline]Examples[/underline][/bold]

    - Initialize a Python manifest in the current directory.

        $ [dim]nextmv manifest init[/dim]

    - Initialize a [magenta]json[/magenta] Go manifest in the [magenta]./my-app[/magenta] directory.

        $ [dim]nextmv manifest init --type go --content-format json --dirpath ./my-app[/dim]

    - Initialize a [magenta]multi-file[/magenta] Java manifest in the [magenta]./my-app[/magenta] directory.

        $ [dim]nextmv manifest init --type java --content-format multi-file --dirpath ./my-app[/dim]
    """

    if options_yes is not None and options_no is not None:
        error("Cannot specify both --options-yes and --options-no. Please choose one.")

    content_format = parse_content_format(content_format)

    if manifest_type is None or manifest_type == "":
        manifest_type = choice(
            msg="What is the type (language) of your Nextmv app?",
            choices=[member.value for member in ManifestType],
            default=ManifestType.PYTHON.value,
        )
        manifest_type = ManifestType(manifest_type)

    if content_format is None or content_format == "":
        choices = [None] * len(ContentFormat)
        for ix, member in enumerate(ContentFormat):
            choices[ix] = questionary.Choice(
                title=member.value,
                description=member.description,
            )

        content_format = choice(
            msg="What is the I/O (input/output) content format of your Nextmv app?",
            choices=choices,
            default=ContentFormat.JSON.value,
        )
        content_format = ContentFormat(content_format)

    if dirpath is None or dirpath == "":
        dirpath = directory_path(
            msg="In which directory would you like to initialize the manifest?",
            default=".",
        )
        dirpath = dirpath or "."

    if options_yes is None and options_no is None:
        with_options = confirmation(
            msg="Would you like to add options (parameters) to your manifest?",
            default=True,
        )
    else:
        with_options = options_yes is not None

    dst = initialize_manifest(
        manifest_type=manifest_type,
        content_format=content_format,
        dirpath=dirpath,
        with_options=with_options,
    )

    msg = (
        f"[magenta]{manifest_type.value}[/magenta], [magenta]{content_format.value}[/magenta] manifest "
        f"initialized at [magenta]{dst}[/magenta]"
    )
    if with_options:
        msg += ", [italic]with[/italic] options."
    else:
        msg += ", [italic]without[/italic] options."

    success(msg)
