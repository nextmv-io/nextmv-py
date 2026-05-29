"""
This module defines the configuration create command for the Nextmv CLI.
"""

from typing import Annotated

import typer
from rich.prompt import Prompt

from nextmv.cli.configuration.config import obscure_api_key
from nextmv.cli.message import choice, error, message, success, warning
from nextmv.config import (
    API_KEY_KEY,
    AUTH_SESSION_KEY,
    CLIENT_ID_KEY,
    DEFAULT_AUTH_SESSION,
    DEFAULT_ENDPOINT,
    ENDPOINT_KEY,
    OIDC_DISCOVERY_URL_KEY,
    PROFILE_TYPE_API_KEY,
    PROFILE_TYPE_KEY,
    PROFILE_TYPE_PKCE,
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
    profile_type: Annotated[
        str | None,
        typer.Option(
            "--profile-type",
            "-t",
            help=(
                "The type of profile to create: [magenta]api_key[/magenta] (default) or "
                "[magenta]pkce[/magenta] (browser-based PKCE login via [code]nextmv login[/code]). "
                "Ignored when [magenta]--api-key[/magenta] is provided."
            ),
            metavar="PROFILE_TYPE",
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
        $ [dim]nextmv configuration create --profile hare --profile-type pkce[/dim]

    - Configure two [magenta]pkce[/magenta] profiles that share a single login session.
        $ [dim]nextmv configuration create --profile dev --profile-type pkce --auth-session my-work[/dim]
        $ [dim]nextmv configuration create --profile staging --profile-type pkce --auth-session my-work[/dim]
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

    # >>> Determine profile type

    # If --api-key is supplied, we always use the api_key profile type regardless
    # of --profile-type, since there's an explicit credential.
    if api_key is not None and api_key.strip():
        resolved_type = PROFILE_TYPE_API_KEY
    elif profile_type is not None:
        profile_type = profile_type.strip().lower()
        if profile_type not in (PROFILE_TYPE_API_KEY, PROFILE_TYPE_PKCE):
            error(
                f"Invalid profile type [magenta]{profile_type}[/magenta]. "
                f"Must be [magenta]{PROFILE_TYPE_API_KEY}[/magenta] or [magenta]{PROFILE_TYPE_PKCE}[/magenta]."
            )
        resolved_type = profile_type
    else:
        # Interactive prompt — ask the user which style they want.
        resolved_type = choice(
            msg="Select configuration type",
            choices=[
                PROFILE_TYPE_API_KEY,
                PROFILE_TYPE_PKCE,
            ],
            default=PROFILE_TYPE_API_KEY,
        )

    config = load_config()

    # >>> For api_key profiles: collect the API key interactively if not provided.

    if resolved_type == PROFILE_TYPE_API_KEY:
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
            # Remove profile_type key from default profile if previously set as
            # pkce, since we are now explicitly creating an api_key profile.
            config.pop(PROFILE_TYPE_KEY, None)
        else:
            if profile not in config:
                config[profile] = {}
            config[profile][API_KEY_KEY] = api_key
            config[profile][ENDPOINT_KEY] = endpoint
            config[profile].pop(PROFILE_TYPE_KEY, None)

        save_config(config)

        success("Configuration saved successfully.")
        message(f"[bold]Profile[/bold]: [magenta]{profile or 'Default'}[/magenta]", indents=1)
        message(f"[bold]Type[/bold]: [magenta]{PROFILE_TYPE_API_KEY}[/magenta]", indents=1)
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

        if profile is None:
            config[PROFILE_TYPE_KEY] = PROFILE_TYPE_PKCE
            config[ENDPOINT_KEY] = endpoint
            # Remove any previously stored api_key from the default profile.
            config.pop(API_KEY_KEY, None)
            if auth_session:
                config[AUTH_SESSION_KEY] = auth_session
            else:
                config.pop(AUTH_SESSION_KEY, None)
        else:
            if profile not in config:
                config[profile] = {}
            config[profile][PROFILE_TYPE_KEY] = PROFILE_TYPE_PKCE
            config[profile][ENDPOINT_KEY] = endpoint
            config[profile].pop(API_KEY_KEY, None)
            if auth_session:
                config[profile][AUTH_SESSION_KEY] = auth_session
            else:
                config[profile].pop(AUTH_SESSION_KEY, None)

        save_config(config)

        effective_session = auth_session or DEFAULT_AUTH_SESSION
        success("Configuration saved successfully.")
        message(f"[bold]Profile[/bold]: [magenta]{profile or 'Default'}[/magenta]", indents=1)
        message(f"[bold]Type[/bold]: [magenta]{PROFILE_TYPE_PKCE}[/magenta]", indents=1)
        message(f"[bold]Auth session[/bold]: [magenta]{effective_session}[/magenta]", indents=1)
        if endpoint != DEFAULT_ENDPOINT:
            message(f"[bold]Endpoint[/bold]: [magenta]{endpoint}[/magenta]", indents=1)
        message(
            "Run [code]nextmv login[/code]" + (f" --profile {profile}" if profile else "") + " to authenticate.",
            indents=1,
        )
