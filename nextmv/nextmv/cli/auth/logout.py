"""
This module defines the ``nextmv auth logout`` command for the Nextmv CLI.

Running ``nextmv auth logout`` deletes stored OAuth2 tokens for one or more
pkce profiles, and revokes them at the identity provider.
"""

import webbrowser
from typing import Annotated

import typer

from nextmv.auth import browser_logout_url, delete_tokens, load_tokens, revoke_refresh_token
from nextmv.cli.message import error, info, message, success, warning
from nextmv.config import (
    CLIENT_ID_KEY,
    OIDC_DISCOVERY_URL_KEY,
    AuthType,
    get_auth_session,
    get_auth_type,
    get_endpoint_oidc_config,
    get_profile_endpoint,
    list_pkce_profiles,
    load_config,
    load_sessions,
)

# Set up subcommand application.
app = typer.Typer()


@app.command()
def logout(
    browser: Annotated[
        bool,
        typer.Option(
            "--browser",
            "-b",
            help=(
                "Also open the sign-out page to clear the session your browser "
                "holds, so the next login cannot reuse it."
            ),
        ),
    ] = False,
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

    Revokes the stored tokens at the identity provider, then deletes the token
    file for the auth session associated with each [magenta]pkce[/magenta]
    profile.  Multiple profiles sharing the same auth session are logged out
    together (tokens are stored per session, not per profile).

    This does not affect the session your [bold]browser[/bold] holds, which is
    what signs you straight back in on the next login. Pass
    [code]--browser[/code] to clear that too. Note that a single sign-on
    session lives with your identity provider and can only be ended from
    [bold]their[/bold] sign-out page.

    [bold][underline]Examples[/underline][/bold]

    - Log out of all pkce profiles.

        $ [dim]nextmv auth logout[/dim]

    - Log out of a specific named profile.

        $ [dim]nextmv auth logout --profile my-auth-profile[/dim]

    - Log out and clear the browser session as well.

        $ [dim]nextmv auth logout --browser[/dim]
    """

    config = load_config()
    profiles_to_logout = _resolve_profiles(config, profile)

    if not profiles_to_logout:
        info(
            "No [magenta]pkce[/magenta] profiles found. "
            "Use [code]nextmv configuration create --auth-type pkce[/code] to create one."
        )
        return

    sessions = load_sessions()

    # Deduplicate by session name, keeping the OIDC configuration of the
    # endpoint each session authenticates against so its tokens can be revoked
    # at the right provider.
    seen_sessions: dict[str, dict] = {}
    for prof in profiles_to_logout:
        session = get_auth_session(config, prof)
        if session in seen_sessions:
            continue
        endpoint = get_profile_endpoint(config, prof)
        seen_sessions[session] = get_endpoint_oidc_config(endpoint, sessions) or {}

    failed: list[str] = []
    for session, oidc_cfg in sorted(seen_sessions.items()):
        try:
            _revoke_session(session, oidc_cfg)
            delete_tokens(session)
            success(f"Logged out of session [magenta]{session}[/magenta].")
        except Exception as exc:
            warning(f"Failed to log out of session [magenta]{session}[/magenta]: {exc}")
            failed.append(session)

    if browser:
        # One sign-out per distinct identity provider, not per session: sessions
        # that authenticate against the same provider share a browser session.
        cleared: set[tuple[str | None, str | None]] = set()
        for oidc_cfg in seen_sessions.values():
            key = (oidc_cfg.get(CLIENT_ID_KEY), oidc_cfg.get(OIDC_DISCOVERY_URL_KEY))
            if key in cleared:
                continue
            cleared.add(key)
            _clear_browser_session(oidc_cfg)

    if failed:
        names = ", ".join(f"[magenta]{n}[/magenta]" for n in failed)
        error(f"Logout failed for the following session(s): {names}.")


def _resolve_profiles(config: dict, profile: str | None) -> list[str | None]:
    """
    Resolve which profiles to log out of.

    Returns the single named profile when one is given, after checking that it
    exists and is a ``pkce`` profile, or every ``pkce`` profile otherwise.
    """
    if profile is None:
        return list_pkce_profiles(config)

    if profile.strip().lower() == "default":
        error(
            "[magenta]default[/magenta] is a reserved profile name. "
            "Use [code]nextmv auth logout[/code] without a profile to log out all profiles."
        )

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

    return [profile]


def _revoke_session(session: str, oidc_cfg: dict) -> None:
    """
    Revoke the refresh token stored for *session* at the identity provider.

    Deleting the local token file only makes the tokens unreachable from this
    machine; until they are revoked they stay valid until they expire.  A
    failure here is reported but does not stop the local tokens being deleted,
    since an unreachable provider should not prevent logging out.
    """
    tokens = load_tokens(session)
    if tokens is None:
        return

    refresh_token = tokens.get("refresh_token")
    if not refresh_token:
        return

    try:
        revoke_refresh_token(
            refresh_token,
            client_id=oidc_cfg.get(CLIENT_ID_KEY),
            oidc_discovery_url=oidc_cfg.get(OIDC_DISCOVERY_URL_KEY),
        )
    except Exception as exc:
        warning(
            f"Could not revoke the tokens for session [magenta]{session}[/magenta]: {exc}. "
            "They have been deleted locally and will expire on their own."
        )


def _clear_browser_session(oidc_cfg: dict) -> None:
    """Open the provider's sign-out page to drop the browser session."""
    try:
        url = browser_logout_url(
            client_id=oidc_cfg.get(CLIENT_ID_KEY),
            oidc_discovery_url=oidc_cfg.get(OIDC_DISCOVERY_URL_KEY),
        )
    except Exception as exc:
        warning(f"Could not resolve the sign-out URL: {exc}")
        return

    info(
        "Opening the sign-out page to clear your browser session. You can close "
        "the sign-in page it lands on. If your browser does not open, visit:"
    )
    message(f"[magenta]{url}[/magenta]")
    webbrowser.open(url)
