import base64
import json
import os
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import requests
from nextmv.cloud import Client


def _make_id_token(aud: str = "test-client-id") -> str:
    """Build a mock JWT id_token with the given aud claim and future exp."""
    exp = int((datetime.now(tz=timezone.utc) + timedelta(hours=1)).timestamp())
    payload = json.dumps({"aud": aud, "exp": exp})
    payload_b64 = base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()
    return f"header.{payload_b64}.sig"


class TestResolveProfile(unittest.TestCase):
    """Tests for Client.__resolve_profile (exercised via __post_init__)."""

    def test_env_var_used_as_profile(self):
        """NEXTMV_PROFILE env var is used as the active profile."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": "my-profile"}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.api_key, "k")

    def test_env_var_overrides_profile_attribute(self):
        """NEXTMV_PROFILE env var takes precedence over the profile attribute."""
        config = {
            "env-profile": {"apikey": "env-key", "endpoint": "api.env.io"},
            "attr-profile": {"apikey": "attr-key", "endpoint": "api.attr.io"},
        }
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": "env-profile"}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="attr-profile")
                self.assertEqual(client.api_key, "env-key")

    def test_profile_attribute_used_when_env_var_absent(self):
        """profile attribute is used when NEXTMV_PROFILE is not set."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "k")

    def test_empty_env_var_falls_back_to_profile_attribute(self):
        """Empty NEXTMV_PROFILE falls back to the profile attribute."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": ""}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "k")

    def test_no_profile_uses_default_config(self):
        """When neither profile source is set, the default config entry is used."""
        config = {"apikey": "default-key"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.api_key, "default-key")

    def test_nonexistent_profile_raises_value_error(self):
        """A profile that is not present in the config file raises ValueError."""
        config = {"other-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": "missing-profile"}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client()


class TestResolveEndpoint(unittest.TestCase):
    """Tests for Client.__resolve_endpoint (exercised via __post_init__)."""

    def test_url_attribute_takes_highest_precedence(self):
        """url attribute is used even when NEXTMV_ENDPOINT is set."""
        with patch.dict(
            os.environ,
            {"NEXTMV_API_KEY": "k", "NEXTMV_ENDPOINT": "https://env.example.com"},
        ) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client(url="https://attr.example.com")
            self.assertEqual(client.url, "https://attr.example.com")

    def test_empty_url_attribute_falls_through_to_env_var(self):
        """An empty url attribute is ignored; NEXTMV_ENDPOINT is used instead."""
        with patch.dict(
            os.environ,
            {"NEXTMV_API_KEY": "k", "NEXTMV_ENDPOINT": "https://env.example.com"},
        ) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client(url="")
            self.assertEqual(client.url, "https://env.example.com")

    def test_env_var_used_when_url_attribute_absent(self):
        """NEXTMV_ENDPOINT is used when no url attribute is provided."""
        with patch.dict(
            os.environ,
            {"NEXTMV_API_KEY": "k", "NEXTMV_ENDPOINT": "https://env.example.com"},
        ) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client()
            self.assertEqual(client.url, "https://env.example.com")

    def test_env_var_takes_precedence_over_config(self):
        """NEXTMV_ENDPOINT takes precedence over the endpoint stored in config."""
        config = {"apikey": "k", "endpoint": "api.config.io"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(
                os.environ,
                {"NEXTMV_API_KEY": "k", "NEXTMV_ENDPOINT": "https://env.example.com"},
            ) as env:
                env.pop("NEXTMV_PROFILE", None)
                client = Client()
                self.assertEqual(client.url, "https://env.example.com")

    def test_profile_endpoint_from_config(self):
        """When a profile is active, its endpoint is resolved from the config."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.profile.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.url, "https://api.profile.io")

    def test_default_endpoint_from_config(self):
        """When no profile is active, the default endpoint is read from config."""
        config = {"apikey": "k", "endpoint": "api.default.io"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.url, "https://api.default.io")

    def test_fallback_to_hardcoded_default_when_no_config(self):
        """Falls back to the hardcoded default URL when the config file is absent."""
        with patch("nextmv.cloud.client.load_config", return_value={}):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k"}) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.url, "https://api.cloud.nextmv.io")

    def test_missing_endpoint_for_profile_raises_value_error(self):
        """A profile with no endpoint key raises ValueError."""
        config = {"my-profile": {"apikey": "k"}}  # no endpoint
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_empty_endpoint_for_profile_raises_value_error(self):
        """A profile with an empty endpoint raises ValueError."""
        config = {"my-profile": {"apikey": "k", "endpoint": ""}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_profile_takes_precedence_over_default_config_endpoint(self):
        """A named profile's endpoint overrides the top-level default endpoint."""
        config = {
            "endpoint": "api.default.io",
            "apikey": "default-k",
            "my-profile": {"apikey": "profile-k", "endpoint": "api.profile.io"},
        }
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.url, "https://api.profile.io")


