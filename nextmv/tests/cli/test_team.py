"""
Unit tests for team resolution in ``nextmv configuration create``.
"""

import os
import unittest
from unittest.mock import patch

import typer
from nextmv.cli.configuration.create import _resolve_team_id
from nextmv.cli.main import app
from typer.testing import CliRunner

_ACME_ID = "6b1f3a52-3c4d-4e5f-8a9b-0c1d2e3f4a5b"
_GLOBEX_ID = "7c2e4b63-4d5e-4f60-9bac-1d2e3f4a5b6c"

_ORGS = [
    {"id": _ACME_ID, "name": "Acme", "role": "admin", "pending_invite": False},
    {"id": _GLOBEX_ID, "name": "Globex", "role": "developer", "pending_invite": False},
]


class TestResolveTeamIdByName(unittest.TestCase):
    """Tests for resolving a team by name via --team."""

    def _resolve(self, team_name, orgs=_ORGS, fetch_side_effect=None):
        with (
            patch(
                "nextmv.cli.configuration.create.fetch_organizations",
                return_value=orgs,
                side_effect=fetch_side_effect,
            ) as mock_fetch,
            patch("nextmv.cli.configuration.create.choice") as mock_choice,
        ):
            result = _resolve_team_id(access_token="tok", endpoint="api.cloud.nextmv.io", team_name=team_name)
            return result, mock_fetch, mock_choice

    def test_name_is_looked_up(self):
        result, mock_fetch, mock_choice = self._resolve("Acme")

        self.assertEqual(result, _ACME_ID)
        mock_fetch.assert_called_once()
        mock_choice.assert_not_called()

    def test_name_lookup_is_case_insensitive(self):
        result, _, _ = self._resolve("acme")
        self.assertEqual(result, _ACME_ID)

    def test_name_is_stripped(self):
        result, _, _ = self._resolve("  Globex  ")
        self.assertEqual(result, _GLOBEX_ID)

    def test_unknown_name_aborts(self):
        with self.assertRaises(typer.Exit):
            self._resolve("Initech")

    def test_empty_team_list_aborts(self):
        with self.assertRaises(typer.Exit):
            self._resolve("Acme", orgs=[])

    def test_failed_fetch_aborts(self):
        with self.assertRaises(typer.Exit):
            self._resolve("Acme", fetch_side_effect=RuntimeError("boom"))

    def test_no_name_prompts(self):
        with (
            patch("nextmv.cli.configuration.create.fetch_organizations", return_value=_ORGS),
            patch("nextmv.cli.configuration.create.choice", return_value="Globex") as mock_choice,
        ):
            result = _resolve_team_id(access_token="tok", endpoint="api.cloud.nextmv.io", team_name=None)

        self.assertEqual(result, _GLOBEX_ID)
        mock_choice.assert_called_once()


class TestResolveTeamIdById(unittest.TestCase):
    """Tests for --team-id, which must not list teams."""

    def _resolve(self, team_id, team_name=None):
        with (
            patch("nextmv.cli.configuration.create.fetch_organizations") as mock_fetch,
            patch("nextmv.cli.configuration.create.choice") as mock_choice,
        ):
            result = _resolve_team_id(
                access_token="tok",
                endpoint="api.cloud.nextmv.io",
                team_name=team_name,
                team_id=team_id,
            )
            return result, mock_fetch, mock_choice

    def test_id_is_used_without_listing_teams(self):
        """The reason the flag exists: no call to the teams endpoint."""
        result, mock_fetch, mock_choice = self._resolve(_ACME_ID)

        self.assertEqual(result, _ACME_ID)
        mock_fetch.assert_not_called()
        mock_choice.assert_not_called()

    def test_id_is_stripped(self):
        result, _, _ = self._resolve(f"  {_ACME_ID}  ")
        self.assertEqual(result, _ACME_ID)

    def test_id_does_not_need_to_be_a_team_the_listing_would_return(self):
        """An unlisted ID is accepted; only the API can judge it."""
        other = "00000000-0000-4000-8000-000000000000"
        result, mock_fetch, _ = self._resolve(other)

        self.assertEqual(result, other)
        mock_fetch.assert_not_called()

    def test_team_name_passed_as_id_aborts(self):
        """The likely mistake: passing a name to --team-id."""
        with self.assertRaises(typer.Exit):
            self._resolve("Acme")

    def test_malformed_id_aborts(self):
        with self.assertRaises(typer.Exit):
            self._resolve("6b1f3a52-3c4d-4e5f-8a9b")

    def test_empty_id_aborts(self):
        with self.assertRaises(typer.Exit):
            self._resolve("   ")

    def test_id_takes_precedence_over_name(self):
        """The command rejects both flags, but the resolver still has an order."""
        result, mock_fetch, _ = self._resolve(_ACME_ID, team_name="Globex")

        self.assertEqual(result, _ACME_ID)
        mock_fetch.assert_not_called()


class TestTeamFlagsAreMutuallyExclusive(unittest.TestCase):
    """Tests that --team and --team-id cannot be combined."""

    def setUp(self):
        self.runner = CliRunner()
        # An API key in the environment takes precedence over --auth-type pkce,
        # which would skip the pkce path these tests assert on.
        self.env_api_key = os.getenv("NEXTMV_API_KEY")
        os.environ.pop("NEXTMV_API_KEY", None)

    def tearDown(self):
        if self.env_api_key is not None:
            os.environ["NEXTMV_API_KEY"] = self.env_api_key

    def test_both_flags_rejected(self):
        with patch("nextmv.cli.configuration.create._create_pkce_profile") as mock_create:
            result = self.runner.invoke(
                app,
                ["configuration", "create", "--auth-type", "pkce", "--team", "Acme", "--team-id", _ACME_ID],
            )

        self.assertEqual(result.exit_code, 1)
        mock_create.assert_not_called()

    def test_team_id_alone_is_accepted(self):
        with patch("nextmv.cli.configuration.create._create_pkce_profile") as mock_create:
            result = self.runner.invoke(
                app,
                ["configuration", "create", "--auth-type", "pkce", "--team-id", _ACME_ID],
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_create.call_args[1]["team_id"], _ACME_ID)
        self.assertIsNone(mock_create.call_args[1]["team"])

    def test_team_alone_is_accepted(self):
        with patch("nextmv.cli.configuration.create._create_pkce_profile") as mock_create:
            result = self.runner.invoke(
                app,
                ["configuration", "create", "--auth-type", "pkce", "--team", "Acme"],
            )

        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(mock_create.call_args[1]["team"], "Acme")
        self.assertIsNone(mock_create.call_args[1]["team_id"])


if __name__ == "__main__":
    unittest.main()
