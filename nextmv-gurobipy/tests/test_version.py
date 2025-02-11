import unittest

import nextmv_gurobipy as ngp


class TestLogger(unittest.TestCase):
    def test_version(self):
        exported_version = ngp.VERSION
        expected_version = ngp.__about__.__version__
        self.assertEqual(exported_version, expected_version)
