"""Tests for the _get_client helper and ProfileSession isolation."""

import asyncio
import contextvars
import unittest
from unittest.mock import patch


class TestGetClient(unittest.TestCase):
    """Tests for the _get_client helper."""

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "test-key-123"}, clear=False)
    def test_get_client_from_env(self):
        """Test that _get_client uses NEXTMV_API_KEY env var."""
        from nextmv.cli.mcp.server import _get_client

        client = _get_client()
        self.assertEqual(client.api_key, "test-key-123")
        self.assertEqual(client.url, "https://api.cloud.nextmv.io")

    @patch.dict("os.environ", {"NEXTMV_API_KEY": "key", "NEXTMV_ENDPOINT": "custom.api.io"}, clear=False)
    def test_get_client_custom_endpoint(self):
        """Test that _get_client respects NEXTMV_ENDPOINT env var."""
        from nextmv.cli.mcp.server import _get_client

        client = _get_client()
        self.assertEqual(client.url, "https://custom.api.io")

    @patch.dict("os.environ", {}, clear=True)
    @patch("nextmv.cli.mcp.tools._helpers.Client", side_effect=Exception("no config"))
    def test_get_client_no_key_no_config_raises(self, mock_client):
        """Test that _get_client raises when no API key or config is available."""
        from nextmv.cli.mcp.server import _get_client

        with self.assertRaises(ValueError) as ctx:
            _get_client()
        self.assertIn("Could not build a Nextmv client", str(ctx.exception))


class TestProfileSessionIsolation(unittest.TestCase):
    """Tests for ProfileSession async context isolation."""

    def test_profile_default_is_none(self):
        """A fresh ProfileSession starts with profile=None."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        self.assertIsNone(s.profile)

    def test_profile_set_get(self):
        """Setting and getting profile works."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        s.profile = "staging"
        self.assertEqual(s.profile, "staging")
        s.profile = None
        self.assertIsNone(s.profile)

    def test_async_context_isolation(self):
        """Profile set in one asyncio.run() does not leak to the next."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()

        async def set_profile():
            s.profile = "isolated"
            return s.profile

        # Set profile inside async context.
        result = asyncio.run(set_profile())
        self.assertEqual(result, "isolated")

        # Outside that context (new asyncio.run), the profile should be default.
        async def get_profile():
            return s.profile

        result = asyncio.run(get_profile())
        self.assertIsNone(result)

    def test_copied_contexts_are_isolated(self):
        """Two copied contexts have independent profile state."""
        from nextmv.cli.mcp.tools._helpers import ProfileSession

        s = ProfileSession()
        results = {}

        def run_a():
            s.profile = "alpha"
            results["a"] = s.profile

        def run_b():
            s.profile = "beta"
            results["b"] = s.profile

        ctx_a = contextvars.copy_context()
        ctx_b = contextvars.copy_context()
        ctx_a.run(run_a)
        ctx_b.run(run_b)

        self.assertEqual(results["a"], "alpha")
        self.assertEqual(results["b"], "beta")
