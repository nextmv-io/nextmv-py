"""
This module contains configuration utilities for the Nextmv CLI.
"""

from pathlib import Path
from typing import Any

import yaml

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
