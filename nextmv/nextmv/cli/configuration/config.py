"""
This module contains configuration utilities for the Nextmv CLI.
"""

from pathlib import Path
from typing import Any

import yaml

from nextmv.cli.confirm import get_confirmation
from nextmv.cli.message import error, success, warning
from nextmv.cloud.account import Account
from nextmv.cloud.application import Application
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


def non_profile_keys() -> set[str]:
    """
    Returns the set of keys that are not profile names in the configuration.

    Returns
    -------
    set[str]
        The set of non-profile keys.
    """
    return {API_KEY_KEY, ENDPOINT_KEY}


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
            error(
                f"Profile [magenta]{profile}[/magenta] does not exist. "
                "Create it using [code]nextmv configuration create[/code] with the --profile option."
            )

        api_key = config[profile].get(API_KEY_KEY)
        if api_key is None or api_key == "":
            error(
                f"API key for profile [magenta]{profile}[/magenta] is not set or is empty. "
                "Set it using [code]nextmv configuration create[/code] with the --profile and --api-key options."
            )

        endpoint = config[profile].get(ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            error(
                f"Endpoint for profile [magenta]{profile}[/magenta] is not set or is empty. "
                "Please run [code]nextmv configuration create[/code]."
            )
    else:
        api_key = config.get(API_KEY_KEY)
        if api_key is None or api_key == "":
            error(
                "Default API key is not set or is empty. "
                "Please run [code]nextmv configuration create[/code] with the --api-key option."
            )

        endpoint = config.get(ENDPOINT_KEY)
        if endpoint is None or endpoint == "":
            error("Default endpoint is not set or is empty. Please run [code]nextmv configuration create[/code].")

    return Client(api_key=api_key, url=f"https://{endpoint}")


def build_app(app_id: str, profile: str | None = None) -> Application:
    """
    Builds a `cloud.Application` using the given application ID and the API
    key and endpoint for the given profile. If no profile is given, the default
    profile is used. If the application does not exist, an exception is raised.

    Parameters
    ----------
    app_id : str
        The application ID.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    Application
        An application object for the given application ID.

    Raises
    ------
    typer.Exit
        If the application does not exist.
    """
    client = build_client(profile)
    exists = Application.exists(client=client, id=app_id)
    if exists:
        return Application(client=client, id=app_id)

    warning(f"Application with ID [magenta]{app_id}[/magenta] does not exist.")
    should_create = get_confirmation(f"Do you want to create a new application with ID [magenta]{app_id}[/magenta]?")
    if not should_create:
        error(
            f"Application with ID [magenta]{app_id}[/magenta] was not created and does not exist. "
            "Use [code]nextmv cloud app create[/code] to create a new app."
        )

    app = Application.new(client=client, id=app_id, name=app_id)
    success(f"Application with ID and name [magenta]{app_id}[/magenta] created successfully.")

    return app


def build_account(account_id: str | None = None, profile: str | None = None) -> Account:
    """
    Builds a `cloud.Account` using the API key and endpoint for the given
    profile. If no profile is given, the default profile is used.

    Parameters
    ----------
    account_id : str | None
        The account ID. If None, no account ID is set.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    Account
        An account object for the configured profile.

    Raises
    ------
    typer.Exit
        If the configuration is invalid or missing.
    """

    client = build_client(profile)

    return Account(account_id=account_id, client=client)


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
