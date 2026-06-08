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
import html
import http.server
import json
import os
import secrets
import ssl
import threading
import urllib.parse
import webbrowser
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import requests
import truststore

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
_FALLBACK_LOGOUT_ENDPOINT = f"{_COGNITO_DOMAIN}/logout"

# Timeout (seconds) to wait for the user to complete the browser auth step.
_BROWSER_TIMEOUT = 300

# Reserved session name used when auth_session is not set on a profile.
DEFAULT_AUTH_SESSION = "default"


# >>> Token storage


# >>> TLS helpers


def _verify_kw(verify: ssl.SSLContext | None) -> dict[str, Any]:
    """Return a ``verify=...`` keyword argument dict, empty when *verify* is ``None``."""
    if verify is not None:
        return {"verify": verify}
    return {}


def get_verify(system_certs: bool) -> ssl.SSLContext | None:
    """
    Return a TLS verification parameter for ``requests`` calls.

    When *system_certs* is ``True``, returns a :class:`truststore.SSLContext`
    that uses the operating system's certificate store instead of the default
    ``certifi`` bundle.  Otherwise returns ``None``, meaning ``requests`` will
    use its default CA bundle (``certifi``).

    Parameters
    ----------
    system_certs : bool
        Whether to use the system certificate store.

    Returns
    -------
    ssl.SSLContext | None
        A ``truststore.SSLContext`` when *system_certs* is ``True``,
        ``None`` otherwise.
    """
    if system_certs:
        return truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    return None


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
    name = session.strip() if session else DEFAULT_AUTH_SESSION
    if not name:
        name = DEFAULT_AUTH_SESSION
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
    # Restrict read/write access to the owner only.  Use os.open to set the
    # mode atomically when the file is created, avoiding a window where the
    # file exists with broader permissions.  Best-effort: silently ignored on
    # filesystems or platforms that don't support POSIX permissions (e.g. Windows).
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as fh:
            json.dump(tokens, fh, indent=2)
    except (OSError, PermissionError):
        # Fallback: write without restrictive mode.
        with path.open("w") as fh:
            json.dump(tokens, fh, indent=2)


def delete_tokens(session: str) -> None:
    """
    Delete stored tokens for *session* from disk.

    Silently does nothing if no token file exists.

    Parameters
    ----------
    session : str
        The auth session name.  Resolve this from a profile via
        :func:`nextmv.config.get_auth_session`.
    """
    path = _token_path(session)
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def is_invalid_grant_error(exc: Exception) -> bool:
    """
    Return ``True`` if *exc* represents an OAuth2 ``invalid_grant`` error.

    Checks for an HTTP 400 response with ``{"error": "invalid_grant"}`` in the
    body, per `RFC 6749 §5.2`_.

    .. _RFC 6749 §5.2: https://datatracker.ietf.org/doc/html/rfc6749#section-5.2
    """
    if not isinstance(exc, requests.HTTPError) or exc.response is None:
        return False
    if exc.response.status_code != 400:
        return False
    try:
        body = exc.response.json()
        return body.get("error") == "invalid_grant"
    except Exception:
        return False


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
        # Unparseable expiry - treat as expired so the token gets refreshed
        # rather than sending a potentially corrupt token to the API.
        return True


# >>> PKCE flow - internal helpers


def _validate_token_response(tokens: dict[str, Any]) -> None:
    """
    Validate a token response from the identity provider.

    Checks the required fields per `RFC 6749 §5.1`_:

    - ``access_token`` must be present.
    - ``token_type`` must be present and equal to ``"bearer"`` (case-insensitive,
      per `RFC 6749 §7.1`_).

    Parameters
    ----------
    tokens : dict[str, Any]
        The parsed JSON token response from the IdP.

    Raises
    ------
    ValueError
        If a required field is missing or ``token_type`` is unsupported.

    .. _RFC 6749 §5.1: https://datatracker.ietf.org/doc/html/rfc6749#section-5.1
    .. _RFC 6749 §7.1: https://datatracker.ietf.org/doc/html/rfc6749#section-7.1
    """
    if "access_token" not in tokens:
        raise ValueError("Token response missing required field 'access_token'.")
    token_type = tokens.get("token_type")
    if token_type is None:
        raise ValueError("Token response missing required field 'token_type'.")
    if str(token_type).lower() != "bearer":
        raise ValueError(f"Unsupported token_type {token_type!r}; only 'bearer' is supported.")


