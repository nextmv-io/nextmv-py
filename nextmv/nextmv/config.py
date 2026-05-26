"""
Configuration constants and helpers shared across the Nextmv SDK.

This module is intentionally free of CLI dependencies so that it can be
imported by both ``nextmv.cloud`` and ``nextmv.cli`` without coupling.

Constants
---------
CONFIG_DIR
    ``~/.nextmv/`` — the root directory for all Nextmv local configuration.
CONFIG_FILE
    ``~/.nextmv/config.yaml`` — the main configuration file.
API_KEY_KEY
    The YAML key used to store the API key in a profile (``"apikey"``).
ENDPOINT_KEY
    The YAML key used to store the endpoint in a profile (``"endpoint"``).
PROFILE_TYPE_KEY
    The YAML key used to store the profile type (``"profile_type"``).
PROFILE_TYPE_API_KEY
    Profile type value for API-key-based authentication (``"api_key"``).
PROFILE_TYPE_PKCE
    Profile type value for PKCE/OAuth2-based authentication (``"pkce"``).
DEFAULT_ENDPOINT
    The default API endpoint (``"api.cloud.nextmv.io"``).
"""

from pathlib import Path
from typing import Any

import yaml

# Paths
CONFIG_DIR = Path.home() / ".nextmv"
CONFIG_FILE = CONFIG_DIR / "config.yaml"

# Config keys
API_KEY_KEY = "apikey"
ENDPOINT_KEY = "endpoint"
PROFILE_TYPE_KEY = "profile_type"

# Profile type values
PROFILE_TYPE_API_KEY = "api_key"
PROFILE_TYPE_PKCE = "pkce"

# Defaults
DEFAULT_ENDPOINT = "api.cloud.nextmv.io"


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
    Returns the set of top-level config keys that are not profile names.

    Returns
    -------
    set[str]
        The set of non-profile keys.
    """
    return {API_KEY_KEY, ENDPOINT_KEY, PROFILE_TYPE_KEY}


def get_profile_type(config: dict, profile: str | None) -> str:
    """
    Returns the profile type for the given profile. Defaults to
    ``PROFILE_TYPE_API_KEY`` if the key is absent (backwards compatible).

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.
    profile : str | None
        The profile name. If None, the default (top-level) profile is used.

    Returns
    -------
    str
        Either ``PROFILE_TYPE_API_KEY`` or ``PROFILE_TYPE_PKCE`` (``"pkce"``).
    """
    if profile is None:
        return config.get(PROFILE_TYPE_KEY, PROFILE_TYPE_API_KEY)
    profile_data = config.get(profile, {})
    if not isinstance(profile_data, dict):
        return PROFILE_TYPE_API_KEY
    return profile_data.get(PROFILE_TYPE_KEY, PROFILE_TYPE_API_KEY)


def list_pkce_profiles(config: dict) -> list[str | None]:
    """
    Returns a list of profile names (or ``None`` for the default profile)
    whose profile type is ``pkce``.

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.

    Returns
    -------
    list[str | None]
        A list where each entry is either a named profile string or ``None``
        (representing the default profile).
    """
    result: list[str | None] = []
    if config.get(PROFILE_TYPE_KEY) == PROFILE_TYPE_PKCE:
        result.append(None)
    skip = non_profile_keys()
    for key, value in config.items():
        if key in skip:
            continue
        if isinstance(value, dict) and value.get(PROFILE_TYPE_KEY) == PROFILE_TYPE_PKCE:
            result.append(key)
    return result
