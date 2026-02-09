"""
This module defines the cloud marketplace app create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_client
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import ProfileOption
from nextmv.cloud.marketplace import MarketplaceApplication

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    partner_id: Annotated[
        str,
        typer.Option(
            "--partner-id",
            "-n",
            help="The partner ID to create the application under.",
            envvar="NEXTMV_MARKETPLACE_PARTNER_ID",
            metavar="PARTNER_ID",
        ),
    ],
    reference_app_id: Annotated[
        str,
        typer.Option(
            "--reference-app-id",
            "-r",
            help="The ID of an existing application to use as a reference for the new application.",
            metavar="REFERENCE_APP_ID",
        ),
    ],
    title: Annotated[
        str,
        typer.Option(
            "--title",
            "-t",
            help="The title of the application to create.",
            metavar="TITLE",
        ),
    ],
    app_id: Annotated[
        str | None,
        typer.Option(
            "--app-id",
            "-a",
            help="An optional ID for the Nextmv Marketplace application. "
            "If not provided, a random ID will be generated.",
            envvar="NEXTMV_MARKETPLACE_APP_ID",
            metavar="APP_ID",
        ),
    ] = None,
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
    profile: ProfileOption = None,
) -> None:
    """
    Create a new Nextmv Marketplace application.

    Marketplace applications are created under a partner ID and are based on a
    reference application. The reference application serves as a template,
    providing the structure and configuration for the new marketplace listing.

    Applications can be enriched with categories and features to improve
    discoverability in the Nextmv Marketplace. If no app ID is provided, a
    random ID will be generated.

    [bold][underline]Examples[/underline][/bold]

    - Create a marketplace application with the title [magenta]Hare Routing[/magenta]. A random ID will be generated.
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing"[/dim]

    - Create a marketplace application with a specific ID [magenta]marketplace-hare[/magenta].
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing" --app-id marketplace-hare[/dim]

    - Create a marketplace application with a description.
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing" \\
            --description "Advanced routing solution for hare logistics"[/dim]

    - Create a marketplace application with categories.
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing" \\
            --categories routing --categories logistics[/dim]

    - Create a marketplace application with features.
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing" \\
            --features "real-time optimization" --features "multi-vehicle support"[/dim]

    - Create a marketplace application with all options.
        $ [dim]nextmv cloud marketplace app create --partner-id fluffy-comrade \\
            --reference-app-id hare-app --title "Hare Routing" --app-id marketplace-hare \\
            --description "Advanced routing solution" --categories routing \\
            --features "real-time optimization"[/dim]
    """

    client = build_client(profile)
    in_progress(msg="Creating application...")
    marketplace_app = MarketplaceApplication.new(
        client=client,
        partner_id=partner_id,
        reference_app_id=reference_app_id,
        title=title,
        app_id=app_id,
        description=description,
        categories=categories,
        features=features,
    )
    print_json(marketplace_app.to_dict())