def _discover_endpoints(
    oidc_discovery_url: str | None = None,
    verify: ssl.SSLContext | None = None,
) -> tuple[str, str, str]:
    """
    Fetch the OIDC discovery document and return
    ``(authorization_endpoint, token_endpoint, logout_endpoint)``.

    Falls back to the hard-coded endpoints if the default discovery URL is
    unreachable or returns an unexpected response.  Raises on failure when an
    explicit discovery URL is provided, since silently falling back would
    authenticate against the wrong identity provider.

    Parameters
    ----------
    oidc_discovery_url : str | None
        The OIDC discovery document URL to use.  When ``None`` the module-level
        constant :data:`OIDC_DISCOVERY_URL` is used (which covers the production
        endpoint).
    verify : ssl.SSLContext | None
        TLS verification parameter passed to ``requests``.  Pass a
        :func:`truststore.SSLContext` to use the system certificate store.

    Returns
    -------
    tuple[str, str, str]
        ``(authorization_endpoint, token_endpoint, logout_endpoint)``

    Raises
    ------
    RuntimeError
        If an explicit *oidc_discovery_url* is provided and the request fails.
    """
    is_custom = oidc_discovery_url is not None
    discovery_url = oidc_discovery_url or OIDC_DISCOVERY_URL
    try:
        resp = requests.get(discovery_url, timeout=10, **_verify_kw(verify))
        resp.raise_for_status()
        doc = resp.json()
        auth_ep = doc.get("authorization_endpoint", _FALLBACK_AUTH_ENDPOINT)
        token_ep = doc.get("token_endpoint", _FALLBACK_TOKEN_ENDPOINT)
        logout_ep = doc.get("end_session_endpoint", _FALLBACK_LOGOUT_ENDPOINT)
        return auth_ep, token_ep, logout_ep
    except Exception as exc:
        if is_custom:
            raise RuntimeError(
                f"Failed to fetch OIDC discovery document from {discovery_url!r}: {exc}. "
                "Check the URL or register the endpoint via `nextmv configuration create`."
            ) from exc
        return _FALLBACK_AUTH_ENDPOINT, _FALLBACK_TOKEN_ENDPOINT, _FALLBACK_LOGOUT_ENDPOINT


