"""
PKCE OAuth2 flow and token storage utilities for Nextmv pkce profiles.

This module contains the core (non-CLI) authentication helpers:

- PKCE authorization-code flow (:func:`run_pkce_flow`, :func:`refresh_tokens`)
- Token persistence (:func:`load_tokens`, :func:`save_tokens`, :func:`is_token_expired`,
  :func:`token_dir`)

PKCE flow overview
------------------
1. Fetch the OIDC discovery document to resolve ``authorization_endpoint`` and
   ``token_endpoint`` (with a hard-coded fallback for the known user pool).
2. Generate a ``code_verifier`` / ``code_challenge`` pair using stdlib ``secrets`` and
   ``hashlib``.
3. Start a temporary local HTTP server on a fixed port to receive the OAuth2 callback.
4. Open the system browser at the authorization URL.
5. Wait for the redirect, extract the authorization ``code``.
6. Exchange the ``code`` + ``code_verifier`` for tokens via a POST to the token endpoint.
7. Return a token dict ready for :func:`save_tokens`.

Token file schema
-----------------
Tokens are stored as JSON keyed by **auth session name** under::

    ~/.nextmv/auth/<session_name>/tokens.json

The session name is resolved from the ``auth_session`` field in the profile
configuration (see :func:`nextmv.config.get_auth_session`).  When that field
is absent the reserved ``"default"`` session is used, so all profiles without
an explicit session share a single token file.

.. code-block:: json

    {
        "access_token": "...",
        "refresh_token": "...",
        "token_type": "Bearer",
        "expires_at": "2026-01-01T00:00:00+00:00"
    }

Constants
---------
OIDC_DISCOVERY_URL
    The OIDC discovery document URL for the Nextmv Cognito user pool.
CLIENT_ID
    The OAuth2 client ID registered in the Cognito user pool.
SCOPES
    Space-separated OAuth2 scopes requested during the flow.
"""

import base64
import hashlib
import http.server
import json
import secrets
import threading
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests

AUTH_DIR = Path.home() / ".nextmv" / "auth"

# >>> Provider constants

OIDC_DISCOVERY_URL = "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_1jHS2b9HU/.well-known/openid-configuration"
CLIENT_ID = "4k91vdlr1m52v9v45h9vc7a25e"
SCOPES = "email openid profile"
CALLBACK_PORT = 56734

# Hard-coded fallback endpoints derived from the discovery document so that
# the flow works even when the discovery URL is temporarily unreachable.
_COGNITO_DOMAIN = "https://auth.cloud.nextmv.io"
_FALLBACK_AUTH_ENDPOINT = f"{_COGNITO_DOMAIN}/oauth2/authorize"
_FALLBACK_TOKEN_ENDPOINT = f"{_COGNITO_DOMAIN}/oauth2/token"

# Timeout (seconds) to wait for the user to complete the browser auth step.
_BROWSER_TIMEOUT = 300

# Reserved session name used when auth_session is not set on a profile.
_DEFAULT_SESSION_NAME = "default"


# >>> Token storage


def token_dir(session: str) -> Path:
    """
    Returns the directory that holds token files for *session*.

    Parameters
    ----------
    session : str
        The auth session name.  The reserved value ``"default"`` (case-
        insensitive) maps to ``~/.nextmv/auth/default/``.  Obtain the correct
        session name for a profile via
        :func:`nextmv.config.get_auth_session`.

    Returns
    -------
    Path
        The directory path ``~/.nextmv/auth/<session>/``.

    Raises
    ------
    ValueError
        If *session* is empty or would escape the auth directory (e.g. path
        traversal).
    """
    name = session.strip() if session else _DEFAULT_SESSION_NAME
    if not name:
        name = _DEFAULT_SESSION_NAME
    path = (AUTH_DIR / name).resolve()
    if not path.is_relative_to(AUTH_DIR.resolve()):
        raise ValueError(f"Invalid session name {name!r}: must not escape the auth directory.")
    return path


def _token_path(session: str) -> Path:
    return token_dir(session) / "tokens.json"


def load_tokens(session: str) -> dict[str, Any] | None:
    """
    Load stored tokens for *session* from disk.

    Parameters
    ----------
    session : str
        The auth session name.  Resolve this from a profile via
        :func:`nextmv.config.get_auth_session`.

    Returns
    -------
    dict[str, Any] | None
        The token dict, or ``None`` if no token file exists.
    """
    path = _token_path(session)
    if not path.exists():
        return None
    with path.open() as fh:
        return json.load(fh)


