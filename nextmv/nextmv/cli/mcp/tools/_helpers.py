"""Shared helpers for MCP tool modules."""

import json
import os
import tempfile
from typing import Any

from nextmv import local
from nextmv.cloud import Application, Client
from nextmv.content_format import ContentFormat
from nextmv.local.executor import process_run_visuals
from nextmv.local.local import LOGS_FILE, LOGS_KEY
from nextmv.logger import log
from nextmv.output import ASSETS_KEY, METRICS_KEY, OUTPUTS_KEY, SOLUTIONS_KEY, STATISTICS_KEY
from nextmv.run import Format, FormatInput, RunConfiguration

DEFAULT_NEXTMV_ENDPOINT = "https://api.cloud.nextmv.io"


class ProfileSession:
    """Manages the active Nextmv Cloud profile for the MCP session.

    Stores the profile as a plain instance attribute so that the value
    set by ``cloud_set_profile`` persists across all subsequent tool calls
    within the same server process.
    """

    def __init__(self) -> None:
        self._profile: str | None = None

    @property
    def profile(self) -> str | None:
        """Return the current profile name, or ``None`` for the default."""

        return self._profile

    @profile.setter
    def profile(self, value: str | None) -> None:
        self._profile = value

    def get_client(self, profile: str | None = None) -> Client:
        """Build a Nextmv Cloud client from env var or CLI config.

        Checks for credentials in the following order:

        1. ``NEXTMV_API_KEY`` environment variable (unless a profile is active).
        2. CLI configuration file at ``~/.nextmv/config.yaml``.

        Args:
            profile: Optional profile name override. If not provided, uses
                the session-level profile.
        """

        resolved = profile or self.profile

        api_key = os.getenv("NEXTMV_API_KEY")
        if api_key and not resolved:
            endpoint = os.getenv("NEXTMV_ENDPOINT", DEFAULT_NEXTMV_ENDPOINT)
            if not endpoint.startswith("http"):
                endpoint = f"https://{endpoint}"
            return Client(api_key=api_key, url=endpoint)

        # Fall back to the CLI configuration file (~/.nextmv/config.yaml).
        try:
            # "default" means use top-level keys (profile=None in Client).
            p = None if resolved is None or resolved == "default" else resolved
            return Client(profile=p)
        except Exception as e:
            raise ValueError(
                f"Could not build a Nextmv client: {e}. Either set the "
                "NEXTMV_API_KEY environment variable or configure the "
                "CLI with: nextmv configuration create"
            ) from e

    def get_app(self, app_id: str, profile: str | None = None) -> Application:
        """Build a cloud Application handle for the given ID."""

        client = self.get_client(profile=profile)
        return Application(client=client, id=app_id)


# Singleton session used by all MCP tool modules.
session = ProfileSession()


def _mask_key(key: str | None) -> str | None:
    """Mask an API key, keeping only the last 4 characters visible."""

    if not key:
        return None
    if len(key) <= 4:
        return "X" * len(key)
    return "X" * (len(key) - 4) + key[-4:]


# ---------------------------------------------------------------------------
# Convenience aliases so tool modules can call ``_helpers._get_client()``
# without reaching into ``session`` directly.
# ---------------------------------------------------------------------------


def _get_client(profile: str | None = None) -> Client:
    return session.get_client(profile=profile)


def _get_app(app_id: str, profile: str | None = None) -> Application:
    return session.get_app(app_id=app_id, profile=profile)


def _get_local_app(app_dir: str, app_id: str | None = None) -> local.Application:
    """Build a local Application, registering it if needed."""

    app, _ = local.Application.get_or_register(app_src=app_dir, app_id=app_id)
    return app


_VALID_CONTENT_FORMATS = {f.value for f in ContentFormat}


def _validate_content_format(content_format: str) -> None:
    """Raise ``ValueError`` if *content_format* is not a recognised value."""

    if content_format not in _VALID_CONTENT_FORMATS:
        raise ValueError(f"Invalid content_format '{content_format}'. Allowed values: {sorted(_VALID_CONTENT_FORMATS)}")


