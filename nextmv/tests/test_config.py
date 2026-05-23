"""
Unit tests for the configuration helpers in nextmv.config.
"""

import unittest

from nextmv.config import (
    PROFILE_TYPE_API_KEY,
    PROFILE_TYPE_AUTH_FLOW,
    get_profile_type,
    list_auth_flow_profiles,
)


class TestGetProfileType(unittest.TestCase):
    """Tests for get_profile_type helper."""

    def test_default_profile_no_key_returns_api_key(self):
        config = {"apikey": "sk-xxx", "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(get_profile_type(config, None), PROFILE_TYPE_API_KEY)

    def test_default_profile_auth_flow(self):
        config = {"profile_type": PROFILE_TYPE_AUTH_FLOW, "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(get_profile_type(config, None), PROFILE_TYPE_AUTH_FLOW)

    def test_named_profile_api_key(self):
        config = {
            "staging": {
                "apikey": "sk-yyy",
                "endpoint": "api.cloud.nextmv.io",
                "profile_type": PROFILE_TYPE_API_KEY,
            }
        }
        self.assertEqual(get_profile_type(config, "staging"), PROFILE_TYPE_API_KEY)

    def test_named_profile_auth_flow(self):
        config = {
            "auth-profile": {
                "endpoint": "api.cloud.nextmv.io",
                "profile_type": PROFILE_TYPE_AUTH_FLOW,
            }
        }
        self.assertEqual(get_profile_type(config, "auth-profile"), PROFILE_TYPE_AUTH_FLOW)

    def test_named_profile_missing_type_defaults_to_api_key(self):
        config = {"legacy": {"apikey": "sk-zzz", "endpoint": "api.cloud.nextmv.io"}}
        self.assertEqual(get_profile_type(config, "legacy"), PROFILE_TYPE_API_KEY)


class TestListAuthFlowProfiles(unittest.TestCase):
    """Tests for list_auth_flow_profiles helper."""

    def test_no_auth_profiles(self):
        config = {"apikey": "sk-xxx", "endpoint": "api.cloud.nextmv.io"}
        self.assertEqual(list_auth_flow_profiles(config), [])

    def test_default_auth_profile(self):
        config = {"profile_type": PROFILE_TYPE_AUTH_FLOW, "endpoint": "api.cloud.nextmv.io"}
        self.assertIn(None, list_auth_flow_profiles(config))

    def test_named_auth_profile(self):
        config = {
            "myauth": {
                "profile_type": PROFILE_TYPE_AUTH_FLOW,
                "endpoint": "api.cloud.nextmv.io",
            },
            "apionly": {
                "apikey": "sk",
                "endpoint": "api.cloud.nextmv.io",
            },
        }
        result = list_auth_flow_profiles(config)
        self.assertIn("myauth", result)
        self.assertNotIn("apionly", result)

    def test_mixed_profiles(self):
        config = {
            "profile_type": PROFILE_TYPE_AUTH_FLOW,
            "endpoint": "api.cloud.nextmv.io",
            "named-auth": {"profile_type": PROFILE_TYPE_AUTH_FLOW, "endpoint": "api.cloud.nextmv.io"},
            "named-api": {"apikey": "sk", "endpoint": "api.cloud.nextmv.io"},
        }
        result = list_auth_flow_profiles(config)
        self.assertIn(None, result)
        self.assertIn("named-auth", result)
        self.assertNotIn("named-api", result)


if __name__ == "__main__":
    unittest.main()
