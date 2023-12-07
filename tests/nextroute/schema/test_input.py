import json
import os
import unittest

from nextmv.nextroute.schema import Input


class TestInput(unittest.TestCase):
    def test_from_json(self):
        filepath = os.path.join(os.path.dirname(__file__), "input.json")
        input = Input.from_json(filepath)
        parsed = input.to_dict()
        with open(filepath) as f:
            expected = json.load(f)

        self.maxDiff = None
        self.assertEqual(
            parsed,
            expected,
            "Parsing the JSON into the class and back should yield the same result.",
        )
