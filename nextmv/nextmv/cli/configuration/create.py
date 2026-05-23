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
    DEFAULT_ENDPOINT,
    ENDPOINT_KEY,
    PROFILE_TYPE_API_KEY,
    PROFILE_TYPE_AUTH_FLOW,
    PROFILE_TYPE_KEY,
    load_config,
    save_config,
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
                "[magenta]auth_flow[/magenta] (browser-based PKCE login via [code]nextmv login[/code]). "
                "Ignored when [magenta]--api-key[/magenta] is provided."
            ),
            metavar="PROFILE_TYPE",
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

    - Configure a named [magenta]auth_flow[/magenta] profile (login separately via [code]nextmv login[/code]).
        $ [dim]nextmv configuration create --profile hare --profile-type auth_flow[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error("[magenta]default[/magenta] is a reserved profile name.")

    endpoint = str(endpoint)
    if endpoint.startswith("https://"):
        endpoint = endpoint[len("https://") :]
    elif endpoint.startswith("http://"):
        endpoint = endpoint[len("http://") :]

    # >>> Determine profile type

    # If --api-key is supplied, we always use the api_key profile type regardless
    # of --profile-type, since there's an explicit credential.
    if api_key is not None and api_key.strip():
        resolved_type = PROFILE_TYPE_API_KEY
    elif profile_type is not None:
        profile_type = profile_type.strip().lower()
        if profile_type not in (PROFILE_TYPE_API_KEY, PROFILE_TYPE_AUTH_FLOW):
            error(
                f"Invalid profile type [magenta]{profile_type}[/magenta]. "
                f"Must be [magenta]{PROFILE_TYPE_API_KEY}[/magenta] or [magenta]{PROFILE_TYPE_AUTH_FLOW}[/magenta]."
            )
        resolved_type = profile_type
    else:
        # Interactive prompt — ask the user which style they want.
        resolved_type = choice(
            msg="Select configuration type",
            choices=[
                PROFILE_TYPE_API_KEY,
                PROFILE_TYPE_AUTH_FLOW,
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
            # auth_flow, since we are now explicitly creating an api_key profile.
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

    # >>> For auth_flow profiles: just store the metadata; no API key needed.

    else:
        if profile is None:
            config[PROFILE_TYPE_KEY] = PROFILE_TYPE_AUTH_FLOW
            config[ENDPOINT_KEY] = endpoint
            # Remove any previously stored api_key from the default profile.
            config.pop(API_KEY_KEY, None)
        else:
            if profile not in config:
                config[profile] = {}
            config[profile][PROFILE_TYPE_KEY] = PROFILE_TYPE_AUTH_FLOW
            config[profile][ENDPOINT_KEY] = endpoint
            config[profile].pop(API_KEY_KEY, None)

        save_config(config)

        success("Configuration saved successfully.")
        message(f"[bold]Profile[/bold]: [magenta]{profile or 'Default'}[/magenta]", indents=1)
        message(f"[bold]Type[/bold]: [magenta]{PROFILE_TYPE_AUTH_FLOW}[/magenta]", indents=1)
        if endpoint != DEFAULT_ENDPOINT:
            message(f"[bold]Endpoint[/bold]: [magenta]{endpoint}[/magenta]", indents=1)
        message(
            "Run [code]nextmv login[/code]" + (f" --profile {profile}" if profile else "") + " to authenticate.",
            indents=1,
        )
