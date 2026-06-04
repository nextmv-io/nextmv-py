"""
This module defines the cloud marketplace version get command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import (
    DebugOption,
    MarketplaceAppIDOption,
    MarketplacePartnerIDOption,
    MarketplaceVersionIDOption,
    ProfileOption,
)

# Set up subcommand application.
app = typer.Typer()


@app.command()
def get(
    app_id: MarketplaceAppIDOption,
    partner_id: MarketplacePartnerIDOption,
    version_id: MarketplaceVersionIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the version information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Get a marketplace version for an application.

    [bold][underline]Examples[/underline][/bold]

    - Get the marketplace version with the ID [magenta]mkt-v1[/magenta].
        $ [dim]nextmv cloud marketplace version get --partner-id my-partner \\
            --app-id marketplace-hare --version-id mkt-v1[/dim]

    - Get the marketplace version and save the information to a [magenta]version.json[/magenta] file.
        $ [dim]nextmv cloud marketplace version get --partner-id my-partner \\
            --app-id marketplace-hare --version-id mkt-v1 --output version.json[/dim]
    """

    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    in_progress(msg="Getting version...")
    version = mkt_app.version(version_id=version_id)
    version_dict = version.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(version_dict, f, indent=2)

        success(msg=f"Version information saved to [magenta]{output}[/magenta].")

        return

    print_json(version_dict)