def save_tokens(session: str, tokens: dict[str, Any]) -> None:
    """
    Persist *tokens* for *session* to disk.

    Creates any missing parent directories with mode 0o700.

    Parameters
    ----------
    session : str
        The auth session name.  Resolve this from a profile via
        :func:`nextmv.config.get_auth_session`.
    tokens : dict[str, Any]
        The token dict to persist.  Must contain at least ``access_token``.
    """
    path = _token_path(session)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    with path.open("w") as fh:
        json.dump(tokens, fh, indent=2)
    # Restrict read access to the owner only.  Best-effort: silently ignored on
    # filesystems or platforms that don't support POSIX permissions (e.g. Windows).
    try:
        path.chmod(0o600)
    except (OSError, PermissionError):
        pass


def is_token_expired(tokens: dict[str, Any]) -> bool:
    """
    Return ``True`` when the stored access token is expired (or will expire within the
    next 30 seconds), ``False`` otherwise.

    If ``expires_at`` is absent the token is treated as *not* expired so that tokens
    without an explicit expiry still work.

    Parameters
    ----------
    tokens : dict[str, Any]
        The token dict loaded from disk.

    Returns
    -------
    bool
    """
    expires_at_str: str | None = tokens.get("expires_at")
    if not expires_at_str:
        return False
    try:
        expires_at = datetime.fromisoformat(expires_at_str)
        # Ensure timezone-aware comparison.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        # Consider expired if within 30-second buffer.
        return (expires_at - now).total_seconds() < 30
    except ValueError:
        # Unparseable expiry — treat as not expired.
        return False


# >>> PKCE flow — internal helpers


def _discover_endpoints(oidc_discovery_url: str | None = None) -> tuple[str, str]:
    """
    Fetch the OIDC discovery document and return
    ``(authorization_endpoint, token_endpoint)``.

    Falls back to the hard-coded endpoints if the discovery URL is unreachable or returns
    an unexpected response.

    Parameters
    ----------
    oidc_discovery_url : str | None
        The OIDC discovery document URL to use.  When ``None`` the module-level
        constant :data:`OIDC_DISCOVERY_URL` is used (which covers the production
        endpoint).

    Returns
    -------
    tuple[str, str]
        ``(authorization_endpoint, token_endpoint)``
    """
    discovery_url = oidc_discovery_url or OIDC_DISCOVERY_URL
    try:
        resp = requests.get(discovery_url, timeout=10)
        resp.raise_for_status()
        doc = resp.json()
        auth_ep = doc.get("authorization_endpoint", _FALLBACK_AUTH_ENDPOINT)
        token_ep = doc.get("token_endpoint", _FALLBACK_TOKEN_ENDPOINT)
        return auth_ep, token_ep
    except Exception:
        return _FALLBACK_AUTH_ENDPOINT, _FALLBACK_TOKEN_ENDPOINT


def _generate_pkce_pair() -> tuple[str, str]:
    """
    Generate a PKCE ``code_verifier`` and its ``code_challenge``.

    The verifier is a cryptographically random URL-safe string (43-128 chars as per
    RFC 7636). The challenge is the base64url-encoded SHA-256 hash of the verifier.

    Returns
    -------
    tuple[str, str]
        ``(code_verifier, code_challenge)``
    """
    code_verifier = secrets.token_urlsafe(64)
    digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return code_verifier, code_challenge


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """
    Minimal HTTP handler that captures the OAuth2 callback query parameters.

    The captured parameters are stored in ``self.server.callback_params``.
    """

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        params = dict(urllib.parse.parse_qsl(parsed.query))
        # Store on the server instance so the main thread can read them.
        self.server.callback_params = params  # type: ignore[attr-defined]

        if "error" in params:
            body = (
                "<html><body>"
                "<h2>Authentication failed.</h2>"
                f"<p>{params.get('error_description', params['error'])}</p>"
                "<p>You may close this tab.</p>"
                "</body></html>"
            ).encode()
        else:
            body = (
                b"<html><body>"
                b"<h2>Authentication successful!</h2>"
                b"<p>You may close this tab and return to your terminal.</p>"
                b"</body></html>"
            )

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: Any) -> None:  # noqa: D102
        # Silence the default access log so it doesn't pollute the terminal.
        pass


def _wait_for_callback(port: int) -> dict[str, str]:
    """
    Start a one-shot local HTTP server and block until the OAuth2 provider redirects the
    browser to ``http://127.0.0.1:<port>``.

    Parameters
    ----------
    port : int
        The port to listen on.

    Returns
    -------
    dict[str, str]
        The query parameters extracted from the callback URL.

    Raises
    ------
    TimeoutError
        If no callback is received within ``_BROWSER_TIMEOUT`` seconds.
    RuntimeError
        If the provider returns an error parameter.
    """
    server = http.server.HTTPServer(("127.0.0.1", port), _CallbackHandler)
    server.callback_params = {}  # type: ignore[attr-defined]
    server.timeout = _BROWSER_TIMEOUT

    # Handle exactly one request.
    server.handle_request()
    server.server_close()

    params: dict[str, str] = server.callback_params  # type: ignore[attr-defined]
    if not params:
        raise TimeoutError(
            f"No callback received within {_BROWSER_TIMEOUT} seconds. Please try running `nextmv login` again."
        )
    if "error" in params:
        raise RuntimeError(f"Authorization error: {params.get('error_description', params['error'])}")
    return params


