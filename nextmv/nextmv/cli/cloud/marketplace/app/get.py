"""
This module defines the cloud marketplace app get command for the Nextmv CLI.
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
def get(
    app_id: MarketplaceAppIDOption,
    partner_id: MarketplacePartnerIDOption,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the app information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Get a Nextmv Marketplace application.


    [bold][underline]Examples[/underline][/bold]

    - Get the marketplace application with the ID [magenta]marketplace-hare[/magenta].
        $ [dim]nextmv cloud marketplace app get --partner-id my-partner \\
            --app-id marketplace-hare[/dim]

    - Get the marketplace application and save the information to an [magenta]app.json[/magenta] file.
        $ [dim]nextmv cloud marketplace app get --partner-id my-partner \\
            --app-id marketplace-hare --output app.json[/dim]
    """

    in_progress(msg="Getting application...")
    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    mkt_app_dict = mkt_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(mkt_app_dict, f, indent=2)

        success(msg=f"Application information saved to [magenta]{output}[/magenta].")

        return

    print_json(mkt_app_dict)
