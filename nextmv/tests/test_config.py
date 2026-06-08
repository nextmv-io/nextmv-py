"""
Unit tests for the configuration helpers in nextmv.config.
"""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from nextmv.config import (
    CLIENT_ID_KEY,
    DEFAULT_AUTH_SESSION,
    DEFAULT_ENDPOINT,
    OIDC_DISCOVERY_URL_KEY,
    AuthType,
    get_auth_session,
    get_auth_type,
    get_endpoint_oidc_config,
    get_profile_endpoint,
    get_team_id,
    list_pkce_profiles,
    load_sessions,
    save_sessions,
)


class TestGetProfileType(unittest.TestCase):
    """Tests for get_auth_type helper."""

    def test_default_profile_no_key_returns_api_key(self):
        config = {"apikey": "sk-xxx", "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(get_auth_type(config, None), AuthType.API_KEY)

    def test_default_profile_pkce(self):
        config = {"auth_type": AuthType.PKCE, "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(get_auth_type(config, None), AuthType.PKCE)

    def test_named_profile_api_key(self):
        config = {
            "staging": {
                "apikey": "sk-yyy",
                "endpoint": "api.cloud.nextmv.io",
                "auth_type": AuthType.API_KEY,
            }
        }
        self.assertEqual(get_auth_type(config, "staging"), AuthType.API_KEY)

    def test_named_profile_pkce(self):
        config = {
            "auth-profile": {
                "endpoint": "api.cloud.nextmv.io",
                "auth_type": AuthType.PKCE,
            }
        }
        self.assertEqual(get_auth_type(config, "auth-profile"), AuthType.PKCE)

    def test_named_profile_missing_type_defaults_to_api_key(self):
        config = {"legacy": {"apikey": "sk-zzz", "endpoint": "api.cloud.nextmv.io"}}
        self.assertEqual(get_auth_type(config, "legacy"), AuthType.API_KEY)


class TestGetAuthSession(unittest.TestCase):
    """Tests for get_auth_session helper."""

    def test_default_profile_no_auth_session_returns_default(self):
        config = {"auth_type": AuthType.PKCE, "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(get_auth_session(config, None), DEFAULT_AUTH_SESSION)

    def test_default_profile_explicit_auth_session(self):
        config = {
            "auth_type": AuthType.PKCE,
            "endpoint": "api.cloud.nextmv.io",
            "auth_session": "my-work",
        }
        self.assertEqual(get_auth_session(config, None), "my-work")

    def test_named_profile_no_auth_session_returns_default(self):
        config = {
            "dev": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
            }
        }
        self.assertEqual(get_auth_session(config, "dev"), DEFAULT_AUTH_SESSION)

    def test_named_profile_explicit_auth_session(self):
        config = {
            "dev": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
                "auth_session": "my-work",
            }
        }
        self.assertEqual(get_auth_session(config, "dev"), "my-work")

    def test_two_profiles_sharing_same_session(self):
        config = {
            "dev": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
                "auth_session": "shared",
            },
            "staging": {
                "auth_type": AuthType.PKCE,
                "endpoint": "staging.cloud.nextmv.io",
                "auth_session": "shared",
            },
        }
        self.assertEqual(get_auth_session(config, "dev"), "shared")
        self.assertEqual(get_auth_session(config, "staging"), "shared")

    def test_profiles_without_session_share_default(self):
        config = {
            "dev": {"auth_type": AuthType.PKCE, "endpoint": "api.cloud.nextmv.io"},
            "staging": {"auth_type": AuthType.PKCE, "endpoint": "staging.cloud.nextmv.io"},
        }
        self.assertEqual(get_auth_session(config, "dev"), DEFAULT_AUTH_SESSION)
        self.assertEqual(get_auth_session(config, "staging"), DEFAULT_AUTH_SESSION)

    def test_whitespace_only_auth_session_returns_default(self):
        config = {
            "dev": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
                "auth_session": "   ",
            }
        }
        self.assertEqual(get_auth_session(config, "dev"), DEFAULT_AUTH_SESSION)

    def test_auth_session_value_is_stripped(self):
        config = {
            "dev": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
                "auth_session": "  my-session  ",
            }
        }
        self.assertEqual(get_auth_session(config, "dev"), "my-session")


