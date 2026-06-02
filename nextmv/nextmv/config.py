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
SESSIONS_FILE
    ``~/.nextmv/sessions.yaml`` — per-endpoint OIDC configuration.  Each top-
    level key is an endpoint hostname (e.g. ``api.cloud.nextmv.io``) and the
    value is a mapping with ``oidc_discovery_url`` and ``client_id``.  The
    production endpoint ``api.cloud.nextmv.io`` is always available as a
    built-in fallback, sourced from :data:`nextmv.auth.OIDC_DISCOVERY_URL` and
    :data:`nextmv.auth.CLIENT_ID`.
API_KEY_KEY
    The YAML key used to store the API key in a profile (``"apikey"``).
ENDPOINT_KEY
    The YAML key used to store the endpoint in a profile (``"endpoint"``).
AUTH_TYPE_KEY
    The YAML key used to store the authentication type in a profile
    (``"auth_type"``).
AUTH_SESSION_KEY
    The YAML key used to store the auth session name in a profile
    (``"auth_session"``).  When present on a ``pkce`` profile, tokens are
    shared with all other profiles that reference the same session name,
    allowing a single browser login to cover multiple profiles.  When absent,
    the ``"default"`` session is used.
TEAM_ID_KEY
    The YAML key used to store the team (organization) UUID in a ``pkce``
    profile (``"team_id"``).  The value is sent as the ``nextmv-account``
    request header so the API can scope requests to the correct team.
OIDC_DISCOVERY_URL_KEY
    The YAML key used in ``sessions.yaml`` to store the OIDC discovery URL for
    an endpoint (``"oidc_discovery_url"``).
CLIENT_ID_KEY
    The YAML key used in ``sessions.yaml`` to store the OAuth2 client ID for
    an endpoint (``"client_id"``).
AUTH_TYPE_API_KEY
    Auth type value for API-key-based authentication (``"api_key"``).
AUTH_TYPE_PKCE
    Auth type value for PKCE/OAuth2-based authentication (``"pkce"``).
DEFAULT_AUTH_SESSION
    The reserved session name used when ``auth_session`` is not specified
    (``"default"``).  This name cannot be used as a profile name.
DEFAULT_ENDPOINT
    The default API endpoint (``"api.cloud.nextmv.io"``).
"""

from pathlib import Path
from typing import Any

import yaml

from nextmv.auth import CLIENT_ID as _AUTH_CLIENT_ID
from nextmv.auth import OIDC_DISCOVERY_URL as _AUTH_OIDC_DISCOVERY_URL

# Paths
CONFIG_DIR = Path.home() / ".nextmv"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
SESSIONS_FILE = CONFIG_DIR / "sessions.yaml"

# Config keys
API_KEY_KEY = "apikey"
ENDPOINT_KEY = "endpoint"
AUTH_TYPE_KEY = "auth_type"
AUTH_SESSION_KEY = "auth_session"
TEAM_ID_KEY = "team_id"

# Sessions keys
OIDC_DISCOVERY_URL_KEY = "oidc_discovery_url"
CLIENT_ID_KEY = "client_id"

# Auth type values
AUTH_TYPE_API_KEY = "api_key"
AUTH_TYPE_PKCE = "pkce"

# Defaults
DEFAULT_AUTH_SESSION = "default"
DEFAULT_ENDPOINT = "api.cloud.nextmv.io"

# Built-in OIDC config for known endpoints.  These are used as a fallback when
# the endpoint is not present in sessions.yaml, so existing users don't need to
# re-run `nextmv configuration create` after upgrading.
# Values are sourced from auth.OIDC_DISCOVERY_URL and auth.CLIENT_ID so there
# is a single source of truth.
_BUILTIN_OIDC: dict[str, dict[str, str]] = {
    DEFAULT_ENDPOINT: {
        OIDC_DISCOVERY_URL_KEY: _AUTH_OIDC_DISCOVERY_URL,
        CLIENT_ID_KEY: _AUTH_CLIENT_ID,
    },
}


def _strip_scheme(url: str) -> str:
    """Strip a leading ``https://`` or ``http://`` scheme and trailing slash."""
    s = url.strip()
    for prefix in ("https://", "http://"):
        if s.startswith(prefix):
            s = s[len(prefix):]
            break
    return s.rstrip("/")