def _build_run_configuration(content_format: str | None):
    """Build a RunConfiguration for the given content format string, or None."""

    if content_format is None:
        return None

    _validate_content_format(content_format)
    config = RunConfiguration()
    config.format = Format(
        format_input=FormatInput(input_type=ContentFormat(content_format)),
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


def _save_to_file(data: Any, prefix: str, suffix: str) -> str:
    """Serialize data to a temp file and return a message with the path.

    This keeps large payloads out of the MCP response (and thus out of
    the LLM context window). The caller can selectively read the file
    using standard file-reading tools.
    """

    fd, path = tempfile.mkstemp(prefix=f"{prefix}_", suffix=suffix)
    with os.fdopen(fd, "w") as fh:
        fh.write(data)
    return f"Data saved to {path} — use file-reading tools to inspect the contents."


def _save_to_json_file(data: Any, prefix: str) -> str:
    """Serialize data to a temp JSON file and return a message with the path."""

    return _save_to_file(json.dumps(data, indent=2), prefix=prefix, suffix=".json")


def _cloud_run_dir(endpoint: str, run_id: str) -> str:
    """Build the local cache directory for a cloud run.

    Returns ``~/.nextmv/runs/{endpoint}/{run_id}``. The *endpoint*
    parameter should already have the URL scheme (``https://`` /
    ``http://``) stripped.
    """

    return os.path.join(os.path.expanduser("~"), ".nextmv", "runs", endpoint, run_id)


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

    url: str = app.client.url or ""
    for scheme in ("https://", "http://"):
        if url.startswith(scheme):
            url = url[len(scheme) :]
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


def _extract_cloud_run_outputs(result_dict: dict[str, Any], endpoint: str, run_id: str) -> None:
    """Extract output components from a cloud result into separate files.

    Mirrors the local run ``outputs/`` directory structure:

    * ``outputs/solutions/solution.json`` — the full output dict (matches local)
    * ``outputs/metrics/metrics.json`` — raw metrics value
    * ``outputs/statistics/statistics.json`` — wrapped as ``{"statistics": ...}``
    * ``outputs/assets/assets.json`` — wrapped as ``{"assets": ...}``

    Skipped when *output* is not a dict with inline data (e.g. csv-archive
    results where the SDK already extracted files via ``output_dir_path``).
    """

    output = result_dict.get("output")
    if not isinstance(output, dict) or "solution" not in output:
        return

    run_dir = _cloud_run_dir(endpoint, run_id)
    outputs_dir = os.path.join(run_dir, OUTPUTS_KEY)

    # solution → outputs/solutions/solution.json
    # Local writes the entire stdout output dict here, so we do the same.
    path = os.path.join(outputs_dir, SOLUTIONS_KEY, "solution.json")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as fh:
        json.dump(output, fh, indent=2)

    # metrics → outputs/metrics/metrics.json (raw, matching local)
    metrics = output.get(METRICS_KEY)
    if metrics:
        path = os.path.join(outputs_dir, METRICS_KEY, f"{METRICS_KEY}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(metrics, fh, indent=2)

    # statistics → outputs/statistics/statistics.json (wrapped, matching local)
    statistics = output.get(STATISTICS_KEY)
    if statistics:
        path = os.path.join(outputs_dir, STATISTICS_KEY, f"{STATISTICS_KEY}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump({STATISTICS_KEY: statistics}, fh, indent=2)

    # assets → outputs/assets/assets.json (wrapped, matching local)
    assets = output.get(ASSETS_KEY)
    if assets:
        path = os.path.join(outputs_dir, ASSETS_KEY, f"{ASSETS_KEY}.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump({ASSETS_KEY: assets}, fh, indent=2)

    # Generate visuals from assets (Plotly/GeoJSON → HTML), matching local.
    try:
        process_run_visuals(run_dir=run_dir, outputs_dir=outputs_dir)
    except Exception as exc:
        log(f"Visual generation failed for run {run_id}: {exc}")


def _save_cloud_run_logs(data: Any, endpoint: str, run_id: str) -> str:
    """Write cloud run logs as plain text to match local run format.

    Accepts either a ``RunLog.to_dict()`` (``{"log": "..."}`` with an
    optional ``"stderr"`` key) or a list of poll entries
    (``[{"timestamp": ..., "log": ...}, ...]``).
    """

    path = os.path.join(_cloud_run_dir(endpoint, run_id), LOGS_KEY, LOGS_FILE)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as fh:
        if isinstance(data, list):
            # Poll entries: write each as "timestamp log\n".
            for entry in data:
                ts = entry.get("timestamp") or ""
                log = entry.get("log") or ""
                fh.write(f"{ts} {log}\n")
        elif isinstance(data, dict):
            # RunLog.to_dict(): write the log string directly.
            log = data.get("log", "")
            if log:
                fh.write(log)
                if not log.endswith("\n"):
                    fh.write("\n")
            stderr = data.get("stderr", "")
            if stderr:
                fh.write(stderr)
                if not stderr.endswith("\n"):
                    fh.write("\n")
        else:
            fh.write(str(data))

    return path
