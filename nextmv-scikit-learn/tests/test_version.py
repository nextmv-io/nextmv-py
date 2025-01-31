import unittest

import nextmv_sklearn as nsklearn


class TestLogger(unittest.TestCase):
    def test_version(self):
        exported_version = nsklearn.VERSION
        expected_version = nsklearn.__about__.__version__
        self.assertEqual(exported_version, expected_version)
