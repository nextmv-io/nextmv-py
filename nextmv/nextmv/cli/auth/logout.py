"""
This module defines the ``nextmv auth logout`` command for the Nextmv CLI.

Running ``nextmv auth logout`` deletes stored OAuth2 tokens for one or more
pkce profiles.
"""

from typing import Annotated

import typer

from nextmv.auth import delete_tokens
from nextmv.cli.message import error, info, success, warning
from nextmv.config import (
    AuthType,
    get_auth_session,
    get_auth_type,
    list_pkce_profiles,
    load_config,
)

# Set up subcommand application.
app = typer.Typer()


@app.command()
def logout(
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            "-p",
            help="Profile to log out of. If omitted, all pkce profiles are logged out.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ] = None,
) -> None:
    """
    Log out of Nextmv and delete stored access tokens.

    Deletes the token file for the auth session associated with each
    [magenta]pkce[/magenta] profile.  Multiple profiles sharing the same
    auth session are logged out together (tokens are stored per session,
    not per profile).

    [bold][underline]Examples[/underline][/bold]

    - Log out of all pkce profiles.
        $ [dim]nextmv auth logout[/dim]

    - Log out of a specific named profile.
        $ [dim]nextmv auth logout --profile my-auth-profile[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error(
            "[magenta]default[/magenta] is a reserved profile name. "
            "Use [code]nextmv auth logout[/code] without a profile to log out all profiles."
        )

    config = load_config()

    if profile is not None:
        profile = profile.strip()
        if profile not in config:
            error(
                f"Profile [magenta]{profile}[/magenta] does not exist. "
                "Use [code]nextmv configuration create[/code] to create it."
            )
        ptype = get_auth_type(config, profile)
        if ptype != AuthType.PKCE:
            error(
                f"Profile [magenta]{profile}[/magenta] is not a [magenta]pkce[/magenta] profile. "
                "Only [magenta]pkce[/magenta] profiles store tokens that can be deleted."
            )
        profiles_to_logout: list[str | None] = [profile]
    else:
        profiles_to_logout = list_pkce_profiles(config)

    if not profiles_to_logout:
        info(
            "No [magenta]pkce[/magenta] profiles found. "
            "Use [code]nextmv configuration create --auth-type pkce[/code] to create one."
        )
        return

    # Deduplicate by session name.
    seen_sessions: set[str] = set()
    for prof in profiles_to_logout:
        session = get_auth_session(config, prof)
        seen_sessions.add(session)

    failed: list[str] = []
    for session in sorted(seen_sessions):
        try:
            delete_tokens(session)
            success(f"Logged out of session [magenta]{session}[/magenta].")
        except Exception as exc:
            warning(f"Failed to log out of session [magenta]{session}[/magenta]: {exc}")
            failed.append(session)

    if failed:
        names = ", ".join(f"[magenta]{n}[/magenta]" for n in failed)
        error(f"Logout failed for the following session(s): {names}.")
