"""
Unit tests for the PKCE auth helpers in nextmv.auth.
"""

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

    def test_invalid_expires_at_not_expired(self):
        self.assertFalse(is_token_expired({"access_token": "x", "expires_at": "not-a-date"}))


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


class TestDiscoverEndpoints(unittest.TestCase):
    """Tests for _discover_endpoints with custom oidc_discovery_url."""

    def test_custom_url_is_fetched(self):
        custom_url = "https://idp.example.com/.well-known/openid-configuration"
        mock_doc = {
            "authorization_endpoint": "https://idp.example.com/authorize",
            "token_endpoint": "https://idp.example.com/token",
            "end_session_endpoint": "https://idp.example.com/logout",
        }
        mock_response = MagicMock()
        mock_response.json.return_value = mock_doc
        mock_response.raise_for_status.return_value = None

        with patch("nextmv.auth.requests.get", return_value=mock_response) as mock_get:
            auth_ep, token_ep = _discover_endpoints(custom_url)

        mock_get.assert_called_once_with(custom_url, timeout=10)
        self.assertEqual(auth_ep, "https://idp.example.com/authorize")
        self.assertEqual(token_ep, "https://idp.example.com/token")

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

    def test_fallback_on_request_failure(self):
        with patch("nextmv.auth.requests.get", side_effect=Exception("network error")):
            auth_ep, token_ep = _discover_endpoints("https://broken.example.com/discovery")
        # Should return the module-level fallbacks without raising.
        self.assertTrue(auth_ep.startswith("http"))
        self.assertTrue(token_ep.startswith("http"))


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

    def test_endpoint_with_scheme_preserved(self):
        with patch("nextmv.auth.requests.get", return_value=self._mock_response([])) as mock_get:
            fetch_organizations("tok", "https://api.cloud.nextmv.io")
        called_url = mock_get.call_args[0][0]
        self.assertTrue(called_url.startswith("https://"))

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

    def _run(self, force: bool) -> str:
        """Run the flow and return the URL that was opened in the browser."""
        import threading

        opened_urls: list[str] = []
        state_holder: list[str] = []
        ready = threading.Event()

        def fake_open(url: str) -> None:
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
            "expires_in": 3600,
        }

        with (
            patch("nextmv.auth._discover_endpoints", return_value=(self._AUTH_EP, self._TOKEN_EP, self._LOGOUT_EP)),
            patch("nextmv.auth.webbrowser.open", side_effect=fake_open),
            patch("nextmv.auth._wait_for_callback", side_effect=fake_wait_for_callback),
            patch("nextmv.auth.requests.post", return_value=mock_token_resp),
        ):
            from nextmv.auth import run_pkce_flow

            run_pkce_flow(force=force)

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


if __name__ == "__main__":
    unittest.main()