def _exchange_code_for_tokens(
    token_endpoint: str,
    code: str,
    code_verifier: str,
    redirect_uri: str,
    client_id: str | None = None,
) -> dict[str, Any]:
    """
    Exchange an authorization ``code`` for tokens.

    Parameters
    ----------
    token_endpoint : str
        The token endpoint URL.
    code : str
        The authorization code received from the provider.
    code_verifier : str
        The PKCE code verifier generated at the start of the flow.
    redirect_uri : str
        The redirect URI used in the authorization request (must match exactly).
    client_id : str | None
        The OAuth2 client ID.  When ``None`` the module-level :data:`CLIENT_ID`
        constant is used.

    Returns
    -------
    dict[str, Any]
        The raw token response body augmented with an ``expires_at`` field
        (ISO-8601 UTC string).

    Raises
    ------
    requests.HTTPError
        If the token endpoint returns a non-2xx response.
    """
    cid = client_id or CLIENT_ID
    payload = {
        "grant_type": "authorization_code",
        "client_id": cid,
        "code": code,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }
    resp = requests.post(
        token_endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise requests.HTTPError(f"Token exchange failed ({resp.status_code}): {resp.text}") from exc

    tokens: dict[str, Any] = resp.json()
    # Compute and store an absolute expiry timestamp.
    expires_in: int = tokens.get("expires_in", 3600)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    tokens["expires_at"] = expires_at.isoformat()
    return tokens


# >>> PKCE flow — public API


def refresh_tokens(
    refresh_token: str,
    token_endpoint: str | None = None,
    client_id: str | None = None,
    oidc_discovery_url: str | None = None,
) -> dict[str, Any]:
    """
    Use a refresh token to obtain a new access token.

    Parameters
    ----------
    refresh_token : str
        A valid refresh token previously obtained via :func:`run_pkce_flow`.
    token_endpoint : str | None
        The token endpoint URL.  If ``None``, the OIDC discovery document is fetched to
        resolve it.
    client_id : str | None
        The OAuth2 client ID.  When ``None`` the module-level :data:`CLIENT_ID`
        constant is used.
    oidc_discovery_url : str | None
        The OIDC discovery document URL.  Used only when *token_endpoint* is
        ``None``.  When ``None`` the module-level :data:`OIDC_DISCOVERY_URL` is
        used.

    Returns
    -------
    dict[str, Any]
        The refreshed token response body augmented with an ``expires_at`` field
        (ISO-8601 UTC string).

    Raises
    ------
    requests.HTTPError
        If the token endpoint returns a non-2xx response.
    """
    if token_endpoint is None:
        _, token_endpoint = _discover_endpoints(oidc_discovery_url)

    cid = client_id or CLIENT_ID
    payload = {
        "grant_type": "refresh_token",
        "client_id": cid,
        "refresh_token": refresh_token,
    }
    resp = requests.post(
        token_endpoint,
        data=payload,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=30,
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise requests.HTTPError(f"Token refresh failed ({resp.status_code}): {resp.text}") from exc

    tokens: dict[str, Any] = resp.json()
    expires_in: int = tokens.get("expires_in", 3600)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    tokens["expires_at"] = expires_at.isoformat()
    # The Cognito refresh response does not include a new refresh_token;
    # preserve the existing one.
    if "refresh_token" not in tokens:
        tokens["refresh_token"] = refresh_token
    return tokens


def run_pkce_flow(
    oidc_discovery_url: str | None = None,
    client_id: str | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """
    Execute the full PKCE authorization-code flow.

    This function:

    1. Resolves the OIDC endpoints.
    2. Generates a PKCE pair.
    3. Listens for the redirect callback on the fixed port ``CALLBACK_PORT`` (``56734``).
    4. Opens the system browser at the authorization URL (or the logout URL when
       ``force=True``, which clears the Cognito session and chains into a fresh login).
    5. Waits for the redirect callback (up to ``_BROWSER_TIMEOUT`` seconds).
    6. Exchanges the authorization code for tokens.

    Parameters
    ----------
    oidc_discovery_url : str | None
        The OIDC discovery document URL for the identity provider backing this
        profile's endpoint.  When ``None`` the module-level
        :data:`OIDC_DISCOVERY_URL` constant is used (production endpoint).
    client_id : str | None
        The OAuth2 client ID for the identity provider.  When ``None`` the
        module-level :data:`CLIENT_ID` constant is used.
    force : bool
        When ``True``, opens the Cognito logout endpoint first (``/logout``),
        which clears any active browser session, and chains all authorization
        parameters onto it so that Cognito immediately presents the login page.
        This is more reliable than ``prompt=login``, which Cognito's classic
        hosted UI silently ignores.  Defaults to ``False``.

    Returns
    -------
    dict[str, Any]
        A token dict containing at minimum ``access_token``, ``token_type``,
        and ``expires_at``.  Also contains ``refresh_token`` and ``id_token``
        when the provider issues them.

    Raises
    ------
    TimeoutError
        If the user does not complete the browser flow within the timeout.
    RuntimeError
        If the provider returns an error.
    requests.HTTPError
        If the token exchange request fails.
    """
    auth_endpoint, token_endpoint, logout_endpoint = _discover_endpoints(oidc_discovery_url)
    cid = client_id or CLIENT_ID
    code_verifier, code_challenge = _generate_pkce_pair()
    redirect_uri = f"http://127.0.0.1:{CALLBACK_PORT}"
    # Generate a random state value to prevent login CSRF / authorization-code injection.
    # The callback is validated against this value before the code is exchanged for
    # tokens.
    state = secrets.token_urlsafe(16)

    auth_params = {
        "response_type": "code",
        "client_id": cid,
        "redirect_uri": redirect_uri,
        "scope": SCOPES,
        "code_challenge_method": "S256",
        "code_challenge": code_challenge,
        "state": state,
    }

    if force:
        # Use the logout endpoint to clear the Cognito session, then chain the
        # full authorization request onto it.  Cognito will log the user out
        # and immediately redirect to the login page with all auth params intact.
        # The redirect_uri must be registered as an Allowed Callback URL (same
        # requirement as the normal authorization flow — no additional sign-out
        # URL registration is needed).
        logout_params = {
            "client_id": cid,
            **auth_params,
        }
        open_url = logout_endpoint + "?" + urllib.parse.urlencode(logout_params)
    else:
        open_url = auth_endpoint + "?" + urllib.parse.urlencode(auth_params)

    # Start the callback listener in a background thread so we can open the
    # browser on the main thread without blocking.
    callback_result: dict[str, str] = {}
    exc_holder: list[Exception] = []

    def _listen() -> None:
        try:
            result = _wait_for_callback(CALLBACK_PORT)
            callback_result.update(result)
        except Exception as exc:
            exc_holder.append(exc)

    listener = threading.Thread(target=_listen, daemon=True)
    listener.start()

    webbrowser.open(open_url)

    listener.join(timeout=_BROWSER_TIMEOUT + 5)

    if exc_holder:
        raise exc_holder[0]

    # Verify the state before trusting the code — protects against login CSRF where a
    # malicious local page hits our callback with an attacker-supplied code.
    returned_state = callback_result.get("state")
    if returned_state != state:
        raise RuntimeError(
            "OAuth2 state mismatch: the callback state does not match the expected value. "
            "This may indicate a login CSRF attempt. Please try running `nextmv login` again."
        )

    code = callback_result.get("code")
    if not code:
        raise RuntimeError("No authorization code received. Please try running `nextmv login` again.")

    return _exchange_code_for_tokens(token_endpoint, code, code_verifier, redirect_uri, cid)


def fetch_organizations(access_token: str, endpoint: str) -> list[dict[str, Any]]:
    """
    Fetch the list of organizations (teams) the authenticated user belongs to.

    Calls ``GET https://<endpoint>/v1/internal/me/organization`` and returns
    the response body as a list of organization dicts.

    Each dict contains at minimum:

    - ``id`` (str) — the team UUID; use this for the ``nextmv-account`` header.
    - ``name`` (str) — the human-readable team name; show this to the user.
    - ``role`` (str) — the user's role in the team.
    - ``pending_invite`` (bool) — whether the user has a pending invite.

    Parameters
    ----------
    access_token : str
        A valid access token (or id_token) for the authenticated user.
    endpoint : str
        The API endpoint hostname, e.g. ``"api.cloud.nextmv.io"``.  Leading
        ``https://`` / ``http://`` schemes are accepted and preserved.

    Returns
    -------
    list[dict[str, Any]]
        The list of organization objects returned by the API.

    Raises
    ------
    requests.HTTPError
        If the API returns a non-2xx response.
    """
    # Ensure the endpoint has a scheme.
    base = endpoint if endpoint.startswith(("https://", "http://")) else f"https://{endpoint}"
    url = f"{base.rstrip('/')}/v1/internal/me/organization"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()
