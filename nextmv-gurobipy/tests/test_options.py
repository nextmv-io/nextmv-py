import json
import os
import unittest

import nextmv_gurobipy as ngp


class TestModelOptions(unittest.TestCase):
    def test_to_nextmv(self):
        gopt = ngp.ModelOptions()
        nopt = gopt.to_nextmv()
        got = nopt.parameters_dict()

        path = os.path.join(os.path.dirname(__file__), "expected_option_parameters.json")
        with open(path) as f:
            expected = json.load(f)

        self.assertListEqual(got, expected)
