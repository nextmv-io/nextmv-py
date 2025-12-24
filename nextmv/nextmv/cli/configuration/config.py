"""
This module contains configuration utilities for the Nextmv CLI.
"""

from pathlib import Path
from typing import Any

import yaml

from nextmv.cli.error import error
from nextmv.cloud.client import Client

# Some useful constants.
CONFIG_DIR = Path.home() / ".nextmv"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
API_KEY_KEY = "apikey"
ENDPOINT_KEY = "endpoint"
DEFAULT_ENDPOINT = "api.cloud.nextmv.io"
GO_CLI_PATH = CONFIG_DIR / "nextmv"


def load_config() -> dict[str, Any]:
    """
    Load the current configuration from the config file. Returns an empty
    dictionary if no configuration file exists.

    Returns
    -------
    dict[str, Any]
        The current configuration as a dictionary.
    """

    if not CONFIG_FILE.exists():
        return {}

    with CONFIG_FILE.open() as file:
        config = yaml.safe_load(file)

    if config is None:
        return {}
    return config


def save_config(config: dict[str, Any]) -> None:
    """
    Save the given configuration to the config file.

    Parameters
    ----------
    config : dict[str, Any]
        The configuration to save.
    """

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with CONFIG_FILE.open("w") as file:
        yaml.safe_dump(config, file)


def build_client(profile: str | None = None) -> Client:
    """
    Builds a `cloud.Client` using the API key and endpoint for the given
    profile. If no profile is given, the default profile is used. If either the
    API key or endpoint is missing, an exception is raised. If the config is
    not available, an exception is raised.

    Parameters
    ----------
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    Client
        A client configured with the API key and endpoint for the selected
        profile or the default configuration.

    Raises
    ------
    typer.Exit
        If no configuration is found, if the requested profile does not exist,
        or if the API key or endpoint (for either the selected profile or the
        default configuration) is not set or is empty.
    """

    config = load_config()
    if config == {}:
        error("No configuration found. Please run [code]nextmv configuration create[/code].")

    if profile is not None:
        if profile not in config:
            error(f"Profile [bold magenta]{profile}[/bold magenta] does not exist.")

        api_key = config[profile].get(API_KEY_KEY)
        if api_key is None or api_key == "":
            error(f"API key for profile [bold magenta]{profile}[/bold magenta] is not set or is empty.")

        endpoint = config[profile].get(ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            error(f"Endpoint for profile [bold magenta]{profile}[/bold magenta] is not set or is empty.")
    else:
        api_key = config.get(API_KEY_KEY)
        if api_key is None or api_key == "":
            error("Default API key is not set or is empty.")

        endpoint = config.get(ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            error("Default endpoint is not set or is empty.")

    return Client(api_key=api_key, url=f"https://{endpoint}")


def obscure_api_key(api_key: str) -> str:
    """
    Obscure an API key for display purposes.

    Parameters
    ----------
    api_key : str
        The API key to obscure.

    Returns
    -------
    str
        The obscured API key.
    """

    if len(api_key) <= 4:
        return "*" * len(api_key)

    return api_key[:2] + "*" * 4 + api_key[-2:]
