import unittest

from nextmv.cloud.safe import _name_and_id


class TestSafeNameID(unittest.TestCase):
    def test_safe_name_id(self):
        name, id = _name_and_id(prefix="inpset", entity_id="scenario-1")
        self.assertIn("Inpset Scenario 1", name)
        self.assertIn("inpset-scenario-1", id)
