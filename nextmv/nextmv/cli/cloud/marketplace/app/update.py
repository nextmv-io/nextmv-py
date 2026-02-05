"""
This module defines the cloud marketplace app update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_app
from nextmv.cli.message import enum_values, in_progress, print_json, success
from nextmv.cli.options import MarketplaceAppIDOption, MarketplacePartnerIDOption, ProfileOption
from nextmv.cloud.marketplace import MarketplaceState

# Set up subcommand application.
app = typer.Typer()


@app.command()
def update(
    app_id: MarketplaceAppIDOption,
    partner_id: MarketplacePartnerIDOption,
    categories: Annotated[
        list[str] | None,
        typer.Option(
            "--categories",
            "-c",
            help="Optional categories for the application. Pass multiple categories by repeating the flag.",
            metavar="CATEGORIES",
        ),
    ] = None,
    description: Annotated[
        str | None,
        typer.Option(
            "--description",
            "-d",
            help="An optional description for the application.",
            metavar="DESCRIPTION",
        ),
    ] = None,
    features: Annotated[
        list[str] | None,
        typer.Option(
            "--features",
            "-f",
            help="Optional features for the application. Pass multiple features by repeating the flag.",
            metavar="FEATURES",
        ),
    ] = None,
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the app information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    state: Annotated[
        MarketplaceState | None,
        typer.Option(
            "--state",
            "-s",
            help=f"The state of the application. Allowed values are: {enum_values(MarketplaceState)}.",
            metavar="STATE",
        ),
    ] = None,
    title: Annotated[
        str | None,
        typer.Option(
            "--title",
            "-t",
            help="The title of the application to create.",
            metavar="TITLE",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Update a Nextmv Marketplace application.

    This command allows you to update the attributes of an existing marketplace
    application, including its title, description, categories, features, and
    state. Only the fields you specify will be updated; all other fields will
    remain unchanged.

    [bold][underline]Examples[/underline][/bold]

    - Update the title of a marketplace application.
        $ [dim]nextmv cloud marketplace app update --partner-id my-partner \\
            --app-id marketplace-hare --title "Advanced Hare Routing"[/dim]

    - Update the description of a marketplace application.
        $ [dim]nextmv cloud marketplace app update --partner-id my-partner \\
            --app-id marketplace-hare --description "Enterprise-grade routing solution"[/dim]

    - Update categories and features.
        $ [dim]nextmv cloud marketplace app update --partner-id my-partner \\
            --app-id marketplace-hare --categories routing --categories logistics \\
            --features "real-time optimization"[/dim]

    - Update the state of a marketplace application.
        $ [dim]nextmv cloud marketplace app update --partner-id my-partner \\
            --app-id marketplace-hare --state published[/dim]

    - Update multiple fields and save the result to a file.
        $ [dim]nextmv cloud marketplace app update --partner-id my-partner \\
            --app-id marketplace-hare --title "New Title" --state published \\
            --output app.json[/dim]
    """

    in_progress(msg="Getting application...")
    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    updated_app = mkt_app.update(
        title=title,
        description=description,
        categories=categories,
        features=features,
        state=state,
    )
    success(
        f"Application [magenta]{app_id}[/magenta] with partner ID [magenta]{partner_id}[/magenta] updated successfully."
    )
    updated_app_dict = updated_app.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_app_dict, f, indent=2)

        success(msg=f"Updated application information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_app_dict)
