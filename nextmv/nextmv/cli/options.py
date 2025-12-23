"""
Shared CLI options for the Nextmv CLI.

This module defines reusable option types that can be imported
and used across all CLI commands.
"""

from typing import Annotated

import typer

# Profile option - can be used in any command to specify which profile to use.
# Usage: profile: ProfileOption = None
ProfileOption = Annotated[
    str | None,
    typer.Option(
        "--profile",
        "-p",
        help="Specify the profile to use. Use [code]nextmv configuration[/code] to manage profiles.",
        envvar="NEXTMV_PROFILE",
        metavar="PROFILE_NAME",
    ),
]