class TestResolveApiKey(unittest.TestCase):
    """Tests for Client.__resolve_api_key (exercised via __post_init__)."""

    def test_api_key_attribute_takes_highest_precedence(self):
        """api_key attribute is used even when NEXTMV_API_KEY is set."""
        with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client(api_key="attr-key")
            self.assertEqual(client.api_key, "attr-key")

    def test_empty_api_key_attribute_falls_through_to_env_var(self):
        """An empty api_key attribute is ignored; NEXTMV_API_KEY is used instead."""
        with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client(api_key="")
            self.assertEqual(client.api_key, "env-key")

    def test_env_var_used_when_no_api_key_attribute(self):
        """NEXTMV_API_KEY env var is used when no api_key attribute is provided."""
        with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client()
            self.assertEqual(client.api_key, "env-key")

    def test_env_var_takes_precedence_over_config(self):
        """NEXTMV_API_KEY takes precedence over the key stored in config."""
        config = {"apikey": "config-key"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
                env.pop("NEXTMV_PROFILE", None)
                client = Client()
                self.assertEqual(client.api_key, "env-key")

    def test_profile_api_key_from_config(self):
        """When a profile is active, its api_key is resolved from the config."""
        config = {"my-profile": {"apikey": "profile-key", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "profile-key")

    def test_default_api_key_from_config(self):
        """When no profile is active, the default api_key is read from config."""
        config = {"apikey": "default-key"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.api_key, "default-key")

    def test_profile_takes_precedence_over_default_config_api_key(self):
        """A named profile's api_key overrides the top-level default api_key."""
        config = {
            "apikey": "default-key",
            "my-profile": {"apikey": "profile-key", "endpoint": "api.profile.io"},
        }
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "profile-key")

    def test_all_sources_absent_raises_value_error(self):
        """Raises ValueError with a helpful message when no API key is found."""
        with patch("nextmv.cloud.client.load_config", return_value={}):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                with self.assertRaises(ValueError) as ctx:
                    Client()
                self.assertIn("API key is missing", str(ctx.exception))

    def test_missing_api_key_for_profile_raises_value_error(self):
        """A profile with no apikey raises ValueError."""
        config = {"my-profile": {"endpoint": "api.example.io"}}  # no apikey
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_empty_api_key_for_profile_raises_value_error(self):
        """A profile with an empty apikey raises ValueError."""
        config = {"my-profile": {"apikey": "", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_missing_default_api_key_in_config_raises_value_error(self):
        """Config file without a top-level apikey raises ValueError."""
        config = {"endpoint": "api.default.io"}  # no apikey
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError) as ctx:
                    Client()
                self.assertIn("API key is missing", str(ctx.exception))


class TestSetHeadersApiKey(unittest.TestCase):
    """Tests for Client.__set_headers_api_key (exercised via __post_init__)."""

    def test_authorization_header_uses_bearer_scheme(self):
        """Authorization header is set to 'Bearer <api_key>'."""
        client = Client(api_key="my-secret-key")
        self.assertEqual(client.headers["Authorization"], "Bearer my-secret-key")

    def test_content_type_header_is_application_json(self):
        """Content-Type header is always set to 'application/json'."""
        client = Client(api_key="my-secret-key")
        self.assertEqual(client.headers["Content-Type"], "application/json")

    def test_headers_dict_is_not_none(self):
        """headers attribute is a non-None dict after __post_init__."""
        client = Client(api_key="my-secret-key")
        self.assertIsNotNone(client.headers)
        self.assertIsInstance(client.headers, dict)

    def test_headers_reflect_api_key_from_env_var(self):
        """Authorization header uses the API key resolved from NEXTMV_API_KEY."""
        with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
            env.pop("NEXTMV_PROFILE", None)
            client = Client()
            self.assertEqual(client.headers["Authorization"], "Bearer env-key")

    def test_headers_reflect_api_key_from_config(self):
        """Authorization header uses the API key resolved from the config file."""
        config = {"apikey": "config-key"}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.headers["Authorization"], "Bearer config-key")

    def test_headers_reflect_api_key_from_profile_config(self):
        """Authorization header uses the API key resolved from a named profile."""
        config = {"my-profile": {"apikey": "profile-key", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.headers["Authorization"], "Bearer profile-key")


class TestSetHeadersPkce(unittest.TestCase):
    """Tests for nextmv-account header on pkce profiles."""

    def _pkce_config(self, team_id=None, profile_name="work"):
        entry = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        if team_id:
            entry["team_id"] = team_id
        return {profile_name: entry}

    def _make_pkce_client(self, config, profile="work", token=None):
        from datetime import datetime, timezone

        id_token = token if token else _make_id_token()
        tokens = {
            "id_token": id_token,
            "access_token": "acc-tok",
            "refresh_token": "refresh-xyz",
            "expires_at": (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat(),
        }
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch("nextmv.cloud.client.load_tokens", return_value=tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=False):
                    with patch("nextmv.cloud.client._validate_id_token"):  # skip JWT validation
                        with patch.dict(os.environ) as env:
                            env.pop("NEXTMV_API_KEY", None)
                            env.pop("NEXTMV_PROFILE", None)
                            env.pop("NEXTMV_ENDPOINT", None)
                            return Client(profile=profile)

    def test_nextmv_account_header_set_when_team_id_present(self):
        """nextmv-account header is set to the team UUID for pkce profiles."""
        config = self._pkce_config(team_id="team-uuid-123")
        client = self._make_pkce_client(config)
        self.assertEqual(client.headers.get("nextmv-account"), "team-uuid-123")

    def test_nextmv_account_header_absent_when_no_team_id(self):
        """nextmv-account header is not set when team_id is absent."""
        config = self._pkce_config(team_id=None)
        client = self._make_pkce_client(config)
        self.assertNotIn("nextmv-account", client.headers)

    def test_authorization_header_uses_id_token(self):
        """Authorization header uses the id_token for pkce profiles."""
        config = self._pkce_config(team_id="tid")
        id_token = _make_id_token(aud="test-client-id")
        client = self._make_pkce_client(config, token=id_token)
        self.assertIn("Bearer", client.headers["Authorization"])


class TestRequestUnreachableServer(unittest.TestCase):
    """Tests for Client.request when the server is unreachable."""

    def _make_client(self):
        return Client(api_key="test-key", url="https://api.does-not-exist.invalid")

    def test_connection_error_raises_friendly_message(self):
        """ConnectionError is re-raised with a helpful message about the endpoint."""
        client = self._make_client()
        with patch("requests.Session.request", side_effect=requests.exceptions.ConnectionError("raw")):
            with self.assertRaises(requests.exceptions.ConnectionError) as ctx:
                client.request(method="GET", endpoint="/v1/test")
            msg = str(ctx.exception)
            self.assertIn("https://api.does-not-exist.invalid", msg)
            self.assertIn("unreachable", msg)

    def test_timeout_raises_friendly_message(self):
        """Timeout is re-raised with a helpful message mentioning the timeout value."""
        client = self._make_client()
        with patch("requests.Session.request", side_effect=requests.exceptions.Timeout("raw")):
            with self.assertRaises(requests.exceptions.Timeout) as ctx:
                client.request(method="GET", endpoint="/v1/test")
            msg = str(ctx.exception)
            self.assertIn("/v1/test", msg)
            self.assertIn(str(client.timeout), msg)
            self.assertIn("timeout", msg.lower())

    def test_connection_error_preserves_original_cause(self):
        """The original ConnectionError is chained as __cause__."""
        client = self._make_client()
        original = requests.exceptions.ConnectionError("original cause")
        with patch("requests.Session.request", side_effect=original):
            with self.assertRaises(requests.exceptions.ConnectionError) as ctx:
                client.request(method="GET", endpoint="/v1/test")
            self.assertIs(ctx.exception.__cause__, original)

    def test_timeout_preserves_original_cause(self):
        """The original Timeout is chained as __cause__."""
        client = self._make_client()
        original = requests.exceptions.Timeout("original cause")
        with patch("requests.Session.request", side_effect=original):
            with self.assertRaises(requests.exceptions.Timeout) as ctx:
                client.request(method="GET", endpoint="/v1/test")
            self.assertIs(ctx.exception.__cause__, original)


class TestUploadToPresignedUrlUnreachableServer(unittest.TestCase):
    """Tests for Client.upload_to_presigned_url when the server is unreachable."""

    def _make_client(self):
        return Client(api_key="test-key", url="https://api.does-not-exist.invalid")

    def test_connection_error_raises_friendly_message(self):
        """ConnectionError during upload is re-raised with a helpful message."""
        client = self._make_client()
        with patch("requests.Session.put", side_effect=requests.exceptions.ConnectionError("raw")):
            with self.assertRaises(requests.exceptions.ConnectionError) as ctx:
                client.upload_to_presigned_url(data={"key": "value"}, url="https://storage.example.com/presigned")
            msg = str(ctx.exception)
            self.assertIn("unreachable", msg)

    def test_timeout_raises_friendly_message(self):
        """Timeout during upload is re-raised with a helpful message."""
        client = self._make_client()
        with patch("requests.Session.put", side_effect=requests.exceptions.Timeout("raw")):
            with self.assertRaises(requests.exceptions.Timeout) as ctx:
                client.upload_to_presigned_url(data={"key": "value"}, url="https://storage.example.com/presigned")
            msg = str(ctx.exception)
            self.assertIn(str(client.timeout), msg)
            self.assertIn("timeout", msg.lower())

    def test_connection_error_preserves_original_cause(self):
        """The original ConnectionError is chained as __cause__ during upload."""
        client = self._make_client()
        original = requests.exceptions.ConnectionError("original cause")
        with patch("requests.Session.put", side_effect=original):
            with self.assertRaises(requests.exceptions.ConnectionError) as ctx:
                client.upload_to_presigned_url(data={"key": "value"}, url="https://storage.example.com/presigned")
            self.assertIs(ctx.exception.__cause__, original)

    def test_timeout_preserves_original_cause(self):
        """The original Timeout is chained as __cause__ during upload."""
        client = self._make_client()
        original = requests.exceptions.Timeout("original cause")
        with patch("requests.Session.put", side_effect=original):
            with self.assertRaises(requests.exceptions.Timeout) as ctx:
                client.upload_to_presigned_url(data={"key": "value"}, url="https://storage.example.com/presigned")
            self.assertIs(ctx.exception.__cause__, original)


# Shared config / env helpers for pkce tests.
_PKCE_CONFIG = {
    "my-auth-profile": {
        "auth_type": "pkce",
        "endpoint": "api.example.io",
    }
}


def _clean_env(env):
    """Remove all auth/profile env vars so tests are fully config-driven."""
    for key in ("NEXTMV_API_KEY", "NEXTMV_PROFILE", "NEXTMV_ENDPOINT"):
        env.pop(key, None)


class TestResolveBearerTokenForPkce(unittest.TestCase):
    """Tests for Client.__resolve_bearer_token_for_pkce (via __post_init__)."""

    def test_pkce_profile_uses_stored_token(self):
        """A valid, non-expired token is used directly as the bearer token."""
        id_token = _make_id_token()
        tokens = {"id_token": id_token, "access_token": "stored-access", "expires_at": _future()}
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=False):
                    with patch("nextmv.cloud.client._validate_id_token"):
                        with patch.dict(os.environ) as env:
                            _clean_env(env)
                            client = Client(profile="my-auth-profile")
                            self.assertEqual(client.api_key, id_token)

    def test_pkce_profile_uses_id_token_only(self):
        """Only the id_token is used (no access_token fallback)."""
        id_token = _make_id_token()
        tokens = {"id_token": id_token, "access_token": "decoy", "expires_at": _future()}
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=False):
                    with patch("nextmv.cloud.client._validate_id_token"):
                        with patch.dict(os.environ) as env:
                            _clean_env(env)
                            client = Client(profile="my-auth-profile")
                            self.assertEqual(client.api_key, id_token)

    def test_expired_token_triggers_refresh_and_save(self):
        """An expired token is refreshed, saved, and the old id_token is preserved."""
        old_id_token = _make_id_token()
        old_tokens = {"id_token": old_id_token, "access_token": "old", "refresh_token": "rt", "expires_at": _past()}
        new_tokens = {"access_token": "new", "expires_at": _future()}  # refresh response: no id_token
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=old_tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=True):
                    with patch("nextmv.cloud.client.load_sessions", return_value={}):
                        with patch("nextmv.cloud.client.refresh_tokens", return_value=new_tokens) as mock_refresh:
                            with patch("nextmv.cloud.client.save_tokens") as mock_save:
                                with patch("nextmv.cloud.client._validate_id_token"):
                                    with patch.dict(os.environ) as env:
                                        _clean_env(env)
                                        client = Client(profile="my-auth-profile")
                                        self.assertEqual(client.api_key, old_id_token)
                                        mock_refresh.assert_called_once_with(
                                            "rt",
                                            oidc_discovery_url=None,
                                            client_id=None,
                                        )
                                    # Tokens are saved against the resolved session name
                                    # ("default" because _PKCE_CONFIG has no auth_session).
                                    mock_save.assert_called_once_with("default", new_tokens)

    def test_expired_token_triggers_refresh_and_save_named_session(self):
        """Tokens are saved against the named session, not the profile name."""
        config = {
            "my-auth-profile": {
                "auth_type": "pkce",
                "endpoint": "api.example.io",
                "auth_session": "my-session",
            }
        }
        old_tokens = {"id_token": _make_id_token(), "access_token": "old", "refresh_token": "rt", "expires_at": _past()}
        new_tokens = {"access_token": "new", "expires_at": _future()}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch("nextmv.cloud.client.load_tokens", return_value=old_tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=True):
                    with patch("nextmv.cloud.client.refresh_tokens", return_value=new_tokens):
                        with patch("nextmv.cloud.client.save_tokens") as mock_save:
                            with patch("nextmv.cloud.client._validate_id_token"):
                                with patch.dict(os.environ) as env:
                                    _clean_env(env)
                                    Client(profile="my-auth-profile")
                                    mock_save.assert_called_once_with("my-session", new_tokens)

    def test_shared_session_two_profiles_load_same_session(self):
        """Two profiles sharing an auth_session both resolve to the same session name."""
        config = {
            "profile-a": {
                "auth_type": "pkce",
                "endpoint": "api.example.io",
                "auth_session": "shared",
            },
            "profile-b": {
                "auth_type": "pkce",
                "endpoint": "staging.example.io",
                "auth_session": "shared",
            },
        }
        tokens = {"id_token": _make_id_token(), "access_token": "tok", "expires_at": _future()}
        load_calls: list[str] = []

        def _load_tokens(session: str):
            load_calls.append(session)
            return tokens

        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch("nextmv.cloud.client.load_tokens", side_effect=_load_tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=False):
                    with patch("nextmv.cloud.client._validate_id_token"):
                        with patch.dict(os.environ) as env:
                            _clean_env(env)
                            Client(profile="profile-a")
                            Client(profile="profile-b")
        # Both profiles must have loaded from the same "shared" session.
        self.assertEqual(load_calls, ["shared", "shared"])

    def test_expired_token_without_refresh_token_raises(self):
        """Expired token with no refresh_token raises ValueError."""
        tokens = {"id_token": _make_id_token(), "access_token": "old", "expires_at": _past()}  # no refresh_token
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=True):
                    with patch.dict(os.environ) as env:
                        _clean_env(env)
                        with self.assertRaises(ValueError) as ctx:
                            Client(profile="my-auth-profile")
                        self.assertIn("no refresh token", str(ctx.exception))

    def test_missing_tokens_raises(self):
        """No stored tokens raises ValueError directing the user to nextmv auth login."""
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=None):
                with patch.dict(os.environ) as env:
                    _clean_env(env)
                    with self.assertRaises(ValueError) as ctx:
                        Client(profile="my-auth-profile")
                    self.assertIn("nextmv auth login", str(ctx.exception))

    def test_refresh_failure_raises(self):
        """A failed token refresh raises ValueError with a helpful message."""
        tokens = {"access_token": "old", "refresh_token": "rt", "expires_at": _past()}
        with patch("nextmv.cloud.client.load_config", return_value=_PKCE_CONFIG):
            with patch("nextmv.cloud.client.load_tokens", return_value=tokens):
                with patch("nextmv.cloud.client.is_token_expired", return_value=True):
                    with patch("nextmv.cloud.client.refresh_tokens", side_effect=RuntimeError("network error")):
                        with patch.dict(os.environ) as env:
                            _clean_env(env)
                            with self.assertRaises(ValueError) as ctx:
                                Client(profile="my-auth-profile")
                            self.assertIn("network error", str(ctx.exception))

    def test_api_key_profile_uses_api_key_path(self):
        """A standard api_key profile is unaffected and still resolves the API key."""
        config = {"my-api-profile": {"apikey": "sk-123", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ) as env:
                _clean_env(env)
                client = Client(profile="my-api-profile")
                self.assertEqual(client.api_key, "sk-123")


class TestSystemCerts(unittest.TestCase):
    """Tests for system_certs resolution via env var and config."""

    def test_env_var_enables_system_certs(self):
        """NEXTMV_SYSTEM_CERTS=true enables system certs."""
        with patch("nextmv.cloud.client.load_config", return_value={"apikey": "k"}):
            with patch("nextmv.cloud.client.apply_system_certs") as mock_apply:
                with patch.dict(os.environ, {"NEXTMV_API_KEY": "k", "NEXTMV_SYSTEM_CERTS": "true"}):
                    client = Client()
                    self.assertTrue(client.system_certs)
                    mock_apply.assert_called_once()

    def test_env_var_one_enables_system_certs(self):
        """NEXTMV_SYSTEM_CERTS=1 enables system certs."""
        with patch("nextmv.cloud.client.load_config", return_value={"apikey": "k"}):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k", "NEXTMV_SYSTEM_CERTS": "1"}):
                client = Client()
                self.assertTrue(client.system_certs)

    def test_env_var_yes_enables_system_certs(self):
        """NEXTMV_SYSTEM_CERTS=yes enables system certs."""
        with patch("nextmv.cloud.client.load_config", return_value={"apikey": "k"}):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k", "NEXTMV_SYSTEM_CERTS": "yes"}):
                client = Client()
                self.assertTrue(client.system_certs)

    def test_env_var_false_does_not_enable(self):
        """NEXTMV_SYSTEM_CERTS=false does not enable system certs."""
        with patch("nextmv.cloud.client.load_config", return_value={"apikey": "k"}):
            with patch("nextmv.cloud.client.apply_system_certs") as mock_apply:
                with patch.dict(os.environ, {"NEXTMV_API_KEY": "k", "NEXTMV_SYSTEM_CERTS": "false"}):
                    client = Client()
                    self.assertFalse(client.system_certs)
                    mock_apply.assert_not_called()

    def test_explicit_constructor_overrides_env(self):
        """system_certs=True on constructor takes precedence over env var."""
        with patch("nextmv.cloud.client.load_config", return_value={"apikey": "k"}):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k", "NEXTMV_SYSTEM_CERTS": "false"}):
                client = Client(system_certs=True)
                self.assertTrue(client.system_certs)

    def test_config_fallback_when_no_env(self):
        """Falls back to config when env var is not set."""
        config = {"apikey": "k", "system_certs": True}
        with patch("nextmv.cloud.client.load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k"}, clear=False):
                os.environ.pop("NEXTMV_SYSTEM_CERTS", None)
                client = Client()
                self.assertTrue(client.system_certs)


def _future() -> str:
    return (datetime.now(tz=timezone.utc) + timedelta(hours=1)).isoformat()


def _past() -> str:
    return (datetime.now(tz=timezone.utc) - timedelta(hours=1)).isoformat()
