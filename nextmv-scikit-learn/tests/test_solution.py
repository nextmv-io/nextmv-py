import os
import unittest
from typing import Any

from nextmv_sklearn.dummy import DummyRegressor, DummyRegressorOptions, DummyRegressorSolution, DummyRegressorStatistics
from nextmv_sklearn.ensemble import (
    GradientBoostingRegressor,
    GradientBoostingRegressorOptions,
    GradientBoostingRegressorSolution,
    GradientBoostingRegressorStatistics,
    RandomForestRegressor,
    RandomForestRegressorOptions,
    RandomForestRegressorSolution,
    RandomForestRegressorStatistics,
)
from nextmv_sklearn.linear_model import (
    LinearRegression,
    LinearRegressionOptions,
    LinearRegressionSolution,
    LinearRegressionStatistics,
)
from nextmv_sklearn.neural_network import (
    MLPRegressor,
    MLPRegressorOptions,
    MLPRegressorSolution,
    MLPRegressorStatistics,
)
from nextmv_sklearn.tree import (
    DecisionTreeRegressor,
    DecisionTreeRegressorOptions,
    DecisionTreeRegressorSolution,
    DecisionTreeRegressorStatistics,
)
from sklearn.datasets import load_diabetes

import nextmv


class TestModel(unittest.TestCase):
    SOLUTION_FILE_NAME = "solution_output.json"

    def setUp(self):
        X, y = load_diabetes(return_X_y=True)
        self.X = X
        self.y = y

    def tearDown(self):
        if os.path.exists(self.SOLUTION_FILE_NAME):
            os.remove(self.SOLUTION_FILE_NAME)

    def test_dummy(self):
        dum_opt = DummyRegressorOptions().to_nextmv()
        dum_reg = DummyRegressor(dum_opt)
        self.assert_load_model(
            opt=dum_opt,
            model=dum_reg,
            solution_class=DummyRegressorSolution,
            statistics=DummyRegressorStatistics,
        )

    def test_ensemble(self):
        gb_opt = GradientBoostingRegressorOptions().to_nextmv()
        gb_reg = GradientBoostingRegressor(gb_opt)
        self.assert_load_model(
            opt=gb_opt,
            model=gb_reg,
            solution_class=GradientBoostingRegressorSolution,
            statistics=GradientBoostingRegressorStatistics,
        )

        rf_opt = RandomForestRegressorOptions().to_nextmv()
        rf_reg = RandomForestRegressor(rf_opt)
        self.assert_load_model(
            opt=rf_opt,
            model=rf_reg,
            solution_class=RandomForestRegressorSolution,
            statistics=RandomForestRegressorStatistics,
        )

    def test_linear_model(self):
        lm_opt = LinearRegressionOptions().to_nextmv()
        lm_reg = LinearRegression(lm_opt)
        self.assert_load_model(
            opt=lm_opt,
            model=lm_reg,
            solution_class=LinearRegressionSolution,
            statistics=LinearRegressionStatistics,
        )

    def test_neural_network(self):
        nn_opt = MLPRegressorOptions().to_nextmv()
        nn_reg = MLPRegressor(nn_opt)
        self.assert_load_model(
            opt=nn_opt,
            model=nn_reg,
            solution_class=MLPRegressorSolution,
            statistics=MLPRegressorStatistics,
        )

    def test_tree(self):
        dt_opt = DecisionTreeRegressorOptions().to_nextmv()
        dt_reg = DecisionTreeRegressor(dt_opt)
        self.assert_load_model(
            opt=dt_opt,
            model=dt_reg,
            solution_class=DecisionTreeRegressorSolution,
            statistics=DecisionTreeRegressorStatistics,
        )

    def assert_load_model(
        self,
        opt: nextmv.Options,
        model: Any,
        solution_class: Any,
        statistics: callable,
    ):
        fit = model.fit(self.X, self.y)
        self.assertIsNotNone(fit)

        sol = solution_class.from_model(fit)
        self.assertIsNotNone(sol)

        stats: nextmv.Statistics = statistics(fit, self.X, self.y)

        output = nextmv.Output(
            options=opt,
            solution=sol.to_dict(),
            statistics=stats,
        )

        nextmv.write(output, self.SOLUTION_FILE_NAME)

        nm_input = nextmv.load(path=self.SOLUTION_FILE_NAME)

        sol_2 = nextmv.from_dict(nm_input.data["solution"])
        self.assertIsNotNone(sol_2)

        fit_2 = sol_2.to_model()
        self.assertIsNotNone(fit_2)

        pred = fit_2.predict(self.X[:1])
        self.assertIsNotNone(pred)
        self.assertEqual(len(pred), 1)
        self.assertIsInstance(pred[0], float)
        self.assertGreaterEqual(pred[0], 0)
