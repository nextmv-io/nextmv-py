import datetime
import json
import unittest

import nextmv.serialization


class TestSerialization(unittest.TestCase):
    """Tests for the common serialization functionality."""

    def test_default_serialization(self):
        """Test the default serialization"""

        data = {
            "name": "Test",
            "value": 42,
            "timestamp": nextmv.serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        serialized = nextmv.serialization.serialize_json(data)
        expected = json.dumps(
            {
                "name": "Test",
                "value": 42,
                "timestamp": "2023-10-01T00:00:00",
            },
            separators=(",", ":"),
        )
        self.assertEqual(serialized, expected)

    def test_custom_serialization(self):
        """Test custom serialization with additional configurations"""

        data = {
            "name": "Test",
            "value": 42,
            "timestamp": nextmv.serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        json_configurations = {
            "indent": 2,
            "default": nextmv.serialization._custom_serial,
            "separators": (",", ": "),
        }
        serialized = nextmv.serialization.serialize_json(data, json_configurations)
        expected = json.dumps(
            {
                "name": "Test",
                "value": 42,
                "timestamp": "2023-10-01T00:00:00",
            },
            indent=2,
            separators=(",", ": "),
        )
        self.assertEqual(serialized, expected)