def _generate_pkce_pair() -> tuple[str, str]:
    """
    Generate a PKCE ``code_verifier`` and its ``code_challenge``.

    The verifier is a cryptographically random URL-safe string of 86 characters (43-128
    chars as per RFC 7636). The challenge is the base64url-encoded SHA-256 hash of the
    verifier.

    See https://datatracker.ietf.org/doc/html/rfc7636#section-4.2 for details.

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
    Only the root path (``/``) is accepted; any other path returns a 404.
    """

    # Simple Nextmv logo as an inline SVG.
    _LOGO_SVG = (
        '<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">'  # noqa: E501
        '<path d="M14.7642 17.7171C14.3087 14.9415 13.2695 11.9682 13.2695 11.9682C13.2695 11.9682 14.123 9.43872 15.4541 7.0242C16.7852 4.60968 18.2136 3 18.2136 3C18.2136 3 21.318 9.5537 20.973 15.9924C20.7155 20.7993 18.7918 26.0548 17.8333 28.4099H15.1526C15.1526 28.4099 15.3387 21.2174 14.7642 17.7171Z" fill="#008393"/>'  # noqa: E501
        '<path fill-rule="evenodd" clip-rule="evenodd" d="M5.45131 3C5.45131 3 10.5103 7.48411 12.5799 15.3026C14.0207 20.7457 13.7297 29.6747 13.7297 29.6747H10.5103C10.5103 29.6747 5.33899 22.5047 4.30156 17.1422C3.20512 11.4747 5.45131 3 5.45131 3ZM8.38998 9.96094C8.38998 9.96094 6.32617 11.8218 7.46745 17.1737C8.60874 22.5257 12.456 28.5733 12.456 28.5733C12.456 28.5733 12.2661 24.8898 11.5771 19.1028C10.8882 13.3157 8.38998 9.96094 8.38998 9.96094Z" fill="#005B6B"/>'  # noqa: E501
        "</svg>"
    )

    # Simple HTML template for the callback response page.
    _PAGE_TEMPLATE = (
        "<!DOCTYPE html>"
        '<html lang="en"><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>{title}</title>"
        "<style>"
        "body{{font-family:system-ui,-apple-system,sans-serif;display:flex;align-items:center;"
        "justify-content:center;min-height:100vh;margin:0;background:#013641;color:#111827}}"
        ".card{{text-align:center;padding:2.5rem 3rem;border-radius:1rem;"
        "box-shadow:0 4px 12px rgba(0,0,0,.25);background:#fff;max-width:420px}}"
        "h2{{margin:.75rem 0 .25rem;font-size:1.25rem}}"
        "p{{margin:.25rem 0;color:#6b7280;font-size:.95rem}}"
        ".ok h2{{color:#018494}}"
        ".err h2{{color:#fc6262}}"
        "</style></head><body>"
        '<div class="card {cls}">'
        "{logo}"
        "<h2>{heading}</h2>"
        "<p>{message}</p>"
        "</div></body></html>"
    )

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)

        # Only accept the root path — anything else is a 404.
        if parsed.path != "/":
            self._send_page(
                404,
                "Not Found",
                "This page does not exist.",
                "err",
            )
            return

        params = dict(urllib.parse.parse_qsl(parsed.query))
        # Store on the server instance so the main thread can read them.
        self.server.callback_params = params  # type: ignore[attr-defined]

        logo = self._LOGO_SVG

        if "error" in params:
            escaped = html.escape(params.get("error_description", params["error"]))
            self._send_page(
                200,
                "Authentication failed",
                escaped,
                "err",
                logo,
            )
        else:
            self._send_page(
                200,
                "Authentication successful!",
                "You may close this tab and return to your terminal.",
                "ok",
                logo,
            )

    def _send_page(
        self,
        status: int,
        title: str,
        message: str,
        cls: str,
        logo: str = "",
    ) -> None:
        body = self._PAGE_TEMPLATE.format(
            title=html.escape(title),
            heading=html.escape(title),
            message=message,
            cls=cls,
            logo=logo,
        ).encode("utf-8")
        self.send_response(status)
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
        If the provider returns an error parameter or the port cannot be bound.
    """
    try:
        server = http.server.HTTPServer(("127.0.0.1", port), _CallbackHandler)
    except OSError as exc:
        raise RuntimeError(
            f"Cannot start local auth server on port {port}: {exc}. Is another process already using this port?"
        ) from exc

    server.callback_params = {}  # type: ignore[attr-defined]
    server.timeout = _BROWSER_TIMEOUT

    try:
        # Handle exactly one request.
        server.handle_request()
    finally:
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
    verify: ssl.SSLContext | None = None,
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
    verify : ssl.SSLContext | None
        TLS verification parameter passed to ``requests``.

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
        **_verify_kw(verify),
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise requests.HTTPError(f"Token exchange failed ({resp.status_code}): {resp.text}") from exc

    tokens: dict[str, Any] = resp.json()
    _validate_token_response(tokens)
    # Compute and store an absolute expiry timestamp.
    expires_in: int = tokens.get("expires_in", 3600)
    expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)
    tokens["expires_at"] = expires_at.isoformat()
    return tokens


# >>> PKCE flow - public API


def refresh_tokens(
    refresh_token: str,
    token_endpoint: str | None = None,
    client_id: str | None = None,
    oidc_discovery_url: str | None = None,
    verify: ssl.SSLContext | None = None,
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
    verify : ssl.SSLContext | None
        TLS verification parameter passed to ``requests``.

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
        _, _, token_endpoint = _discover_endpoints(oidc_discovery_url, verify=verify)

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
        **_verify_kw(verify),
    )
    try:
        resp.raise_for_status()
    except requests.HTTPError as exc:
        raise requests.HTTPError(f"Token refresh failed ({resp.status_code}): {resp.text}") from exc

    tokens: dict[str, Any] = resp.json()
    _validate_token_response(tokens)
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
    verify: ssl.SSLContext | None = None,
) -> dict[str, Any]:
    """
    Execute the full PKCE authorization-code flow.

    This function:

    1. Resolves the OIDC endpoints.
    2. Generates a PKCE pair.
    3. Listens for the redirect callback on the fixed port ``CALLBACK_PORT`` (``56734``).
    4. Opens the system browser at the authorization URL (or the logout URL when
       ``force=True``, which clears the identity provider session and chains
       into a fresh login).
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
        When ``True``, opens the identity provider's logout endpoint first,
        which clears any active browser session, and chains all authorization
        parameters onto it so that the provider immediately presents the login
        page.  Defaults to ``False``.
    verify : ssl.SSLContext | None
        TLS verification parameter passed to ``requests``.

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
    auth_endpoint, token_endpoint, logout_endpoint = _discover_endpoints(oidc_discovery_url, verify=verify)
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
        # requirement as the normal authorization flow - no additional sign-out
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

    # Verify the state before trusting the code - protects against login CSRF where a
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

    return _exchange_code_for_tokens(token_endpoint, code, code_verifier, redirect_uri, cid, verify=verify)


