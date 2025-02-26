import unittest

import nextmv_gurobipy as ngp


class TestModel(unittest.TestCase):
    def test_model(self):
        # Super simple test to check that instantiating a model works.
        opt = ngp.ModelOptions().to_nextmv()
        model = ngp.Model(opt)
        model.optimize()

        obj = model.ObjVal
        self.assertEqual(obj, 0.0)
