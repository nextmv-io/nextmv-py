"""
This module defines the cloud marketplace version list command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_app
from nextmv.cli.message import in_progress, print_json, success
from nextmv.cli.options import MarketplaceAppIDOption, MarketplacePartnerIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def list(
    app_id: MarketplaceAppIDOption,
    partner_id: MarketplacePartnerIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the version list information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    List all versions of a marketplace application.

    [bold][underline]Examples[/underline][/bold]

    - List all marketplace versions for an application.
        $ [dim]nextmv cloud marketplace version list --partner-id my-partner \\
            --app-id marketplace-hare[/dim]

    - List all versions using the profile named [magenta]hare[/magenta].
        $ [dim]nextmv cloud marketplace version list --partner-id my-partner \\
            --app-id marketplace-hare --profile hare[/dim]

    - List all versions and save the information to a [magenta]versions.json[/magenta] file.
        $ [dim]nextmv cloud marketplace version list --partner-id my-partner \\
            --app-id marketplace-hare --output versions.json[/dim]
    """

    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    in_progress(msg="Listing versions...")
    versions = mkt_app.list_versions()
    versions_dicts = [version.to_dict() for version in versions]

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(versions_dicts, f, indent=2)

        success(msg=f"Version list information saved to [magenta]{output}[/magenta].")

        return

    print_json(versions_dicts)
