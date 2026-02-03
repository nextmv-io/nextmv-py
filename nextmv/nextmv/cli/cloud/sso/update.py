"""
This module defines the cloud sso update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_sso_config
from nextmv.cli.message import print_json, success
from nextmv.cli.options import ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    metadata_url: Annotated[
        str | None,
        typer.Option(
            "--metadata-url",
            "-u",
            help="The URL to the SSO metadata document to update.",
            metavar="METADATA_URL",
        ),
    ] = None,
    metadata_document: Annotated[
        str | None,
        typer.Option(
            "--metadata-document",
            "-d",
            help="The SSO metadata document as a string to update.",
            metavar="METADATA_DOCUMENT",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated SSO configuration information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Updates information of a Nextmv Cloud SSO configuration.

    This command allows you to update the metadata URL or metadata document of
    an existing SSO configuration.

    [bold][underline]Examples[/underline][/bold]

    - Update the SSO configuration with a new metadata URL.
        $ [dim]nextmv cloud sso update --metadata-url "https://example.com/metadata.xml"[/dim]

    - Update the SSO configuration with a new metadata document and save the updated information to an
        [magenta]updated_sso_config.json[/magenta] file.
        $ [dim]nextmv cloud sso update --metadata-document "<xml>...</xml>" --output updated_sso_config.json[/dim]
    """

    sso_config = build_sso_config(profile)
    updated_config = sso_config.update(metadata_url=metadata_url, metadata_document=metadata_document)
    success("SSO configuration updated successfully.")
    updated_config_dict = updated_config.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_config_dict, f, indent=2)

        success(msg=f"Updated SSO configuration information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_config_dict)
