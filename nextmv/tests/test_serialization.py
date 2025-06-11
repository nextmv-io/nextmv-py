import datetime
import json
import unittest

import nextmv._serialization


class TestSerialization(unittest.TestCase):
    """Tests for the common serialization functionality."""

    def test_default_serialization(self):
        """Test the default serialization"""

        data = {
            "name": "Test",
            "value": 42,
            "timestamp": nextmv._serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        serialized = nextmv._serialization.serialize_json(data)
        expected = json.dumps(
            {
                "name": "Test",
                "value": 42,
                "timestamp": "2023-10-01T00:00:00",
            },
            indent=2,
        )
        self.assertEqual(serialized, expected)

    def test_default_deflated_serialization(self):
        """Test the default deflated serialization"""

        data = {
            "name": "Test",
            "value": 42,
            "timestamp": nextmv._serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        serialized = nextmv._serialization.deflated_serialize_json(data)
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
            "timestamp": nextmv._serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        json_configurations = {
            "indent": 2,
            "default": nextmv._serialization._custom_serial,
            "separators": (",", ": "),
        }
        serialized = nextmv._serialization.serialize_json(data, json_configurations)
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

    def test_compressed_serialization(self):
        """Test a requested compressed serialization"""

        data = {
            "name": "Test",
            "value": 42,
            "timestamp": nextmv._serialization._custom_serial(datetime.datetime(2023, 10, 1)),
        }
        json_configurations = {
            "separators": (",", ":"),  # Remove spaces for a compressed format
            "indent": None,  # No indentation for compressed format
        }
        serialized = nextmv._serialization.serialize_json(data, json_configurations)
        expected = json.dumps(
            {
                "name": "Test",
                "value": 42,
                "timestamp": "2023-10-01T00:00:00",
            },
            separators=(",", ":"),
            indent=None,
        )
        self.assertEqual(serialized, expected)
