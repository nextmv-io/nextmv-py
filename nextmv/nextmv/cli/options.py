"""
Shared CLI options for the Nextmv CLI.

This module defines reusable option types that can be imported
and used across all CLI commands.
"""

from typing import Annotated

import typer

# profile option - can be used in any command to specify which profile to use.
# Define it as follows in commands or callbacks, as necessary:
# profile: ProfileOption = None
ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Profile to use for this action. Use [code]nextmv configuration[/code] to manage profiles.",
        envvar="NEXTMV_PROFILE",
        metavar="PROFILE_NAME",
    ),
]

# app_id option - can be used in any command that requires an application ID.
# Define it as follows in commands or callbacks, as necessary:
# app_id: AppIDOption
AppIDOption = Annotated[
    str,
    typer.Option(
        "--app-id",
        "-a",
        help="The Nextmv Cloud application ID to use for this action.",
        envvar="NEXTMV_APP_ID",
        metavar="APP_ID",
    ),
]
