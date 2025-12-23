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
