"""
This module defines the cloud marketplace version create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_app
from nextmv.cli.message import in_progress, print_json
from nextmv.cli.options import MarketplaceAppIDOption, MarketplacePartnerIDOption, ProfileOption

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    app_id: MarketplaceAppIDOption,
    change_log: Annotated[
        list[str],
        typer.Option(
            "--change-log",
            "-c",
            help="Changelog entries for the version. Pass multiple entries by repeating the flag.",
            metavar="CHANGE_LOG",
        ),
    ],
    partner_id: MarketplacePartnerIDOption,
    reference_version_id: Annotated[
        str,
        typer.Option(
            "--reference-version-id",
            "-r",
            help="The ID of the version to reference.",
            metavar="REFERENCE_VERSION_ID",
        ),
    ],
    version_id: Annotated[
        str | None,
        typer.Option(
            "--version-id",
            "-v",
            help="The ID to assign to the new marketplace version. If not provided, a random ID will be generated.",
            envvar="NEXTMV_MARKETPLACE_VERSION_ID",
            metavar="VERSION_ID",
        ),
    ] = None,
    profile: ProfileOption = None,
) -> None:
    """
    Create a new marketplace version for an application.

    Marketplace versions are created by referencing an existing version from
    the underlying application. The change log provides information about what
    has changed in this marketplace version. If no version ID is provided, a
    random ID will be generated.

    [bold][underline]Examples[/underline][/bold]

    - Create a marketplace version with change log entries. A random ID will be generated.
        $ [dim]nextmv cloud marketplace version create --partner-id my-partner \\
            --app-id marketplace-hare --reference-version-id v1.0.0 \\
            --change-log "Improved performance" --change-log "Fixed bug in routing"[/dim]

    - Create a marketplace version with a specific version ID.
        $ [dim]nextmv cloud marketplace version create --partner-id my-partner \\
            --app-id marketplace-hare --reference-version-id v1.0.0 \\
            --version-id mkt-v1 --change-log "Initial marketplace release"[/dim]

    - Create a marketplace version with multiple change log entries.
        $ [dim]nextmv cloud marketplace version create --partner-id my-partner \\
            --app-id marketplace-hare --reference-version-id v2.0.0 \\
            --change-log "Added new features" --change-log "Performance improvements" \\
            --change-log "Updated documentation"[/dim]
    """

    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    in_progress(msg="Creating version...")
    version = mkt_app.new_version(
        change_log=change_log,
        reference_version_id=reference_version_id,
        version_id=version_id,
    )
    print_json(version.to_dict())
