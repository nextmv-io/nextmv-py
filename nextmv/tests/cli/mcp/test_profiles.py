"""Tests for profile management tools."""

import asyncio
import json
import unittest
from unittest.mock import MagicMock, patch


class TestProfiles(unittest.TestCase):
    """Tests for profile management tools."""

    def test_mask_key(self):
        """Test that _mask_key masks keys correctly."""
        from nextmv.cli.mcp.server import _mask_key

        self.assertIsNone(_mask_key(None))
        self.assertEqual(_mask_key("abcd"), "XXXX")
        self.assertEqual(_mask_key("abc"), "XXX")
        self.assertEqual(_mask_key("abcde12345"), "XXXXXX2345")

    def test_set_and_get_profile(self):
        """Test that cloud_set_profile and cloud_get_profile work together."""
        from nextmv.cli.mcp.server import create_server

        mock_config = {
            "apikey": "test-key",
            "endpoint": "api.cloud.nextmv.io",
            "staging": {
                "apikey": "stg-key",
                "endpoint": "staging.api.nextmv.io",
            },
        }

        with patch(
            "nextmv.cli.mcp.tools.profile.load_config",
            return_value=mock_config,
        ):
            server = create_server()
            set_tool = server._tool_manager._tools["cloud_set_profile"]
            get_tool = server._tool_manager._tools["cloud_get_profile"]

            # Default profile.
            result = asyncio.run(get_tool.run({}))
            text = json.loads(result[0].text) if hasattr(result[0], "text") else str(result)
            self.assertIn("default", str(text))

            # Set and get must run in the same async context for the
            # ContextVar state to be visible, since asyncio.run() creates
            # a fresh context each time.
            async def _set_then_get(profile: str) -> str:
                await set_tool.run({"profile": profile})
                result = await get_tool.run({})
                return json.loads(result[0].text) if hasattr(result[0], "text") else str(result)

            # Switch to a named profile.
            text = asyncio.run(_set_then_get("staging"))
            self.assertIn("staging", str(text))

            # Switch back to default.
            text = asyncio.run(_set_then_get("default"))
            self.assertIn("default", str(text))

    def test_list_profiles(self):
        """Test that cloud_list_profiles reads config correctly."""
        from nextmv.cli.mcp.server import create_server

        mock_config = {
            "apikey": "my-secret-key-1234",
            "endpoint": "api.cloud.nextmv.io",
            "staging": {
                "apikey": "stg-key-5678",
                "endpoint": "staging.api.nextmv.io",
            },
        }

        with patch(
            "nextmv.cli.mcp.tools.profile.load_config",
            return_value=mock_config,
        ):
            server = create_server()
            tool = server._tool_manager._tools["cloud_list_profiles"]
            result = asyncio.run(tool.run({}))
            profiles = json.loads(result[0].text) if hasattr(result[0], "text") else result
            self.assertEqual(len(profiles), 2)
            self.assertEqual(profiles[0]["name"], "default")
            self.assertEqual(profiles[0]["endpoint"], "api.cloud.nextmv.io")
            self.assertIn("1234", profiles[0]["api_key"])
            self.assertNotIn("my-secret", profiles[0]["api_key"])
            self.assertEqual(profiles[1]["name"], "staging")
            self.assertIn("5678", profiles[1]["api_key"])

    @patch.dict("os.environ", {}, clear=True)
    @patch("nextmv.cli.mcp.tools._helpers.Client")
    def test_get_client_uses_profile(self, mock_client):
        """Test that _get_client passes the profile to Client."""
        from nextmv.cli.mcp.tools._helpers import session

        mock_client.return_value = MagicMock()

        # Explicit profile override.
        session.get_client(profile="staging")
        mock_client.assert_called_with(profile="staging")

        # Session-level profile.
        session.profile = "prod"
        try:
            session.get_client()
            mock_client.assert_called_with(profile="prod")
        finally:
            session.profile = None

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "env-key"}, clear=False)
    def test_get_client_env_skipped_when_profile_set(self):
        """Test that env var is skipped when a profile is active."""
        from nextmv.cli.mcp.tools._helpers import session

        with patch("nextmv.cli.mcp.tools._helpers.Client") as mock_client:
            mock_client.return_value = MagicMock()
            session.profile = "staging"
            try:
                session.get_client()
                mock_client.assert_called_with(profile="staging")
            finally:
                session.profile = None
