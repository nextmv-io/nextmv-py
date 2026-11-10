"""
Unit tests for the ``nextmv auth logout`` command.
"""

import unittest
from unittest.mock import patch

from nextmv.cli.main import app
from nextmv.config import DEFAULT_AUTH_SESSION
from typer.testing import CliRunner

_BUILTIN_OIDC_CFG = {
    "oidc_discovery_url": "https://cognito-idp.us-east-2.amazonaws.com/us-east-2_1jHS2b9HU/.well-known/openid-configuration",
    "client_id": "test-client-id",
}

_STORED_TOKENS = {"access_token": "tok", "refresh_token": "ref", "id_token": "id"}


class TestLogout(unittest.TestCase):
    """Tests for token deletion and revocation."""

    def setUp(self):
        self.runner = CliRunner()

    def _invoke(self, config=None, extra_args=None, tokens=_STORED_TOKENS, revoke_side_effect=None):
        if config is None:
            config = {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io"}
        args = ["auth", "logout"] + (extra_args or [])
        with (
            patch("nextmv.cli.auth.logout.load_config", return_value=config),
            patch("nextmv.cli.auth.logout.load_sessions", return_value={}),
            patch("nextmv.cli.auth.logout.get_endpoint_oidc_config", return_value=_BUILTIN_OIDC_CFG),
            patch("nextmv.cli.auth.logout.load_tokens", return_value=tokens),
            patch(
                "nextmv.cli.auth.logout.revoke_refresh_token",
                side_effect=revoke_side_effect,
            ) as mock_revoke,
            patch("nextmv.cli.auth.logout.delete_tokens") as mock_delete,
            patch("nextmv.cli.auth.logout.browser_logout_url", return_value="https://auth.example.com/logout?x=1"),
            patch("nextmv.cli.auth.logout.webbrowser.open") as mock_browser,
        ):
            result = self.runner.invoke(app, args)
            return result, mock_revoke, mock_delete, mock_browser

    def test_tokens_are_revoked_then_deleted(self):
        result, mock_revoke, mock_delete, _ = self._invoke()

        self.assertEqual(result.exit_code, 0, result.output)
        mock_revoke.assert_called_once()
        self.assertEqual(mock_revoke.call_args[0][0], "ref")
        mock_delete.assert_called_once_with(DEFAULT_AUTH_SESSION)

    def test_revocation_uses_the_profile_oidc_config(self):
        _, mock_revoke, _, _ = self._invoke()

        kwargs = mock_revoke.call_args[1]
        self.assertEqual(kwargs["client_id"], _BUILTIN_OIDC_CFG["client_id"])
        self.assertEqual(kwargs["oidc_discovery_url"], _BUILTIN_OIDC_CFG["oidc_discovery_url"])

    def test_nothing_to_revoke_when_no_tokens_stored(self):
        result, mock_revoke, mock_delete, _ = self._invoke(tokens=None)

        self.assertEqual(result.exit_code, 0, result.output)
        mock_revoke.assert_not_called()
        mock_delete.assert_called_once()

    def test_failed_revocation_still_deletes_locally(self):
        """An unreachable provider must not block logging out."""
        result, _, mock_delete, _ = self._invoke(revoke_side_effect=RuntimeError("boom"))

        self.assertEqual(result.exit_code, 0, result.output)
        mock_delete.assert_called_once()
        self.assertIn("will expire on their own", result.output)

    def test_browser_not_opened_by_default(self):
        _, _, _, mock_browser = self._invoke()
        mock_browser.assert_not_called()

    def test_browser_flag_opens_sign_out_page(self):
        result, _, _, mock_browser = self._invoke(extra_args=["--browser"])

        self.assertEqual(result.exit_code, 0, result.output)
        mock_browser.assert_called_once_with("https://auth.example.com/logout?x=1")

    def test_browser_sign_out_is_opened_once_per_provider(self):
        """Sessions sharing an identity provider share a browser session."""
        config = {
            "dev": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "work"},
            "personal": {"auth_type": "pkce", "endpoint": "api.cloud.nextmv.io", "auth_session": "home"},
        }
        result, _, mock_delete, mock_browser = self._invoke(config=config, extra_args=["--browser"])

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_delete.call_count, 2)
        mock_browser.assert_called_once()

    def test_non_pkce_profile_is_rejected(self):
        config = {"my-profile": {"auth_type": "api_key", "endpoint": "api.cloud.nextmv.io"}}
        result, _, mock_delete, _ = self._invoke(config=config, extra_args=["--profile", "my-profile"])

        self.assertEqual(result.exit_code, 1)
        mock_delete.assert_not_called()

    def test_unknown_profile_is_rejected(self):
        result, _, mock_delete, _ = self._invoke(extra_args=["--profile", "nope"])

        self.assertEqual(result.exit_code, 1)
        mock_delete.assert_not_called()


if __name__ == "__main__":
    unittest.main()
