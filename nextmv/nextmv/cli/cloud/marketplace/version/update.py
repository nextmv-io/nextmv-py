"""
This module defines the cloud marketplace version update command for the Nextmv CLI.
"""

import json
from typing import Annotated

import typer

from nextmv.cli.configuration.config import build_marketplace_app
from nextmv.cli.message import print_json, success
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
def update(
    app_id: MarketplaceAppIDOption,
    partner_id: MarketplacePartnerIDOption,
    version_id: MarketplaceVersionIDOption,
    change_log: Annotated[
        list[str],
        typer.Option(
            "--change-log",
            "-c",
            help="Changelog entries for the version. Pass multiple entries by repeating the flag.",
            metavar="CHANGE_LOG",
        ),
    ],
    output: Annotated[
        str | None,
        typer.Option(
            "--output",
            "-o",
            help="Saves the updated version information to this location.",
            metavar="OUTPUT_PATH",
        ),
    ] = None,
    _: DebugOption = False,
    profile: ProfileOption = None,
) -> None:
    """
    Update a marketplace version's change log.

    This command allows you to update the change log entries for an existing
    marketplace version. Pass multiple change log entries by repeating the
    --change-log flag.

    [bold][underline]Examples[/underline][/bold]

    - Update a version's change log with a single entry.

        $ [dim]nextmv cloud marketplace version update --partner-id my-partner \\
            --app-id marketplace-hare --version-id mkt-v1 \\
            --change-log "Fixed critical bug in routing algorithm"[/dim]

    - Update a version's change log with multiple entries.

        $ [dim]nextmv cloud marketplace version update --partner-id my-partner \\
            --app-id marketplace-hare --version-id mkt-v1 \\
            --change-log "Performance improvements" --change-log "Added new features" \\
            --change-log "Updated documentation"[/dim]

    - Update a version and save the updated information to a [magenta]updated_version.json[/magenta] file.

        $ [dim]nextmv cloud marketplace version update --partner-id my-partner \\
            --app-id marketplace-hare --version-id mkt-v1 \\
            --change-log "Bug fixes" --output updated_version.json[/dim]
    """

    mkt_app = build_marketplace_app(app_id=app_id, partner_id=partner_id, profile=profile)
    updated_version = mkt_app.update_version(
        version_id=version_id,
        change_log=change_log,
    )
    success(
        f"Version [magenta]{version_id}[/magenta] updated successfully in application [magenta]{app_id}[/magenta] "
        f"belonging to partner [magenta]{partner_id}[/magenta]."
    )
    updated_version_dict = updated_version.to_dict()

    if output is not None and output != "":
        with open(output, "w") as f:
            json.dump(updated_version_dict, f, indent=2)

        success(msg=f"Updated version information saved to [magenta]{output}[/magenta].")

        return

    print_json(updated_version_dict)
