import json
import os
import unittest
from typing import Any

from nextmv_sklearn.dummy import DummyRegressorOptions
from nextmv_sklearn.ensemble import GradientBoostingRegressorOptions, RandomForestRegressorOptions
from nextmv_sklearn.linear_model import LinearRegressionOptions
from nextmv_sklearn.neural_network import MLPRegressorOptions
from nextmv_sklearn.tree import DecisionTreeRegressorOptions


class TestOptions(unittest.TestCase):
    def test_dummy(self):
        opt = DummyRegressorOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "dummy")

    def test_ensemble(self):
        opt = GradientBoostingRegressorOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "gradient_boosting")

        opt = RandomForestRegressorOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "random_forest")

    def test_linear_model(self):
        opt = LinearRegressionOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "linear_regression")

    def test_neural_network(self):
        opt = MLPRegressorOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "mlp_regressor")

    def test_tree(self):
        opt = DecisionTreeRegressorOptions()
        self.assertIsNotNone(opt)
        self.compare(opt, "decision_tree")

    def compare(self, opt: Any, expected_path: str):
        n_opt = opt.to_nextmv()
        got = n_opt.options_dict()

        path = os.path.join(os.path.dirname(__file__), f"expected_{expected_path}_option_parameters.json")
        with open(path) as f:
            expected = json.load(f)

        self.assertListEqual(got, expected)
