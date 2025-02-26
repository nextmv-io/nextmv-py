import time
import unittest

import nextmv_gurobipy as ngp

import nextmv


class TestStatistics(unittest.TestCase):
    def test_to_nextmv(self):
        start_time = time.time()
        opt = ngp.ModelOptions().to_nextmv()
        model = ngp.Model(opt)
        model.optimize()
        stats = ngp.ModelStatistics(model, run_duration_start=start_time)

        self.assertIsNotNone(stats)
        self.assertIsInstance(stats, nextmv.Statistics)
        self.assertIsInstance(stats.run, nextmv.RunStatistics)
        self.assertIsInstance(stats.result, nextmv.ResultStatistics)

        self.assertGreaterEqual(stats.run.duration, 0.0)
        self.assertEqual(stats.result.value, 0.0)
        self.assertGreaterEqual(stats.result.duration, 0.0)
        self.assertDictEqual(stats.result.custom, {"status": "OPTIMAL", "variables": 0, "constraints": 0})