_OIDC_DISCOVERY_SUFFIX = "/.well-known/openid-configuration"


def _normalize_oidc_discovery_url(url: str) -> str:
    """Append the OIDC discovery suffix if not already present.

    Allows users to store the shorter base URL in ``sessions.yaml`` (e.g.
    ``https://cognito-idp.us-east-1.amazonaws.com/us-east-1_abc123``) and
    have the full discovery URL resolved automatically.
    """
    stripped = url.strip().rstrip("/")
    if stripped.endswith(_OIDC_DISCOVERY_SUFFIX):
        return stripped
    return stripped + _OIDC_DISCOVERY_SUFFIX


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

    return config if isinstance(config, dict) else {}


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


def load_sessions() -> dict[str, Any]:
    """
    Load the sessions configuration from ``~/.nextmv/sessions.yaml``.

    Returns an empty dictionary if the file does not exist.  The returned dict
    is keyed by endpoint hostname; each value is a mapping with at least
    ``oidc_discovery_url`` and ``client_id``.

    Returns
    -------
    dict[str, Any]
        The sessions configuration, or ``{}`` if the file is absent.
    """
    if not SESSIONS_FILE.exists():
        return {}

    with SESSIONS_FILE.open() as fh:
        data = yaml.safe_load(fh)

    return data if isinstance(data, dict) else {}


def save_sessions(sessions: dict[str, Any]) -> None:
    """
    Persist the sessions configuration to ``~/.nextmv/sessions.yaml``.

    Parameters
    ----------
    sessions : dict[str, Any]
        The full sessions mapping to write, keyed by endpoint hostname.
    """
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    with SESSIONS_FILE.open("w") as fh:
        yaml.safe_dump(sessions, fh)


def get_endpoint_oidc_config(endpoint: str, sessions: dict[str, Any] | None = None) -> dict[str, str] | None:
    """
    Return the OIDC configuration (``oidc_discovery_url`` and ``client_id``)
    for *endpoint*.

    Lookup order:

    1. *sessions* (the caller-supplied dict, typically loaded from
       ``sessions.yaml``).
    2. The built-in fallback table :data:`_BUILTIN_OIDC` — covers
       ``api.cloud.nextmv.io`` so that existing users don't need to re-run
       ``nextmv configuration create``.

    Parameters
    ----------
    endpoint : str
        The endpoint hostname, e.g. ``"api.cloud.nextmv.io"``.  Leading
        ``https://`` or ``http://`` are stripped automatically.
    sessions : dict[str, Any] | None
        The sessions mapping loaded from ``sessions.yaml``.  Pass ``None`` (or
        omit) to skip the file lookup and rely solely on the built-in table.

    Returns
    -------
    dict[str, str] | None
        A dict with ``oidc_discovery_url`` and ``client_id`` keys, or ``None``
        if the endpoint is not known.
    """
    # Normalise the endpoint to a bare hostname.
    ep = _strip_scheme(endpoint)

    if sessions:
        entry = sessions.get(ep)
        if isinstance(entry, dict):
            url = entry.get(OIDC_DISCOVERY_URL_KEY)
            cid = entry.get(CLIENT_ID_KEY)
            if url and cid:
                return {OIDC_DISCOVERY_URL_KEY: _normalize_oidc_discovery_url(url), CLIENT_ID_KEY: cid}

    return _BUILTIN_OIDC.get(ep)


def non_profile_keys() -> set[str]:
    """
    Returns the set of top-level config keys that are not profile names.

    Returns
    -------
    set[str]
        The set of non-profile keys.
    """
    return {API_KEY_KEY, ENDPOINT_KEY, AUTH_TYPE_KEY, AUTH_SESSION_KEY, TEAM_ID_KEY, DEFAULT_AUTH_SESSION}


