import unittest
from typing import Any

from nextmv_sklearn.dummy import DummyRegressor, DummyRegressorOptions
from nextmv_sklearn.ensemble import (
    GradientBoostingRegressor,
    GradientBoostingRegressorOptions,
    RandomForestRegressor,
    RandomForestRegressorOptions,
)
from nextmv_sklearn.linear_model import LinearRegression, LinearRegressionOptions
from nextmv_sklearn.neural_network import MLPRegressor, MLPRegressorOptions
from nextmv_sklearn.tree import DecisionTreeRegressor, DecisionTreeRegressorOptions
from sklearn.datasets import load_diabetes


class TestModel(unittest.TestCase):
    def setUp(self):
        X, y = load_diabetes(return_X_y=True)
        self.X = X
        self.y = y

    def test_dummy(self):
        dum_opt = DummyRegressorOptions().to_nextmv()
        dum_reg = DummyRegressor(dum_opt)
        self.assert_model(dum_reg)

    def test_ensemble(self):
        gb_opt = GradientBoostingRegressorOptions().to_nextmv()
        gb_reg = GradientBoostingRegressor(gb_opt)
        self.assert_model(gb_reg)

        rf_opt = RandomForestRegressorOptions().to_nextmv()
        rf_reg = RandomForestRegressor(rf_opt)
        self.assert_model(rf_reg)

    def test_linear_model(self):
        lm_opt = LinearRegressionOptions().to_nextmv()
        lm_reg = LinearRegression(lm_opt)
        self.assert_model(lm_reg)

    def test_neural_network(self):
        nn_opt = MLPRegressorOptions().to_nextmv()
        nn_reg = MLPRegressor(nn_opt)
        self.assert_model(nn_reg)

    def test_tree(self):
        dt_opt = DecisionTreeRegressorOptions().to_nextmv()
        dt_reg = DecisionTreeRegressor(dt_opt)
        self.assert_model(dt_reg)

    def assert_model(self, model: Any):
        fit = model.fit(self.X, self.y)
        pred = model.predict(self.X[:1])
        self.assertIsNotNone(fit)
        self.assertIsNotNone(pred)
        self.assertEqual(len(pred), 1)
        self.assertIsInstance(pred[0], float)
        self.assertGreaterEqual(pred[0], 0)
