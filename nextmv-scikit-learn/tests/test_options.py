import json
import os
import unittest

from nextmv_sklearn.dummy import DummyRegressorOptions
from nextmv_sklearn.ensemble import GradientBoostingRegressorOptions, RandomForestRegressorOptions
from nextmv_sklearn.linear_model import LinearRegressionOptions
from nextmv_sklearn.neural_network import MLPRegressorOptions
from nextmv_sklearn.tree import DecisionTreeRegressorOptions


class TestOptions(unittest.TestCase):
    def test_imports(self):
        dum_opt = DummyRegressorOptions()
        self.assertIsNotNone(dum_opt)
        n_dum_opt = dum_opt.to_nextmv()
        got = n_dum_opt.parameters_dict()
        self.compare(got, "dummy")

        gbr_opt = GradientBoostingRegressorOptions()
        self.assertIsNotNone(gbr_opt)

        rf_opt = RandomForestRegressorOptions()
        self.assertIsNotNone(rf_opt)

        lr_opt = LinearRegressionOptions()
        self.assertIsNotNone(lr_opt)

        nn_opt = MLPRegressorOptions()
        self.assertIsNotNone(nn_opt)

        dt_opt = DecisionTreeRegressorOptions()
        self.assertIsNotNone(dt_opt)

    def compare(self, got: dict[str, any], expected_path: str):
        path = os.path.join(os.path.dirname(__file__), f"expected_{expected_path}_options.json")
        with open(path) as f:
            expected = json.load(f)

        self.assertListEqual(got, expected)