def get_auth_type(config: dict, profile: str | None) -> str:
    """
    Returns the auth type for the given profile. Defaults to
    ``AUTH_TYPE_API_KEY`` if the key is absent (backwards compatible).

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.
    profile : str | None
        The profile name. If None, the default (top-level) profile is used.

    Returns
    -------
    str
        Either ``AUTH_TYPE_API_KEY`` or ``AUTH_TYPE_PKCE`` (``"pkce"``).
    """
    if profile is None:
        return config.get(AUTH_TYPE_KEY, AUTH_TYPE_API_KEY)
    profile_data = config.get(profile, {})
    if not isinstance(profile_data, dict):
        return AUTH_TYPE_API_KEY
    return profile_data.get(AUTH_TYPE_KEY, AUTH_TYPE_API_KEY)


def get_auth_session(config: dict, profile: str | None) -> str:
    """
    Returns the auth session name to use for token storage for *profile*.

    When ``auth_session`` is explicitly set on the profile, that value is
    returned.  Otherwise the reserved ``DEFAULT_AUTH_SESSION`` (``"default"``)
    is returned, meaning that all profiles without an explicit session share a
    single set of tokens.  This is the expected UX for users who have only one
    Nextmv identity.

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.
    profile : str | None
        The profile name.  If ``None``, the default (top-level) profile is
        used.

    Returns
    -------
    str
        The session name (never empty; falls back to ``DEFAULT_AUTH_SESSION``).
    """
    if profile is None:
        raw = config.get(AUTH_SESSION_KEY)
    else:
        profile_data = config.get(profile, {})
        raw = profile_data.get(AUTH_SESSION_KEY) if isinstance(profile_data, dict) else None

    if raw and isinstance(raw, str) and raw.strip():
        return raw.strip()
    return DEFAULT_AUTH_SESSION


def get_team_id(config: dict, profile: str | None) -> str | None:
    """
    Returns the team (organization) UUID stored in *profile*, or ``None`` if
    not set.

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.
    profile : str | None
        The profile name.  If ``None``, the default (top-level) profile is
        used.

    Returns
    -------
    str | None
        The team UUID, or ``None`` when the key is absent or the profile is
        not a ``pkce`` profile.
    """
    if profile is None:
        raw = config.get(TEAM_ID_KEY)
    else:
        profile_data = config.get(profile, {})
        raw = profile_data.get(TEAM_ID_KEY) if isinstance(profile_data, dict) else None

    if raw and isinstance(raw, str) and raw.strip():
        return raw.strip()
    return None


def get_profile_endpoint(config: dict, profile: str | None) -> str:
    """
    Returns the endpoint hostname for *profile*.

    Parameters
    ----------
    config : dict
        The full configuration dictionary loaded from config.yaml.
    profile : str | None
        The profile name.  If ``None``, the default (top-level) profile is
        used.

    Returns
    -------
    str
        The endpoint hostname, falling back to ``DEFAULT_ENDPOINT`` when not
        set.
    """
    if profile is None:
        ep = config.get(ENDPOINT_KEY, DEFAULT_ENDPOINT)
    else:
        profile_data = config.get(profile, {})
        ep = profile_data.get(ENDPOINT_KEY, DEFAULT_ENDPOINT) if isinstance(profile_data, dict) else DEFAULT_ENDPOINT

    if ep is None:
        return DEFAULT_ENDPOINT
    return _strip_scheme(str(ep)) or DEFAULT_ENDPOINT


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
    if config.get(AUTH_TYPE_KEY) == AUTH_TYPE_PKCE:
        result.append(None)
    skip = non_profile_keys()
    for key, value in config.items():
        if key in skip:
            continue
        if isinstance(value, dict) and value.get(AUTH_TYPE_KEY) == AUTH_TYPE_PKCE:
            result.append(key)
    return result
