"""
Unit tests for the PKCE auth helpers in nextmv.auth.
"""

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import nextmv.auth as auth_module
from nextmv.auth import _discover_endpoints, _generate_pkce_pair, is_token_expired, load_tokens, save_tokens, token_dir


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


if __name__ == "__main__":
    unittest.main()
