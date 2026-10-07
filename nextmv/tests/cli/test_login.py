"""
Unit tests for the ``nextmv auth login`` command.
"""

import base64
import json
import unittest
from unittest.mock import patch

from nextmv.cli.main import app
from nextmv.config import DEFAULT_AUTH_SESSION
from typer.testing import CliRunner

_BUILTIN_OIDC_CFG = {
    "oidc_discovery_url": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_1jHS2b9HU/.well-known/openid-configuration",
    "client_id": "test-client-id",
}

_FAKE_TOKENS = {"access_token": "tok", "refresh_token": "ref", "id_token": "id"}


class TestLoginDeduplication(unittest.TestCase):
    """Tests that nextmv login only triggers one browser flow per session."""

    def setUp(self):
        self.runner = CliRunner()

    def _run_login(self, config, sessions=None):
        if sessions is None:
            sessions = {}
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value=sessions),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.login.run_pkce_flow", return_value=_FAKE_TOKENS) as mock_flow,
            patch("nextmv.cli.auth.login.save_tokens") as mock_save,
        ):
            result = self.runner.invoke(app, ["auth", "login"])
            return result, mock_flow, mock_save

    def test_single_profile_one_flow(self):
        """One pkce profile -> one browser flow."""
        config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        result, mock_flow, mock_save = self._run_login(config)

        self.assertEqual(result.exit_code, 0, result.output)
        mock_flow.assert_called_once()
        mock_save.assert_called_once_with(DEFAULT_AUTH_SESSION, _FAKE_TOKENS)

    def test_two_profiles_same_session_one_flow(self):
        """Two pkce profiles sharing the same auth session -> one browser flow."""
        config = {
            "dev": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
            "staging": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
        }
        result, mock_flow, mock_save = self._run_login(config)

        self.assertEqual(result.exit_code, 0, result.output)
        mock_flow.assert_called_once()
        mock_save.assert_called_once_with("work", _FAKE_TOKENS)

    def test_two_profiles_different_sessions_two_flows(self):
        """Two pkce profiles with different sessions -> two browser flows."""
        config = {
            "dev": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
            "personal": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "home"},
        }
        result, mock_flow, mock_save = self._run_login(config)

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_flow.call_count, 2)
        self.assertEqual(mock_save.call_count, 2)
        saved_sessions = {c.args[0] for c in mock_save.call_args_list}
        self.assertEqual(saved_sessions, {"work", "home"})

    def test_two_profiles_same_name_different_endpoints_two_flows(self):
        """Same session name but different endpoints -> two browser flows (different OIDC configs)."""
        prod_oidc = {**_BUILTIN_OIDC_CFG}
        staging_oidc = {**_BUILTIN_OIDC_CFG, "client_id": "staging-client"}

        config = {
            "prod": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "myid"},
            "staging": {"auth_type": "pkce", "endpoint": "staging.nextmv.io", "auth_session": "myid"},
        }

        def oidc_side_effect(endpoint, sessions):
            if endpoint == "staging.nextmv.io":
                return staging_oidc
            return prod_oidc

        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", side_effect=oidc_side_effect),
            patch("nextmv.cli.auth.login.run_pkce_flow", return_value=_FAKE_TOKENS) as mock_flow,
            patch("nextmv.cli.auth.login.save_tokens") as mock_save,
        ):
            result = self.runner.invoke(app, ["auth", "login"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_flow.call_count, 2)
        self.assertEqual(mock_save.call_count, 2)

    def test_no_pkce_profiles_no_flow(self):
        """No pkce profiles -> no browser flow, informational message."""
        config = {"api_key": "key123", "endpoint": "api.cloud.nextmv.io"}
        result, mock_flow, mock_save = self._run_login(config)

        self.assertEqual(result.exit_code, 0, result.output)
        mock_flow.assert_not_called()
        mock_save.assert_not_called()

    def test_missing_oidc_config_skips_and_fails(self):
        """Profile with no OIDC config is skipped and exits non-zero."""
        config = {"auth_type": "pkce", "endpoint": "unknown.example.com"}
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=None),
            patch("nextmv.cli.auth.login.run_pkce_flow") as mock_flow,
            patch("nextmv.cli.auth.login.save_tokens") as mock_save,
        ):
            result = self.runner.invoke(app, ["auth", "login"])

        self.assertNotEqual(result.exit_code, 0)
        mock_flow.assert_not_called()
        mock_save.assert_not_called()

    def test_failed_flow_marks_profiles_failed(self):
        """If the PKCE flow raises, all profiles in that session are reported as failed."""
        config = {
            "dev": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
            "staging": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
        }
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.login.run_pkce_flow", side_effect=RuntimeError("browser closed")),
            patch("nextmv.cli.auth.login.save_tokens") as mock_save,
        ):
            result = self.runner.invoke(app, ["auth", "login"])

        self.assertNotEqual(result.exit_code, 0)
        mock_save.assert_not_called()
        self.assertIn("dev", result.output)
        self.assertIn("staging", result.output)


