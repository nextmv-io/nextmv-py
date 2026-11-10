"""
This module defines the ``nextmv auth login`` command for the Nextmv CLI.

Running ``nextmv auth login`` executes the PKCE authorization-code flow for
every ``pkce`` profile configured in ``~/.nextmv/config.yaml``, or for a
specific profile when ``--profile`` is given.  Tokens are stored under
``~/.nextmv/auth/<session>/tokens.json``, where ``<session>`` is the
``auth_session`` value configured on the profile (or ``default`` when
``auth_session`` is not set).
"""

from typing import Annotated

import typer

from nextmv.auth import (
    apply_system_certs,
    fetch_sso_provider,
    identity_mismatch,
    run_pkce_flow,
    save_tokens,
    token_identity,
)
from nextmv.cli.message import error, in_progress, info, message, success, warning
from nextmv.config import (
    CLIENT_ID_KEY,
    OIDC_DISCOVERY_URL_KEY,
    AuthType,
    get_auth_session,
    get_auth_type,
    get_endpoint_oidc_config,
    get_profile_endpoint,
    get_sso_domain,
    get_system_certs,
    list_pkce_profiles,
    load_config,
    load_sessions,
)

# Set up subcommand application.
app = typer.Typer()


@app.command()
def login(
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help=(
                "Force re-authentication even if an active browser session exists. "
                "Clears the existing Nextmv sign-in session before starting the login "
                "flow. Has no effect on a single sign-on session, which only your "
                "identity provider can end; use --no-browser for that."
            ),
        ),
    ] = False,
    no_browser: Annotated[
        bool,
        typer.Option(
            "--no-browser",
            help=(
                "Print the sign-in URL instead of opening a browser. Use this to "
                "open it in a private window or a different browser profile, so no "
                "cached session from a previous login is reused."
            ),
        ),
    ] = False,
    profile: Annotated[
        str | None,
        typer.Option(
            "--profile",
            "-p",
            help="Profile to log in to. If omitted, all pkce profiles are logged in.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ] = None,
) -> None:
    """
    Log in to Nextmv using the browser-based PKCE auth flow.

    Opens your browser, completes the OAuth2 PKCE flow, and stores the
    resulting tokens under [magenta]~/.nextmv/auth/[/magenta].

    If --profile is given, only that profile is logged in (it must be configured
    with [code]--auth-type pkce[/code] via [code]nextmv configuration create[/code]).
    If no profile is given, all [magenta]pkce[/magenta] profiles found in
    [magenta]~/.nextmv/config.yaml[/magenta] are logged in sequentially.

    Your browser may still hold a session from an earlier login and reuse it,
    which signs you back in as the previous user. [code]--force[/code] clears
    that session for a Nextmv login; for single sign-on, only
    [code]--no-browser[/code] with a private window is reliable.

    [bold][underline]Examples[/underline][/bold]

    - Log in with the default auth profile.

        $ [dim]nextmv auth login[/dim]

    - Log in with a specific named profile.

        $ [dim]nextmv auth login --profile my-auth-profile[/dim]

    - Force re-authentication, bypassing any active browser session.

        $ [dim]nextmv auth login --force[/dim]

    - Print the sign-in URL to open in a private window.

        $ [dim]nextmv auth login --no-browser[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error(
            "[magenta]default[/magenta] is a reserved profile name. "
            "Use [code]nextmv auth login[/code] without a profile to log in to the default profile."
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
        if ptype != AuthType.PKCE:
            error(
                f"Profile [magenta]{profile}[/magenta] is not a [magenta]pkce[/magenta] profile "
                f"(it is [magenta]{ptype}[/magenta]). "
                "Only [magenta]pkce[/magenta] profiles require [code]nextmv auth login[/code]."
            )
        profiles_to_login: list[str | None] = [profile]
    else:
        profiles_to_login = list_pkce_profiles(config)

    if not profiles_to_login:
        info(
            "No [magenta]pkce[/magenta] profiles found. "
            "Use [code]nextmv configuration create --auth-type pkce[/code] to create one."
        )
        return

    # Run the login flow for the selected profiles.
    _run_login(profiles_to_login, config, sessions, force, no_browser)


def _run_login(  # noqa: C901
    profiles_to_login: list[str | None],
    config: dict,
    sessions: dict,
    force: bool,
    no_browser: bool = False,
) -> None:
    """Run the login flow for the given list of profiles."""
    failed: list[str] = []
    # Deduplicate: one browser flow per unique (session, endpoint) pair.
    # Multiple profiles can share the same auth session — logging in once is enough
    # because tokens are stored per session, not per profile.
    seen_sessions: dict[tuple[str, str], list[str]] = {}  # (session, endpoint) -> [display_name, ...]
    session_oidc: dict[tuple[str, str], tuple[str | None, str | None]] = {}
    session_system_certs: dict[tuple[str, str], bool] = {}
    session_sso_domain: dict[tuple[str, str], str | None] = {}

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
        if get_system_certs(config, prof):
            session_system_certs[key] = True
        sso = get_sso_domain(config, prof)
        if sso and key not in session_sso_domain:
            session_sso_domain[key] = sso

    for (session, endpoint), profile_names in seen_sessions.items():
        oidc_discovery_url, oidc_client_id = session_oidc[(session, endpoint)]
        if session_system_certs.get((session, endpoint), False):
            apply_system_certs()

        identity_provider: str | None = None
        sso_domain = session_sso_domain.get((session, endpoint))
        if sso_domain:
            try:
                identity_provider = fetch_sso_provider(sso_domain, endpoint)
            except Exception:
                warning(
                    f"Failed to check SSO status for domain [magenta]{sso_domain}[/magenta]. "
                    "Falling back to standard login."
                )

        profiles_display = ", ".join(f"[magenta]{n}[/magenta]" for n in profile_names)
        in_progress(
            f"Logging in to session [magenta]{session}[/magenta] "
            f"(used by profile(s): {profiles_display}). "
            + (
                "Open the URL below to complete the sign-in flow."
                if no_browser
                else "Your browser will open — please complete the sign-in flow there."
            )
        )

        if force and identity_provider:
            warning(
                "[code]--force[/code] only clears a Nextmv sign-in session, and this profile "
                f"signs in through [magenta]{identity_provider}[/magenta]. If you are signed back "
                "in as the wrong user, re-run with [code]--no-browser[/code] and open the URL in a "
                "private window."
            )

        try:
            tokens = run_pkce_flow(
                oidc_discovery_url=oidc_discovery_url,
                client_id=oidc_client_id,
                force=force,
                identity_provider=identity_provider,
                open_browser=not no_browser,
                url_callback=(lambda url: message(f"[magenta]{url}[/magenta]")) if no_browser else None,
            )
        except Exception as exc:
            warning(f"Login failed for session [magenta]{session}[/magenta]: {exc}")
            failed.extend(profile_names)
            continue

        # The provider can return a token for a different identity than the one
        # requested, by replaying a session the browser still holds from an
        # earlier login.  Verify before storing, so a stale session surfaces
        # here instead of as a confusing failure on a later command.
        id_token = tokens.get("id_token")
        if id_token and not _identity_verified(session, id_token, identity_provider, sso_domain, no_browser):
            failed.extend(profile_names)
            continue

        save_tokens(session, tokens)
        signed_in_as = ""
        if id_token:
            try:
                email = token_identity(id_token).email
            except ValueError:
                email = None
            if email:
                signed_in_as = f" as [magenta]{email}[/magenta]"
        success(f"Logged in to session [magenta]{session}[/magenta]{signed_in_as} successfully.")

    if failed:
        names = ", ".join(f"[magenta]{n}[/magenta]" for n in failed)
        error(f"Login failed for the following profile(s): {names}.")


def _identity_verified(
    session: str,
    id_token: str,
    identity_provider: str | None,
    sso_domain: str | None,
    no_browser: bool,
) -> bool:
    """
    Check that *id_token* belongs to the identity the flow asked for.

    A wrong identity provider means the login did not go through the configured
    provider at all, so the tokens are rejected.  A merely unexpected email
    domain is reported but accepted, since a profile can legitimately be used
    with a secondary address.

    Returns ``True`` when the tokens are safe to store.
    """
    try:
        mismatch = identity_mismatch(
            id_token,
            expected_provider=identity_provider,
            expected_domain=sso_domain,
        )
    except ValueError as exc:
        warning(f"Login failed for session [magenta]{session}[/magenta]: {exc}")
        return False

    if mismatch is None:
        return True

    if mismatch.kind == "provider":
        warning(
            f"Login failed for session [magenta]{session}[/magenta]: {mismatch.reason}. "
            "Your browser most likely reused a sign-in session from an earlier login."
            + ("" if no_browser else " Re-run with [code]--no-browser[/code] and open the URL in a private window.")
        )
        return False

    warning(f"Logged in to session [magenta]{session}[/magenta], but {mismatch.reason}.")
    return True