def fetch_organizations(
    access_token: str,
    endpoint: str,
    verify: ssl.SSLContext | None = None,
) -> list[dict[str, Any]]:
    """
    Fetch the list of organizations (teams) the authenticated user belongs to.

    Calls ``GET https://<endpoint>/v1/internal/me/organization`` and returns
    the response body as a list of organization dicts.

    Each dict contains at minimum:

    - ``id`` (str) - the team UUID; use this for the ``nextmv-account`` header.
    - ``name`` (str) - the human-readable team name; show this to the user.
    - ``role`` (str) - the user's role in the team.
    - ``pending_invite`` (bool) - whether the user has a pending invite.

    Parameters
    ----------
    access_token : str
        A valid access token (or id_token) for the authenticated user.
    endpoint : str
        The API endpoint hostname, e.g. ``"api.cloud.nextmv.io"``.  A leading
        ``https://`` scheme is accepted and stripped.  Plain ``http://`` is
        rejected to prevent sending tokens over an unencrypted connection.
    verify : ssl.SSLContext | None
        TLS verification parameter passed to ``requests``.

    Returns
    -------
    list[dict[str, Any]]
        The list of organization objects returned by the API.

    Raises
    ------
    ValueError
        If *endpoint* uses ``http://``.
    requests.HTTPError
        If the API returns a non-2xx response.
    """
    if endpoint.startswith("http://"):
        raise ValueError(
            f"Refusing to send tokens over plain HTTP for endpoint {endpoint!r}. Use https:// or a bare hostname."
        )
    # Strip https:// if present so we always build a consistent URL.
    bare = endpoint.removeprefix("https://").removeprefix("http://")
    url = f"https://{bare.rstrip('/')}/v1/internal/me/organization"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
        timeout=15,
        **_verify_kw(verify),
    )
    resp.raise_for_status()
    return resp.json()
