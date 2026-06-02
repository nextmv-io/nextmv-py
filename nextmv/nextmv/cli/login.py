"""
This module defines the ``nextmv login`` command for the Nextmv CLI.

Running ``nextmv login`` executes the PKCE authorization-code flow for every
``pkce`` profile configured in ``~/.nextmv/config.yaml``, or for a
specific profile when ``--profile`` is given.  Tokens are stored under
``~/.nextmv/auth/<session>/tokens.json``, where ``<session>`` is the
``auth_session`` value configured on the profile (or ``default`` when
``auth_session`` is not set).
"""

from typing import Annotated

import typer

from nextmv.auth import run_pkce_flow, save_tokens
from nextmv.cli.message import error, info, message, success, warning
from nextmv.config import (
    AUTH_TYPE_PKCE,
    CLIENT_ID_KEY,
    OIDC_DISCOVERY_URL_KEY,
    get_auth_session,
    get_auth_type,
    get_endpoint_oidc_config,
    get_profile_endpoint,
    list_pkce_profiles,
    load_config,
    load_sessions,
)

# Set up subcommand application.
app = typer.Typer(invoke_without_command=True)


@app.callback()
def login(
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            "-p",
            help="Profile to log in to. If omitted, all [magenta]pkce[/magenta] profiles are logged in.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ] = None,
) -> None:
    """
    Log in to Nextmv using the browser-based PKCE auth flow.

    Opens your browser, completes the OAuth2 PKCE flow, and stores the
    resulting tokens under [magenta]~/.nextmv/auth/[/magenta].

    If [magenta]--profile[/magenta] is given, only that profile is logged in
    (it must be configured with [code]auth_type: pkce[/code]).  If no
    profile is given, all [magenta]pkce[/magenta] profiles found in
    [magenta]~/.nextmv/config.yaml[/magenta] are logged in sequentially.

    [bold][underline]Examples[/underline][/bold]

    - Log in with the default auth profile.
        $ [dim]nextmv login[/dim]

    - Log in with a specific named profile.
        $ [dim]nextmv login --profile my-auth-profile[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error(
            "[magenta]default[/magenta] is a reserved profile name. "
            "Use [code]nextmv login[/code] without a profile to log in to the default profile."
        )

    config = load_config()
    sessions = load_sessions()

    if profile is not None:
        # Validate that the requested profile exists and is a pkce profile.
        profile = profile.strip()
        if profile not in config:
            error(
                f"Profile [magenta]{profile}[/magenta] does not exist. "
                "Use [code]nextmv configuration create[/code] to create it."
            )
        ptype = get_auth_type(config, profile)
        if ptype != AUTH_TYPE_PKCE:
            error(
                f"Profile [magenta]{profile}[/magenta] is not a [magenta]pkce[/magenta] profile "
                f"(it is [magenta]{ptype}[/magenta]). "
                "Only [magenta]pkce[/magenta] profiles require [code]nextmv login[/code]."
            )
        profiles_to_login: list[str | None] = [profile]
    else:
        profiles_to_login = list_pkce_profiles(config)

    if not profiles_to_login:
        info(
            "No [magenta]pkce[/magenta] profiles found. "
            "Use [code]nextmv configuration create[/code] to create one, "
            "or set [magenta]auth_type: pkce[/magenta] in "
            "[magenta]~/.nextmv/config.yaml[/magenta]."
        )
        return

    failed: list[str] = []

    # Deduplicate: one browser flow per unique (session, endpoint) pair.
    # Multiple profiles can share the same auth session — logging in once is enough
    # because tokens are stored per session, not per profile.
    seen_sessions: dict[tuple[str, str], list[str]] = {}  # (session, endpoint) -> [display_name, ...]
    session_oidc: dict[tuple[str, str], tuple[str | None, str | None]] = {}

    for prof in profiles_to_login:
        display_name = prof if prof is not None else "default"
        session = get_auth_session(config, prof)
        endpoint = get_profile_endpoint(config, prof)
        oidc_cfg = get_endpoint_oidc_config(endpoint, sessions)
        if oidc_cfg is None:
            warning(
                f"Skipping profile [magenta]{display_name}[/magenta]: "
                f"no OIDC configuration found for endpoint [magenta]{endpoint}[/magenta]. "
                "Run [code]nextmv configuration create[/code] for this endpoint first."
            )
            failed.append(display_name)
            continue
        key = (session, endpoint)
        seen_sessions.setdefault(key, []).append(display_name)
        session_oidc[key] = (oidc_cfg.get(OIDC_DISCOVERY_URL_KEY), oidc_cfg.get(CLIENT_ID_KEY))

    for (session, endpoint), profile_names in seen_sessions.items():
        oidc_discovery_url, oidc_client_id = session_oidc[(session, endpoint)]
        profiles_display = ", ".join(f"[magenta]{n}[/magenta]" for n in profile_names)
        message(
            f"Logging in to session [magenta]{session}[/magenta] "
            f"(used by profile(s): {profiles_display}). "
            "Your browser will open — please complete the sign-in flow there."
        )
        try:
            tokens = run_pkce_flow(profile=None, oidc_discovery_url=oidc_discovery_url, client_id=oidc_client_id)
            save_tokens(session, tokens)
            success(f"Logged in to session [magenta]{session}[/magenta] successfully.")
        except Exception as exc:
            warning(f"Login failed for session [magenta]{session}[/magenta]: {exc}")
            failed.extend(profile_names)

    if failed:
        names = ", ".join(f"[magenta]{n}[/magenta]" for n in failed)
        error(f"Login failed for the following profile(s): {names}.")
