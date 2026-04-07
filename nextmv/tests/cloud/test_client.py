import os
import unittest
from unittest.mock import patch

from nextmv.cloud import Client


class TestResolveProfile(unittest.TestCase):
    """Tests for Client.__resolve_profile (exercised via __post_init__)."""

    def test_env_var_used_as_profile(self):
        """NEXTMV_PROFILE env var is used as the active profile."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": "env-profile"}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="attr-profile")
                self.assertEqual(client.api_key, "env-key")

    def test_profile_attribute_used_when_env_var_absent(self):
        """profile attribute is used when NEXTMV_PROFILE is not set."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "k")

    def test_empty_env_var_falls_back_to_profile_attribute(self):
        """Empty NEXTMV_PROFILE falls back to the profile attribute."""
        config = {"my-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_PROFILE": ""}) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "k")

    def test_no_profile_uses_default_config(self):
        """When neither profile source is set, the default config entry is used."""
        config = {"apikey": "default-key"}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.api_key, "default-key")

    def test_nonexistent_profile_raises_value_error(self):
        """A profile that is not present in the config file raises ValueError."""
        config = {"other-profile": {"apikey": "k", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.url, "https://api.profile.io")

    def test_default_endpoint_from_config(self):
        """When no profile is active, the default endpoint is read from config."""
        config = {"apikey": "k", "endpoint": "api.default.io"}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.url, "https://api.default.io")

    def test_fallback_to_hardcoded_default_when_no_config(self):
        """Falls back to the hardcoded default URL when the config file is absent."""
        with patch("nextmv.cloud.client._load_config", return_value={}):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "k"}) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.url, "https://api.cloud.nextmv.io")

    def test_missing_endpoint_for_profile_raises_value_error(self):
        """A profile with no endpoint key raises ValueError."""
        config = {"my-profile": {"apikey": "k"}}  # no endpoint
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_empty_endpoint_for_profile_raises_value_error(self):
        """A profile with an empty endpoint raises ValueError."""
        config = {"my-profile": {"apikey": "k", "endpoint": ""}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ, {"NEXTMV_API_KEY": "env-key"}) as env:
                env.pop("NEXTMV_PROFILE", None)
                client = Client()
                self.assertEqual(client.api_key, "env-key")

    def test_profile_api_key_from_config(self):
        """When a profile is active, its api_key is resolved from the config."""
        config = {"my-profile": {"apikey": "profile-key", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "profile-key")

    def test_default_api_key_from_config(self):
        """When no profile is active, the default api_key is read from config."""
        config = {"apikey": "default-key"}
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.api_key, "profile-key")

    def test_all_sources_absent_raises_value_error(self):
        """Raises ValueError with a helpful message when no API key is found."""
        with patch("nextmv.cloud.client._load_config", return_value={}):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                with self.assertRaises(ValueError) as ctx:
                    Client()
                self.assertIn("API key is missing", str(ctx.exception))

    def test_missing_api_key_for_profile_raises_value_error(self):
        """A profile with no apikey raises ValueError."""
        config = {"my-profile": {"endpoint": "api.example.io"}}  # no apikey
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_empty_api_key_for_profile_raises_value_error(self):
        """A profile with an empty apikey raises ValueError."""
        config = {"my-profile": {"apikey": "", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                with self.assertRaises(ValueError):
                    Client(profile="my-profile")

    def test_missing_default_api_key_in_config_raises_value_error(self):
        """Config file without a top-level apikey raises ValueError."""
        config = {"endpoint": "api.default.io"}  # no apikey
        with patch("nextmv.cloud.client._load_config", return_value=config):
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
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client()
                self.assertEqual(client.headers["Authorization"], "Bearer config-key")

    def test_headers_reflect_api_key_from_profile_config(self):
        """Authorization header uses the API key resolved from a named profile."""
        config = {"my-profile": {"apikey": "profile-key", "endpoint": "api.example.io"}}
        with patch("nextmv.cloud.client._load_config", return_value=config):
            with patch.dict(os.environ) as env:
                env.pop("NEXTMV_API_KEY", None)
                env.pop("NEXTMV_PROFILE", None)
                env.pop("NEXTMV_ENDPOINT", None)
                client = Client(profile="my-profile")
                self.assertEqual(client.headers["Authorization"], "Bearer profile-key")
