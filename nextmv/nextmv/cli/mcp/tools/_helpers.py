"""Shared helpers for MCP tool modules."""

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from nextmv import local
from nextmv.cloud import Application, Client

# Session-level profile. None means "default" (top-level config keys).
_current_profile: str | None = None


def _mask_key(key: str | None) -> str | None:
    """Mask an API key, keeping only the last 4 characters visible."""

    if not key:
        return None
    if len(key) <= 4:
        return key
    return "X" * (len(key) - 4) + key[-4:]


def _get_client(profile: str | None = None) -> Client:
    """Build a Nextmv Cloud client from env var or CLI config.

    Checks for credentials in the following order:

    1. ``NEXTMV_API_KEY`` environment variable (unless a profile is active).
    2. CLI configuration file at ``~/.nextmv/config.yaml``.

    Args:
        profile: Optional profile name override. If not provided, uses
            the session-level ``_current_profile``.
    """

    resolved = profile or _current_profile

    api_key = os.getenv("NEXTMV_API_KEY")
    if api_key and not resolved:
        endpoint = os.getenv("NEXTMV_ENDPOINT", "https://api.cloud.nextmv.io")
        if not endpoint.startswith("http"):
            endpoint = f"https://{endpoint}"
        return Client(api_key=api_key, url=endpoint)

    # Fall back to the CLI configuration file (~/.nextmv/config.yaml).
    try:
        from nextmv.cli.configuration.config import build_client

        # "default" means use top-level keys (profile=None in build_client).
        p = None if resolved is None or resolved == "default" else resolved
        return build_client(profile=p)
    except Exception as e:
        raise ValueError(
            "No Nextmv API key found. Either set the NEXTMV_API_KEY "
            "environment variable or configure the CLI with: "
            "nextmv configuration create"
        ) from e


def _get_app(app_id: str, profile: str | None = None) -> Application:
    """Build a cloud Application handle for the given ID."""

    client = _get_client(profile=profile)
    return Application(client=client, id=app_id)


def _get_local_app(app_dir: str, app_id: str | None = None) -> local.Application:
    """Build a local Application, registering it if needed."""

    app, _ = local.Application.get_or_register(app_src=app_dir, app_id=app_id)
    return app


def _build_run_configuration(content_format: str | None):
    """Build a RunConfiguration for the given content format string, or None."""

    if content_format is None:
        return None

    from nextmv.input import InputFormat
    from nextmv.run import Format, FormatInput, RunConfiguration

    config = RunConfiguration()
    config.format = Format(
        format_input=FormatInput(
            input_type=InputFormat(content_format),
        ),
    )
    return config


def _none_if_empty(value: str | None) -> str | None:
    """Convert empty or whitespace-only strings to None.

    LLMs sometimes pass ``""`` instead of omitting optional parameters.
    This normalises empty strings so downstream code sees ``None``.
    Whitespace-only strings (e.g. ``"  "``) are also treated as empty.
    """

    if value is None or not value.strip():
        return None
    return value.strip()


def _require_non_empty(value: str, name: str) -> str:
    """Raise a clear error when a required string parameter is empty."""

    if not value or not value.strip():
        raise ValueError(f"'{name}' is required and must not be empty.")
    return value.strip()


def _save_to_file(data: Any, prefix: str) -> str:
    """Serialize data to a temp JSON file and return a message with the path.

    This keeps large payloads out of the MCP response (and thus out of
    the LLM context window). The caller can selectively read the file
    using standard file-reading tools.
    """

    fd, path = tempfile.mkstemp(suffix=".json", prefix=f"{prefix}_")
    with os.fdopen(fd, "w") as fh:
        json.dump(data, fh, indent=2)
    return f"Data saved to {path} — use file-reading tools to inspect the contents."


def _cloud_run_dir(endpoint: str, run_id: str) -> str:
    """Build the local cache directory for a cloud run.

    Returns ``~/.nextmv/runs/{endpoint}/{run_id}``. The *endpoint*
    parameter should already have the URL scheme (``https://`` /
    ``http://``) stripped.
    """

    return str(Path.home() / ".nextmv" / "runs" / endpoint / run_id)


def _cloud_run_file_exists(endpoint: str, run_id: str, *path_parts: str) -> str | None:
    """Return the file path if a cached cloud run file exists, else None.

    Args:
        endpoint: API endpoint with scheme stripped.
        run_id: The run ID.
        *path_parts: Path components relative to the run directory
            (e.g. ``"inputs", "input.json"``).
    """

    path = os.path.join(_cloud_run_dir(endpoint, run_id), *path_parts)
    return path if os.path.exists(path) else None


def _endpoint_from_app(app: Application) -> str:
    """Return the API endpoint from an Application with scheme stripped."""

    url: str = app.client.url
    for scheme in ("https://", "http://"):
        if url.startswith(scheme):
            url = url[len(scheme):]
            break
    return url


def _save_cloud_run_file(data: Any, endpoint: str, run_id: str, *path_parts: str) -> str:
    """Serialize *data* as JSON into the cloud run cache and return the path.

    Creates intermediate directories as needed. The *endpoint* parameter
    should already have the URL scheme stripped.
    """

    path = os.path.join(_cloud_run_dir(endpoint, run_id), *path_parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=2)
    return path