class TestLoginForceFlag(unittest.TestCase):
    """Tests that --force is forwarded to run_pkce_flow."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, extra_args=None):
        config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        args = ["auth", "login"] + (extra_args or [])
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.login.run_pkce_flow", return_value=_FAKE_TOKENS) as mock_flow,
            patch("nextmv.cli.auth.login.save_tokens"),
        ):
            result = self.runner.invoke(app, args)
            return result, mock_flow

    def test_no_force_flag_passes_false(self):
        """Without --force, run_pkce_flow receives force=False."""
        result, mock_flow = self._invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        _, kwargs = mock_flow.call_args
        self.assertFalse(kwargs.get("force", False))

    def test_force_flag_passes_true(self):
        """With --force, run_pkce_flow receives force=True."""
        result, mock_flow = self._invoke(["--force"])
        self.assertEqual(result.exit_code, 0, result.output)
        _, kwargs = mock_flow.call_args
        self.assertTrue(kwargs.get("force", False))


class TestLoginNoBrowserFlag(unittest.TestCase):
    """Tests for the --no-browser flag."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, extra_args=None):
        config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        args = ["auth", "login"] + (extra_args or [])
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.login.run_pkce_flow", return_value=_FAKE_TOKENS) as mock_flow,
            patch("nextmv.cli.auth.login.save_tokens"),
        ):
            result = self.runner.invoke(app, args)
            return result, mock_flow

    def test_default_opens_browser(self):
        result, mock_flow = self._invoke()
        self.assertEqual(result.exit_code, 0, result.output)
        _, kwargs = mock_flow.call_args
        self.assertTrue(kwargs["open_browser"])
        self.assertIsNone(kwargs["url_callback"])

    def test_no_browser_suppresses_browser_and_reports_url(self):
        result, mock_flow = self._invoke(["--no-browser"])
        self.assertEqual(result.exit_code, 0, result.output)
        _, kwargs = mock_flow.call_args
        self.assertFalse(kwargs["open_browser"])
        self.assertIsNotNone(kwargs["url_callback"])


class TestLoginIdentityCheck(unittest.TestCase):
    """Tests that a login returning the wrong identity is rejected."""

    def setUp(self):
        self.runner = CliRunner()

    @staticmethod
    def _jwt(claims):
        payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")
        return f"header.{payload}.signature"

    def _invoke(self, claims, sso_provider="Okta"):
        config = {
            "auth_type": "pkce",
            "endpoint": "api.cloud.nextmv.io",
            "sso_domain": "example.com",
        }
        tokens = {"access_token": "tok", "refresh_token": "ref", "id_token": self._jwt(claims)}
        with (
            patch("nextmv.cli.auth.login.load_config", return_value=config),
            patch("nextmv.cli.auth.login.load_sessions", return_value={}),
            patch("nextmv.cli.auth.login.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.login.fetch_sso_provider", return_value=sso_provider),
            patch("nextmv.cli.auth.login.run_pkce_flow", return_value=tokens),
            patch("nextmv.cli.auth.login.save_tokens") as mock_save,
        ):
            result = self.runner.invoke(app, ["auth", "login"])
            return result, mock_save

    def test_matching_identity_is_stored(self):
        result, mock_save = self._invoke({"email": "user@example.com", "identities": [{"providerName": "Okta"}]})
        self.assertEqual(result.exit_code, 0, result.output)
        mock_save.assert_called_once()
        self.assertIn("user@example.com", result.output)

    def test_stale_session_identity_is_rejected(self):
        """
        A token without the requested federated identity is not stored.

        This is the stale browser session case: the flow completes, but the
        token belongs to the previous login context.
        """
        result, mock_save = self._invoke({"email": "user@example.com"})
        self.assertEqual(result.exit_code, 1)
        mock_save.assert_not_called()
        self.assertIn("--no-browser", result.output)

    def test_unexpected_email_domain_is_reported_but_stored(self):
        """A secondary address is legitimate, so it warns rather than failing."""
        result, mock_save = self._invoke(
            {"email": "user@other.com", "identities": [{"providerName": "Okta"}]},
        )
        self.assertEqual(result.exit_code, 0, result.output)
        mock_save.assert_called_once()
        self.assertIn("other.com", result.output)


if __name__ == "__main__":
    unittest.main()
