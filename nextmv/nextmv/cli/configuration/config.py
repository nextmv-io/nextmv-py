"""
This module contains configuration utilities for the Nextmv CLI.

Shared configuration constants and pure helpers (profile type resolution,
load/save, etc.) live in ``nextmv.config``.  This module re-exports the
symbols that CLI sub-commands commonly need, and adds CLI-specific helpers
(``build_*``, ``obscure_api_key``) that depend on typer and cloud objects.
"""

import platform
from pathlib import Path

from nextmv import cloud, local
from nextmv.cli.message import confirmation, error, info, success, warning
from nextmv.cloud.account import Account
from nextmv.cloud.client import Client
from nextmv.cloud.marketplace import MarketplaceApplication, MarketplaceSubscription
from nextmv.cloud.sso import SSOConfiguration
from nextmv.config import (
    CONFIG_DIR,
)

# Path to the obsolete Go CLI binary.
GO_CLI_PATH = CONFIG_DIR / "nextmv"
if platform.system() == "Windows":
    GO_CLI_PATH = Path(str(GO_CLI_PATH) + ".exe")


def build_cloud_app(app_id: str, profile: str | None = None) -> tuple[cloud.Application, bool]:
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
    tuple[cloud.Application, bool]
        A tuple containing the application object for the given application ID
        and a boolean indicating whether the application was newly created.

    Raises
    ------
    typer.Exit
        If the application does not exist.
    """

    client = Client(profile=profile)
    exists = cloud.Application.exists(client=client, id=app_id)
    if exists:
        return cloud.Application(client=client, id=app_id), False

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

    return app, True


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

    client = Client(profile=profile)
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

    client = Client(profile=profile)
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

    client = Client(profile=profile)

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

    client = Client(profile=profile)

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
