import unittest
from typing import Any

from nextmv_sklearn.dummy import DummyRegressor, DummyRegressorOptions, DummyRegressorStatistics
from nextmv_sklearn.ensemble import (
    GradientBoostingRegressor,
    GradientBoostingRegressorOptions,
    GradientBoostingRegressorStatistics,
    RandomForestRegressor,
    RandomForestRegressorOptions,
    RandomForestRegressorStatistics,
)
from nextmv_sklearn.linear_model import LinearRegression, LinearRegressionOptions, LinearRegressionStatistics
from nextmv_sklearn.neural_network import MLPRegressor, MLPRegressorOptions, MLPRegressorStatistics
from nextmv_sklearn.tree import DecisionTreeRegressor, DecisionTreeRegressorOptions, DecisionTreeRegressorStatistics
from sklearn.datasets import load_diabetes

import nextmv


class TestModel(unittest.TestCase):
    def setUp(self):
        X, y = load_diabetes(return_X_y=True)
        self.X = X
        self.y = y

    def test_dummy(self):
        dum_opt = DummyRegressorOptions().to_nextmv()
        dum_reg = DummyRegressor(dum_opt)
        self.assert_statistics(dum_reg, DummyRegressorStatistics)

    def test_ensemble(self):
        gb_opt = GradientBoostingRegressorOptions().to_nextmv()
        gb_reg = GradientBoostingRegressor(gb_opt)
        self.assert_statistics(gb_reg, GradientBoostingRegressorStatistics)

        rf_opt = RandomForestRegressorOptions().to_nextmv()
        rf_reg = RandomForestRegressor(rf_opt)
        self.assert_statistics(rf_reg, RandomForestRegressorStatistics)

    def test_linear_model(self):
        lm_opt = LinearRegressionOptions().to_nextmv()
        lm_reg = LinearRegression(lm_opt)
        self.assert_statistics(lm_reg, LinearRegressionStatistics)

    def test_neural_network(self):
        nn_opt = MLPRegressorOptions().to_nextmv()
        nn_reg = MLPRegressor(nn_opt)
        self.assert_statistics(nn_reg, MLPRegressorStatistics)

    def test_tree(self):
        dt_opt = DecisionTreeRegressorOptions().to_nextmv()
        dt_reg = DecisionTreeRegressor(dt_opt)
        self.assert_statistics(dt_reg, DecisionTreeRegressorStatistics)

    def assert_statistics(self, model: Any, statistics: callable):
        fit = model.fit(self.X, self.y)
        stats: nextmv.Statistics = statistics(fit, self.X, self.y)
        self.assertIsNotNone(fit)
        self.assertIsNotNone(stats)

        stats_dict = stats.to_dict()
        self.assertIsInstance(stats_dict, dict)
        self.assertGreaterEqual(len(stats_dict), 3)

        custom = stats.result.custom
        self.assertIsInstance(custom, dict)
        self.assertGreaterEqual(len(custom), 1)
