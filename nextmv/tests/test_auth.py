"""
Unit tests for the PKCE auth helpers in nextmv.auth.
"""

import base64
import json
import os
import tempfile
import unittest
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import nextmv.auth as auth_module
from nextmv.auth import (
    _discover_endpoints,
    _generate_pkce_pair,
    fetch_organizations,
    is_token_expired,
    load_tokens,
    save_tokens,
    token_dir,
)


class TestTokenDir(unittest.TestCase):
    """Tests for token_dir path resolution."""

    def test_default_session_name(self):
        path = token_dir("default")
        self.assertEqual(path.name, "default")

    def test_named_session(self):
        path = token_dir("staging")
        self.assertEqual(path.name, "staging")

    def test_session_name_whitespace_stripped(self):
        path = token_dir("  prod  ")
        self.assertEqual(path.name, "prod")

    def test_empty_string_maps_to_default(self):
        path = token_dir("")
        self.assertEqual(path.name, "default")

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            token_dir("../evil")

    def test_absolute_path_rejected(self):
        with self.assertRaises(ValueError):
            token_dir("/etc/passwd")


class TestSaveLoadTokens(unittest.TestCase):
    """Tests for save_tokens / load_tokens round-trip."""

    def test_roundtrip_named_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                tokens = {
                    "access_token": "abc123",
                    "refresh_token": "def456",
                    "token_type": "Bearer",
                    "expires_at": "2099-01-01T00:00:00+00:00",
                }
                save_tokens("my-session", tokens)
                loaded = load_tokens("my-session")
                self.assertEqual(loaded, tokens)

    def test_roundtrip_default_session(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                tokens = {"access_token": "xyz", "expires_at": "2099-01-01T00:00:00+00:00"}
                save_tokens("default", tokens)
                loaded = load_tokens("default")
                self.assertEqual(loaded, tokens)

    def test_two_profiles_sharing_same_session_see_same_tokens(self):
        """Profiles that map to the same session name share a token file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                tokens = {"access_token": "shared", "expires_at": "2099-01-01T00:00:00+00:00"}
                save_tokens("shared-session", tokens)
                # Both reads from the same session name return the same tokens.
                self.assertEqual(load_tokens("shared-session"), tokens)
                self.assertEqual(load_tokens("shared-session"), tokens)

    def test_load_nonexistent_returns_none(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                result = load_tokens("does-not-exist")
                self.assertIsNone(result)

    def test_file_permissions(self):
        """Token file should be owner-read/write only (0o600)."""
        import platform

        if platform.system() == "Windows":
            self.skipTest("chmod not applicable on Windows")
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                save_tokens("perm-test", {"access_token": "t"})
                path = Path(tmpdir) / "perm-test" / "tokens.json"
                mode = path.stat().st_mode & 0o777
                self.assertEqual(mode, 0o600)


class TestIsTokenExpired(unittest.TestCase):
    """Tests for is_token_expired."""

    def test_future_token_not_expired(self):
        future = (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()
        self.assertFalse(is_token_expired({"access_token": "x", "expires_at": future}))

    def test_past_token_expired(self):
        past = (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat()
        self.assertTrue(is_token_expired({"access_token": "x", "expires_at": past}))

    def test_token_expiring_within_30s_considered_expired(self):
        soon = (datetime.now(tz=timezone.utc) + timedelta(seconds=10)).isoformat()
        self.assertTrue(is_token_expired({"access_token": "x", "expires_at": soon}))

    def test_missing_expires_at_not_expired(self):
        self.assertFalse(is_token_expired({"access_token": "x"}))

    def test_invalid_expires_at_treated_as_expired(self):
        self.assertTrue(is_token_expired({"access_token": "x", "expires_at": "not-a-date"}))


class TestPKCEGeneration(unittest.TestCase):
    """Tests for PKCE code verifier / challenge generation."""

    def test_code_verifier_url_safe(self):
        verifier, _ = _generate_pkce_pair()
        # URL-safe base64 characters plus '-' and '_'.
        self.assertRegex(verifier, r"^[A-Za-z0-9_\-]+$")

    def test_code_challenge_url_safe_no_padding(self):
        _, challenge = _generate_pkce_pair()
        self.assertNotIn("=", challenge)
        self.assertNotIn("+", challenge)
        self.assertNotIn("/", challenge)

    def test_different_verifiers_each_call(self):
        v1, _ = _generate_pkce_pair()
        v2, _ = _generate_pkce_pair()
        self.assertNotEqual(v1, v2)

    def test_challenge_is_sha256_of_verifier(self):
        import base64
        import hashlib

        verifier, challenge = _generate_pkce_pair()
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        expected = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        self.assertEqual(challenge, expected)


class TestApplySystemCerts(unittest.TestCase):
    """Tests for apply_system_certs helper."""

    def test_calls_inject_into_ssl(self):
        import truststore  # noqa: F401
        from nextmv.auth import apply_system_certs

        with patch("truststore.inject_into_ssl") as mock_inject:
            apply_system_certs()
            mock_inject.assert_called_once()

    def test_idempotent(self):
        import truststore  # noqa: F401
        from nextmv.auth import apply_system_certs

        with patch("truststore.inject_into_ssl") as mock_inject:
            apply_system_certs()
            apply_system_certs()
            self.assertEqual(mock_inject.call_count, 2)

    def test_sets_uv_system_certs_env_var(self):
        """UV_SYSTEM_CERTS is set so uv subprocesses trust the system cert store."""
        import truststore  # noqa: F401
        from nextmv.auth import apply_system_certs

        old_val = os.environ.pop("UV_SYSTEM_CERTS", None)
        try:
            with patch("truststore.inject_into_ssl"):
                apply_system_certs()
            self.assertEqual(os.environ.get("UV_SYSTEM_CERTS"), "true")
        finally:
            if old_val is not None:
                os.environ["UV_SYSTEM_CERTS"] = old_val
            else:
                os.environ.pop("UV_SYSTEM_CERTS", None)

    def test_does_not_override_existing_uv_system_certs(self):
        """If UV_SYSTEM_CERTS is already set, apply_system_certs does not overwrite it."""
        import truststore  # noqa: F401
        from nextmv.auth import apply_system_certs

        os.environ["UV_SYSTEM_CERTS"] = "false"
        try:
            with patch("truststore.inject_into_ssl"):
                apply_system_certs()
            self.assertEqual(os.environ["UV_SYSTEM_CERTS"], "false")
        finally:
            os.environ.pop("UV_SYSTEM_CERTS", None)


class TestValidateTokenResponse(unittest.TestCase):
    """Tests for _validate_token_response."""

    def test_valid_bearer_response(self):
        from nextmv.auth import _validate_token_response

        # Should not raise.
        _validate_token_response({"access_token": "tok", "token_type": "Bearer"})

    def test_valid_bearer_case_insensitive(self):
        from nextmv.auth import _validate_token_response

        _validate_token_response({"access_token": "tok", "token_type": "bearer"})
        _validate_token_response({"access_token": "tok", "token_type": "BEARER"})

    def test_missing_access_token(self):
        from nextmv.auth import _validate_token_response

        with self.assertRaises(ValueError) as ctx:
            _validate_token_response({"token_type": "Bearer"})
        self.assertIn("access_token", str(ctx.exception))

    def test_missing_token_type(self):
        from nextmv.auth import _validate_token_response

        with self.assertRaises(ValueError) as ctx:
            _validate_token_response({"access_token": "tok"})
        self.assertIn("token_type", str(ctx.exception))

    def test_unsupported_token_type(self):
        from nextmv.auth import _validate_token_response

        with self.assertRaises(ValueError) as ctx:
            _validate_token_response({"access_token": "tok", "token_type": "mac"})
        self.assertIn("mac", str(ctx.exception))


class TestValidateIdToken(unittest.TestCase):
    """Tests for _validate_id_token JWT validation."""

    @staticmethod
    def _make_jwt(payload: dict) -> str:
        import base64
        import json

        payload_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=").decode()
        return f"header.{payload_b64}.sig"

    def test_valid_token_passes(self):
        import time

        from nextmv.auth import CLIENT_ID as cid
        from nextmv.auth import _validate_id_token

        jwt = self._make_jwt({"aud": cid, "exp": int(time.time()) + 3600})
        _validate_id_token(jwt, cid)  # should not raise

    def test_aud_mismatch_raises(self):
        import time

        from nextmv.auth import _validate_id_token

        jwt = self._make_jwt({"aud": "wrong", "exp": int(time.time()) + 3600})
        with self.assertRaises(ValueError) as ctx:
            _validate_id_token(jwt, "expected")
        self.assertIn("aud", str(ctx.exception))

    def test_expired_token_raises(self):
        import time

        from nextmv.auth import CLIENT_ID as cid
        from nextmv.auth import _validate_id_token

        jwt = self._make_jwt({"aud": cid, "exp": int(time.time()) - 1})
        with self.assertRaises(ValueError) as ctx:
            _validate_id_token(jwt, cid)
        self.assertIn("expired", str(ctx.exception).lower())

    def test_missing_exp_raises(self):
        from nextmv.auth import _validate_id_token

        jwt = self._make_jwt({"aud": "x"})
        with self.assertRaises(ValueError) as ctx:
            _validate_id_token(jwt, "x")
        self.assertIn("exp", str(ctx.exception))

    def test_broken_jwt_raises(self):
        from nextmv.auth import _validate_id_token

        with self.assertRaises(ValueError):
            _validate_id_token("not.a.jwt", "x")


class TestDiscoverEndpoints(unittest.TestCase):
    """Tests for _discover_endpoints with custom oidc_discovery_url."""

    def test_custom_url_is_fetched(self):
        custom_url = "https://idp.example.com/.well-known/openid-configuration"
        mock_doc = {
            "authorization_endpoint": "https://idp.example.com/authorize",
            "token_endpoint": "https://idp.example.com/token",
            "end_session_endpoint": "https://idp.example.com/logout",
            "revocation_endpoint": "https://idp.example.com/revoke",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_doc
        mock_response.raise_for_status.return_value = None

        with patch("nextmv.auth.requests.get", return_value=mock_response) as mock_get:
            endpoints = _discover_endpoints(custom_url)

        mock_get.assert_called_once_with(custom_url, timeout=10)
        self.assertEqual(endpoints.authorization, "https://idp.example.com/authorize")
        self.assertEqual(endpoints.token, "https://idp.example.com/token")
        self.assertEqual(endpoints.logout, "https://idp.example.com/logout")
        self.assertEqual(endpoints.revocation, "https://idp.example.com/revoke")

    def test_custom_url_logout_fallback_when_absent(self):
        """end_session_endpoint absent from discovery doc -> falls back to hardcoded value."""
        mock_doc = {
            "authorization_endpoint": "https://idp.example.com/authorize",
            "token_endpoint": "https://idp.example.com/token",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_doc
        mock_response.raise_for_status.return_value = None

        with patch("nextmv.auth.requests.get", return_value=mock_response):
            endpoints = _discover_endpoints("https://idp.example.com/.well-known/openid-configuration")

        self.assertEqual(endpoints.logout, auth_module._FALLBACK_LOGOUT_ENDPOINT)
        self.assertEqual(endpoints.revocation, auth_module._FALLBACK_REVOKE_ENDPOINT)

    def test_none_uses_module_level_constant(self):
        mock_doc = {
            "authorization_endpoint": "https://prod.example.com/authorize",
            "token_endpoint": "https://prod.example.com/token",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_doc
        mock_response.raise_for_status.return_value = None

        with patch("nextmv.auth.requests.get", return_value=mock_response) as mock_get:
            _discover_endpoints(None)

        mock_get.assert_called_once_with(auth_module.OIDC_DISCOVERY_URL, timeout=10)

    def test_fallback_on_default_url_failure(self):
        """Default URL failure falls back to hardcoded endpoints."""
        with patch("nextmv.auth.requests.get", side_effect=Exception("network error")):
            endpoints = _discover_endpoints(None)
        for endpoint in endpoints:
            self.assertTrue(endpoint.startswith("http"))

    def test_custom_url_failure_raises(self):
        """Explicit URL failure raises instead of falling back silently."""
        with patch("nextmv.auth.requests.get", side_effect=Exception("network error")):
            with self.assertRaises(RuntimeError) as ctx:
                _discover_endpoints("https://broken.example.com/discovery")
        self.assertIn("Failed to fetch", str(ctx.exception))


class TestFetchOrganizations(unittest.TestCase):
    """Tests for fetch_organizations helper."""

    _SAMPLE_ORGS = [
        {"id": "uuid-1", "name": "Acme Corp", "pending_invite": False, "role": "admin"},
        {"id": "uuid-2", "name": "Nextmv", "pending_invite": False, "role": "developer"},
    ]

    def _mock_response(self, payload):
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_resp.raise_for_status.return_value = None
        return mock_resp

    def test_returns_org_list(self):
        with patch("nextmv.auth.requests.get", return_value=self._mock_response(self._SAMPLE_ORGS)) as mock_get:
            result = fetch_organizations("tok-abc", "api.cloud.nextmv.io")
        self.assertEqual(result, self._SAMPLE_ORGS)
        called_url = mock_get.call_args[0][0]
        self.assertIn("/v1/internal/me/organization", called_url)

    def test_bearer_token_sent(self):
        with patch("nextmv.auth.requests.get", return_value=self._mock_response([])) as mock_get:
            fetch_organizations("my-token", "api.cloud.nextmv.io")
        headers = mock_get.call_args[1]["headers"]
        self.assertEqual(headers["Authorization"], "Bearer my-token")

    def test_endpoint_without_scheme_gets_https(self):
        with patch("nextmv.auth.requests.get", return_value=self._mock_response([])) as mock_get:
            fetch_organizations("tok", "api.cloud.nextmv.io")
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith("https://"))

    def test_endpoint_with_https_scheme_stripped(self):
        with patch("nextmv.auth.requests.get", return_value=self._mock_response([])) as mock_get:
            fetch_organizations("tok", "https://api.cloud.nextmv.io")
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith("https://"))
        self.assertNotIn("https://https://", called_url)

    def test_http_endpoint_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            fetch_organizations("tok", "http://api.cloud.nextmv.io")
        self.assertIn("Refusing", str(ctx.exception))

    def test_http_error_propagates(self):
        import requests as req_lib

        mock_resp = MagicMock()
        mock_resp.raise_for_status.side_effect = req_lib.HTTPError("403 Forbidden")
        with patch("nextmv.auth.requests.get", return_value=mock_resp):
            with self.assertRaises(req_lib.HTTPError):
                fetch_organizations("bad-token", "api.cloud.nextmv.io")


class TestRunPkceFlowForceParam(unittest.TestCase):
    """Tests that run_pkce_flow uses the logout-chain URL when force=True."""

    _AUTH_EP = "https://auth.example.com/oauth2/authorize"
    _TOKEN_EP = "https://auth.example.com/oauth2/token"
    _LOGOUT_EP = "https://auth.example.com/logout"
    _REVOKE_EP = "https://auth.example.com/oauth2/revoke"

    def _run(self, force: bool, **kwargs) -> str:
        """Run the flow and return the URL that was opened in the browser."""
        import threading

        opened_urls: list[str] = []
        state_holder: list[str] = []
        ready = threading.Event()

        def record(url: str) -> None:
            opened_urls.append(url)
            qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
            state_holder.append(qs.get("state", ""))
            ready.set()

        def fake_wait_for_callback(port):
            ready.wait(timeout=5)
            return {"code": "authcode123", "state": state_holder[0] if state_holder else ""}

        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status.return_value = None
        mock_token_resp.json.return_value = {
            "access_token": "acc",
            "refresh_token": "ref",
            "id_token": "id",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        endpoints = auth_module._Endpoints(
            authorization=self._AUTH_EP,
            token=self._TOKEN_EP,
            logout=self._LOGOUT_EP,
            revocation=self._REVOKE_EP,
        )

        with (
            patch("nextmv.auth._discover_endpoints", return_value=endpoints),
            patch("nextmv.auth.webbrowser.open", side_effect=record),
            patch("nextmv.auth._wait_for_callback", side_effect=fake_wait_for_callback),
            patch("nextmv.auth.requests.post", return_value=mock_token_resp),
        ):
            from nextmv.auth import run_pkce_flow

            # `url_callback` keeps the state available when the browser is not
            # opened, so the fake callback can echo it back.
            run_pkce_flow(force=force, url_callback=record, **kwargs)

        return opened_urls[0]

    def test_force_false_opens_auth_endpoint(self):
        """Without force=True, the authorization endpoint is opened directly."""
        url = self._run(force=False)
        self.assertTrue(url.startswith(self._AUTH_EP), url)
        qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        self.assertNotIn("prompt", qs)

    def test_force_true_opens_logout_endpoint(self):
        """With force=True, the logout endpoint is opened (logout-chain approach)."""
        url = self._run(force=True)
        self.assertTrue(url.startswith(self._LOGOUT_EP), url)

    def test_force_true_logout_url_contains_auth_params(self):
        """The logout-chain URL carries all required PKCE/auth params."""
        url = self._run(force=True)
        qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        for key in ("client_id", "redirect_uri", "response_type", "scope", "code_challenge", "state"):
            self.assertIn(key, qs, f"Missing param: {key}")

    def test_force_with_identity_provider_keeps_authorize_endpoint(self):
        """
        The logout chain is skipped for a federated login.

        The logout endpoint redirects to the login page, which drops
        `identity_provider` and offers the user pool's own sign-in form.
        """
        url = self._run(force=True, identity_provider="Okta")
        self.assertTrue(url.startswith(self._AUTH_EP), url)
        qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        self.assertEqual(qs["identity_provider"], "Okta")
        self.assertIn("code_challenge", qs)

    def test_open_browser_false_does_not_open_a_browser(self):
        """With open_browser=False the URL is reported but no browser is opened."""
        import threading

        reported: list[str] = []
        ready = threading.Event()

        def report(url: str) -> None:
            reported.append(url)
            ready.set()

        def fake_wait_for_callback(port):
            ready.wait(timeout=5)
            qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(reported[0]).query))
            return {"code": "authcode123", "state": qs.get("state", "")}

        mock_token_resp = MagicMock()
        mock_token_resp.raise_for_status.return_value = None
        mock_token_resp.json.return_value = {
            "access_token": "acc",
            "token_type": "Bearer",
            "expires_in": 3600,
        }

        endpoints = auth_module._Endpoints(
            authorization=self._AUTH_EP,
            token=self._TOKEN_EP,
            logout=self._LOGOUT_EP,
            revocation=self._REVOKE_EP,
        )

        with (
            patch("nextmv.auth._discover_endpoints", return_value=endpoints),
            patch("nextmv.auth.webbrowser.open") as mock_open,
            patch("nextmv.auth._wait_for_callback", side_effect=fake_wait_for_callback),
            patch("nextmv.auth.requests.post", return_value=mock_token_resp),
        ):
            from nextmv.auth import run_pkce_flow

            run_pkce_flow(open_browser=False, url_callback=report)

        mock_open.assert_not_called()
        self.assertTrue(reported[0].startswith(self._AUTH_EP), reported[0])


class TestRefreshTokens(unittest.TestCase):
    """Tests for refresh_tokens."""

    _TOKEN_EP = "https://auth.example.com/oauth2/token"
    _LOGOUT_EP = "https://auth.example.com/logout"

    def _mock_post(self, payload=None):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = payload or {
            "access_token": "new-acc",
            "token_type": "Bearer",
            "expires_in": 3600,
        }
        return mock_resp

    def test_discovered_token_endpoint_is_used(self):
        """
        The grant is posted to the token endpoint.

        Regression test: the endpoints were unpacked positionally, which sent
        the grant to the logout endpoint and made every refresh fail.
        """
        endpoints = auth_module._Endpoints(
            authorization="https://auth.example.com/oauth2/authorize",
            token=self._TOKEN_EP,
            logout=self._LOGOUT_EP,
            revocation="https://auth.example.com/oauth2/revoke",
        )

        with (
            patch("nextmv.auth._discover_endpoints", return_value=endpoints),
            patch("nextmv.auth.requests.post", return_value=self._mock_post()) as mock_post,
        ):
            auth_module.refresh_tokens("my-refresh-token")

        self.assertEqual(mock_post.call_args[0][0], self._TOKEN_EP)

    def test_explicit_token_endpoint_skips_discovery(self):
        with (
            patch("nextmv.auth._discover_endpoints") as mock_discover,
            patch("nextmv.auth.requests.post", return_value=self._mock_post()) as mock_post,
        ):
            auth_module.refresh_tokens("my-refresh-token", token_endpoint=self._TOKEN_EP)

        mock_discover.assert_not_called()
        self.assertEqual(mock_post.call_args[0][0], self._TOKEN_EP)

    def test_refresh_grant_payload(self):
        with patch("nextmv.auth.requests.post", return_value=self._mock_post()) as mock_post:
            auth_module.refresh_tokens("my-refresh-token", token_endpoint=self._TOKEN_EP, client_id="cid-1")

        payload = mock_post.call_args[1]["data"]
        self.assertEqual(payload["grant_type"], "refresh_token")
        self.assertEqual(payload["refresh_token"], "my-refresh-token")
        self.assertEqual(payload["client_id"], "cid-1")

    def test_existing_refresh_token_is_preserved(self):
        """The provider omits the refresh token on refresh; it must be kept."""
        with patch("nextmv.auth.requests.post", return_value=self._mock_post()):
            tokens = auth_module.refresh_tokens("my-refresh-token", token_endpoint=self._TOKEN_EP)

        self.assertEqual(tokens["refresh_token"], "my-refresh-token")
        self.assertIn("expires_at", tokens)

    def test_http_error_is_wrapped(self):
        import requests as req_lib

        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = '{"error":"invalid_grant"}'
        mock_resp.raise_for_status.side_effect = req_lib.HTTPError("400")

        with patch("nextmv.auth.requests.post", return_value=mock_resp):
            with self.assertRaises(req_lib.HTTPError) as ctx:
                auth_module.refresh_tokens("stale", token_endpoint=self._TOKEN_EP)

        self.assertIn("Token refresh failed", str(ctx.exception))


class TestRevokeRefreshToken(unittest.TestCase):
    """Tests for revoke_refresh_token."""

    _REVOKE_EP = "https://auth.example.com/oauth2/revoke"

    def _endpoints(self):
        return auth_module._Endpoints(
            authorization="https://auth.example.com/oauth2/authorize",
            token="https://auth.example.com/oauth2/token",
            logout="https://auth.example.com/logout",
            revocation=self._REVOKE_EP,
        )

    def test_posts_token_to_revocation_endpoint(self):
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None

        with (
            patch("nextmv.auth._discover_endpoints", return_value=self._endpoints()),
            patch("nextmv.auth.requests.post", return_value=mock_resp) as mock_post,
        ):
            auth_module.revoke_refresh_token("my-refresh-token", client_id="cid-1")

        self.assertEqual(mock_post.call_args[0][0], self._REVOKE_EP)
        payload = mock_post.call_args[1]["data"]
        self.assertEqual(payload["token"], "my-refresh-token")
        self.assertEqual(payload["client_id"], "cid-1")

    def test_http_error_is_wrapped(self):
        import requests as req_lib

        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "nope"
        mock_resp.raise_for_status.side_effect = req_lib.HTTPError("400")

        with (
            patch("nextmv.auth._discover_endpoints", return_value=self._endpoints()),
            patch("nextmv.auth.requests.post", return_value=mock_resp),
        ):
            with self.assertRaises(req_lib.HTTPError) as ctx:
                auth_module.revoke_refresh_token("my-refresh-token")

        self.assertIn("Token revocation failed", str(ctx.exception))


class TestBrowserLogoutUrl(unittest.TestCase):
    """Tests for browser_logout_url."""

    def test_url_targets_logout_endpoint_with_allowed_callback(self):
        endpoints = auth_module._Endpoints(
            authorization="https://auth.example.com/oauth2/authorize",
            token="https://auth.example.com/oauth2/token",
            logout="https://auth.example.com/logout",
            revocation="https://auth.example.com/oauth2/revoke",
        )

        with patch("nextmv.auth._discover_endpoints", return_value=endpoints):
            url = auth_module.browser_logout_url(client_id="cid-1")

        self.assertTrue(url.startswith("https://auth.example.com/logout?"), url)
        qs = dict(urllib.parse.parse_qsl(urllib.parse.urlparse(url).query))
        self.assertEqual(qs["client_id"], "cid-1")
        # The landing URL has to be an allowed callback URL, which the local
        # callback already is.
        self.assertEqual(qs["redirect_uri"], f"http://127.0.0.1:{auth_module.CALLBACK_PORT}")
        self.assertEqual(qs["response_type"], "code")


class TestTokenIdentity(unittest.TestCase):
    """Tests for token_identity and identity_mismatch."""

    @staticmethod
    def _jwt(claims: dict) -> str:
        payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        return f"header.{payload}.signature"

    def test_local_user_has_no_providers(self):
        identity = auth_module.token_identity(self._jwt({"email": "user@example.com"}))
        self.assertEqual(identity.email, "user@example.com")
        self.assertEqual(identity.providers, ())

    def test_federated_user_providers_are_read(self):
        jwt = self._jwt(
            {
                "email": "user@example.com",
                "identities": [{"providerName": "Okta", "providerType": "SAML"}],
            }
        )
        self.assertEqual(auth_module.token_identity(jwt).providers, ("Okta",))

    def test_identities_claim_encoded_as_string(self):
        jwt = self._jwt({"identities": json.dumps([{"providerName": "Okta"}])})
        self.assertEqual(auth_module.token_identity(jwt).providers, ("Okta",))

    def test_identities_claim_as_single_object(self):
        jwt = self._jwt({"identities": {"providerName": "Okta"}})
        self.assertEqual(auth_module.token_identity(jwt).providers, ("Okta",))

    def test_missing_email_is_none(self):
        self.assertIsNone(auth_module.token_identity(self._jwt({"sub": "abc"})).email)

    def test_undecodable_token_raises(self):
        with self.assertRaises(ValueError):
            auth_module.token_identity("not.a.jwt")

    def test_no_expectations_means_no_mismatch(self):
        jwt = self._jwt({"email": "user@example.com"})
        self.assertIsNone(auth_module.identity_mismatch(jwt))

    def test_matching_provider_and_domain(self):
        jwt = self._jwt({"email": "user@example.com", "identities": [{"providerName": "Okta"}]})
        self.assertIsNone(auth_module.identity_mismatch(jwt, expected_provider="Okta", expected_domain="example.com"))

    def test_sso_requested_but_local_login_returned(self):
        """The stale browser session case: no federated identity in the token."""
        jwt = self._jwt({"email": "user@example.com"})
        mismatch = auth_module.identity_mismatch(jwt, expected_provider="Okta")
        self.assertEqual(mismatch.kind, "provider")
        self.assertIn("directly against the user pool", mismatch.reason)

    def test_sso_requested_but_other_provider_returned(self):
        jwt = self._jwt({"email": "user@example.com", "identities": [{"providerName": "Google"}]})
        mismatch = auth_module.identity_mismatch(jwt, expected_provider="Okta")
        self.assertEqual(mismatch.kind, "provider")
        self.assertIn("Google", mismatch.reason)

    def test_domain_mismatch_is_reported(self):
        jwt = self._jwt({"email": "user@other.com"})
        mismatch = auth_module.identity_mismatch(jwt, expected_domain="example.com")
        self.assertEqual(mismatch.kind, "domain")
        self.assertIn("other.com", mismatch.reason)

    def test_domain_comparison_is_case_insensitive(self):
        jwt = self._jwt({"email": "User@Example.COM"})
        self.assertIsNone(auth_module.identity_mismatch(jwt, expected_domain="example.com"))

    def test_domain_not_checked_without_email(self):
        jwt = self._jwt({"sub": "abc"})
        self.assertIsNone(auth_module.identity_mismatch(jwt, expected_domain="example.com"))


if __name__ == "__main__":
    unittest.main()
