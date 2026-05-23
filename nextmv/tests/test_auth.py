"""
Unit tests for the PKCE auth helpers in nextmv.auth.
"""

import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

from nextmv.auth import _generate_pkce_pair, is_token_expired, load_tokens, save_tokens, token_dir


class TestTokenDir(unittest.TestCase):
    """Tests for token_dir path resolution."""

    def test_none_profile_maps_to_default(self):
        path = token_dir(None)
        self.assertTrue(path.name == "default")

    def test_default_string_maps_to_default(self):
        path = token_dir("default")
        self.assertTrue(path.name == "default")

    def test_named_profile(self):
        path = token_dir("staging")
        self.assertTrue(path.name == "staging")

    def test_named_profile_whitespace(self):
        path = token_dir("  prod  ")
        self.assertTrue(path.name == "prod")

    def test_traversal_rejected(self):
        with self.assertRaises(ValueError):
            token_dir("../evil")

    def test_absolute_path_rejected(self):
        with self.assertRaises(ValueError):
            token_dir("/etc/passwd")


class TestSaveLoadTokens(unittest.TestCase):
    """Tests for save_tokens / load_tokens round-trip."""

    def test_roundtrip_named_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                tokens = {
                    "access_token": "abc123",
                    "refresh_token": "def456",
                    "token_type": "Bearer",
                    "expires_at": "2099-01-01T00:00:00+00:00",
                }
                save_tokens("myprofile", tokens)
                loaded = load_tokens("myprofile")
                self.assertEqual(loaded, tokens)

    def test_roundtrip_default_profile(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.auth.AUTH_DIR", Path(tmpdir)):
                tokens = {"access_token": "xyz", "expires_at": "2099-01-01T00:00:00+00:00"}
                save_tokens(None, tokens)
                loaded = load_tokens(None)
                self.assertEqual(loaded, tokens)

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


if __name__ == "__main__":
    unittest.main()
