"""
This module defines the configuration create command for the Nextmv CLI.
"""

from typing import Annotated

import typer

from nextmv.cli.configuration.config import (
    API_KEY_KEY,
    DEFAULT_ENDPOINT,
    ENDPOINT_KEY,
    load_config,
    obscure_api_key,
    save_config,
)
from nextmv.cli.message import error, info, success

# Set up subcommand application.
app = typer.Typer()


@app.command()
def create(
    api_key: Annotated[
        str,
        typer.Option(
            "--api-key",
            "-a",
            help="A valid Nextmv Cloud API key. "
            + "Get one from [link=https://cloud.nextmv.io][bold]https://cloud.nextmv.io[/bold][/link].",
            envvar="NEXTMV_API_KEY",
            metavar="NEXTMV_API_KEY",
        ),
    ],
    endpoint: Annotated[  # Hidden because it is meant for internal use.
        str | None,
        typer.Option(
            "--endpoint",
            "-e",
            hidden=True,
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
) -> None:
    """
    Create a new configuration or update an existing one.

    [bold][underline]Examples[/underline][/bold]

    - Default configuration.
        $ [dim]nextmv configuration create --api-key NEXTMV_API_KEY[/dim]

    - Configure a profile named [magenta]hare[/magenta].
        $ [dim]nextmv configuration create --api-key NEXTMV_API_KEY --profile hare[/dim]
    """

    if profile is not None and profile.strip().lower() == "default":
        error("[magenta]default[/magenta] is a reserved profile name.")

    endpoint = str(endpoint)
    if endpoint.startswith("https://"):
        endpoint = endpoint[len("https://") :]
    elif endpoint.startswith("http://"):
        endpoint = endpoint[len("http://") :]

    config = load_config()

    if profile is None:
        config[API_KEY_KEY] = api_key
        config[ENDPOINT_KEY] = endpoint
    else:
        if profile not in config:
            config[profile] = {}

        config[profile][API_KEY_KEY] = api_key
        config[profile][ENDPOINT_KEY] = endpoint

    save_config(config)

    success("Configuration saved successfully.")
    info(f"\t[bold]Profile[/bold]: {profile or 'Default'}")
    info(f"\t[bold]API Key[/bold]: {obscure_api_key(api_key)}")
    if endpoint != DEFAULT_ENDPOINT:
        info(f"\t[bold]Endpoint[/bold]: {endpoint}")
