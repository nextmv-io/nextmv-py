"""
This module defines the configuration create command for the Nextmv CLI.
"""

from typing import Annotated

import typer
from rich.prompt import Prompt

from nextmv.auth import fetch_organizations, is_token_expired, load_tokens, refresh_tokens, run_pkce_flow, save_tokens
from nextmv.cli.configuration.config import obscure_api_key
from nextmv.cli.message import choice, error, message, success, warning
from nextmv.config import (
    API_KEY_KEY,
    AUTH_SESSION_KEY,
    AUTH_TYPE_API_KEY,
    AUTH_TYPE_KEY,
    AUTH_TYPE_PKCE,
    CLIENT_ID_KEY,
    DEFAULT_AUTH_SESSION,
    DEFAULT_ENDPOINT,
    ENDPOINT_KEY,
    OIDC_DISCOVERY_URL_KEY,
    TEAM_ID_KEY,
    _strip_scheme,
    get_endpoint_oidc_config,
    load_config,
    load_sessions,
    save_config,
    save_sessions,
)

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(  # noqa: C901
    api_key: Annotated[
        str | None,
        typer.Option(
            "--api-key",
            "-a",
            help="A valid Nextmv Cloud API key. "
            + "Get one from [link=https://cloud.nextmv.io][bold]https://cloud.nextmv.io[/bold][/link]. "
            + "Setting this flag automatically selects the [magenta]api_key[/magenta] profile type.",
            envvar="NEXTMV_API_KEY",
            metavar="NEXTMV_API_KEY",
        ),
    ] = None,
    endpoint: Annotated[  # Hidden because it is meant for internal use.
        str | None,
        typer.Option(
            "--endpoint",
            "-e",
            hidden=True,
            envvar="NEXTMV_ENDPOINT",
            metavar="NEXTMV_ENDPOINT",
        ),
    ] = DEFAULT_ENDPOINT,
    profile: Annotated[  # Similar to nextmv.cli.options.ProfileOption but with different help text.
        str | None,
        typer.Option(
            "--profile",
            "-p",
            help="Profile name to save the configuration under.",
            envvar="NEXTMV_PROFILE",
            metavar="PROFILE_NAME",
        ),
    ] = None,
    auth_type: Annotated[
        str | None,
        typer.Option(
            "--auth-type",
            "-t",
            help=(
                "The authentication type for this profile: [magenta]api_key[/magenta] (default) or "
                "[magenta]pkce[/magenta] (browser-based PKCE login via [code]nextmv login[/code]). "
                "Ignored when [magenta]--api-key[/magenta] is provided."
            ),
            metavar="AUTH_TYPE",
        ),
    ] = None,
    auth_session: Annotated[
        str | None,
        typer.Option(
            "--auth-session",
            "-s",
            help=(
                "Named auth session to share tokens across profiles. "
                "Only applies to [magenta]pkce[/magenta] profiles. "
                "Multiple profiles that reference the same session name share a single "
                "browser login. "
                f"Defaults to the reserved [magenta]{DEFAULT_AUTH_SESSION}[/magenta] session "
                "when omitted."
            ),
            metavar="SESSION_NAME",
        ),
    ] = None,
    team: Annotated[
        str | None,
        typer.Option(
            "--team",
            help=(
                "Team name to associate with this [magenta]pkce[/magenta] profile. "
                "When omitted, available teams are fetched from the API and you will be "
                "prompted to select one. "
                "Only applies to [magenta]pkce[/magenta] profiles."
            ),
            metavar="TEAM_NAME",
        ),
    ] = None,
    oidc_discovery_url: Annotated[
        str | None,
        typer.Option(
            "--oidc-discovery-url",
            hidden=True,
            help=(
                "OIDC discovery document URL for the identity provider behind the endpoint. "
                "Only needed for non-production endpoints not already in sessions.yaml. "
                "Only applies to [magenta]pkce[/magenta] profiles."
            ),
            metavar="OIDC_DISCOVERY_URL",
        ),
    ] = None,
    oidc_client_id: Annotated[
        str | None,
        typer.Option(
            "--client-id",
            hidden=True,
            help=(
                "OAuth2 client ID for the identity provider behind the endpoint. "
                "Only needed for non-production endpoints not already in sessions.yaml. "
                "Only applies to [magenta]pkce[/magenta] profiles."
            ),
            metavar="OIDC_CLIENT_ID",
        ),
    ] = None,
) -> None:
    """
    Create a new configuration or update an existing one.

    [bold][underline]Examples[/underline][/bold]

    - Default configuration (prompts for type and API key or opens browser).
        $ [dim]nextmv configuration create[/dim]

    - Default API key configuration without prompting.
        $ [dim]nextmv configuration create --api-key NEXTMV_API_KEY[/dim]

    - Configure a named [magenta]api_key[/magenta] profile.
        $ [dim]nextmv configuration create --api-key NEXTMV_API_KEY --profile hare[/dim]

    - Configure a named [magenta]pkce[/magenta] profile (login separately via [code]nextmv login[/code]).
        $ [dim]nextmv configuration create --profile hare --auth-type pkce[/dim]

    - Configure two [magenta]pkce[/magenta] profiles that share a single login session.
        $ [dim]nextmv configuration create --profile dev --auth-type pkce --auth-session my-work[/dim]
        $ [dim]nextmv configuration create --profile staging --auth-type pkce --auth-session my-work[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error("[magenta]default[/magenta] is a reserved profile name.")

    # Validate and normalise auth_session.
    if auth_session is not None:
        auth_session = auth_session.strip()
        if auth_session.lower() == DEFAULT_AUTH_SESSION:
            # Storing the literal "default" is redundant — treat as if omitted.
            auth_session = None
        elif not auth_session:
            auth_session = None

    endpoint = _strip_scheme(str(endpoint))

    # Providing custom OIDC config only makes sense for non-default endpoints.
    if (oidc_discovery_url or oidc_client_id) and endpoint == DEFAULT_ENDPOINT:
        error(
            "Custom [magenta]--oidc-discovery-url[/magenta] / [magenta]--client-id[/magenta] "
            "flags are only valid for non-default endpoints. "
            f"The default endpoint [magenta]{DEFAULT_ENDPOINT}[/magenta] already has built-in OIDC configuration."
        )

    # >>> Determine profile type

    # If --api-key is supplied, we always use the api_key auth type regardless
    # of --auth-type, since there's an explicit credential.
    if api_key is not None and api_key.strip():
        resolved_type = AUTH_TYPE_API_KEY
    elif auth_type is not None:
        auth_type = auth_type.strip().lower()
        if auth_type not in (AUTH_TYPE_API_KEY, AUTH_TYPE_PKCE):
            error(
                f"Invalid auth type [magenta]{auth_type}[/magenta]. "
                f"Must be [magenta]{AUTH_TYPE_API_KEY}[/magenta] or [magenta]{AUTH_TYPE_PKCE}[/magenta]."
            )
        resolved_type = auth_type
    elif oidc_discovery_url or oidc_client_id:
        # OIDC flags imply a pkce auth type — no need to prompt.
        resolved_type = AUTH_TYPE_PKCE
    else:
        # Interactive prompt — ask the user which style they want.
        resolved_type = choice(
            msg="Select authentication type",
            choices=[
                AUTH_TYPE_API_KEY,
                AUTH_TYPE_PKCE,
            ],
            default=AUTH_TYPE_API_KEY,
        )

    config = load_config()

    # >>> For api_key profiles: collect the API key interactively if not provided.

    if resolved_type == AUTH_TYPE_API_KEY:
        if api_key is None or not api_key.strip():
            while True:
                api_key_prompt = Prompt.ask(
                    "Please enter your Nextmv API key to create the configuration",
                    case_sensitive=True,
                    password=True,
                )
                api_key = api_key_prompt.strip()
                if api_key:
                    break

                warning("API key cannot be empty. Please try again.")

        if profile is None:
            config[API_KEY_KEY] = api_key
            config[ENDPOINT_KEY] = endpoint
            # Remove auth_type key from default profile if previously set as
            # pkce, since we are now explicitly creating an api_key profile.
            config.pop(AUTH_TYPE_KEY, None)
        else:
            if profile not in config:
                config[profile] = {}
            config[profile][API_KEY_KEY] = api_key
            config[profile][ENDPOINT_KEY] = endpoint
            config[profile].pop(AUTH_TYPE_KEY, None)

        save_config(config)

        success("Configuration saved successfully.")
        message(f"[bold]Profile[/bold]: [magenta]{profile or 'Default'}[/magenta]", indents=1)
        message(f"[bold]Type[/bold]: [magenta]{AUTH_TYPE_API_KEY}[/magenta]", indents=1)
        message(f"[bold]API Key[/bold]: [magenta]{obscure_api_key(api_key)}[/magenta]", indents=1)
        if endpoint != DEFAULT_ENDPOINT:
            message(f"[bold]Endpoint[/bold]: [magenta]{endpoint}[/magenta]", indents=1)

    # >>> For pkce profiles: store metadata and ensure OIDC config is known.

    else:
        # Check whether we already have OIDC config for this endpoint.
        sessions = load_sessions()
        existing_oidc = get_endpoint_oidc_config(endpoint, sessions)

        if existing_oidc is None:
            # Endpoint is unknown — collect OIDC config from flags or interactively.
            if oidc_discovery_url and oidc_client_id:
                resolved_discovery_url = oidc_discovery_url.strip()
                resolved_client_id = oidc_client_id.strip()
            else:
                if not oidc_discovery_url:
                    while True:
                        resolved_discovery_url = Prompt.ask(
                            f"Enter the OIDC discovery URL for endpoint [magenta]{endpoint}[/magenta]"
                        ).strip()
                        if resolved_discovery_url:
                            break
                        warning("OIDC discovery URL cannot be empty. Please try again.")
                else:
                    resolved_discovery_url = oidc_discovery_url.strip()

                if not oidc_client_id:
                    while True:
                        resolved_client_id = Prompt.ask(
                            f"Enter the OAuth2 client ID for endpoint [magenta]{endpoint}[/magenta]"
                        ).strip()
                        if resolved_client_id:
                            break
                        warning("Client ID cannot be empty. Please try again.")
                else:
                    resolved_client_id = oidc_client_id.strip()

            # Persist OIDC config for this endpoint.
            sessions[endpoint] = {
                OIDC_DISCOVERY_URL_KEY: resolved_discovery_url,
                CLIENT_ID_KEY: resolved_client_id,
            }
            save_sessions(sessions)

        # >>> Resolve team ID: ensure we have a valid token, then look up orgs.

        effective_session = auth_session or DEFAULT_AUTH_SESSION
        oidc_cfg = get_endpoint_oidc_config(endpoint, load_sessions())
        resolved_oidc_url = oidc_cfg.get(OIDC_DISCOVERY_URL_KEY) if oidc_cfg else None
        resolved_oidc_client_id = oidc_cfg.get(CLIENT_ID_KEY) if oidc_cfg else None

        access_token = _ensure_token(
            session=effective_session,
            profile=profile,
            endpoint=endpoint,
            oidc_discovery_url=resolved_oidc_url,
            client_id=resolved_oidc_client_id,
        )

        team_id = _resolve_team_id(
            access_token=access_token,
            endpoint=endpoint,
            team_name=team,
        )

        # >>> Write profile to config.yaml.

        if profile is None:
            config[AUTH_TYPE_KEY] = AUTH_TYPE_PKCE
            config[ENDPOINT_KEY] = endpoint
            config[TEAM_ID_KEY] = team_id
            # Remove any previously stored api_key from the default profile.
            config.pop(API_KEY_KEY, None)
            if auth_session:
                config[AUTH_SESSION_KEY] = auth_session
            else:
                config.pop(AUTH_SESSION_KEY, None)
        else:
            if profile not in config:
                config[profile] = {}
            config[profile][AUTH_TYPE_KEY] = AUTH_TYPE_PKCE
            config[profile][ENDPOINT_KEY] = endpoint
            config[profile][TEAM_ID_KEY] = team_id
            config[profile].pop(API_KEY_KEY, None)
            if auth_session:
                config[profile][AUTH_SESSION_KEY] = auth_session
            else:
                config[profile].pop(AUTH_SESSION_KEY, None)

        save_config(config)

        success("Configuration saved successfully.")
        message(f"[bold]Profile[/bold]: [magenta]{profile or 'Default'}[/magenta]", indents=1)
        message(f"[bold]Type[/bold]: [magenta]{AUTH_TYPE_PKCE}[/magenta]", indents=1)
        message(f"[bold]Auth session[/bold]: [magenta]{effective_session}[/magenta]", indents=1)
        message(f"[bold]Team ID[/bold]: [magenta]{team_id}[/magenta]", indents=1)
        if endpoint != DEFAULT_ENDPOINT:
            message(f"[bold]Endpoint[/bold]: [magenta]{endpoint}[/magenta]", indents=1)


def _ensure_token(
    session: str,
    profile: str | None,
    endpoint: str,
    oidc_discovery_url: str | None,
    client_id: str | None,
) -> str:
    """
    Return a valid access token for *session*, running the PKCE browser flow
    only when necessary.

    Token resolution order:
    1. Load existing tokens from disk for *session*.
    2. If expired but a refresh token is present, refresh silently.
    3. If no tokens exist (or refresh fails), run the full browser PKCE flow.

    Parameters
    ----------
    session : str
        The auth session name.
    profile : str | None
        Profile name used only for display in the browser flow.
    endpoint : str
        Endpoint hostname, used for display messages.
    oidc_discovery_url : str | None
        OIDC discovery URL; passed through to the PKCE flow.
    client_id : str | None
        OAuth2 client ID; passed through to the PKCE flow.

    Returns
    -------
    str
        A valid access token (id_token preferred, access_token as fallback).
    """
    tokens = load_tokens(session)

    if tokens is not None and not is_token_expired(tokens):
        # Happy path: existing, valid token.
        token = tokens.get("id_token") or tokens.get("access_token")
        if token:
            return token

    if tokens is not None and is_token_expired(tokens):
        refresh_token = tokens.get("refresh_token")
        if refresh_token:
            try:
                tokens = refresh_tokens(
                    refresh_token,
                    client_id=client_id,
                    oidc_discovery_url=oidc_discovery_url,
                )
                save_tokens(session, tokens)
                token = tokens.get("id_token") or tokens.get("access_token")
                if token:
                    return token
            except Exception:
                pass  # Fall through to full browser flow.

    # No usable token — open the browser.
    message(
        f"Opening browser to authenticate session [magenta]{session}[/magenta] "
        f"against [magenta]{endpoint}[/magenta]...",
    )
    tokens = run_pkce_flow(
        profile=profile,
        oidc_discovery_url=oidc_discovery_url,
        client_id=client_id,
    )
    save_tokens(session, tokens)
    token = tokens.get("id_token") or tokens.get("access_token")
    if not token:
        error("Authentication succeeded but no access token was returned. Please try again.")
    return token  # type: ignore[return-value]  # error() raises


def _resolve_team_id(
    access_token: str,
    endpoint: str,
    team_name: str | None,
) -> str:
    """
    Resolve the team UUID the user wants to associate with this profile.

    If *team_name* is provided, look it up in the org list and return its ID.
    Otherwise fetch the org list and prompt the user to choose.

    Parameters
    ----------
    access_token : str
        A valid access token for the authenticated user.
    endpoint : str
        The API endpoint hostname.
    team_name : str | None
        The team name provided via ``--team``, or ``None`` to prompt.

    Returns
    -------
    str
        The team UUID.
    """
    try:
        orgs = fetch_organizations(access_token, endpoint)
    except Exception as exc:
        error(f"Failed to fetch teams from [magenta]{endpoint}[/magenta]: {exc}")

    if not orgs:
        error(f"No teams found for your account on [magenta]{endpoint}[/magenta].")

    # Build name → id mapping (case-insensitive lookup for --team flag).
    name_to_id: dict[str, str] = {o["name"]: o["id"] for o in orgs}
    name_to_id_lower: dict[str, str] = {k.lower(): v for k, v in name_to_id.items()}

    if team_name is not None:
        team_id = name_to_id_lower.get(team_name.strip().lower())
        if team_id is None:
            available = ", ".join(f"[magenta]{n}[/magenta]" for n in name_to_id)
            error(f"Team [magenta]{team_name}[/magenta] not found. Available teams: {available}")
        return team_id  # type: ignore[return-value]  # error() raises

    # Interactive selection — show team names sorted alphabetically.
    sorted_names = sorted(name_to_id)
    selected_name = choice(
        msg="Select the team to associate with this profile",
        choices=sorted_names,
    )
    return name_to_id[selected_name]