class TestListPkceProfiles(unittest.TestCase):
    """Tests for list_pkce_profiles helper."""

    def test_no_pkce_profiles(self):
        config = {"apikey": "sk-xxx", "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(list_pkce_profiles(config), [])

    def test_default_pkce_profile(self):
        config = {"auth_type": AuthType.PKCE, "endpoint": "api.cloud.nextmv.io"}
        self.assertIn(None, list_pkce_profiles(config))

    def test_named_pkce_profile(self):
        config = {
            "myauth": {
                "auth_type": AuthType.PKCE,
                "endpoint": "api.cloud.nextmv.io",
            },
            "apionly": {
                "apikey": "sk",
                "endpoint": "api.cloud.nextmv.io",
            },
        }
        result = list_pkce_profiles(config)
        self.assertIn("myauth", result)
        self.assertNotIn("apionly", result)

    def test_mixed_profiles(self):
        config = {
            "auth_type": AuthType.PKCE,
            "endpoint": "api.cloud.nextmv.io",
            "named-auth": {"auth_type": AuthType.PKCE, "endpoint": "api.cloud.nextmv.io"},
            "named-api": {"apikey": "sk", "endpoint": "api.cloud.nextmv.io"},
        }
        result = list_pkce_profiles(config)
        self.assertIn(None, result)
        self.assertIn("named-auth", result)
        self.assertNotIn("named-api", result)


class TestGetProfileEndpoint(unittest.TestCase):
    """Tests for get_profile_endpoint helper."""

    def test_default_profile_returns_default_endpoint(self):
        config = {"apikey": "sk-xxx"}
        self.assertEqual(get_profile_endpoint(config, None), DEFAULT_ENDPOINT)

    def test_default_profile_explicit_endpoint(self):
        config = {"endpoint": "staging.example.com"}
        self.assertEqual(get_profile_endpoint(config, None), "staging.example.com")

    def test_named_profile_explicit_endpoint(self):
        config = {"dev": {"endpoint": "dev.example.com"}}
        self.assertEqual(get_profile_endpoint(config, "dev"), "dev.example.com")

    def test_https_prefix_stripped(self):
        config = {"endpoint": "https://api.cloud.nextmv.io"}
        self.assertEqual(get_profile_endpoint(config, None), "api.cloud.nextmv.io")

    def test_http_prefix_stripped(self):
        config = {"dev": {"endpoint": "http://dev.example.com/"}}
        self.assertEqual(get_profile_endpoint(config, "dev"), "dev.example.com")

    def test_missing_named_profile_returns_default(self):
        config = {}
        self.assertEqual(get_profile_endpoint(config, "nonexistent"), DEFAULT_ENDPOINT)

    def test_null_endpoint_falls_back_to_default(self):
        config = {"endpoint": None}
        self.assertEqual(get_profile_endpoint(config, None), DEFAULT_ENDPOINT)

    def test_null_endpoint_named_profile_falls_back_to_default(self):
        config = {"dev": {"endpoint": None}}
        self.assertEqual(get_profile_endpoint(config, "dev"), DEFAULT_ENDPOINT)


class TestGetEndpointOidcConfig(unittest.TestCase):
    """Tests for get_endpoint_oidc_config helper."""

    def test_production_endpoint_builtin_fallback(self):
        result = get_endpoint_oidc_config(DEFAULT_ENDPOINT, None)
        self.assertIsNotNone(result)
        self.assertIn(OIDC_DISCOVERY_URL_KEY, result)
        self.assertIn(CLIENT_ID_KEY, result)

    def test_sessions_overrides_builtin(self):
        sessions = {
            DEFAULT_ENDPOINT: {
                OIDC_DISCOVERY_URL_KEY: "https://custom.example.com/.well-known/openid-configuration",
                CLIENT_ID_KEY: "custom-client-id",
            }
        }
        result = get_endpoint_oidc_config(DEFAULT_ENDPOINT, sessions)
        self.assertEqual(result[OIDC_DISCOVERY_URL_KEY], "https://custom.example.com/.well-known/openid-configuration")
        self.assertEqual(result[CLIENT_ID_KEY], "custom-client-id")

    def test_unknown_endpoint_returns_none(self):
        result = get_endpoint_oidc_config("unknown.example.com", None)
        self.assertIsNone(result)

    def test_custom_endpoint_found_in_sessions(self):
        sessions = {
            "dev.example.com": {
                OIDC_DISCOVERY_URL_KEY: "https://idp.dev.example.com/.well-known/openid-configuration",
                CLIENT_ID_KEY: "dev-client-id",
            }
        }
        result = get_endpoint_oidc_config("dev.example.com", sessions)
        self.assertIsNotNone(result)
        self.assertEqual(result[CLIENT_ID_KEY], "dev-client-id")

    def test_https_prefix_stripped_before_lookup(self):
        sessions = {
            "dev.example.com": {
                OIDC_DISCOVERY_URL_KEY: "https://idp.dev.example.com/.well-known/openid-configuration",
                CLIENT_ID_KEY: "dev-client-id",
            }
        }
        result = get_endpoint_oidc_config("https://dev.example.com", sessions)
        self.assertIsNotNone(result)
        self.assertEqual(result[CLIENT_ID_KEY], "dev-client-id")

    def test_incomplete_sessions_entry_falls_through_to_builtin(self):
        # Entry missing client_id — should fall back to builtin for prod endpoint.
        sessions = {DEFAULT_ENDPOINT: {OIDC_DISCOVERY_URL_KEY: "https://custom.example.com/..."}}
        result = get_endpoint_oidc_config(DEFAULT_ENDPOINT, sessions)
        # Incomplete entry falls through; builtin should be returned.
        self.assertIsNotNone(result)
        self.assertIn(CLIENT_ID_KEY, result)


class TestLoadSaveSessions(unittest.TestCase):
    """Tests for load_sessions and save_sessions helpers."""

    def test_load_returns_empty_when_file_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("nextmv.config.SESSIONS_FILE", Path(tmpdir) / "sessions.yaml"):
                result = load_sessions()
        self.assertEqual(result, {})

    def test_roundtrip(self):
        sessions = {
            "dev.example.com": {
                OIDC_DISCOVERY_URL_KEY: "https://idp.dev.example.com/.well-known/openid-configuration",
                CLIENT_ID_KEY: "dev-client-id",
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_path = Path(tmpdir) / "sessions.yaml"
            with patch("nextmv.config.SESSIONS_FILE", sessions_path):
                with patch("nextmv.config.CONFIG_DIR", Path(tmpdir)):
                    save_sessions(sessions)
                    result = load_sessions()
        self.assertEqual(result, sessions)

    def test_load_returns_empty_dict_for_empty_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions_path = Path(tmpdir) / "sessions.yaml"
            sessions_path.write_text("")
            with patch("nextmv.config.SESSIONS_FILE", sessions_path):
                result = load_sessions()
        self.assertEqual(result, {})


class TestGetTeamId(unittest.TestCase):
    """Tests for get_team_id helper."""

    def test_default_profile_with_team_id(self):
        config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "team_id": "abc-123"}
        self.assertEqual(get_team_id(config, None), "abc-123")

    def test_default_profile_without_team_id(self):
        config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        self.assertIsNone(get_team_id(config, None))

    def test_named_profile_with_team_id(self):
        config = {"work": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "team_id": "team-uuid"}}
        self.assertEqual(get_team_id(config, "work"), "team-uuid")

    def test_named_profile_without_team_id(self):
        config = {"work": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}}
        self.assertIsNone(get_team_id(config, "work"))

    def test_whitespace_stripped(self):
        config = {"team_id": "  uuid-with-spaces  "}
        self.assertEqual(get_team_id(config, None), "uuid-with-spaces")

    def test_empty_string_returns_none(self):
        config = {"team_id": ""}
        self.assertIsNone(get_team_id(config, None))

    def test_named_profile_not_in_config_returns_none(self):
        config = {}
        self.assertIsNone(get_team_id(config, "nonexistent"))


class TestGetSystemCerts(unittest.TestCase):
    """Tests for get_system_certs helper."""

    def test_default_profile_no_key_returns_false(self):
        from nextmv.config import get_system_certs
        config = {"apikey": "sk-xxx", "endpoint": "api.cloud.nextmv.io"}
        self.assertFalse(get_system_certs(config, None))

    def test_default_profile_system_certs_true(self):
        from nextmv.config import get_system_certs
        config = {"system_certs": True, "endpoint": "api.cloud.nextmv.io"}
        self.assertTrue(get_system_certs(config, None))

    def test_named_profile_system_certs_true(self):
        from nextmv.config import get_system_certs
        config = {
            "work": {"system_certs": True, "endpoint": "api.cloud.nextmv.io"},
        }
        self.assertTrue(get_system_certs(config, "work"))

    def test_named_profile_no_key_returns_false(self):
        from nextmv.config import get_system_certs
        config = {
            "work": {"endpoint": "api.cloud.nextmv.io"},
        }
        self.assertFalse(get_system_certs(config, "work"))

    def test_missing_profile_returns_false(self):
        from nextmv.config import get_system_certs
        config = {}
        self.assertFalse(get_system_certs(config, "nonexistent"))


if __name__ == "__main__":
    unittest.main()
