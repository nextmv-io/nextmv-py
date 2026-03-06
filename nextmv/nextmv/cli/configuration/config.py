"""
This module contains configuration utilities for the Nextmv CLI.
"""

from pathlib import Path
from typing import Any

import yaml

from nextmv import cloud, local
from nextmv.cli.message import confirmation, error, info, success, warning
from nextmv.cloud.account import Account
from nextmv.cloud.client import Client
from nextmv.cloud.marketplace import MarketplaceApplication, MarketplaceSubscription
from nextmv.cloud.sso import SSOConfiguration

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


def build_cloud_app(app_id: str, profile: str | None = None) -> cloud.Application:
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
    cloud.Application
        An application object for the given application ID.

    Raises
    ------
    typer.Exit
        If the application does not exist.
    """

    client = build_client(profile)
    exists = cloud.Application.exists(client=client, id=app_id)
    if exists:
        return cloud.Application(client=client, id=app_id)

    warning(f"Cloud application with ID [magenta]{app_id}[/magenta] does not exist.")
    should_create = confirmation(
        f"Do you want to create a new Cloud application with ID [magenta]{app_id}[/magenta]?",
        default=True,
    )
    if not should_create:
        error(
            f"Cloud application with ID [magenta]{app_id}[/magenta] was not created and does not exist. "
            "Use [code]nextmv cloud app create[/code] to create a new Cloud app."
        )

    app = cloud.Application.new(client=client, id=app_id, name=app_id)
    success(f"Cloud application with ID and name [magenta]{app_id}[/magenta] created successfully.")

    return app


def build_marketplace_app(app_id: str, partner_id: str, profile: str | None = None) -> MarketplaceApplication:
    """
    Builds a `cloud.MarketplaceApplication` using the given application ID,
    partner ID, and the API key and endpoint for the given profile. If no
    profile is given, the default profile is used. If the application does not
    exist, an exception is raised.

    Parameters
    ----------
    app_id : str
        The marketplace application ID.
    partner_id : str
        The partner ID.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    MarketplaceApplication
        A marketplace application object for the given application ID and
        partner ID.

    Raises
    ------
    typer.Exit
        If the marketplace application does not exist.
    """

    client = build_client(profile)
    try:
        return MarketplaceApplication.get(
            client=client,
            partner_id=partner_id,
            app_id=app_id,
        )
    except Exception as e:
        error(
            f"There was an issue retrieving the Marketplace application with ID [magenta]{app_id}[/magenta] "
            f"and partner ID [magenta]{partner_id}[/magenta]: {e}. "
            "Use [code]nextmv cloud marketplace app create[/code] to create a new app."
        )


def build_marketplace_subscription(subscription_id: str, profile: str | None = None) -> MarketplaceSubscription:
    """
    Builds a `cloud.MarketplaceSubscription` using the given subscription ID and
    the API key and endpoint for the given profile. If no profile is given, the
    default profile is used. If the subscription does not exist, an exception is
    raised.

    Parameters
    ----------
    subscription_id : str
        The marketplace subscription ID.
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    MarketplaceSubscription
        A marketplace subscription object for the given subscription ID.

    Raises
    ------
    typer.Exit
        If the marketplace subscription does not exist.
    """

    client = build_client(profile)
    try:
        return MarketplaceSubscription.get(client=client, subscription_id=subscription_id)
    except Exception as e:
        error(
            "There was an issue retrieving the Marketplace subscription "
            f"with ID [magenta]{subscription_id}[/magenta]: {e}"
        )


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


def build_sso_config(profile: str | None = None) -> SSOConfiguration:
    """
    Builds a `cloud.SSOConfiguration` using the API key and endpoint for the given
    profile. If no profile is given, the default profile is used.

    Parameters
    ----------
    profile : str | None
        The profile name to use. If None, the default profile is used.

    Returns
    -------
    SSOConfiguration
        An SSOConfiguration object for the configured profile.

    Raises
    ------
    typer.Exit
        If the configuration is invalid or missing.
    """

    client = build_client(profile)

    return SSOConfiguration(client=client)


def build_local_app(app_src: str, app_id: str | None) -> local.Application:
    """
    Builds a local application by either retrieving it from the registry if it
    is already registered, or registering it if it is not.

    Parameters
    ----------
    app_src : str
        The source path of the local application.
    app_id : str | None
        The ID of the local application. If None, the application will be registered
        without an ID and a random one will be generated.

    Returns
    -------
    local.Application
        The local application instance.
    """

    local_app, registered = local.Application.get_or_register(app_src=app_src, app_id=app_id)
    if registered:
        info(
            f"Application at path [magenta]{local_app.src}[/magenta] registered locally with "
            f"ID [magenta]{local_app.app_id}[/magenta]."
        )

    return local_app


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
