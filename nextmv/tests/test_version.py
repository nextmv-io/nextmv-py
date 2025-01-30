import unittest

import nextmv


class TestLogger(unittest.TestCase):
    def test_version(self):
        exported_version = nextmv.VERSION
        expected_version = nextmv.__about__.__version__
        self.assertEqual(exported_version, expected_version)
